---
id: spring-security-context-disappeared
title: "消失的 Spring Security Context"
description: "一个诡异的登录信息消失问题调查"
date: 2026.11.29 10:34
categories:
    - Spring
    - Java
tags: [Spring Security, Java, Spring]
keywords: Spring Security, SPRING_SECURITY_CONTEXT, SaveContextOnUpdateOrErrorResponseWrapper, HttpSessionSecurityContextRepository, saveContext, flush, response, onResponseCommitted
cover: /contents/spring-security-context-disappeared/cover.png
---

## 现象

一个接口的两个相似实现，实现中都通过新线程操作了原始 HTTP 请求线程的响应。在调用其中一个之后，再访问任何需要登录的接口，都会返回 403 Forbidden。另一个实现则不会出现这个问题。项目使用 Spring Security 做登录认证。

## 可重现问题的 MVP

[mvp.zip](https://github.com/AlphaHinex/AlphaHinex.github.io/tree/develop/source/contents/spring-security-context-disappeared/mvp.zip) 提供了一个可以复现问题的 Spring Boot MVP。

在 Java 11 以上环境通过 `./mvnw spring-boot:run` 启动后，可按如下操作重现问题：

```Bash
# 1. 登录，保存 session cookie
curl -i -c /tmp/cookies.txt -d 'username=user&password=password' http://localhost:8080/login

# 2. /me 正常
curl -i -b /tmp/cookies.txt http://localhost:8080/me
# -> 200 user / [ROLE_USER]

# 3. background-first streaming
curl -N -b /tmp/cookies.txt http://localhost:8080/stream/background-first

# 4. BUG：/me 现在返回 403
curl -i -b /tmp/cookies.txt http://localhost:8080/me
# -> 403 Forbidden
```

## 根因

### 1. 新线程中调用 OutputStream.flush()

访问问题接口 `/stream/background-first` 时，将 `ServletOutputStream` 发送给了新的线程，在新线程中第一次调用了 `flush()`：

```java
/** First response commit happens on the worker thread. */
@GetMapping(value = "/stream/background-first", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public void backgroundFirst(HttpServletResponse response) throws Exception {
    response.setContentType("text/event-stream;charset=utf-8");
    ServletOutputStream outputStream = response.getOutputStream();
    // IMPORTANT: no write/flush on the request thread before the worker work.
    runWorker(outputStream);
}

private final ExecutorService executor = Executors.newCachedThreadPool(r -> {
    Thread thread = new Thread(r);
    thread.setName("stream-worker");
    thread.setDaemon(true);
    return thread;
});

private void runWorker(ServletOutputStream outputStream) throws InterruptedException {
    CountDownLatch latch = new CountDownLatch(1);
    executor.submit(() -> {
        try {
            outputStream.write("data: from-worker-thread\n\n".getBytes(StandardCharsets.UTF_8));
            outputStream.flush();
            outputStream.write("data: [DONE]\n\n".getBytes(StandardCharsets.UTF_8));
            outputStream.flush();
        } catch (IOException e) {
            System.err.println("worker write failed: " + e);
        } finally {
            latch.countDown();
        }
    });
    latch.await();
}
```

### 2. flush 触发了 onResponseCommitted

在 Spring Security 环境中，这个 outputStream 实际是 [OnCommittedResponseWrapper.SaveContextServletOutputStream](https://github.com/spring-projects/spring-security/blob/187895ce347cb342820b9f9eccbd594baad970d2/web/src/main/java/org/springframework/security/web/util/OnCommittedResponseWrapper.java#L537)，[flush](https://github.com/spring-projects/spring-security/blob/main/web/src/main/java/org/springframework/security/web/util/OnCommittedResponseWrapper.java#L552C15-L552C20) 在新线程上触发 [SaveContextOnUpdateOrErrorResponseWrapper.onResponseCommitted](https://github.com/spring-projects/spring-security/blob/187895ce347cb342820b9f9eccbd594baad970d2/web/src/main/java/org/springframework/security/web/context/SaveContextOnUpdateOrErrorResponseWrapper.java#L104)，进而调用 [HttpSessionSecurityContextRepository.SaveToSessionResponseWrapper.saveContext](https://github.com/spring-projects/spring-security/blob/187895ce347cb342820b9f9eccbd594baad970d2/web/src/main/java/org/springframework/security/web/context/HttpSessionSecurityContextRepository.java#L396)，其中下面代码会将 `SPRING_SECURITY_CONTEXT` session 属性删除：

```java
if (httpSession != null && this.authBeforeExecution != null) {
    // SEC-1587 A non-anonymous context may still be in the session
    // SEC-1735 remove if the contextBeforeExecution was not anonymous
    httpSession.removeAttribute(springSecurityContextKey);
    ...
```

### 3. Spring Security 版本小于 5.4.4

Spring Security 5.4.3 及更早版本中，[HttpSessionSecurityContextRepository.saveContext](https://github.com/spring-projects/spring-security/blob/5.4.3/web/src/main/java/org/springframework/security/web/context/HttpSessionSecurityContextRepository.java#L142) 在 Context 被保存过之后，不会再次调用 `responseWrapper.saveContext`：

```java
// saveContext() might already be called by the response wrapper if something in
// the chain called sendError() or sendRedirect(). This ensures we only call it
// once per request.
if (!responseWrapper.isContextSaved()) {
    responseWrapper.saveContext(context);
}
```

这就导致前面非请求线程将 Spring Security Context 清除之后，没有机会再通过请求线程将正确的 Spring Security Context 保存回 session，**也就是导致这个问题的根本原因**。

## 日志证据

以下日志来自实际运行，开启了 `logging.level.org.springframework.security.web.context=DEBUG`。

**5.4.3（background-first，触发 403）**：

```log
[nio-8080-exec-5] Set SecurityContextHolder to SecurityContextImpl [Authentication=UsernamePasswordAuthenticationToken...]
[stream-worker]     Did not store empty SecurityContext
[nio-8080-exec-5] Cleared SecurityContextHolder to complete request
                      ↑ 没有 "Stored"，saveContext 被 isContextSaved() 守卫跳过
```

**5.4.4（background-first，未触发 403）**：

```log
[nio-8080-exec-4] Set SecurityContextHolder to SecurityContextImpl [Authentication=UsernamePasswordAuthenticationToken...]
[stream-worker]     Did not store empty SecurityContext
[nio-8080-exec-4] Stored SecurityContextImpl [Authentication=UsernamePasswordAuthenticationToken...]
                      ↑ 又写回去了！request 线程 finally 的 saveContext 照常执行
[nio-8080-exec-4] Cleared SecurityContextHolder to complete request
```

## 解决方案

### 方案一：升级 Spring Security 到 5.4.4+

Spring Security 5.4.4 及之后版本，经由 [c72a6fa](https://github.com/spring-projects/spring-security/commit/c72a6fac04853912a4b7caad5f0500f2aace5a79) 对这部分逻辑进行了优化，将“是否已保存”的状态管理内聚到包装器内部：新代码移除了外部的 `isContextSaved()` 检查，改为在 `SaveToSessionResponseWrapper` 内部新增一个 `isSaveContextInvoked` 布尔字段。这个字段在真正执行了会话属性设置（`setAttribute`）或移除（r`emoveAttribute`）时被置为 `true`。这确保了 `SecurityContextPersistenceFilter` 的 [doFilter](https://github.com/spring-projects/spring-security/blob/187895ce347cb342820b9f9eccbd594baad970d2/web/src/main/java/org/springframework/security/web/context/SecurityContextPersistenceFilter.java#L123) 方法在 finally 块中，会在 **request 线程** 上执行一次 `repository.saveContext(context, request, response)`。这次 save 携带的是 filter 开头 `loadContext` 拿到的完整登录 context —— 不是空的，所以会在 `HttpSessionSecurityContextRepository.saveContext` 中再次将 context 放回 session 中。

```java
// We may have a new session, so check also whether the context attribute
// is set SEC-1561
if (contextChanged(context) || httpSession.getAttribute(springSecurityContextKey) == null) {
    httpSession.setAttribute(springSecurityContextKey, context);
    this.isSaveContextInvoked = true;
    if (this.logger.isDebugEnabled()) {
        this.logger.debug(LogMessage.format("Stored %s to HttpSession [%s]", context, httpSession));
    }
}
```

### 方案二：请求线程先 flush

如果不能升级 Spring Security，可以让第一次 commit 发生在 request 线程，携带登录 context。worker 线程的 commit 是空操作（因为 `contextSaved` 已经是 `true`）：

```java
@GetMapping(value = "/stream/background-first-fixed", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public void backgroundFirstFixed(HttpServletResponse response) throws Exception {
    response.setContentType("text/event-stream;charset=utf-8");
    ServletOutputStream outputStream = response.getOutputStream();
    response.flushBuffer(); // 请求线程先 commit，携带登录 context
    runWorker(outputStream);
}
```
