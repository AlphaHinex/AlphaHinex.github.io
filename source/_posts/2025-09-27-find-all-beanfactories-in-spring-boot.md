---
id: find-all-beanfactories-in-spring-boot
title: "如何找到 SpringBoot 应用中的所有 BeanFactory"
description: "纵向层级关系，横向关联关系"
date: 2025.09.27 10:26
categories:
    - Spring
tags: [Spring, Spring Boot, Java]
keywords: Spring, Spring Boot, Spring Framework, Java, debug, ApplicationContext, BeanFactory, DispatcherServlet, SpringBootApplication
cover: /contents/covers/find-all-beanfactories-in-spring-boot.png
---

在 [还在给每个请求加前缀避免模块间接口冲突呢？](https://alphahinex.github.io/2020/04/24/multi-dispatcherservlet/) 中，我们讨论了在一个 Spring Boot 应用中注册多个 `DispatcherServlet` 来实现应用上下文隔离的方案，以达到在不同 Servlet 关联的上下文中，注册相同 `RequestMapping` 的 `Controller`，乃至相同名称的 Bean 的效果。

在实际使用这种模式时，可能会遇到某些原因导致上下文隔离的效果跟预期不一致的情况，比如 `SpringBootApplication` 启动类上使用了 `@ComponentScan` 注解，导致某些 Bean 被注册到了多个上下文中，从而引发一些奇怪的问题。

为了排查这些问题，我们需要找到应用中所有的 `BeanFactory`，以及它们各自注册了哪些 Bean。

本文仍以 [multi-dispatcher](https://github.com/AlphaHinex/multi-dispatcher) demo 工程为例，给出通过 debug 方式加入的断点位置，以观察所有的 `BeanFactory` 及 `ApplicationContext`。

> 断点行数以 Spring Boot 2.2.2.RELEASE 和 Spring Framework 5.2.2.RELEASE 为例，不同版本可能会有差异。

# 根 ApplicationContext 及 BeanFactory

通常，Spring Boot 应用启动时，会包含如下 main 方法：

```java
public static void main(String[] args) {
    SpringApplication.run(WebApplication.class, args);
}
```

`run` 方法返回的 `ConfigurableApplicationContext` 就是根 `ApplicationContext`：

```java
public static ConfigurableApplicationContext run(Class<?> primarySource, String... args)
```

根 `BeanFactory` 保存在 Spring Context 中提供的 `GenericApplicationContext` 类的 `beanFactory` 字段中：

```java
private final DefaultListableBeanFactory beanFactory;
```

## 断点：SpringApplication:311

我们可以在 `SpringApplication.run` 方法中调用 `createApplicationContext` 方法处加入断点：

```java
context = createApplicationContext();
```

### 断点：SpringApplication:588

`createApplicationContext` 方法会根据 Web 应用类型初始化不同的 `ApplicationContext`。对于本例中的 Servlet Web 应用来说，通常会返回 `AnnotationConfigServletWebServerApplicationContext`：

```java
protected ConfigurableApplicationContext createApplicationContext() {
    Class<?> contextClass = this.applicationContextClass;
    if (contextClass == null) {
        try {
            switch (this.webApplicationType) {
            case SERVLET:
                contextClass = Class.forName(DEFAULT_SERVLET_WEB_CONTEXT_CLASS);
                break;
            case REACTIVE:
                contextClass = Class.forName(DEFAULT_REACTIVE_WEB_CONTEXT_CLASS);
                break;
            default:
                contextClass = Class.forName(DEFAULT_CONTEXT_CLASS);
            }
        }
        catch (ClassNotFoundException ex) {
            throw new IllegalStateException(
                    "Unable create a default ApplicationContext, please specify an ApplicationContextClass", ex);
        }
    }
    return (ConfigurableApplicationContext) BeanUtils.instantiateClass(contextClass);
}
```

### 断点：ClassPathBeanDefinitionScanner:273

`ClassPathBeanDefinitionScanner` 类的 `doScan` 方法可以观察到当前初始化的 BeanFactory 会扫描的基础包：

```java
protected Set<BeanDefinitionHolder> doScan(String... basePackages)
```

### 断点：DefaultListableBeanFactory:853

`DefaultListableBeanFactory` 类的 `preInstantiateSingletons` 方法可以观察到当前 BeanFactory 中包含的 Bean 定义，`preInstantiateSingletons` 方法会在 BeanFactory 创建的最终阶段被调用：

```java
// Iterate over a copy to allow for init methods which in turn register new bean definitions.
// While this may not be part of the regular factory bootstrap, it does otherwise work fine.
List<String> beanNames = new ArrayList<>(this.beanDefinitionNames);
```

# 每个 Servlet 关联的 WebApplicationContext 及 BeanFactory

## 断点：FrameworkServlet:530

在 `DispatcherServlet` 的父类 `FrameworkServlet` 的 `initServletBean` 方法中，会对 Servlet 关联的 `WebApplicationContext` 进行初始化：

```java
/**
 * Overridden method of {@link HttpServletBean}, invoked after any bean properties
 * have been set. Creates this servlet's WebApplicationContext.
 */
@Override
protected final void initServletBean() throws ServletException {
    getServletContext().log("Initializing Spring " + getClass().getSimpleName() + " '" + getServletName() + "'");
    if (logger.isInfoEnabled()) {
        logger.info("Initializing Servlet '" + getServletName() + "'");
    }
    long startTime = System.currentTimeMillis();

    try {
        this.webApplicationContext = initWebApplicationContext();
        initFrameworkServlet();
    }
    catch (ServletException | RuntimeException ex) {
        logger.error("Context initialization failed", ex);
        throw ex;
    }

    if (logger.isDebugEnabled()) {
        String value = this.enableLoggingRequestDetails ?
                "shown which may lead to unsafe logging of potentially sensitive data" :
                "masked to prevent unsafe logging of potentially sensitive data";
        logger.debug("enableLoggingRequestDetails='" + this.enableLoggingRequestDetails +
                "': request parameters and headers will be " + value);
    }

    if (logger.isInfoEnabled()) {
        logger.info("Completed initialization in " + (System.currentTimeMillis() - startTime) + " ms");
    }
}
```

### 断点：AbstractRefreshableApplicationContext:130

`AbstractRefreshableApplicationContext` 类的 `refreshBeanFactory` 方法会创建 `WebApplicationContext` 的 `BeanFactory`：

```java
/**
 * This implementation performs an actual refresh of this context's underlying
 * bean factory, shutting down the previous bean factory (if any) and
 * initializing a fresh bean factory for the next phase of the context's lifecycle.
 */
@Override
protected final void refreshBeanFactory() throws BeansException {
    if (hasBeanFactory()) {
        destroyBeans();
        closeBeanFactory();
    }
    try {
        DefaultListableBeanFactory beanFactory = createBeanFactory();
        beanFactory.setSerializationId(getId());
        customizeBeanFactory(beanFactory);
        loadBeanDefinitions(beanFactory);
        synchronized (this.beanFactoryMonitor) {
            this.beanFactory = beanFactory;
        }
    }
    catch (IOException ex) {
        throw new ApplicationContextException("I/O error parsing bean definition source for " + getDisplayName(), ex);
    }
}
```

# Demo 应用中的 BeanFactory 和 ApplicationContext 列表

| Root        | BeanFactory | ApplicationContext |
| ----------- | ----------- | ------------------ |
| ID          | application | org.springframework.boot.web.servlet.context.AnnotationConfigServletWebServerApplicationContext@6e01f9b0 |
| Code        | @3157       | @3149              |
| Parent      | null        | null               |

| Bar Servlet | BeanFactory | ApplicationContext |
| ----------- | ----------- | ------------------ |
| ID          | org.springframework.web.context.WebApplicationContext:/Bar servlet | org.springframework.web.context.WebApplicationContext:/Bar servlet |
| Code        | @5578       | @5591              |
| Parent      | @3157       | @3149              |

| Foo Servlet | BeanFactory | ApplicationContext |
| ----------- | ----------- | ------------------ |
| ID          | org.springframework.web.context.WebApplicationContext:/Foo servlet | org.springframework.web.context.WebApplicationContext:/Foo servlet |
| Code        | @5778       | @5777              |
| Parent      | @3157       | @3149              |
