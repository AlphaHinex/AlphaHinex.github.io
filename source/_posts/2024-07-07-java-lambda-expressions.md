---
id: java-lambda-expressions
title: "【转】Java 8 In Action Lambda"
description: "代码优化的过程中通过使用 lambda 表达式，减少代码量，提高代码可读性。"
date: 2024.07.07 10:34
categories:
    - Java
tags: [Java, Stream]
keywords: functional interface, lambda, method reference, closure
cover: /contents/java-lambda-expressions/cover.png
---

原文地址：https://wyiyi.github.io/amber/

## 引言

在优化代码的过程中，通过使用`Java 8 lambda`表达式，减少代码量，提高代码可读性。

## lambda 表达式简介

Lambda 表达式可以理解为一种匿名函数，它没有名称，但有参数列表、函数体、返回类型，并且可能还有一个可能抛出的异常列表。Lambda 表达式可以作为参数传递给方法，也可以存储在变量中。与匿名内部类相比，Lambda 表达式更加简洁。

从一个例子入手：写一个比较苹果的重量的逻辑：

- 传统方式：

```java
Comparator<Apple> byWeight = new Comparator<Apple>() {
     public int compare(Apple a1, Apple a2){
        return a1.getWeight().compareTo(a2.getWeight());
     }
};
```

- 使用 lambda 表达式：

```java
Comparator<Apple> byWeight = (Apple a1, Apple a2) -> a1.getWeight().compareTo(a2.getWeight());
```

必须承认，代码看起来变得更清晰了。

[引用 Java 8 inAction：](https://book.douban.com/subject/25912747/)

> A lambda expression is composed of parameters, an arrow, and a body.

![labmda](/contents/java-lambda-expressions/lambda.jpeg)

* 参数列表：在这个例子中，它反映了`Comparator`的`compare`方法的参数（两个`Apple`对象）。
* 箭头：箭头`->`将参数列表与`lambda`的函数体分隔开。
* `Lambda`的函数体：使用它们的重量比较两个`Apple`对象。这个表达式被认为是`lambda`的返回值。


### Lambda 的基本语法

```java
(parameters) -> expression // 表达式风格
// 或者（注意使用花括号表示语句）
(parameters) ->{ statements; } // 块风格
```

### 简单的示例

```java
// 一个布尔表达式
(List<String> list) -> list.isEmpty();

// 创建对象
() -> new Apple(10); 

// 从对象中消费
(Apple a) -> { System.out.println(a.getWeight()); }

// 从对象中选择/提取 
(String s) -> s.length();

// 组合两个值 
(int a, int b) -> a * b; 

// 比较两个对象 
(Apple a1, Apple a2) -> a1.getWeight().compareTo(a2.getWeight());
```

## 函数式接口

在`Java 8`的`java.util.function`包中引入了一系列的函数式接口，如：`Predicate`，`Consumer`，和 `Function`等。函数式接口是一种特殊的接口，它只定义了一个抽象方法，这样的接口可以用来表示`Lambda`表达式。

### 函数式接口特点：

* 函数式接口可以有一个或多个默认方法（`default methods`），这些默认方法可以有实现。
* 函数式接口可以有多个静态方法（`static methods`），这些静态方法也可以有实现。
* 函数式接口可以有多个从父接口继承的抽象方法，但这些方法必须都是唯一的，也就是说，函数式接口里只能有一个抽象方法。
* 函数式接口可以用`@FunctionalInterface`注解来标记，但这不是必须的。这个注解的作用是帮助编译器检查接口是否符合函数式接口的定义。

### For a Example

- `Predicate<T>`：接受一个泛型`T`的对象，并返回一个布尔值。常用于条件判断。

```java
Predicate<String> predicate = s -> s.isEmpty();
boolean result = predicate.test("");
```

- `Consumer<T>`：接受一个泛型`T`的对象，并执行一些操作，但没有返回值。常用于数据消费。

```java
Consumer<String> consumer = System.out::println;
consumer.accept("Hello World");
```

- `Function<T, R>`：接受一个泛型`T`的对象，并返回一个泛型`R`的对象。常用于转换数据。

```java
Function<Integer, String> function = String::valueOf;
String apply = function.apply(123);
```

- `Supplier<T>`：提供一个泛型`T`的对象，但不接受任何参数。常用于提供数据源。

```java
Supplier<String> supplier = () -> "Hello";
String s = supplier.get();
```

- `Runnable`：定义一个无参数无返回值的执行块。

```java
Runnable runnable = () -> System.out.println("Hello World");
new Thread(runnable).start();
```

## 方法引用

方法引用是`lambda`表达式的更简洁的语法，它允许我们引用类中的现有方法。

当使用方法引用时，目标引用放在分隔符`::`之前，方法名称在它之后提供，即：目标引用`::`方法。

使用 `::` 运算符作为 `Lambda` 调用特定方法的缩写，并且拥有更好的可读性。

lambda 表达式与方法引用等价示例：

```java
(Apple a) -> a.getWeight() Apple::getWeight
        
() -> Thread.currentThread().dumpStack() Thread.currentThread()::dumpStack
        
(str, i) -> str.substring(i) String::substring
        
(String s) -> System.out.println(s) System.out::println
```

### 方法引用的三种类型

1. **静态方法引用**：如：

* lambda表达式: `(s) -> Integer.parseInt(s)`
* 方法引用: `Integer::parseInt`

2. **任意类型的实例方法引用**：引用一个类型的实例方法，并且这个实例作为参数传递给`lambda`表达式时使用。如：

* lambda表达式: `(s) -> s.toUpperCase()`
* 方法引用: `String::toUpperCase`

3. **现有对象的实例方法引用**：在`lambda`表达式中调用一个已经存在的对象的方法时使用。如：

* lambda表达式: `() -> expensiveTransaction.getValue()`
* 方法引用: `expensiveTransaction::getValue`

## 总结

`Java 8` 中的 `Lambda` 表达式可以让代码更加简洁、易读，并且提高开发效率。