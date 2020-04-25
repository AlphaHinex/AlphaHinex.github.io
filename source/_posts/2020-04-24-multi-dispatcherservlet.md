---
id: multi-dispatcherservlet
title: "还在给每个请求加前缀避免模块间接口冲突呢？"
description: "优雅解决 RequestMapping url 冲突"
date: 2020.04.24 19:26
categories:
    - Spring
tags: [Java, Spring, Servlet, MVC]
keywords: Spring, Servlet, DispatcherServlet, Spring Boot, ServletRegistrationBean, AnnotationConfigWebApplicationContext, WebMvcConfigurer, EnableWebMvc, WebMvcConfigurationSupport
cover: /contents/covers/multi-dispatcherservlet.jpg
---

场景
===

Spring MVC 按模块开发时，可能经常会遇到这个场景：一个模块由一个开发人员负责开发，模块内能较好的保证 RequestMapping 的 path 不重复，但模块间就很难有效的方式保证唯一。

通常有两种处理方式：

1. 对开发进行规范或约定，为每个模块起一个前缀，要求在模块内开发的所有 controller 都带上前缀，这样就只要保证模块内唯一即可。
1. 每个模块部署为单独的服务，通过 servlet context path 进行区分。

两种方式都能解决问题，但同时也都会带来一些问题：

1. 依赖开发、给开发带来额外负担、不够优雅；如果已经存在海量已完成的 controller，需要统一处理增加前缀。
1. 可能导致本不需要拆分为独立服务的不合理拆分，服务粒度过细，造成额外负担。

有没有更优雅的解决方案呢？


分析
===

答案是肯定的。

定义多个 servlet 就好了嘛，每个 servlet 可以设定单独的 url mapping，同样能起到增加前缀的效果，一劳永逸，成本低，不增加额外负担。

Spring MVC 使用 `DispatcherServlet` 处理请求，在其 [JavaDoc](https://github.com/spring-projects/spring-framework/blob/v5.2.2.RELEASE/spring-webmvc/src/main/java/org/springframework/web/servlet/DispatcherServlet.java#L143-L146) 中有如下说明：

>  * <p><b>A web application can define any number of DispatcherServlets.</b>
 * Each servlet will operate in its own namespace, loading its own application context
 * with mappings, handlers, etc. Only the root application context as loaded by
 * {@link org.springframework.web.context.ContextLoaderListener}, if any, will be shared.

传统 Spring MVC 项目中有 `web.xml` 文件，可以使用 `<servlet>` 及 `<servlet-mapping>` 配置多个 DispatcherServlet。

但在 Spring Boot 环境中，自动配置了一个开箱即用的 DispatcherServlet，映射路径为 `/`，而且没有了 `web.xml`，这个时候如果我们想配置多个 DispatcherServlet 要怎么做呢？

Spring Boot 提供了一个 `org.springframework.boot.web.servlet.ServletRegistrationBean` 来满足注册 servlet 的需求，可以像注册 bean 一样配置 servlet。


实例
===

直接上实例：https://github.com/AlphaHinex/multi-dispatcher

实例中定义了三个 Controller，分别对应默认的 DispatcherServlet 和自定义的两个不同的 url mapping：

```java
@Bean
public ServletRegistrationBean fooServlet() {
    DispatcherServlet fooServlet = new DispatcherServlet();

    AnnotationConfigWebApplicationContext context = new AnnotationConfigWebApplicationContext();
    context.register(FooConfiguration.class);
    fooServlet.setApplicationContext(context);

    ServletRegistrationBean<DispatcherServlet> bean = new ServletRegistrationBean<>(fooServlet, "/foo/*");
    bean.setName("Foo servlet");
    bean.setLoadOnStartup(1);
    return bean;
}

@Bean
public ServletRegistrationBean barServlet() {
    AnnotationConfigWebApplicationContext context = new AnnotationConfigWebApplicationContext();
    context.scan("alpha.hinex.demo.bar");
    DispatcherServlet barServlet = new DispatcherServlet(context);
    ServletRegistrationBean<DispatcherServlet> bean = new ServletRegistrationBean<>(barServlet, "/bar/*");
    bean.setName("Bar servlet");
    bean.setLoadOnStartup(1);
    return bean;
}
```

按不同方式为两个自定义的 DispatcherServlet 进行配置：

```java
@Configuration
@EnableWebMvc
@ComponentScan("alpha.hinex.demo.foo.controller")
public class FooConfiguration implements WebMvcConfigurer {
}
```

```java
@Configuration
public class BarConfiguration extends WebMvcConfigurationSupport {
}
```

两个对应自定义 DispatcherServlet 的 Controller 上配置的 RequestMapping 的 path 是相同的 `/same/path`。

可在实例中，启动应用进行验证，或执行集成测试验证效果。详细可见实例 [README](https://github.com/AlphaHinex/multi-dispatcher/README.md)。
