---
id: thymeleaf
title: "Thymeleaf —— 简化 Java Web 开发的强大模板引擎"
description: "Thymeleaf 是一种用于在服务器端和客户端之间渲染 HTML、XML、JavaScript、CSS 和文本的 Java 模板引擎。"
date: 2023.08.13 10:26
categories:
    - Java
tags: [Thymeleaf, Java, Spring]
keywords: Thymeleaf, template, fragment
cover: /contents/covers/thymeleaf.png
---

原文地址：https://wyiyi.github.io/amber/2023/08/01/thymeleaf/

Thymeleaf 是一种用于在服务器端和客户端之间渲染 HTML、XML、JavaScript、CSS 和文本的 Java 模板引擎。

模板引擎在 Web 领域的主要作用：让网站实现界面和数据分离，这样大大提高了开发效率，提供自然、灵活的模板处理功能，让代码重用更加容易。

# Springboot 官方支持的模板引擎：Thymeleaf

- 官方支持：[Spring Boot 提供对 Thymeleaf 的官方支持](https://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/#web.servlet.spring-mvc.template-engines)，做了很多默认配置，开发者只需编写对应 html 即可，大大减轻了上手难度和配置复杂度。
- 动静分离：Thymeleaf 选用 html 作为模板页，通过一些特定标签语法代表其含义，但并未破坏 html 结构，即使无网络、不通过后端渲染也能在浏览器成功打开，大大方便界面的测试和修改。
- 强大的表达式功能: Thymeleaf 支持强大的表达式语言（SpEL），可以在模板中执行复杂的表达式操作，如变量赋值、条件判断、迭代循环等。
- 易于集成：与 Spring Boot 框架紧密集成，提供了许多与 Spring Boot 相关的特性和扩展。它可以与 Spring MVC、Spring Security 等框架无缝集成。
- 应用广泛：Thymeleaf 是目前应用广泛的模板引擎之一，拥有活跃的社区和丰富的生态系统。它被广泛用于开发各种类型的 Web 应用和邮件模板。

# Thymeleaf 的用法

**1、添加 Thymeleaf 依赖**

在项目的构建文件中添加 Thymeleaf 的相关依赖：

- Maven 依赖
```xml
  <dependency>
      <groupId>org.thymeleaf</groupId>
      <artifactId>thymeleaf</artifactId>
      <version>3.1.2.RELEASE</version>
  </dependency>
```
- Gradle 依赖
```groovy
  dependencies {
     implementation 'org.thymeleaf:thymeleaf:3.1.2.RELEASE'
  }
```

**2、编写模板文件**

创建一个以 `.html` 为后缀的模板文件，在其中使用 Thymeleaf 的模板语法。

通过使用 Thymeleaf 的标签和表达式，我们可以插入动态数据、进行条件判断、循环迭代等操作。

示例：引入 `www.thymeleaf.org` `<p>` 中 `th:text="'Hello, ' + ${name} + '!'"` 为 Thymeleaf 语法。

   ```html
    <!DOCTYPE HTML>
    <html xmlns:th="http://www.thymeleaf.org">
    <head>
        <title>Getting Started: Serving Web Content</title>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    </head>
    <body>
        <p th:text="'Hello, ' + ${name} + '!'" />
    </body>
    </html>
   ```

**3、控制器中使用 Thymeleaf**

在 Spring MVC 的控制器中，参数的值将添加到 `Model` 对象，传递给 `Thymeleaf 模板`。
Thymeleaf 会自动根据模板中的表达式来渲染数据，并生成最终的 `HTML` 页面。

```java
package com.example.servingwebcontent;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

@Controller
public class GreetingController {

    @GetMapping("/greeting")
    public String greeting(@RequestParam(name="name", required=false, defaultValue="World") String name, Model model) {
        model.addAttribute("name", name);
        return "greeting";
    }

}
```

# 如何使用标准方言

如果你看过使用[标准方言](https://www.thymeleaf.org/doc/articles/sayhelloextendingthymeleaf5minutes.html)编写的代码片段，你应该注意到可处理的属性都是以 th: 开头。

这个 `th` 被称为方言前缀，它意味着所有由该方言处理的标签和属性都将以这个前缀开始。每个方言可以指定自己的前缀。

还要注意的是，一个模板引擎可以同时设置多个方言，从而允许处理包含所有指定方言特性的模板（把方言视为一种类似 JSP 标签库的增强功能）。
其中一些方言可以共享前缀，实际上充当一个聚合方言的作用。

## 基本属性

Thymeleaf 提供了许多 `th` 属性，用于评估表达式并将这些属性的值设置为其结果。
它们的名称与它们所设置的属性的名称相似，用来对应不同的 XHTML 和 HTML5 属性。

标准方言中的几个最基本的属性：

```html
// 替换了标签的主体
<p th:text="#{msg.welcome}">Welcome everyone!</p>

// 语法等同于 foreach
<li th:each="book : ${books}" th:text="${book.title}">En las Orillas del Sar</li>

// 提交表单时，浏览器将向 /createOrder 发送POST请求 
<form th:action="@{/createOrder}" method="post">
    
// 使用表达式 #{form.submit} 的求值结果作为按钮的值
<input type="button" th:value="#{form.submit}" />

// 跳转到 /admin/users 地址
<a th:href="@{/admin/users}">
...
```

## Thymeleaf 标准表达式

大多数 Thymeleaf 属性允许将其值设置为或包含表达式，由于它们使用的方言，我们将其称为标准表达式。

包含以下五种类型：

### ${...} : Variable expressions.

变量表达式用于在模板中访问和显示变量的值。
变量可以是通过控制器传递给模板的模型属性、请求参数、会话属性等。

**1、访问自定义对象**
```html
<p th:text="${user.name}"></p>
```
`${user.name}` 表达式用于访问模型中名为 "user" 对象的 "name" 的属性，并将其值插入到 `<p>` 元素中。

**2、访问内置对象**

① 访问请求对象：
```html
<input id="requestURI" th:value="${#request.requestURI}"/>
```
[Thymeleaf 文档](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#base-objects") 中可通过 `${ #ctx.request }` 在上下文对象中获取 request，也可以通过简化形式 `${ #request }` 获得到 request。再通过 request 中的 requestURI 获得。

② 访问请求参数：
```html
<p th:text="${param.email}"></p>
```
`${param.email}` 表达式用于获取名为 "email" 的请求参数的值，并将其插入到 `<p>` 元素中。

③ 访问会话属性：
```html
${session.user}
```
`${session.user}` 表达式用于获取会话中名为 "user" 的属性的值，并将其插入到 `<p>` 元素中。

【注意】：${...} 变量表达式在模板中只能读取变量的值，不能修改变量的值。

### *{...} : Selection expressions.

选择表达式与变量表达式一样，将在选定的对象上执行，而不是在整个上下文变量映射上执行。

```html
<div th:object="${user}">
   <p th:text="${user.name}"></p>
   <p th:text="*{age}"></p>
</div>
```

`${user}` 是一个对象绑定到上下文变量中的用户对象。`th:object` 指令会将该对象设置为当前选择对象。
然后，我们可以使用选择表达式 `*{age}` 相当于 `${user.age}` 来获取对象的属性值。

### #{...} : Message(i18n) expressions.

#{...} 是一种用于国际化（i18n）的消息表达式。它的主要目的是在软件中支持多语言的消息处理。

```JS
const name = 'Alice';
const greeting = `Hello, #{name}!`;
console.log(greeting);
```
`#{name}` 表达式用来将变量 name 的值动态地插入到问候消息中，生成适当的本地化文本。

### @{...} : Link(URL) expressions.

`@{...}` 表达式是链接表达式（Link Expressions），用于生成动态链接（URL）。可以轻松地处理路由和参数传递，无需手动构建 URL。

**1、生成相对路径链接：**
```html
<a th:href="@{/home}">Home</a>
```
`@{/home}` 表达式将生成一个相对于当前上下文路径的链接，指向 "home" 路径。当用户点击链接时，将导航到 "/home" 页面。

**2、生成带参数的链接：**
```html
<a th:href="@{/user/details(userId=${user.id})}">View Details</a>
```
`@{/user/details(userId=${user.id})}` 表达式生成一个带有参数的链接。
`${user.id}` 是一个变量表达式，表示用户的 ID。生成的链接将包含用户 ID 作为查询参数，例如： "/user/details?userId=123"。

**3、生成 URI 片段链接：**
```html
<a th:href="@{#section-1}">Go to Section 1</a>
```
直接跳转到具有 ID 为 "section-1" 的页面片段。

【注意】：
- 链接表达式只能在 HTML 标签的属性中使用，用于生成正确的链接。
- 片段表达式在 `Thymeleaf 3.0` 及更高版本中引入。

### ~{...} : Fragment expressions.

`~{...}` 表达式是[片段表达式（Fragment Expressions）](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#template-layout")，用于引入和使用模板片段，重用可独立使用的模块或组件。
通过引入和参数化片段，在不同的地方使用相同的代码片段，提高了模板的可维护性和重用性。

通过 `th:fragment` 定义模板，然后用 `th:insert` 或 `th:replace` 使用定义的模板。

**使用格式为：** `{templatename::selector}`，应用于名为 `templatename` 的模板上的指定标记选择器所得到的片段。也可以使用：
- `~{templatename}` ：包含名为 templatename 的完整模板。
- `~{::selector} 或 ~{this::selector}` ：插入与选择器匹配的来自同一个模板的片段。

**常见属性：**
- th:insert：它将简单地插⼊指定宿主标签的标签体中
- th:replace：⽤指定的⽚段替换其宿主标签

**1、包含模板片段：**

定义了一个名为 `copy` 的片段：
```html
<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<body>
    <footer th:fragment="copy">
        &copy; 2011 The Good Thymes Virtual Grocery
    </footer>
</body>
</html>
```
使用 `th:insert` 或 `th:replace` 属性在页面中包含该片段：
```html
<body>
  <div th:insert="~{footer :: copy}"></div>
  <div th:replace="~{footer :: copy}"></div>
</body>
```
`th:insert` 或 `th:replace` 期望一个片段表达式（~{...}），它是一个返回片段的表达式。执行结果：
```html
<body>
  <div>
    <footer>
        &copy; 2011 The Good Thymes Virtual Grocery
    </footer>
  </div>

  <footer>
      &copy; 2011 The Good Thymes Virtual Grocery
  </footer>
</body>
```
借助于标记选择器的强大功能，可以不使用任何 `th:fragment` 属性的片段。通过 `CSS` 选择器的方式如：选择器 `id` 引用它。
```html
<div id="copy-section">
    &copy; 2011 The Good Thymes Virtual Grocery
</div>
```
```html
<body>
    <div th:insert="~{footer :: #copy-section}"></div>
</body>
```

**2、参数化片段：**

使用 `th:fragment` 属性为片段定义参数，并调用带参数的片段。

代码定义了一个名为 `myFragment` 的片段，接收两个参数 `param1` 和 `param2`：
```html
<div th:fragment="myFragment (param1, param2)">
    <p th:text="${param1} + ' - ' + ${param2}">...</p>
</div>
```
调用带参数的片段：
```html
<div th:replace="~{ ::myFragment (${value1},${value2}) }">...</div>
<div th:replace="~{ ::myFragment (param1=${value1},param2=${value2}) }">...</div>
```

`th:replace="~{::myFragment (param1=${value1},param2=${value2})}"` 这相当于 `th:replace` 和 `th:with` 的组合：
```html
<div th:replace="~{::myFragment}" th:with="param1=${value1},param2=${value2}">
```

【注意】：片段表达式在 `Thymeleaf 3.0` 及更高版本中引入。

### Literals and operations

在Thymeleaf模板引擎中，字面量（Literals）和表达式操作（Operations）用于在模板中进行数据处理和计算。
这些表达式可以用于文本替换、条件判断、循环迭代等操作，从而使模板更具动态性和灵活性。

**文字：**
    - 文本文字：'一段文字'，'另一个！'，...
    - 数字文字：0，34，3.0，12.3，...
    - 布尔文字：true，false
    - 空文字：null
    - 文字标记：one，sometext，main，...

**文字操作：**
    - 字符串连接：+
    - 文字替换：|The name is \${name}|

**算术操作：**
    - 二元运算符：+，-，\*，/，%
    - 减号（一元运算符）：-
    
**布尔操作：**
    - 二元运算符：and，or
    - 布尔否定（一元运算符）：！，not

**比较和相等：**
    - 比较运算符：>，<，>=，<=（gt，lt，ge，le）
    - 相等运算符：==，!=（eq，ne）

**条件运算符：**
    - If-then: (if) ? (then)
    - If-then-else: (if) ? (then) : (else)
    - Default: (value) ?: (defaultvalue)

示例：

**1、字符串字面量：**
```html
<p th:text="'Hello, Thymeleaf!'"></p>
```
`'Hello, Thymeleaf!'` 是一个字符串字面量，可以在 `<p>` 元素中显示文本 "Hello, Thymeleaf!"。

**2、数字字面量：**
```html
<p th:text="42"></p>
```
`42` 是一个数字字面量，可以在 `<p>` 元素中显示数字 42。

**3、变量引用：**
```html
<p th:text="${username}"></p>
```
`${username}` 是一个变量引用，通过该表达式可以获取名为 "username" 的变量的值，并在 `<p>` 元素中显示。

**4、算术操作：**
```html
<p th:text="${number1 + number2}"></p>
```
`${number1 + number2}`是一个算术操作，通过该表达式可以对 number1 和 number2 变量进行加法运算，并在 `<p>` 元素中显示结果。

**5、逻辑操作：**
```html
<p th:if="${age >= 18}">You are an adult.</p>
```
`${age >= 18}` 是一个逻辑操作，通过该表达式可以判断 age 变量是否大于或等于 18，如果条件满足，则显示 "You are an adult."。

### Expression preprocessing

表达式预处理（Expression Preprocessing）是一种用于对表达式进行预处理和修改的机制。可以使用预处理器在表达式求值之前对其进行操作和转换。
预处理器提供了一些特殊语法和功能，可以扩展表达式的功能并提供更好的灵活性和可读性。

预处理的具体用法：

**1、转义表达式：**
```html
<p th:text="|Hello, \${name}!|"></p>
```
`|\${name}|` 是一个转义表达式，通过在表达式外添加竖线字符 "|"，可以防止表达式被求值，而直接显示为文本 "Hello, ${name}!"。

**2、默认值设置：**
```html
<p th:text="${username} ?: 'Guest'"></p>
```
`${username} ?: 'Guest'` 是一个默认值设置，如果 username 变量为空或不存在，将使用默认值 "Guest"。

**3、集合选择：**
```html
<ul>
    <li th:each="item : ${items}" th:text="${item.name}"></li>
</ul>
```
`${item.name}` 是一个集合选择表达式，用于从 items 集合中选取每个元素的 name 属性并显示在列表项中。

**4、字符串拼接：**
```html
<p th:text="'Hello ' + ${name}"></p>
```
`'Hello ' + ${name}` 是一个字符串拼接表达式，可将字符串 "Hello " 和 name 变量的值进行拼接。

【注意】：片段表达式在 `Thymeleaf 3.0` 及更高版本中引入。

# 总结
`Thymeleaf` 是一种 Java 模板引擎，大大提高开发效率，提高代码复用率，拥有快速开发网页能力，掌握它还是很有必要的！
若想了解更多 `Thymeleaf` ，请到[Thymeleaf 官网](https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html#introducing-thymeleaf)深入学习。
