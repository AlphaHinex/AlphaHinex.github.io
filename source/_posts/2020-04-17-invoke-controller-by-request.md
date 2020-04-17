---
id: invoke-controller-by-request
title: "Spring 中如何根据请求调用对应方法"
description: "给你个 HttpServletRequest，怎么调到对应 Spring Controller 的方法并获得返回值？"
date: 2020.04.17 19:34
categories:
    - Spring
tags: [Java, Spring, Servlet, MVC]
keywords: Spring, Servlet, DispatcherServlet, HttpServletRequest, HandlerMapping, HandlerAdapter, RequestMapping, RequestMappingHandlerMapping, RequestMappingHandlerAdapter
cover: /contents/invoke-controller-by-request/spring-mvc.jpg
---

需求
===

假设能够获得到一个 `HttpServletRequest`，需要根据这个请求内的具体信息，找到其所对应的 Spring Controller 中的方法，并对方法进行调用，获得该方法的返回值。


分析
===

这个需求，与 `DispatcherServlet` 的作用非常类似。先看一下请求到达 `DispatcherServlet` 之后的处理流程：

![DispatcherServlet Processing](/contents/invoke-controller-by-request/spring-mvc.jpg)

因为最终目标是获得请求对应的 Controller 方法的返回值，所以上图中的流程走到第 4 步即可。

1. HttpServletRequest 请求抵达 DispatcherServlet
1. 通过 HandlerMapping 将请求映射到处理器（Handler)和拦截器
1. 通过 Handler 找到对应的 HandlerAdapter
1. 通过 HandlerAdapter 调用处理器

