---
id: spring-beanfactory-applicationcontext
title: "Spring 中 BeanFactory 和 ApplicationContext 的关系梳理"
description: "从源码角度，老生常谈一下这个问题"
date: 2025.08.31 10:34
categories:
    - Spring
tags: [Java, Spring]
keywords: Spring, BeanFactory, ApplicationContext, IoC, WebApplication, 
cover: /contents/covers/spring-beanfactory-applicationcontext.png
---

![](https://alphahinex.github.io/contents/covers/spring-beanfactory-applicationcontext.png)

几个重点：

1. `BeanFactory` 接口提供的查找 Bean 的方法，需要时都会到父级工厂（如果有的话）中去查找。
1. `ListableBeanFactory` 接口中可以获得一类 Bean，不会包含父级工厂中的 Bean。
1. `ApplicationContext` 接口继承了 `ListableBeanFactory` 接口，同时继承了 `HierarchicalBeanFactory` 接口以支持父级上下文。
1. `WebApplicationContext` 接口在 `ApplicationContext` 的基础上，增加了对 Web 环境的支持。
1. 每个 Web 应用有一个根上下文，每个 Servlet（包括 DispatcherServlet）都有自己的子上下文。
