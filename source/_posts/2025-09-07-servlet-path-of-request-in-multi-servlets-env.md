---
id: servlet-path-of-request-in-multi-servlets-env
title: "多 Servlet 环境下，请求的 ServletPath 是什么"
description: "默认 Servlet 跟其他 Servlet 的 ServletPath 有所不同"
date: 2025.09.07 10:34
categories:
    - Java
    - Servlet
tags: [Java, Servlet]
keywords: Servlet, HttpServletRequest, ServletPath, PathInfo, Tomcat, Jetty, Undertow, Jakarta
cover: /contents/covers/servlet-path-of-request-in-multi-servlets-env.png
---

Servlet
=======

Servlet 是 Java EE（现为 Jakarta EE）规范中的一个重要组件，用于处理客户端请求并生成动态响应。Servlet 通常运行在 Servlet 容器（如 Apache Tomcat、Jetty 等）中，负责接收 HTTP 请求、处理业务逻辑并返回 HTTP 响应。

以下内容引自 [廖雪峰的官方网站 - 手写Tomcat - Servlet规范](https://liaoxuefeng.com/books/jerrymouse/servlet-spec/index.html)：

> Servlet规范有好几个版本，每个版本都有一些新的功能。以下是一些常见版本的新功能：
> 
> Servlet 1.0：定义了Servlet组件，一个Servlet组件运行在Servlet容器（Container）中，通过与容器交互，就可以响应一个HTTP请求；
> 
> Servlet 2.0：定义了JSP组件，一个JSP页面可以被动态编译为Servlet组件；
> 
> Servlet 2.4：定义了Filter（过滤器）组件，可以实现过滤功能；
> 
> Servlet 2.5：支持注解，提供了ServletContextListener接口，增加了一些安全性相关的特性；
> 
> Servlet 3.0：支持异步处理的Servlet，支持注解配置Servlet和过滤器，增加了SessionCookieConfig接口；
> 
> Servlet 3.1：提供了WebSocket的支持，增加了对HTTP请求和响应的流式操作的支持，增加了对HTTP协议的新特性的支持；
> 
> Servlet 4.0：支持HTTP/2的新特性，提供了HTTP/2的Server Push等特性；
> 
> Servlet 5.0：主要是把javax.servlet包名改成了jakarta.servlet；
> 
> Servlet 6.0：继续增加一些新功能，并废除一部分功能。

Servlet 4.0 及之前的规范，可以从 https://jcp.org/en/jsr/summary?id=servlet 获取：

- [JSR-000369 Java Servlet 4.0 Specification Final Release](https://download.oracle.com/otndocs/jcp/servlet-4-final-spec/index.html)
- [Online JavaDoc](https://jakarta.ee/specifications/servlet/4.0/apidocs/)

Servlet 5.0 及之后的规范，可直接在线获取：

- [Jakarta Servlet Specification 6.1](https://jakarta.ee/specifications/servlet/6.1/jakarta-servlet-spec-6.1)
- [Online JavaDoc](https://javadoc.io/doc/jakarta.servlet/jakarta.servlet-api/)
- [Project jakartaee/servlet on GitHub](https://github.com/jakartaee/servlet)

Maven 坐标从 4.0.2 开始，由

```xml
<!-- https://mvnrepository.com/artifact/javax.servlet/javax.servlet-api -->
<dependency>
    <groupId>javax.servlet</groupId>
    <artifactId>javax.servlet-api</artifactId>
    <version>4.0.1</version>
    <scope>provided</scope>
</dependency>
```

更换为：

```xml
<!-- https://mvnrepository.com/artifact/jakarta.servlet/jakarta.servlet-api -->
<dependency>
    <groupId>jakarta.servlet</groupId>
    <artifactId>jakarta.servlet-api</artifactId>
    <version>4.0.2</version>
    <scope>provided</scope>
</dependency>
```

源码 package 从 5.0 开始由 [javax.servlet](https://github.com/jakartaee/servlet/tree/4.0.4-RELEASE/api/src/main/java/javax/servlet) 更换为 [jakarta.servlet](https://github.com/jakartaee/servlet/tree/5.0.0-RELEASE/api/src/main/java/jakarta/servlet)。


附：Servlet 规范相关资源
----------------------

- [Jakarta Servlet 4.0~6.2](https://jakarta.ee/specifications/servlet/)
- [Jakarta Servlet GitHub Pages](https://jakartaee.github.io/servlet/)
- [Java Community Process](https://jcp.org/en/jsr/summary?id=servlet)
- [Eclipse EE4J Servlet Project](https://projects.eclipse.org/projects/ee4j.servlet)


HttpServletRequest.getServletPath()
===================================

Servlet 规范中，`HttpServletRequest` 接口关于 `getServletPath()` 方法的描述如下。

[Servlet 4.0](https://jakarta.ee/specifications/servlet/4.0/apidocs/javax/servlet/http/httpservletrequest#getServletPath--)

```java
    /**
     * Returns the part of this request's URL that calls the servlet. This path
     * starts with a "/" character and includes either the servlet name or a
     * path to the servlet, but does not include any extra path information or a
     * query string. Same as the value of the CGI variable SCRIPT_NAME.
     * <p>
     * This method will return an empty string ("") if the servlet used to
     * process this request was matched using the "/*" pattern.
     *
     * @return a <code>String</code> containing the name or path of the servlet
     *         being called, as specified in the request URL, decoded, or an
     *         empty string if the servlet used to process the request is
     *         matched using the "/*" pattern.
     */
    public String getServletPath();
```

[Servlet 6.1](https://github.com/jakartaee/servlet/blob/6.1.0-RELEASE/api/src/main/java/jakarta/servlet/http/HttpServletRequest.java#L432-L452)

```java
    /**
     * Returns the part of this request's URL that calls the servlet. This path starts with a "/" character and includes the
     * path to the servlet, but does not include any extra path information or a query string.
     *
     * <p>
     * This method will return an empty string ("") if the servlet used to process this request was matched using the "/*"
     * pattern.
     *
     * @return a <code>String</code> containing the path of the servlet being called, as specified in the request URL, or an
     * empty string if the servlet used to process the request is matched using the "/*" pattern. The path will be
     * canonicalized as per <a href=
     * "https://jakarta.ee/specifications/servlet/6.0/jakarta-servlet-spec-6.0.html#request-uri-path-processing">Servlet
     * 6.0, 3.5</a>. This method will not return any encoded characters unless the container is configured specifically to
     * allow them.
     * @throws IllegalArgumentException In standard configuration, this method will never throw. However, a container may be
     * configured to not reject some suspicious sequences identified by <a href=
     * "https://jakarta.ee/specifications/servlet/6.0/jakarta-servlet-spec-6.0.html#uri-path-canonicalization">Servlet 6.0,
     * 3.5.2<a/>, furthermore the container may be configured to allow such paths to only be accessed via safer methods like
     * {@link #getRequestURI()} and to throw IllegalArgumentException if this method is called for such suspicious paths.
     */
    String getServletPath();
```

两个版本细节处有些区别，没有本质差异。

规范文档中，针对 `requestURI` 的组成部分及各部分含义有明确的说明，以及一个简明的例子：

> requestURI = contextPath + servletPath + pathInfo

有三个 Servlet：

> |Context Path|/catalog|
> |:-----------|:-------|
> |Servlet Mapping|Pattern: `/lawn/*`<br>Servlet: `LawnServlet`|
> |Servlet Mapping|Pattern: `/garden/*`<br>Servlet: `GardenServlet`|
> |Servlet Mapping|Pattern: `*.jsp`<br>Servlet: `JSPServlet`|

不同请求 URI 对应的各部分值：

> |Request Path|Path Elements|
> |:-----------|:------------|
> |/catalog/lawn/index.html|ContextPath: `/catalog`<br>ServletPath: `/lawn`<br>PathInfo: `/index.html`|
> |/catalog/garden/implements/|ContextPath: `/catalog`<br>ServletPath: `/garden`<br>PathInfo: `/implements/`|
> |/catalog/help/feedback.jsp|ContextPath: `/catalog`<br>ServletPath: `/help/feedback.jsp`<br>PathInfo: null|

可以看到其中 `ServletPath` 与 `Servlet Mapping` 的 `Pattern` 是对应的。

但是这个例子中没有提到存在匹配 `/*` 路径的 Servlet 的情况。按照接口描述中说明，此时返回的 `ServletPath` 应该是空字符串 `""`。让我们看看一些 Servlet 容器实际的实现情况。


Demo 工程
=========

延续 [还在给每个请求加前缀避免模块间接口冲突呢？](https://alphahinex.github.io/2020/04/24/multi-dispatcherservlet/)  中构造的 demo 工程 [multi-dispatcher](https://github.com/AlphaHinex/multi-dispatcher)，略微调整以适应本文示例需求。

通过 env 参数切换使用不同的 Servlet 容器：

```bash
# 默认使用 tomcat 容器
$ ./gradlew bootRun
# 使用 jetty 容器
$ ./gradlew bootRun -Denv=jetty
# 使用 undertow 容器
$ ./gradlew bootRun -Denv=undertow
```

添加 `--args='--server.servlet.context-path=/demo'` 指定上下文根：

```bash
$ ./gradlew bootRun -Denv=undertow --args='--server.servlet.context-path=/demo'
```

启动后可通过类似下面的日志验证使用的容器：

```log
2025-09-06 11:18:52.297  INFO 6679 --- [           main] o.s.b.w.e.u.UndertowServletWebServer     : Undertow started on port(s) 8080 (http) with context path '/demo'
```

之后访问如下地址：

- http://localhost:8080/demo/same/path
- http://localhost:8080/demo/foo/same/path
- http://localhost:8080/demo/bar/same/path

示例响应：

```json
{
  "Context Path": "/demo",
  "Request URL": "http://localhost:8080/demo/foo/same/path",
  "Servlet Path": "/foo",
  "Request URI": "/demo/foo/same/path",
  "Servlet": "Foo Servlet",
  "Path Info": "/same/path",
  "URL Mapping": "/foo/*"
}
```

Tomcat 的实现
=============

在 [Servlet 注册到了哪？](https://alphahinex.github.io/2020/04/30/where-are-servlets/) 和 [Tomcat 是怎么找到用来处理请求的 Servlet 的？](https://alphahinex.github.io/2020/08/02/how-request-find-servlet/) 中，我们梳理过 Tomcat 处理请求的过程。本文继续以 Tomcat 9 为例，说明其实现 Servlet 4.0 规范的情况，Tomcat 版本与 Servlet 版本的对应关系可见：[Apache Tomcat Versions](https://tomcat.apache.org/whichversion.html)。

[org.apache.catalina.connector.Request](https://github.com/apache/tomcat/blob/9.0.109/java/org/apache/catalina/connector/Request.java#L2273-L2276) 实现了 `HttpServletRequest` 接口，对 `getServletPath()` 方法的实现如下：

```java
    @Override
    public String getServletPath() {
        return mappingData.wrapperPath.toStringType();
    }
```

`mappingData` 是在 [org.apache.catalina.connector.CoyoteAdapter.postParseRequest](https://github.com/apache/tomcat/blob/9.0.109/java/org/apache/catalina/connector/CoyoteAdapter.java#L697) 方法中映射上的：

```java
connector.getService().getMapper().map(serverName, decodedURI, version, request.getMappingData());
```

不同类型的 Servlet，对 [MappingData](https://github.com/apache/tomcat/blob/9.0.109/java/org/apache/catalina/mapper/MappingData.java) 的 `wrapperPath` 的设置方式不同。

默认 Serlvet：

[Mapper.internalMapWrapper](https://github.com/apache/tomcat/blob/9.0.109/java/org/apache/catalina/mapper/Mapper.java#L950-L957)

```java
        // Rule 7 -- Default servlet
        if (mappingData.wrapper == null && !checkJspWelcomeFiles) {
            if (contextVersion.defaultWrapper != null) {
                mappingData.wrapper = contextVersion.defaultWrapper.object;
                mappingData.requestPath.setChars(path.getBuffer(), path.getStart(), path.getLength());
                mappingData.wrapperPath.setChars(path.getBuffer(), path.getStart(), path.getLength());
                mappingData.matchType = MappingMatch.DEFAULT;
            }
        ...
```

通配符匹配的 Servlet：

[Mapper.internalMapWildcardWrapper](https://github.com/apache/tomcat/blob/9.0.109/java/org/apache/catalina/mapper/Mapper.java#L1052-L1062)

```java
            if (found) {
                mappingData.wrapperPath.setString(wrappers[pos].name);
                if (path.getLength() > length) {
                    mappingData.pathInfo.setChars(path.getBuffer(), path.getStart() + length,
                            path.getLength() - length);
                }
                mappingData.requestPath.setChars(path.getBuffer(), path.getStart(), path.getLength());
                mappingData.wrapper = wrappers[pos].object;
                mappingData.jspWildCard = wrappers[pos].jspWildCard;
                mappingData.matchType = MappingMatch.PATH;
            }
```

实测
----

```bash
$ ./gradlew bootRun --args='--server.servlet.context-path=/demo'
```

| Servlet                   | Default Servlet             | Foo Servlet                 |
|---------------------------|-----------------------------|-----------------------------|
| url mapping               | `/*`                        | `/foo/*`                    |
| request.getContextPath()  | `/demo`                     | `/demo`                     |
| request.getServletPath()  | `/same/path`                | `/foo`                      |
| request.PathInfo()        |                             | `/same/path`                |
| request.getRequestURI()   | `/demo/same/path`           | `/demo/foo/same/path`       |
| request.getRequestURL()   | `http://localhost:8080/demo/same/path` | `http://localhost:8080/demo/foo/same/path` |

由默认 Servlet（URL mapping 是 `/*`）处理的请求，其 `ServletPath` 是请求的实际路径，跟 Servlet 规范中描述的情况不一致：

> **Servlet Path**: The path section that directly corresponds to the mapping which
> activated this request. This path starts with a ’/’ character except in the case
> where the request is matched with the ‘/*’ or ““ pattern, in which case it is an
> empty string

Jetty 和 Undertow 的结果
=======================

以下面命令分别切换容器启动：

```bash
$ ./gradlew bootRun -Denv=jetty --args='--server.servlet.context-path=/demo'
$ ./gradlew bootRun -Denv=undertow --args='--server.servlet.context-path=/demo'
```

结果与使用 Tomcat 容器的情况一致，均是：

| Servlet                   | Default Servlet             | Foo Servlet                 |
|---------------------------|-----------------------------|-----------------------------|
| url mapping               | `/*`                        | `/foo/*`                    |
| request.getContextPath()  | `/demo`                     | `/demo`                     |
| request.getServletPath()  | `/same/path`                | `/foo`                      |
| request.PathInfo()        |                             | `/same/path`                |
| request.getRequestURI()   | `/demo/same/path`           | `/demo/foo/same/path`       |
| request.getRequestURL()   | `http://localhost:8080/demo/same/path` | `http://localhost:8080/demo/foo/same/path` |


结论
====

目前三个主流的开源 Servlet 容器：Tomcat、Jetty 和 Undertow，处理请求的 ServletPath 方式基本一致：
1. 由默认 Servlet 处理的请求，其 ServletPath 是请求的实际路径（Context Path 之后，不包括请求参数等）；
1. 非默认 Servlet 处理的请求，其 ServletPath 是 Servlet 的映射路径，不包括请求的实际路径。
