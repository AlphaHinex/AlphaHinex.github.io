---
id: reactive-programming-flux-mono
title: "【转】响应式编程——初识 Flux 和 Mono"
description: "Reactor 是一个响应式编程的基础类库，其中有两个很关键的类：Flux 和 Mono。掌握这两个类和相关概念有助于我们学习响应式编程。"
date: 2026.08.02 10:34
categories:
    - Java
tags: [Java, reactive]
keywords: reactive programming, flux, mono, reactor, java
cover: /contents/reactive-programming-flux-mono/flux.png
---

- 原文地址：https://www.emanjusaka.com/archives/reactive-programming-flux-mono
- 原文作者：[emanjusaka](https://www.emanjusaka.com/about)

---

## 前言

Reactor 是一个响应式编程的基础类库，其中有两个很关键的类：Flux 和 Mono。掌握这两个类和相关概念有助于我们学习响应式编程。

Flux 和 Mono 都是数据流的发布者，使用 Flux 和 Mono 都可以发出三种数据信号：元素值，错误信号，完成信号；错误信号和完成信号都代表终止信号，终止信号用于告诉订阅者数据流结束了，错误信号终止数据流同时把错误信息传递给订阅者。

## 一、Flux

具有 rx 运算符的响应式流发布器，发出 0 到 N 个元素，然后完成（成功或有错误）。

下图显示了 Flux 如何转换项目：

![Flux 转换示意图](https://alphahinex.github.io/contents/reactive-programming-flux-mono/flux.png)

Flux\<T> 是一个标准的 Publisher\<T>，表示一个异步的 0 到 N 个发出的项目序列，可选择终止于完成信号或错误信号。根据 Reactive Streams 规范，这三种类型的信号转换为对下游 Subscriber 的 onNext、onComplete 和 onError 方法的调用。

由于可能出现的信号范围很大，Flux 是通用的响应式类型。请注意，所有事件，包括终止事件，都是可选的：没有 onNext 事件但有 onComplete 事件表示一个空的有限序列，但如果去掉 onComplete，则得到一个无限的空序列（除了用于取消测试之外，不是特别有用）。同样，无限序列不一定为空。例如，`Flux.interval(Duration)` 会生成一个无限的 Flux\<Long>，从时钟发出定期的滴答声。Flux\<T> 是标准的 Publisher\<T>，它表示 0 到 N 个发出项的异步序列，可以选择由完成信号或错误终止。与 Reactive Streams 规范中一样，这三种类型的信号转换为对下游订阅者的 onNext、onComplete 和 onError 方法的调用。

凭借如此大范围的可能信号，Flux 是通用的无功类型。请注意，所有事件，甚至终止事件，都是可选的：没有 onNext 事件，但 onComplete 事件表示一个空的有限序列，但删除 onComplete 并且您有一个无限的空序列（不是特别有用，除了围绕取消的测试）。同样，无限序列不一定是空的。例如，`Flux.interval(Duration)` 生成无限的 Flux\<Long> 并从时钟发出规则的滴答声。

## 二、Mono

具有基本 rx 运算符的 Reactive Streams Publisher 通过 onNext 信号最多发出一项，然后以 onComplete 信号终止（成功的 Mono，有或没有值），或者仅发出单个 onError 信号（失败的 Mono）。

下图显示了 Mono 如何转换项目：

![Mono 转换示意图](https://alphahinex.github.io/contents/reactive-programming-flux-mono/mono.png)

Mono\<T> 是一种特殊的 Publisher\<T>，通过 onNext 信号发出最多一个项目，然后通过 onComplete 信号终止（成功的 Mono，有或没有值），或者只发出一个 onError 信号（失败的 Mono）。

大多数 Mono 实现在调用 onNext 后立即调用其 Subscriber 的 onComplete。`Mono.never()` 是一个例外：它不发出任何信号，在技术上并不禁止，但在测试之外没有太大用处。另一方面，明确禁止使用 onNext 和 onError 的组合。

Mono 只提供了 Flux 可用的操作符的子集，而某些操作符（特别是将 Mono 与另一个 Publisher 组合的操作符）会切换到 Flux。例如，`Mono.concatWith(Publisher)` 返回一个 Flux，而 `Mono.then(Mono)` 返回另一个 Mono。

请注意，您可以使用 Mono 来表示只有完成概念的无值异步过程（类似于 Runnable）。要创建一个，您可以使用一个空的 Mono\<Void>。

## 三、代码示例

- 创建一个 Flux，发出一系列字符串元素并订阅打印出来：

```java
package top.emanjusaka;

import reactor.core.publisher.Flux;

public class Main {
    public static void main(String[] args) {
        Flux flux = Flux.just("Hello", "emanjusaka", "!");
        flux.subscribe(System.out::println);
    }
}

// 输出
Hello
emanjusaka
!
```

- 创建一个 Mono，发出一个字符串元素并订阅打印出来：

```java
package top.emanjusaka;

import reactor.core.publisher.Mono;

public class Main {
    public static void main(String[] args) {
        Mono mono = Mono.just("Hello");
        mono.subscribe(System.out::println);
    }
}

// 输出
Hello
```

- 使用 Flux 的操作符进行元素转换和过滤：

```java
package top.emanjusaka;

import reactor.core.publisher.Flux;

public class Main {
    public static void main(String[] args) {
        Flux numbers = Flux.range(1, 10);
        numbers.map(num -> num * 2)
               .filter(num -> num % 3 == 0)
               .subscribe(System.out::println);
    }
}

// 输出
6
12
18
```

- 使用 Mono 的操作符进行元素转换和错误处理：

```java
package top.emanjusaka;

import reactor.core.publisher.Mono;

public class Main {
    public static void main(String[] args) {
        Mono number = Mono.just(5);
        number.map(num -> num * 2)
              .doOnError(Throwable::printStackTrace)
              .subscribe(System.out::println);
    }
}

// 输出
10
```

## 四、总结

Flux 和 Mono 都是位于 `reactor.core.publisher` 包下的类。

Reactor 中的 Flux 和 Mono 是用于实现响应式编程的两种基本类型：

- Flux：表示一个异步序列，可以发出 0 到 N 个项目。它可以终止于完成信号或错误信号。Flux 适用于处理多个项目的情况，可以使用各种操作符来处理和转换序列。
- Mono：表示一个异步序列，最多发出一个项目。它要么终止于完成信号（有或没有值），要么只发出一个错误信号。Mono 适用于处理单个项目的情况，也可以使用一些操作符来处理和转换序列。

这两种类型都是 Publisher 的实现，遵循 Reactive Streams 规范，并可以与其他响应式库和框架进行互操作。

Flux 和 Mono 都可以表示无限序列，也可以表示空序列。它们提供了丰富的操作符来处理和转换序列，例如映射、过滤、合并、扁平化等。此外，它们还支持异步和并发处理，可以与其他操作符和操作进行组合使用。

总的来说，Flux 适用于处理多个项目的情况，而 Mono 适用于处理单个项目的情况。它们是 Reactor 中用于实现响应式编程的基本类型，提供了丰富的操作符和功能来处理和转换异步序列。

## 五、参考文献

- [《Reactor》参考文档](https://projectreactor.io/docs/core/release/reference/index.html)