以 [Spring Framework v5.2.2.RELEASE](https://github.com/spring-projects/spring-framework/tree/v5.2.2.RELEASE) 版本为例，
看看 DispatcherServlet 实现上述功能的过程：

## HttpServletRequest 请求抵达 DispatcherServlet

HttpServletRequest 被 Servlet 容器和 Spring Framework 送至  [org.springframework.web.servlet.DispatcherServlet#doService](https://github.com/spring-projects/spring-framework/blob/v5.2.2.RELEASE/spring-webmvc/src/main/java/org/springframework/web/servlet/DispatcherServlet.java#L910)，之后委托 [org.springframework.web.servlet.DispatcherServlet#doDispatch](https://github.com/spring-projects/spring-framework/blob/v5.2.2.RELEASE/spring-webmvc/src/main/java/org/springframework/web/servlet/DispatcherServlet.java#L1000) 执行真正的请求分发。

## 通过 HandlerMapping 将请求映射到处理器（Handler)和拦截器

在 `doDispatch` 中，调用 `getHandler` 方法，根据 `HttpServletRequest` 获得 `HandlerExecutionChain`。

[DispatcherServlet.java#L1224-L1241](https://github.com/spring-projects/spring-framework/blob/v5.2.2.RELEASE/spring-webmvc/src/main/java/org/springframework/web/servlet/DispatcherServlet.java#L1224-L1241)
```java
/**
 * Return the HandlerExecutionChain for this request.
 * <p>Tries all handler mappings in order.
 * @param request current HTTP request
 * @return the HandlerExecutionChain, or {@code null} if no handler could be found
 */
@Nullable
protected HandlerExecutionChain getHandler(HttpServletRequest request) throws Exception {
    if (this.handlerMappings != null) {
        for (HandlerMapping mapping : this.handlerMappings) {
            HandlerExecutionChain handler = mapping.getHandler(request);
            if (handler != null) {
                return handler;
            }
        }
    }
    return null;
}
```

该方法中，遍历在该类上初始化好的所有 [HandlerMapping](https://github.com/spring-projects/spring-framework/blob/v5.2.2.RELEASE/spring-webmvc/src/main/java/org/springframework/web/servlet/HandlerMapping.java)，`HandlerMapping` 接口中定义的唯一一个方法，与上述方法签名相同。

[HandlerMapping.java#L132-L148](https://github.com/spring-projects/spring-framework/blob/v5.2.2.RELEASE/spring-webmvc/src/main/java/org/springframework/web/servlet/HandlerMapping.java#L132-L148)
```java
@Nullable
HandlerExecutionChain getHandler(HttpServletRequest request) throws Exception;
```

[HandlerExecutionChain](https://github.com/spring-projects/spring-framework/blob/v5.2.2.RELEASE/spring-webmvc/src/main/java/org/springframework/web/servlet/HandlerExecutionChain.java) 是一个包含一个处理器（Handler）和一个拦截器（HandlerInterceptor）集合的结构体，其中的 Handler 就是我们需要的 Controller。

## 通过 Handler 找到对应的 HandlerAdapter

从 `HandlerExecutionChain` 中获得到 handler 之后，可以根据 handler 找到对应的适配器（HandlerAdapter）。

[DispatcherServlet.java#L1262-L1277](https://github.com/spring-projects/spring-framework/blob/v5.2.2.RELEASE/spring-webmvc/src/main/java/org/springframework/web/servlet/DispatcherServlet.java#L1262-L1277)
```java
/**
 * Return the HandlerAdapter for this handler object.
 * @param handler the handler object to find an adapter for
 * @throws ServletException if no HandlerAdapter can be found for the handler. This is a fatal error.
 */
protected HandlerAdapter getHandlerAdapter(Object handler) throws ServletException {
    if (this.handlerAdapters != null) {
        for (HandlerAdapter adapter : this.handlerAdapters) {
            if (adapter.supports(handler)) {
                return adapter;
            }
        }
    }
    throw new ServletException("No adapter for handler [" + handler +
            "]: The DispatcherServlet configuration needs to include a HandlerAdapter that supports this handler");
}
```

[HandlerAdapter](https://github.com/spring-projects/spring-framework/blob/v5.2.2.RELEASE/spring-webmvc/src/main/java/org/springframework/web/servlet/HandlerAdapter.java) 接口定义了三个方法：

```java
boolean supports(Object handler);

@Nullable
ModelAndView handle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception;

long getLastModified(HttpServletRequest request, Object handler);
```

## 通过 HandlerAdapter 调用处理器

可以看到 `handle` 方法的返回值类型是 `ModelAndView`，即此方法完成了上图中的 4、5 两步。而我们的需求中只需要根据请求找到并调用 Controller 对应的方法，并获得该方法的返回值。

Spring 为其 Controller 提供了 HandlerMapping 和 HandlerAdapter 接口的对应实现：[RequestMappingHandlerMapping](https://github.com/spring-projects/spring-framework/blob/v5.2.2.RELEASE/spring-webmvc/src/main/java/org/springframework/web/servlet/mvc/method/annotation/RequestMappingHandlerMapping.java) 和 [RequestMappingHandlerAdapter](https://github.com/spring-projects/spring-framework/blob/v5.2.2.RELEASE/spring-webmvc/src/main/java/org/springframework/web/servlet/mvc/method/annotation/RequestMappingHandlerAdapter.java)。

### RequestMappingHandlerMapping

![RequestMappingHandlerMapping](/contents/invoke-controller-by-request/RequestMappingHandlerMapping.png)

抽象类 `AbstractHandlerMapping` 在实现 `HanlderMapping` 接口的 `getHandler` 方法时，将获得具体 handler 的方法委托给了抽象方法 `getHandlerInternal`。

[AbstractHandlerMapping.java#L441-L442](https://github.com/spring-projects/spring-framework/blob/v5.2.2.RELEASE/spring-webmvc/src/main/java/org/springframework/web/servlet/handler/AbstractHandlerMapping.java#L441-L442)
```java
@Nullable
protected abstract Object getHandlerInternal(HttpServletRequest request) throws Exception;
```

继承了这个抽象类的 `AbstractHandlerMethodMapping` 将 `getHandlerInternal` 方法的返回值类型具体化为了 `HandlerMethod`。

[AbstractHandlerMethodMapping.java#L358-L373](https://github.com/spring-projects/spring-framework/blob/v5.2.2.RELEASE/spring-webmvc/src/main/java/org/springframework/web/servlet/handler/AbstractHandlerMethodMapping.java#L358-L373)
```java
/**
 * Look up a handler method for the given request.
 */
@Override
protected HandlerMethod getHandlerInternal(HttpServletRequest request) throws Exception {
    String lookupPath = getUrlPathHelper().getLookupPathForRequest(request);
    request.setAttribute(LOOKUP_PATH, lookupPath);
    this.mappingRegistry.acquireReadLock();
    try {
        HandlerMethod handlerMethod = lookupHandlerMethod(lookupPath, request);
        return (handlerMethod != null ? handlerMethod.createWithResolvedBean() : null);
    }
    finally {
        this.mappingRegistry.releaseReadLock();
    }
}
```

[HandlerMethod](https://github.com/spring-projects/spring-framework/blob/v5.2.2.RELEASE/spring-web/src/main/java/org/springframework/web/method/HandlerMethod.java) 将 handler 的 method 信息进行了封装，可以方便的获得 method，bean，入参及返回值类型信息，以及注解等信息。

### RequestMappingHandlerAdapter

![RequestMappingHandlerAdapter](/contents/invoke-controller-by-request/RequestMappingHandlerAdapter.png)

在 `RequestMappingHandlerAdapter` 继承的 `AbstractHandlerMethodAdapter` 中，实现了 `HandlerAdapter` 中的 `handler` 方法，将 handler 具体化为 `HandlerMethod` 类型，并交由 `handlerInternal` 抽象方法进行实现。

[AbstractHandlerMethodAdapter.java#L79-L88](https://github.com/spring-projects/spring-framework/blob/v5.2.2.RELEASE/spring-webmvc/src/main/java/org/springframework/web/servlet/mvc/method/AbstractHandlerMethodAdapter.java#L79-L88)
```java
/**
 * This implementation expects the handler to be an {@link HandlerMethod}.
 */
@Override
@Nullable
public final ModelAndView handle(HttpServletRequest request, HttpServletResponse response, Object handler)
        throws Exception {

    return handleInternal(request, response, (HandlerMethod) handler);
}
```

`RequestMappingHandlerAdapter` 的 [handleInternal](https://github.com/spring-projects/spring-framework/blob/v5.2.2.RELEASE/spring-webmvc/src/main/java/org/springframework/web/servlet/mvc/method/annotation/RequestMappingHandlerAdapter.java#L771) 方法通过 [invokeHandlerMethod](https://github.com/spring-projects/spring-framework/blob/v5.2.2.RELEASE/spring-webmvc/src/main/java/org/springframework/web/servlet/mvc/method/annotation/RequestMappingHandlerAdapter.java#L845) 来调用 handler，并将结果封装为 `ModelAndView` 返回。

终于刨到根了！

### invokeHandlerMethod

先来看下方法签名：

```java
/**
 * Invoke the {@link RequestMapping} handler method preparing a {@link ModelAndView}
 * if view resolution is required.
 * @since 4.2
 * @see #createInvocableHandlerMethod(HandlerMethod)
 */
@Nullable
protected ModelAndView invokeHandlerMethod(HttpServletRequest request,
        HttpServletResponse response, HandlerMethod handlerMethod) throws Exception
```

方法体中，先根据 HandlerMethod 构建了一个 `ServletInvocableHandlerMethod`

```java
ServletInvocableHandlerMethod invocableMethod = createInvocableHandlerMethod(handlerMethod);
```

进行必要的设置（如入参解析器及返回值处理器等）之后，进行实际调用及处理：

```java
invocableMethod.invokeAndHandle(webRequest, mavContainer);
```

`ServletInvocableHandlerMethod` 的 [invokeAndHandle](https://github.com/spring-projects/spring-framework/blob/v5.2.2.RELEASE/spring-webmvc/src/main/java/org/springframework/web/servlet/mvc/method/annotation/ServletInvocableHandlerMethod.java#L103) 方法执行了实际调用并获得返回值对象：

```java
Object returnValue = invokeForRequest(webRequest, mavContainer, providedArgs);
```

`invokeForRequest` 为定义在 [InvocableHandlerMethod](https://github.com/spring-projects/spring-framework/blob/v5.2.2.RELEASE/spring-web/src/main/java/org/springframework/web/method/support/InvocableHandlerMethod.java) 中的方法，从请求中解析出具体 Controller 方法的入参，并通过反射进行调用。

```java
/**
 * Invoke the method after resolving its argument values in the context of the given request.
 * <p>Argument values are commonly resolved through
 * {@link HandlerMethodArgumentResolver HandlerMethodArgumentResolvers}.
 * The {@code providedArgs} parameter however may supply argument values to be used directly,
 * i.e. without argument resolution. Examples of provided argument values include a
 * {@link WebDataBinder}, a {@link SessionStatus}, or a thrown exception instance.
 * Provided argument values are checked before argument resolvers.
 * <p>Delegates to {@link #getMethodArgumentValues} and calls {@link #doInvoke} with the
 * resolved arguments.
 * @param request the current request
 * @param mavContainer the ModelAndViewContainer for this request
 * @param providedArgs "given" arguments matched by type, not resolved
 * @return the raw value returned by the invoked method
 * @throws Exception raised if no suitable argument resolver can be found,
 * or if the method raised an exception
 * @see #getMethodArgumentValues
 * @see #doInvoke
 */
@Nullable
public Object invokeForRequest(NativeWebRequest request, @Nullable ModelAndViewContainer mavContainer,
        Object... providedArgs) throws Exception {

    Object[] args = getMethodArgumentValues(request, mavContainer, providedArgs);
    if (logger.isTraceEnabled()) {
        logger.trace("Arguments: " + Arrays.toString(args));
    }
    return doInvoke(args);
}
```


实现
====

综上，要满足本文开始处提到的需求，需要实现：

1. 根据请求找到对应的 RequestMappingHandlerMapping
1. 从 HandlerMapping 中获得 HandlerExecutionChain
1. 从 HandlerExecutionChain 中获得 HandlerMethod
1. 利用 HandlerMethod 构造一个 InvocableHandlerMethod
1. 根据 HandlerMethod 找到对应的 RequestMappingHandlerAdapter
1. 从 RequestMappingHandlerAdapter 中获得入参解析器集合
1. 调用 InvocableHandlerMethod 的 invokeForRequest 方法，获得实际返回值

关键部分代码如下：

```java
/**
 * Invoke controller method according to input request.
 * Could build a request with ArtificialHttpServletRequest
 *
 * @param  request http servlet request
 * @return output of controller method or null when could not mapping a controller
 * @throws Exception exception will be thrown when getHandler or invokeForRequest
 */
public Object invoke(HttpServletRequest request) throws Exception {
    // Find the handler method by request
    Optional<HandlerMethod> handlerMethod = handlerMethodHolder.getHandlerMethod(request);
    Assert.isTrue(handlerMethod.isPresent(), "Could NOT find handler method for request " + request.getRequestURI());
    InvocableHandlerMethod invocableHandlerMethod = new InvocableHandlerMethod(handlerMethod.get());

    // Set resolvers
    HandlerMethodArgumentResolverComposite composite = new HandlerMethodArgumentResolverComposite();
    RequestMappingHandlerAdapter handlerAdapter = getHandlerAdapter(invocableHandlerMethod);
    composite.addResolvers(handlerAdapter.getArgumentResolvers());
    invocableHandlerMethod.setHandlerMethodArgumentResolvers(composite);

    // Set data binder factory
    invocableHandlerMethod.setDataBinderFactory(
            new ServletRequestDataBinderFactory(new ArrayList<>(), new ConfigurableWebBindingInitializer()));

    NativeWebRequest nativeWebRequest = new DispatcherServletWebRequest(request);
    return invocableHandlerMethod.invokeForRequest(nativeWebRequest, new ModelAndViewContainer());
}
```

实例可见 [InvokeControllerByRequest.java](https://github.com/AlphaHinex/spring-roll/blob/develop/modules/raw-materials/roll-web/src/main/java/io/github/springroll/web/request/InvokeControllerByRequest.java) 及单元测试 [InvokeControllerByRequestTest.groovy](https://github.com/AlphaHinex/spring-roll/blob/develop/modules/raw-materials/roll-web/src/test/groovy/io/github/springroll/web/request/InvokeControllerByRequestTest.groovy)。