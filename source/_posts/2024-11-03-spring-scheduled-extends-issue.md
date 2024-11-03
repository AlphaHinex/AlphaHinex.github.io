---
id: spring-scheduled-extends-issue
title: "【转】解析 Spring 计划任务执行多次之谜及解决方案"
description: "在 Spring 项目中，@Scheduled 注解配置的计划任务（Scheduled Tasks）可能会出现执行多次的情况"
date: 2024.11.03 10:34
categories:
    - Spring
tags: [Spring]
keywords: Spring, @Scheduled, extends, 重复执行
cover: /contents/covers/spring-scheduled-extends-issue.png
---

原文地址：https://wyiyi.github.io/amber/2024/11/01/Scheduled/

在`Spring`项目中，`@Scheduled`注解配置的计划任务（`Scheduled Tasks`）可能会出现执行多次的情况，尤其是在以下场景中：

- 一个父类定义了`@Scheduled`注解的方法，且被多个子类继承。
- 父类或子类被`Spring`容器错误地实例化为多个`Bean`实例。

本文将针对该特定场景，剖析导致计划任务重复执行的原因，并针对性地提出解决措施。

## 一、现象描述

在`Spring`项目中，我们定义了一个计划任务类`ScheduledTaskParent`，以及两个继承该类的子类`FirstChild`和`SecondChild`。

```Java
@Component
public class ScheduledTaskParent {

    @Scheduled(fixedRate = 5000)
    public void performTask() {
        System.out.println("ScheduledTaskParent 执行计划任务");
    }
}

@Component
public class FirstChild extends ScheduledTaskParent {

    @Scheduled(fixedRate = 5000)
    public void firstTask() {
        System.out.println("FirstChild 执行特定的操作");
    }
}

@Component
public class SecondChild extends ScheduledTaskParent {

    @Scheduled(fixedRate = 5000)
    public void secondTak() {
        System.out.println("SecondChild 执行计划任务");
    }
}
```

当应用启动后，发现`ScheduledTaskParent`中的计划任务被执行了多次，具体表现为每个子类实例都执行了父类的计划任务，导致执行次数为子类数目加1。

```Text
FirstChild 执行特定的操作
ScheduledTaskParent 执行计划任务
ScheduledTaskParent 执行计划任务
SecondChild 执行计划任务
ScheduledTaskParent 执行计划任务
```

## 二、原因分析

> As of Spring Framework 4.3, @Scheduled methods are supported on beans of any scope.
> 
> Make sure that you are not initializing multiple instances of the same @Scheduled annotation class at runtime, unless you do want to schedule callbacks to each such instance. Related to this, make sure that you do not use @Configurable on bean classes that are annotated with @Scheduled and registered as regular Spring beans with the container. Otherwise, you would get double initialization (once through the container and once through the @Configurable aspect), with the consequence of each @Scheduled method being invoked twice.

[Spring 官方文档 ](https://docs.spring.io/spring-framework/reference/integration/scheduling.html)提到，从`Spring Framework 4.3`开始，`@Scheduled`注解支持任何作用域的`bean`。但是，文档也警告，不应该在运行时初始化同一`@Scheduled`注解类的多个实例，除非希望每个实例都调度回调。

在例子中，`ScheduledTaskParent`被标记为`@Component`，因此`Spring`容器会为其创建一个`bean`。由于`FirstChild`和`SecondChild`都继承了`ScheduledTaskParent`，并且它们也被标记为`@Component`，`Spring`容器为每个子类也创建了`bean`。每个`bean`都包含`performTask`方法上的`@Scheduled`注解，因此每个`bean`都会触发该任务的调度。

这就是为什么`performTask`被执行了三次：
一次来自`ScheduledTaskParent`的`bean`，一次来自`FirstChild`的`bean`，还有一次来自`SecondChild`的`bean`。

## 三、解决方案

为了防止计划任务在子类中被重复执行，我们可以在父类中定义一个抽象方法，并在子类中实现具体的计划任务。如下所示：

```Java
public abstract class ScheduledTaskParent {

    public abstract void performTask();
}

@Component
public class FirstChild extends ScheduledTaskParent {

    @Scheduled(fixedRate = 5000)
    @Override
    public void performTask() {
        System.out.println("FirstChild 执行特定的操作");
    }
}

@Component
public class SecondChild extends ScheduledTaskParent {

    @Scheduled(fixedRate = 5000)
    @Override
    public void performTask() {
        System.out.println("SecondChild 执行计划任务");
    }
}
```

通过这种方式，确保每个计划任务只被调度一次，即使有多个子类继承了父类。
