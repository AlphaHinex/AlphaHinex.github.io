---
id: property-binding-in-spring-boot-2-0
title: "【译】Spring Boot 2.0 中的属性绑定"
description: "在 Spring Boot 2.0 中，绑定方式被重新设计，引入了新的抽象和全新的绑定 API。本文将介绍这些新类和接口的作用及其使用方法。"
date: 2024.10.27 10:26
categories:
    - Spring
tags: [Spring Boot]
keywords: Spring Boot, relaxed binding, ConfigurationPropertySource, ConfigurationPropertyName, Origin, Binder, Bindable, BindResult, BindHandler, @ConfigurationProperties
cover: /contents/covers/property-binding-in-spring-boot-2-0.png
---

- 原文地址：[Property Binding in Spring Boot 2.0](https://spring.io/blog/2018/03/28/property-binding-in-spring-boot-2-0)
- 原文作者：[Phil Webb](https://spring.io/team/philwebb)

自 Spring Boot 的第一个版本发布以来，就可以使用 `@ConfigurationProperties` 注解将属性绑定到类。还可以用不同的形式指定属性名称。例如，`person.first-name`、`person.firstName` 和 `PERSON_FIRSTNAME` 都可以互换使用。我们称这个功能为“宽松绑定”（relaxed binding）。

不幸的是，在 Spring Boot 1.x 中，“宽松绑定”有点过于宽松。很难准确定义绑定规则以及何时可以使用特定格式。我们还开始收到一些很难用 1.x 实现修复的问题报告。例如，在 Spring Boot 1.x 中，无法将属性绑定到 `java.util.Set`。

因此，在 Spring Boot 2.0 中，我们开始重新设计绑定方式。我们添加了几个新的抽象，开发了一个全新的绑定 API。在本文中，我们将介绍一些新的类和接口，描述加入它们的原因、它们的作用以及如何在自己的代码中使用它们。

# 属性源（Property Sources）

如果你已经使用 Spring 一段时间，你可能熟悉 `Environment` 抽象。这个接口是一个 `PropertyResolver`，允许你从一些底层的 `PropertySource` 实现中解析属性。

Spring 框架为常见的事物提供了 `PropertySource` 实现，例如系统属性、命令行标志和 properties 文件。Spring Boot 会自动配置这些实现，以一种对大多数应用程序有意义的方式（例如，加载 `application.properties`）。

# 配置属性源（Configuration Property Sources）

Spring Boot 2.0 引入了一个新的 `ConfigurationPropertySource` 接口，而不是直接使用现有的 `PropertySource` 接口进行绑定。我们引入了一个新接口，以便为实现之前属于绑定器一部分的宽松绑定规则提供一个逻辑位置。

这个接口主要的 API 很简单：

```java
ConfigurationProperty getConfigurationProperty(ConfigurationPropertyName name);
```

还有一个 `IterableConfigurationPropertySource` 变体，它实现了 `Iterable<ConfigurationPropertyName>`，因此您可以探索源中包含的所有名称。

您可以使用以下代码将 Spring `Environment` 适配为 `ConfigurationPropertySources`：

```java
Iterable<ConfigurationPropertySource> sources =
    ConfigurationPropertySources.get(environment);
```

如果您需要，我们还提供了一个简单的 `MapConfigurationPropertySource` 实现。

# 配置属性名（Configuration Property Names）

事实证明，如果将宽松属性名称的概念限制为一个方向，实现起来会容易得多。无论属性在底层源中如何表示，您都应该始终使用规范形式在代码中访问属性。

`ConfigurationPropertyName` 类强制执行这些规范命名规则，基本上可以归结为“使用小写端横线命名法（kebab-case）”。

因此，例如，即使底层源中使用 `person.firstName` 或 `PERSON_FIRSTNAME`，您也应该在代码中将属性引用为 `person.first-name`。

# Origin 支持

正如您所期望的那样，从 `ConfigurationPropertySource` 返回的 `ConfigurationProperty` 对象封装了实际的属性值，但它还可以包含一个可选的 `Origin` 对象。

`Origin` 是 Spring Boot 2.0 中引入的一个新接口，它允许您准确定位值的加载位置。有许多 `Origin` 实现，其中可能最有用的是 `TextResourceOrigin`。它提供了加载的 `Resource` 的详细信息，以及值的行和列号。

对于 `.properties` 和 `.yaml` 文件，我们编写了自定义加载器，以跟踪加载文件时的来源。一些已经存在的 Spring Boot 功能特性也已被改进以利用来源信息。例如，绑定验证异常现在显示无法绑定的值和来源。以下是失败分析器显示错误的方式：

```text
*************************** APPLICATION FAILED TO START ***************************

Description:

Binding to target org.springframework.boot.context.properties.bind.BindException: Failed to bind properties under 'person' to scratch.PersonProperties failed:

Property: person.name
Value: Joe
Origin: class path resource \[application.properties\]:1:13
Reason: length must be between 4 and 2147483647

Action:

Update your application's configuration
```

# Binder API

`Binder` 类（在 `org.springframework.boot.context.properties.bind` 包中）允许您从一个或多个 `ConfigurationPropertySource` 中绑定某些内容。更准确地说，`Binder` 接受一个 `Bindable` 并返回一个 `BindResult`。

# Bindable

`Bindable` 可能是一个现有的 Java bean、一个 class 类型或一个复杂的 `ResolvableType`（例如 `List<Person>`）。以下是一些示例：

```java
Bindable.ofInstance(existingBean);
Bindable.of(Integer.class);
Bindable.listOf(Person.class);
Bindable.of(resovableType);
```

`Bindable` 还用于携带注解信息，但通常您不需要担心这一点。

# BindResult

与直接返回绑定对象不同，`bind` 方法返回一个称为 `BindResult` 的东西。类似于 Java 8 的 `Streams` 返回 `Optional`，`BindResult` 表示可能已绑定或未绑定的内容。

如果尝试获取未绑定对象的实际结果，将抛出异常。我们还提供了一些方法，让您在未绑定时提供替代值或映射到不同类型：

```java
var bound = binder.bind("person.date-of-birth",
        Bindable.of(LocalDate.class));

// Return LocalDate or throws if not bound
bound.get();

// Return a formatted date or "No DOB"
bound.map(dateFormatter::format).orElse("No DOB");

// Return LocalDate or throws a custom exception
bound.orElseThrow(NoDateOfBirthException::new);
```

# 格式化和转换

大多数 `ConfigurationPropertySource` 实现将其底层值暴露为字符串。当 `Binder` 需要将源值转换为不同类型时，它会委托给 Spring 的 `ConversionService` API。如果需要调整值的转换方式，可以自由使用 `@NumberFormat` 或 `@DateFormat` 等格式化注解。

Spring Boot 2.0 还引入了一些新的适用于绑定的注解和转换器。例如，现在可以将 `4s` 之类的值转换为 `Duration`。查看 `org.springframework.boot.convert` 包以获取详细信息。

# BindHandler

有时，您可能需要在绑定时实现额外的逻辑，`BindHandler` 接口提供了一个很好的方法来实现这一点。每个 `BindHandler` 都有 `onStart`、`onSuccess`、`onFailure` 和 `onFinish` 方法，可以实现以覆盖行为。

Spring Boot 提供了许多 handler，主要是为了支持现有的 `@ConfigurationProperties` 绑定。例如，`ValidationBindHandler` 可用于在绑定对象上应用 `Validator` 验证。

# @ConfigurationProperties

正如本文开头所提到的，自 Spring Boot 诞生以来，`@ConfigurationProperties` 就是一个重要的特性。很可能 `@ConfigurationProperties` 将继续是大多数人执行绑定的方式。

尽管我们重新编写了整个绑定过程，但大多数人在升级 Spring Boot 1.5 应用程序时似乎没有遇到太多问题。只要您遵循 [迁移指南](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-2.0-Migration-Guide#relaxed-binding) 中的建议，您应该会发现一切正常。如果在升级应用程序时遇到问题，请在 [GitHub 问题跟踪器](https://github.com/spring-projects/spring-boot/issues) 上报告，并附上一个重现问题的小示例。

# 未来工作

我们计划在 Spring Boot 2.1 中继续开发 `Binder`，我们希望支持的第一个功能是不可变配置属性。如果当前需要 getter 和 setter 的配置属性可以使用基于构造函数的绑定，那将非常好：

```java
public class Person {

	private final String firstName;
	private final String lastName;
	private final LocalDateTime dateOfBirth;

	public Person(String firstName, String lastName,
			LocalDateTime dateOfBirth) {
		this.firstName = firstName;
		this.lastName = lastName;
		this.dateOfBirth = dateOfBirth;
	}

	// getters

}
```

我们认为构造函数绑定也将与 [Kotlin 数据类](https://kotlinlang.org/docs/reference/data-classes.html) 非常好地配合使用。如果您对此功能的进展感兴趣，请订阅 [issue #8762](https://github.com/spring-projects/spring-boot/issues/8762)。

# 总结

我们希望您发现 Spring Boot 2.0 中的新绑定功能有用，并希望您考虑升级现有的 Spring Boot 应用程序。

如果您想讨论绑定的一般问题，或者有特定的增强建议或问题，请 [加入我们在 Gitter 上的讨论](https://gitter.im/spring-projects/spring-boot)。
