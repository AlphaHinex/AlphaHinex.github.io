---
id: mockito-core-vs-mockito-inline
title: "【转】Mockito Core 与 Mockito Inline 的区别"
description: "Mockito Inline 可用来替代已不再维护的 PowerMock"
date: 2025.09.14 10:26
categories:
    - Test
    - Java
tags: [Testing, Mockito]
keywords: Mockito, mockito-core, mockito-inline, PowerMock
cover: /contents/covers/mockito-core-vs-mockito-inline.png
---

- 作者：[Oscar Ramadhan](https://www.baeldung.com/author/oscarramadhan)
- 英文版：[Difference Between Mockito Core and Mockito Inline](https://www.baeldung.com/mockito-core-vs-mockito-inline)
- 中文版：[Mockito Core 与 Mockito Inline 的区别](https://www.baeldung-cn.com/mockito-core-vs-mockito-inline)

# 1. 概述

Mockito 是 Java 中最流行的模拟对象框架之一，它提供了 Mockito Core 和 Mockito Inline 两个核心库，用于满足单元测试中不同场景的需求。

✅ 想深入学习 Mockito 测试技巧？可以参考我们的 [Mockito 系列教程](https://www.baeldung-cn.com/tag/mockito/)。

# 2. Mockito Core

Mockito Core 是 Mockito 的基础库，提供创建模拟对象（Mock）、桩对象（Stub）和间谍对象（Spy）的核心功能。对于大多数常见场景，这个库已经足够，但存在明显限制：

❌ **无法模拟 final 类和静态方法**

❌ **无法修改 final 字段**

❌ **无法拦截构造函数**

⚠️ 基础用法示例可参考[这里](https://www.baeldung-cn.com/mockito-mock-methods)

# 3. Mockito Inline

Mockito Inline 是 Mockito Core 的扩展版本，专门解决 Core 版本的限制。从 Mockito Core 5.0.0 开始，它已成为默认的模拟生成器。

## 3.1 模拟 final 类

首先创建一个 final 类：

```java
public final class FinalClass {
    public String greet() {
        return "Hello, World!";
    }
}
```

测试代码示例：

```java
@Test
void testFinalClassMock() {
    FinalClass finalClass = mock(FinalClass.class);
    when(finalClass.greet()).thenReturn("Mocked Greeting");

    assertEquals("Mocked Greeting", finalClass.greet());
}
```

**核心逻辑**： 我们将 `greet()` 方法原本返回的 "Hello, World!" 替换为 "Mocked Greeting"，这是传统 Core 版本无法实现的。

## 3.2 模拟 final 字段

创建包含 final 字段的类：

```java
public class ClassWithFinalField {
    public final String finalField = "Original Value";

    public String getFinalField() {
        return finalField;
    }
}
```

测试代码：

```java
@Test
void testFinalFieldMock() {
    ClassWithFinalField instance = mock(ClassWithFinalField.class);
    when(instance.getFinalField()).thenReturn("Mocked Value");

    assertEquals("Mocked Value", instance.getFinalField());
}
```

**踩坑指南**： 这里通过模拟 `getFinalField()` 方法绕过了 final 字段的不可变性，直接返回预设值 "Mocked Value"。

## 3.3 模拟静态方法

创建含静态方法的类：

```java
public class ClassWithStaticMethod {
    public static String staticMethod() {
        return "Original Static Value";
    }
}
```

测试实现：

```java
@Test
void testStaticMethodMock() {
    try (MockedStatic<ClassWithStaticMethod> mocked = mockStatic(ClassWithStaticMethod.class)) {
        mocked.when(ClassWithStaticMethod::staticMethod).thenReturn("Mocked Static Value");

        assertEquals("Mocked Static Value", ClassWithStaticMethod.staticMethod());
    }
}
```

**关键点**： 使用 `mockStatic()` 创建静态方法模拟上下文，在 try-with-resources 块内替换方法行为。

## 3.4 模拟构造函数

创建含构造函数的类：

```java
public class ClassWithConstructor {
    private String name;

    public ClassWithConstructor(String name) {
        this.name = name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getName() {
        return this.name;
    }
}
```

测试代码：

```java
@Test
void testConstructorMock() {
    try (MockedConstruction<ClassWithConstructor> mocked = mockConstruction(ClassWithConstructor.class,
            (mock, context) -> when(mock.getName()).thenReturn("Mocked Name"))) {

        ClassWithConstructor myClass = new ClassWithConstructor("test");
        assertEquals("Mocked Name", myClass.getName());
    }
}
```

**简单粗暴**： 通过 `mockConstruction()` 拦截所有新实例创建，强制 `getName()` 返回 "Mocked Name" 而非构造参数 "test"。

# 4. 功能对比总结

| 模拟目标   | Mockito Core | Mockito Inline |
|------------|:------------:|:--------------:|
| Final 类   | ❌ 不支持    | ✅ 支持        |
| Final 字段 | ❌ 不支持    | ✅ 支持        |
| 静态方法   | ❌ 不支持    | ✅ 支持        |
| 构造函数   | ❌ 不支持    | ✅ 支持        |

# 5. 结论

Mockito Core 和 Inline 的核心区别非常明确：

- Mockito Core：适用于基础模拟场景，但遇到 final 类/方法、静态成员或构造函数时会束手无策。
- Mockito Inline：完美解决 Core 的所有限制，支持模拟 final 类、final 字段、静态方法和构造函数，是复杂测试场景的终极解决方案。

💡 实际开发建议：直接使用 Mockito Core 5.0.0+（默认集成 Inline），避免因版本差异踩坑。