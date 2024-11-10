---
id: spring-boot-configuration-binding
title: "【译】Spring Boot 配置绑定"
description: "本文详细描述配置项如何绑定到实际对象，包括各种绑定用例、声明式绑定、宽松绑定和配置元数据。"
date: 2024.11.10 10:26
categories:
    - Spring
tags: [Spring Boot, Spring]
keywords: Spring Boot, Configuration Binding, ConfigurationProperties, NestedConfigurationProperty, relaxed binding, ConfigurationPropertySource
cover: /contents/covers/spring-boot-configuration-binding.png
---

- 原文地址：https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-Configuration-Binding

# Spring Boot 配置绑定

本页面的目的是详细描述配置项如何绑定到实际对象。它主要面向 IDE 开发人员，但任何对了解绑定工作原理感兴趣的人都可以在本文档中找到有价值的资源。

> 注意：IDE 对配置绑定的辅助特性在 [单独的文档](https://github.com/spring-projects/spring-boot/wiki/IDE-binding-features) 中描述。

## 配置的结构

无论外部配置文件格式如何，整个 `Environment` 归结为一组概念上层次结构化的键。让我们看一个例子：

```yml
server:
  port: 7070
  tomcat:
    max-threads: 20
```

这个文件贡献了两个键：`server.port` 和 `server.tomcat.max-threads`。后者属于 `server.tomcat` "组"。共享相同概念的配置项在同一个 _前缀_ 下重新分组。大概念下有子概念（例如，Apache Tomcat 的特定配置在 `server.tomcat` 前缀中定义）。

## 绑定用例

绑定 `Environment` 的最基本方法是定义一个 POJO 并向其注入一组键。正如我们稍后将看到的，Spring Boot 在这方面提供了几个有用的功能。但首先，让我们关注支持的各种绑定用例。

在本节的其余部分，我们将涵盖以下内容：

* 简单属性绑定
* 基于集合的绑定
* 基于数组的绑定
* 基于 Map 的绑定
* 嵌套属性

> 注意：虽然理论上可以进行基于字段的绑定，但 Spring Boot 仅使用常规的 getter/setter 进行绑定。

### 简单属性绑定

让我们看一个例子：

```java
public class Foo {

    private String id = "";
    private int port;

    public String getId() { ... }
    void setId(String id) { ... }

    public int getPort() { ... }
    public void setPort(int port) { ... }
}
```

这个对象暴露了一个单一值属性 (`port`)。`id` 没有暴露，因为它的 _setter_ 不是 public 的。单一值被定义为键的 _最后一部分_ 。

> 注意：经验法则是，要暴露属性，应该存在一个有效的 public getter/setter 对。理论上，只有 setter 也能提供足够的信息，但单一属性只有在 getter 和 setter 都存在时才会在元数据中暴露。

### 基于集合的绑定

当属性暴露一个集合类型时，可以通过以逗号分隔的方式或使用方括号表示索引来向其贡献多个值。

```java
public class Foo {

  private final List<String> items = new ArrayList<>();
  private Set<Integer> counters;

  public List<String> getItems() { .... }

  public Set<Integer> getCounters() { ... }
  public void setCounters(Set<Integer> counters) { ... }
}
```

以下配置均会得到预期的结果（假设 foo 是绑定到该对象的上下文）：

```properties
foo.items[1]=twoBis
foo.items[2]=four

foo.counters=1,2,3
```

> 注意：访问集合的规则是，应该存在一个 getter 来访问集合。如果需要初始化集合，则必须提供一个 setter。

> 注意：如果在多个属性源中指定了 `Collection` 属性，则只会使用具有最高优先级的属性源中的元素。在绑定到 `Collection` 时，*不会* 将来自不同属性源的属性组合在一起。例如，如果一个 `.properties` 文件中有：
> 
> ```properties
> foo[0] = 1
> foo[1] = 2
> ```
> 
> 在 `Environment`中有：
> 
> ```bash
> foo=3,4
> ```
> 
> 绑定的集合中智慧包含元素 `3` 和 `4`。

### 基于数组的绑定

基于数组的绑定必需有 setter 方法。

### 基于 Map 的绑定

对于集合，可以通过使用括号表示法或使用 _导航点（navigation dot）_ 来指定键，从而向映射中添加任意值。只有在需要初始化映射时才需要 setter 方法。

```java
public class Foo {

  private final Map<String,Integer> items = new HashMap<>();

  public Map<String,Integer> getItems() { .... }

  private final Map<String,Map<String, Integer>> nested = new HashMap<>();

  public Map<String,Map<String, Integer>> getNested() { .... }
}
```

这里有一些有效的样例：

```properties
foo.items.one=1
foo.items[two]=2
```

> 注意：如果 `key` 中包含点号，并且它是一个嵌套的 Map，则必须使用括号表示法。例如，对于上述场景，使用键 `bar.baz` 的有效示例如下：
> 
> ```properties
> foo.items.bar.baz=1
> foo.nested[bar.baz].bling=2
> ```

对于 YAML 文件，括号需要用引号括起来，以便正确解析键。

```yaml
foo:
  nested: 
    "[bar.baz]":
      bling: 2
```

### 嵌套属性

有几个层次的嵌套。到目前为止，我们使用了简单的值，但更复杂的对象也可以处理。让我们想象以下对象：

```java
public class Bar {
    private String id;
    private Integer counter;
    private boolean active;

    // getter and setter
}
```

一个简单的嵌套示例如下：

```java
public class Foo {

  private final Bar bar = new Bar();

  public Bar getBar() { ... }

}
```

这将允许你编写如下内容：

```properties
foo.bar.id=myId
foo.bar.counter=0
foo.bar.active=true
```

> 提示：如果你希望 `Bar` 按需创建，你可以将其保留为 `null` 并添加一个 _setter_ 方法。

嵌套同样适用于集合和数组。

```java
public class Foo {

  private List<Bar> bars = new ArrayList<>();

  public List<Bar> getBars() { .... }
  public void setBars(List<Bar> bars) { ... }
}
```

这将允许在索引元素上进行嵌套：

```properties
foo.bars[0].id=one
foo.bars[2].counter=3
```

> 提示：除非在绑定器的 `ConversionService` 中注册了 `Converter<String, Bar>`，否则无法以逗号分隔的方式设置此类对象。

如你所想，这同样适用于 Map：

```java
public class Foo {

  private Map<String, Bar> bars = new HashMap<>();

  public Map<String, Bar> getBars() { .... }
}
```

```properties
foo.bars.one.counter=1
foo.bars.one.active=false
foo.bars[two].id=IdOfBarWithKeyTwo
```

最后，嵌套可以使用任意多的层级。`.` 用作在这些关系之间导航。让我们考虑这个相当复杂的键：

```properties
foo.items.myKey.customer.address.street=Acme street
```

这将设置 `items` Map 中键为 `myKey` 的 customer 对象中 address 对象的 street 属性（假设 `foo` 是我们的根对象的引用），类似于：

```java
foo.get("myKey").getCustomer().getAddress().setStreet("Acme street")
```

> 提示：如果中间关系为 `null`，将使用默认构造函数创建一个新实例，并使用相关的 _setter_ 方法进行调用。

### 总结

下表描述了关于是否需要 getter/setter 的规则：

| 绑定类型        | Getter                    | Setter                                        | 示例                      |
|----------------|---------------------------|-----------------------------------------------|--------------------------|
| 简单绑定        | 技术上非必需                | 必需                                           | `foo.name=myName`        |
| 集合绑定        | 必需                       | 若集合已初始化则非必需                           | `foo.items=1,2,3`        |
| List           | 必需                      | 若集合已初始化则非必需                            | `foo.items[1]=2`         |
| Array          | 必需                      | 必需                                           | `foo.items[1]=2`         |
| Map            | 必需                      | 若 Map 已初始化则非必需                          | `foo.items.one=1`        |
| 导航绑定        | 必需                      | 若实例已初始化则非必需                            | `foo.bar.name=myName`    |

## 声明式绑定

Spring Boot 提供了一个 `@ConfigurationProperties` 注解，可以放置在任何对象上以声明其作为 _根_ 前缀。然后，它使用这个前缀和一个增强的绑定器自动从 `Environment` 中绑定匹配前缀的属性。它还会自动将对象暴露为 Spring Bean。

```java
@ConfigurationProperties("foo")
public class FooProperties {

    private String id = "";
    private final Bar bar = new Bar;

    public String getId() { ... }
    pulic void setId(String id) { ... }

    public Bar getBar() { ... }

    static class Bar {
        private String name;
        private boolean active;

        public String getName() { ... }
        public void setName(String name) { ... }

        public boolean isActive() { ... }
        public void setActive(boolean active) { ... }
    }
}
```

如果通过例如 `@EnableConfigurationProperties(FooProperties.class)` 注册对该对象的处理，`FooProperties` 类型的 Bean 将自动注册到上下文中，并且以下键将按预期绑定：

```properties
foo.id=myId
foo.bar.name=barName
foo.bar.active=true
```

> 提示：显然，我们在上面看到的其他所有绑定类型在这里也同样适用。

你也可以在 `@Bean` 声明上应用相同的机制。在这种情况下，一旦对象构建完成，就会应用绑定。这通常对于为第三方对象提供友好的配置非常有用。

假设我们要为在 Spring Boot 应用程序中使用的第三方 `Foo` 类注册 `FooProperties`：

```java
@Configuration
public class MyConfig {

  @Bean
  @ConfigurationProperties("foo")
  public Foo foo() {
      Foo foo = new Foo();
      foo.setId("some id");
      return foo;
  }
}
```

这将暴露与上例完全相同的属性集（因为我们使用了与上面示例相同的前缀）。另外，如果配置中定义了一个 `foo.id=anotherId` 条目，那么该 Bean 的 ID 最终将是 `anotherId`，因为属性绑定是在对象构建后应用的。

## 宽松绑定

由于键可以以各种格式定义，而且某些源有一些限制，Spring Boot 使用了一个 _宽松的_ 绑定器。考虑以下情况：

```java
@ConfigurationProperties("foo")
public class FooProperties {

    private String id;
    private String firstName;
    private String lastName;

    // getters and setters

}
```

Spring Boot 使用一个小写字母并使用连字符分隔单词的规范格式。但如下表所定义的，也支持其他格式：

| 命名方式 | 示例 |
|:--------|:----|
| 统一格式 | `foo.id` - `foo.first-name` - `foo.last-name` |
| 驼峰命名法 | `foo.id` - `foo.firstName` - `foo.lastName` |
| 下划线命名 | `foo.id` - `foo.first_name` - `foo.last_name` |
| 大写字母 | `FOO_ID` - `FOO_FIRST-NAME` - `FOO_LAST-NAME` |

> 注意：实际上支持的变体更多

宽松绑定的主要原因是为了提供灵活性，特别是当属性源不支持某些字符时：操作系统环境变量在某些操作系统上必须是大写或不能包含点号。关于各种属性源宽松绑定的详细信息，可以参阅 [Relaxed Binding 2.0](https://github.com/spring-projects/spring-boot/wiki/Relaxed-Binding-2.0)。

## 配置元数据

本节描述了配置的元数据是如何被发现的，以及围绕它的一些限制。

> 注意：如果您还没有这样做，请先阅读 [开发者指南中的配置元数据部分](https://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/#configuration-metadata) ，因为它定义了本节中使用的基础概念。

元数据的目的是提供一个配置键的 _静态_ 模型，以便工具可以从中受益，并为用户提供内容辅助。当 `spring-boot-configuration-processor` 可用时，在编译期间将自动生成元数据。

属性是当前模块暴露的 _有限_ 集合。例如，`foo.items[myKey].address.street` 是一个有效的配置键，但元数据只暴露 `foo.items` 键，其类型提供了发现其余部分的必要信息，即：

* 类型是一个 `Map`
* 键是一个 `java.lang.String`
* 值是 `com.acme.Person`（在本文的其余部分中称为 _简单的 POJO_），可以进一步调查以获取额外的访问器（一个 `Person` 有一个 `Address`，一个 `Address` 有一个 `street`）

### 单值与嵌套属性

像 Collection 或基于 Map 的绑定等情况很容易发现元数据，因为属性的类型说明了这一点。其他类型的属性很难弄清楚是单个值还是表示我们应该导航的概念。

以前面的例子为例，我们可以写成 `foo.bar=???`，这显然会失败，因为没有 setter，并且该对象的意图是提供一个暴露额外属性的对象。

Spring Boot 使用以下规则：

1. 如果属性的类型是当前对象的内部类，则被认为是嵌套属性（我们经常使用此模式，并发现它可以很好的自动发现。例如 `ServerProperties`）；
1. 如果属性用 `@NestedConfigurationProperty` 标记，Spring Boot 将其视为嵌套属性（参见 `Ssl` 作为示例）；
1. 在所有其他情况下，属性应该是一个单值。

假设 `Bar` 现在在不同的区域中定义（在同一包中或在不同的包中，但不是作为内部类），我们可以重写我们的类以确保以相同的方式发现元数据：

```java
import com.acme.Bar;

@ConfigurationProperties("foo")
public class FooProperties {

    private String id = "";

    @NestedConfigurationProperty
    private final Bar bar = new Bar;

    public String getId() { ... }
    public void setId(String id) { ... }

    public Bar getBar() { ... }

}
```

### 默认值

默认值只能通过使用编译器 API 的低级实用程序来发现。Spring Boot 支持 Oracle JDK，但尚未支持 Eclipse 编译器（APT）。

最好在字段声明本身中设置默认值。如果类本身设置了 `public static` 常量，处理器也会发现它。

例如：

```java
@ConfigurationProperties("my")
public class MyProperties {

    public static final int DEFAULT_INDEX = 0;

    private String name = "myName";
    private int index = DEFAULT_INDEX;

    // getter and setter
}
```

### 文档

文档只从字段的 Javadoc 中提取。这一决定的主要原因是配置键的描述可能与您通常为 setter 编写的描述大不相同。此外，处理器不会清理任何存在的 Javadoc 标签，因此有必要将文档放在单独的位置。

> 注意：如果属性没有相关字段，或者字段不符合约定，则文档不可用。

显然，只有源代码可用时，Javadoc 才可访问。因此，对于以下情况没有描述：

1. 在 `@ConfigurationProperties` 类的父类中定义的键，如果所述基类不在当前编译单元中（即模块）；
1. `@Bean` 暴露的第三方类。

解决这个问题的一种方法是升级 IDE 支持，以便它可以在存在时实时获取该文档，而不仅仅依赖于元数据。
