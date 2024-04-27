---
id: how-to-bind-requestparam-to-object-in-spring
title: "【译】如何在 Spring 中将 @RequestParam 绑定到对象"
description: "TL;DR: 不指定 @RequestParam 注解即可，非空、默认值可借助其他方式实现"
date: 2024.04.27 10:34
categories:
    - Spring
tags: [Spring, Java]
keywords: Spring, @RequestParam, POJO, object, @Valid, nested object, immutable DTO
cover: /contents/how-to-bind-requestparam-to-object-in-spring/cover.png
---

- 原文地址：[How to bind @RequestParam to object in Spring](http://dolszewski.com/spring/how-to-bind-requestparam-to-object/)
- 原文作者：[Daniel Olszewski](http://dolszewski.com/)

你的请求映射方法中是否有多个用 `@RequestParam` 注解的参数？是否感觉它们影响了易读性？

当请求只有一两个入参时，这个注解看起来非常直观，但是当参数列表变长时，你可能会感到不知所措。

你不能在对象内部使用 `@RequestParam` 注解，但这并不意味着你没有其他解决方案。在这篇文章中，我将向你展示 **如何在 Spring 应用中将多个请求参数绑定到一个对象**。

## 过长的 @RequestParams 列表

无论是 controller 还是其他类，我相信你会同意 **过长的方法参数列表很难阅读**。此外，如果参数类型相同，则更容易出错。

静态代码分析工具，如 [Checkstyle 可以检测方法中的大量输入](https://checkstyle.org/checks/sizes/parameternumber.html#ParameterNumber)，因为这通常被认为是一种不良的实践。

> 译注：此处原文链接 http://checkstyle.sourceforge.net/config_sizes.html#ParameterNumber 已失效，已更换。

你将一组参数一起传递给应用程序的不同层次是非常常见的。这组参数通常可以 **形成一个对象**，你需要做的就是 **提取它并给它一个适当的名字**。

让我们来看一个用于搜索产品的 GET 端点的示例：

```java
@RestController
@RequestMapping("/products")
class ProductController {
 
    //...
 
    @GetMapping
    List<Product> searchProducts(@RequestParam String query,
            @RequestParam(required = false, defaultValue = "0") int offset,
            @RequestParam(required = false, defaultValue = "10") int limit) {
        return productRepository.search(query, offset, limit);
    }
 
}
```

三个参数的数量并不令人担忧，但它们很容易增长。例如，搜索通常包括排序或一些额外的过滤器。在这种情况下，它们都被传递到数据访问层，所以它们似乎是 [参数对象](https://refactoring.com/catalog/introduceParameterObject.html) 提取的完美候选者。

## 将 @RequestParam 绑定到 POJO

根据我的经验，开发者不会替换 `@RequestParams` 的长列表，因为他们单纯的没有意识到这是可能的。`@RequestParam` 的文档并未提及替代方案。

首先，更新控制器的方法，使其接受 POJO 作为输入，而不是参数列表。

```java
@GetMapping
List<Product> searchProducts(ProductCriteria productCriteria) {
    return productRepository.search(productCriteria);
}
```

这个 POJO 不需要任何额外的注解。它应该有一系列的字段，这些字段与将从 HTTP 请求绑定的请求参数相匹配，有标准的 getter/setter 方法，以及一个无参数的构造函数。

```java
class ProductCriteria {
 
    private String query;
    private int offset;
    private int limit;
 
    ProductCriteria() {
    }
 
    public String getQuery() {
        return query;
    }
 
    public void setQuery(String query) {
        this.query = query;
    }
 
    // other getters/setters
 
}
```

### 在 POJO 内验证请求参数

好的，但我们不仅仅是使用 `@RequestParam` 注解来绑定 HTTP 参数。该注解的另一个有用特性是可以将给定参数标记为必填项。如果请求中缺少必填参数，我们的端点可以拒绝它。

要在使用 POJO 时达到相同的效果（甚至更多！）我们可以 **使用 bean 验证**。Java 有许多内置的约束，但你总是可以在需要时 [创建自定义验证](http://dolszewski.com/spring/custom-validation-annotation-in-spring/)。

Let’s return to our POJO and add some validation rules to fields. If you just want to **mimic the behavior of `@RequestParam(required = false)`**, all you need is the **`@NotNull` annotation on a required field**.

让我们回到我们的 POJO，并向字段添加一些验证规则。如果你只是想 **模仿 `@RequestParam(required = true)` 的行为**，你需要的只是 **在必填字段上加上 @NotNull 注解**。

> 译注：此处原文为 **mimic the behavior of `@RequestParam(required = false)`**，但是实际上应该是 `@RequestParam(required = true)`，因为 `@NotNull` 是必填项的意思。

在许多情况下，使用 `@NotBlack` 替代 `@NotNull` 更有意义，因为它也覆盖了不希望出现的空字符串问题（长度为零的字符串）。

```java
final class ProductCriteria {
 
    @NotBlank
    private String query;
    @Min(0)
    private int offset;
    @Min(1)
    private int limi;
 
    // ...
 
}
```

需要注意的是：

**仅在字段上添加验证注解还不足以使校验生效。**

你还需要在控制器方法的 POJO 参数上标记 `@Valid` 注解。这样，你就告诉 Spring 在绑定步骤时应执行验证。

```java
@GetMapping
List<Product> searchProducts(@Valid ProductCriteria productCriteria) {
    // ...
}
```

### 在 POJO 内设置请求参数的默认值

`@RequestParam` 注解的另一个有用特性是，当 HTTP 请求中没有参数时，可以定义默认值。

当我们有一个 POJO 时，不需要任何特殊的魔法。你只需要直接为字段指定默认值。当请求中缺少参数时，不会有任何东西覆盖预定义的值。

```java
private int offset = 0;
private int limit = 10;
```

## 多个对象

你并不需要将所有的 HTTP 参数放在一个对象中。你可以将参数分组在几个 POJO 中。

为了说明这一点，让我们向我们的端点添加排序条件。首先，我们需要一个单独的对象。就像之前一样，它有一些验证约束。

```java
final class SortCriteria {
 
    @NotNull
    private SortOrder order;
    @NotBlank
    private String attribute;
 
    // constructor, getters/setters
 
}
```

在 controller 中，你只需将其作为一个单独的输入参数添加。请注意，每个需要验证的参数上都需要 `@Valid` 注解。

```java
@GetMapping
List<Product> searchProducts(@Valid ProductCriteria productCriteria, @Valid SortCriteria sortCriteria) {
    // ...
}
```

## 嵌套对象

作为多个输入请求对象的替代方案，我们也可以使用组合。参数绑定也适用于嵌套对象。

下面你可以找到一个例子，将之前引入的排序条件移动到了产品查询条件 POJO 中。

要校验所有嵌套属性，你应该在嵌套对象字段上添加 `@Valid` 注解。请注意，当嵌套对象字段为 null 时，Spring 不会验证其属性。如果所有嵌套属性都是可选的，那么这可能是预期的解决方案。如果不是，则需在嵌套对象字段上放置 `@NotNull` 注解。

```java
final class ProductCriteria {
 
    @NotNull
    @Valid
    private SortCriteria sort;
 
    // ...
 
}
```

HTTP 参数必须使用点符号与字段名匹配。在我们的例子中，它们应该如下所示：

```java
sort.order=ASC&sort.attribute=name
```

## 不可变的 DTO

如今，你可以观察到一种趋势，即从传统的带有 setter 的 POJO 转向不可变对象。

不可变对象有许多好处（也有一些缺点……但嘘）。在我看来，最大的好处是 **更易于维护**。

你是否曾经跟踪你的应用程序穿过几十层，以理解什么条件导致了对象的特定状态？在哪个地方这个或那个字段发生了变化？为什么它被更新？setter 方法的名称并不能解释任何事情。setter 方法没有任何业务含义。

考虑到 Spring 框架创建时的情况，没有人会对 Spring 强烈依赖 POJO 规范感到惊讶。然而，时代变了，旧时使用的模式已渐渐变成了反模式。

![old-pattern](/contents/how-to-bind-requestparam-to-object-in-spring/old-pattern.jpeg)

没有简单的方法可以通过参数化构造函数将 HTTP 参数神奇地绑定到 POJO。无参数构造函数是不可避免的。然而，我们可以将该构造函数设为 `private`（但遗憾的是，嵌套对象中不能这样做）并移除所有的 setter 方法。从 public 的视角来看，对象将变得不可变。

默认情况下，Spring 需要 setter 方法将 HTTP 参数绑定到字段。幸运的是，可以重新配置绑定器并使用直接字段访问（通过反射）。

为了给你的整个应用程序配置全局数据绑定器，你可以创建一个 controller advice 组件。你可以在一个带有 `@InitBinder` 注解的方法中更改绑定器配置，该方法接受绑定器作为输入。

```java
@ControllerAdvice
class BindingControllerAdvice {

    @InitBinder
    public void initBinder(WebDataBinder binder) {
        binder.initDirectFieldAccess();
    }

}
```

创建了这个简洁的类之后，我们可以回到我们的 POJO，并从类中移除所有的 setter 方法，使其对公共使用只读。

```java
final class ProductCriteria {
 
    @NotBlank
    private String query;
    @Min(0)
    private int offset = 0;
    @Min(1)
    private int limit = 10;
 
    private ProductCriteria() {
    }
 
    public String getQuery() {
        return query;
    }
 
    public int getOffset() {
        return offset;
    }
 
    public int getLimit() {
        return limit;
    }
 
}
```

重启你的应用程序并尝试设置 HTTP 请求的参数。它应该像之前一样正常工作。

## 结论

在这篇文章中，你可以看到在 Spring MVC controller 中使用 `@RequestParam` 绑定的 HTTP 请求参数可以很容易地被替换为一个参数对象，该对象将一些属性组织在一起，它是一个普通的 POJO，或者也是一个不可变的 DTO。

你可以 [在 GitHub 仓库中找到本文中描述的完整代码](https://github.com/danielolszewski/blog/tree/master/spring-requestparam-object)。我希望呈现的案例是自解释的，但如果有任何疑问，或者你想发表你的看法，我强烈建议你在文章下方留下你的评论。
