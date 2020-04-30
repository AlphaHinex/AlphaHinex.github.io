---
id: where-are-servlets
title: "Servlet 注册到了哪？"
description: "注册到了 Servlet 容器？没毛病！但马达马达大内！"
date: 2020.04.30 19:34
categories:
    - Spring
tags: [Java, Spring, Servlet, Tomcat]
keywords: Spring, Servlet, DispatcherServlet, ServletRegistrationBean, Spring Boot, Tomcat, Catalina, Container, Engine, Host, Context, Wrapper
cover: /contents/where-are-servlets/cover.png
---

按 [还在给每个请求加前缀避免模块间接口冲突呢？](https://alphahinex.github.io/2020/04/24/multi-dispatcherservlet/) 中内容，我们可以通过 `ServletRegistrationBean` 注册多个 `DispatcherServlet`，那么 `Servlet` 被注册到哪了呢？

简单的回答：Servlet 容器。

没毛病！但马达马达大内！注册到了 Servlet 容器里的哪？存在什么结构里？

让我们以 Tomcat 容器为例，刨根问底。

## addRegistration

在 `ServletRegistrationBean` 中，有一个 [addRegistration](https://github.com/spring-projects/spring-boot/blob/v2.2.2.RELEASE/spring-boot-project/spring-boot/src/main/java/org/springframework/boot/web/servlet/ServletRegistrationBean.java#L175-L179) 方法，将具体的 Servlet 添加到了 ServletContext 中。

```java
@Override
protected ServletRegistration.Dynamic addRegistration(String description, ServletContext servletContext) {
  String name = getServletName();
  return servletContext.addServlet(name, this.servlet);
}
```

## addServlet

Servlet 容器负责提供 ServletContext 接口的实现。
在 Tomcat 中，ServletContext 的实现类为 [org.apache.catalina.core.ApplicationContext](https://github.com/apache/tomcat/blob/9.0.29/java/org/apache/catalina/core/ApplicationContext.java)。

其私有的 addServlet 方法，将注册的 Servlet [放入了 Wrapper 中](https://github.com/apache/tomcat/blob/9.0.29/java/org/apache/catalina/core/ApplicationContext.java#L947)。

```java
wrapper.setServlet(servlet);
```

[org.apache.catalina.Wrapper](https://github.com/apache/tomcat/blob/9.0.29/java/org/apache/catalina/Wrapper.java) 会被作为 child 加入到 [StandardContext](https://github.com/apache/tomcat/blob/9.0.29/java/org/apache/catalina/core/StandardContext.java) 中。

## addChild

StandardContext 的 addChild 方法，会调用基类 [ContainerBase](https://github.com/apache/tomcat/blob/9.0.29/java/org/apache/catalina/core/ContainerBase.java) 的同名方法，进而调用 [ContainerBase#addChildInternal](https://github.com/apache/tomcat/blob/9.0.29/java/org/apache/catalina/core/ContainerBase.java#L694)，完成注册工作。

```java
synchronized(children) {
    if (children.get(child.getName()) != null)
        throw new IllegalArgumentException(
                sm.getString("containerBase.child.notUnique", child.getName()));
    child.setParent(this);  // May throw IAE
    children.put(child.getName(), child);
}
```

## 结论

Servlet 实例被包装至 StandardWrapper，注册到了其父容器 StandardContext 从基类 [ContainerBase](https://github.com/apache/tomcat/blob/9.0.29/java/org/apache/catalina/core/ContainerBase.java#L163) 继承的一个 `HashMap` 里。

```java
/**
 * The child Containers belonging to this Container, keyed by name.
 */
protected final HashMap<String, Container> children = new HashMap<>();
```

## 引申内容

在 Tomcat Catalina 中，[Container](https://github.com/apache/tomcat/blob/9.0.29/java/org/apache/catalina/Container.java) 负责执行收到的请求，并基于请求返回响应。

Container 又扩展出[四个接口](https://github.com/apache/tomcat/blob/9.0.29/java/org/apache/catalina/Container.java#L39-L48)：

1. Engine：代表整个 Catalina servlet 引擎，一般是包括一个或多个子容器，即 Host 或 Context 的实现，或其他自定义组。
1. Host：表示一个有拥有数个 Context 的虚拟主机。
1. Context：表示一个 ServletContext，包含一个或多个支持 Servlet 的 Wrapper。
1. Wrapper：表示一个独立的 Servlet。

![Container](/contents/where-are-servlets/container.png)
