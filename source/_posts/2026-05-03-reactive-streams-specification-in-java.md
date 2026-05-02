---
id: reactive-streams-specification-in-java
title: "【译】Java 中的 Reactive Streams 规范"
description: "Reactive Streams 是一个跨平台的规范，用于在异步边界（线程、进程或网络连接的计算机）上处理可能无限的事件序列，同时支持非阻塞的背压。"
date: 2026.05.03 10:34
categories:
    - Java
    - Spring
tags: [concurrency, reactive]
keywords: Java, concurrency, Reactive Streams, backpressure, Publisher, Subscriber, Subscription, Processor
cover: /contents/reactive-streams-specification-in-java/cover.png
---

- 原文地址：https://aliakh.github.io/2023/05/25/reactive_streams_specification_in_java/
- 原文作者：[Aliaksandr Liakh](https://github.com/aliakh)

---

## 介绍

Reactive Streams 是一个跨平台的规范，用于在异步边界（线程、进程或网络连接的计算机）上处理可能无限的事件序列，同时支持非阻塞的背压。一个反应式流包含一个发布者，它向前发送 _数据_ 、_错误_ 、_完成_ 事件，以及订阅者，它向后发送 _请求_ 和 _取消_ 背压事件。在发布者和订阅者之间，还可以有中间处理器，用于过滤或转换事件。

<sub><em>背压（Backpressure）</em> 是从订阅者到发布者的应用级流量控制，用于控制发送速率。</sub>

Reactive Streams 规范旨在高效地处理（在 CPU 和内存使用方面）有时间顺序的事件序列。为了高效使用 CPU，规范描述了不同阶段（生产者、处理器、消费者）异步和非阻塞事件处理的契约。为了高效使用内存，规范描述了基于事件处理速率在 _push_ 和 _pull_ 通信模型之间切换的契约，从而避免使用无界缓冲区。

<!-- more -->

##  问题与解决方案

在设计将项目（items）从生产者传输到消费者的系统时，目标是以最小的延迟和最大的吞吐量发送它们。

<sub><em>延迟（Latency）</em> 是从生产者发送一个项目到消费者接收该项目的时间。<em>吞吐量（Throughput）</em> 是单位时间内从生产者发送到消费者的项目数量。</sub>

然而，生产者和消费者可能存在一些限制，这些限制可能会阻止系统达到最佳性能：

* 消费者可能比生产者慢。
* 消费者可能无法跳过它没有时间处理的项目。
* 生产者可能无法减慢或停止发送消费者没有时间处理的项目。
* 生产者和消费者可能只有有限的 CPU 核心来异步处理项目，以及有限的内存来缓冲项目。
* 生产者和消费者之间的通信通道可能带宽有限。

有几种顺序处理项目的模式，可以解决上述一些或大部分限制：

* Iterator
* Observer
* Reactive Extensions
* Reactive Streams

这些模式分为两类：同步 _pull_ 通信模型（消费者决定何时从生产者接收项目）和异步 _push_ 通信模型（生产者决定何时向消费者发送项目）。

### Iterator

在 Iterator 模式中，消费者同步地从生产者那里一个一个地 _pull_ 项目。生产者只有在消费者请求时才发送项目。如果生产者在请求时没有项目，它会发送一个空响应。

![Iterator](https://alphahinex.github.io/contents/reactive-streams-specification-in-java/Iterator.png)

优点：

* 消费者可以在任何时候开始交换。
* 如果消费者尚未处理完前一个项目，则无法请求下一个项目。
* 消费者可以在任何时候停止交换。

缺点：

* 延迟可能由于拉取周期选择不当而不理想（拉取周期过长会导致高延迟；拉取周期过短会浪费 CPU 和 I/O 资源）。
* 吞吐量不理想，因为发送每个项目都需要一次请求-响应。
* 消费者无法确定生产者是否已经完成项目的生成。

当使用 Iterator 模式逐个传输项目时，延迟和吞吐量通常不理想。为了在最小修改的情况下改善这些参数，可以以批量传输项目的方式使用 Iterator 模式，而不是每次只传输一个项目。

![Iterator with batching](https://alphahinex.github.io/contents/reactive-streams-specification-in-java/Iterator_with_batching.png)

优点：

* 消费者可以在任何时候开始交换。
* 如果消费者尚未处理完前一个项目，则无法请求下一个项目。
* 消费者可以在任何时候停止交换。
* 吞吐量增加，因为请求/响应的次数从每个项目一次减少到每个批次一次。

缺点：

* 延迟增加，因为生产者需要更多时间来发送更多项目。
* 如果批次大小过大，可能无法适应生产者或消费者的内存。
* 如果消费者想要停止处理，他只能在接收到整个批次后才能停止。

### Observer

在 Observer 模式中，一个或多个消费者订阅生产者的事件。生产者在生成事件后会异步地将事件 _push_ 给所有已订阅的消费者。如果消费者不再需要事件，可以取消订阅生产者。

![Observer](https://alphahinex.github.io/contents/reactive-streams-specification-in-java/Observer.png)

优点：

* 消费者可以在任何时候开始交换。
* 消费者可以在任何时候停止交换。
* 延迟比同步 _pull_ 通信模型低，因为生产者在事件可用时立即发送给消费者。

缺点：

* 较慢的消费者可能会被较快的生产者的事件淹没。
* 消费者无法确定生产者是否已经完成项目的生成。
* 实现并发的生产者和消费者可能并非易事。

### Reactive Extensions

Reactive Extensions (ReactiveX) 是一系列用于处理同步或异步事件流的多平台框架，最初由 Microsoft 的 Erik Meijer 创建。Reactive Extensions 在 Java 中的实现是 Netflix 的 RxJava 框架。

简而言之，Reactive Extensions 是 Observer 和 Iterator 模式与函数式编程的结合。从 Observer 模式中，它们借用了消费者订阅生产者事件的能力。从 Iterator 模式中，它们借用了处理三种类型事件流（数据、错误、完成）的能力。从函数式编程中，它们借用了使用链式方法（过滤、转换、组合等）处理事件流的能力。

![Reactive Extensions](https://alphahinex.github.io/contents/reactive-streams-specification-in-java/Reactive_Extensions.png)

优点：

* 消费者可以在任何时候开始交换。
* 消费者可以在任何时候停止交换。
* 消费者可以确定生产者何时完成事件的生成。
* 延迟比同步 _pull_ 通信模型低，因为生产者在事件可用时立即发送给消费者。
* 消费者可以统一处理三种类型的事件流（数据、错误、完成）。
* 使用链式方法处理事件流可能比使用许多嵌套的事件处理器更容易。

缺点：

* 较慢的消费者可能会被较快的生产者的事件淹没。
* 实现并发的生产者和消费者可能并非易事。

### Reactive Streams

Reactive Streams 是对 Reactive Extensions 的进一步发展，它使用背压来匹配生产者和消费者的性能。简而言之，Reactive Streams 是 Reactive Extensions 和批处理的结合。

它们之间的主要区别在于谁是交换的发起者。在 Reactive Extensions 中，发布者在事件可用时立即向订阅者发送事件，数量不限。在 Reactive Streams 中，发布者必须在订阅者请求后才向其发送事件，且不超过请求的数量。

![Reactive Streams](https://alphahinex.github.io/contents/reactive-streams-specification-in-java/Reactive_Streams.png)

优点：

* 消费者可以在任何时候开始交换。
* 消费者可以在任何时候停止交换。
* 消费者可以确定生产者何时完成事件的生成。
* 延迟比同步 _pull_ 通信模型低，因为生产者在事件可用时立即发送给消费者。
* 消费者可以统一处理三种类型的事件流（数据、错误、完成）。
* 使用链式方法处理事件流可能比使用许多嵌套的事件处理器更容易。
* 消费者可以根据需要从生产者请求事件。

缺点：

* 实现并发的生产者和消费者可能并非易事。

## Backpressure

对于生产者生成事件的速度比消费者处理事件的速度快的问题，有几种解决方案。在 _pull_ 通信模型中，这种情况不会发生，因为消费者发起交换。在 _push_ 通信模型中，生产者通常无法确定发送速率，因此消费者可能最终会收到比它能处理的更多事件。背压（Backpressure）是解决这个问题的一种方法，通过通知生产者其消费者的处理速率来实现。

不使用背压时，消费者有几种解决方案来处理过多的事件：

* 缓冲事件
* 丢弃事件
* 丢弃事件并通过它们的标识符请求生产者重新发送它

<sub>任何在消费者端丢弃事件的解决方案都可能效率低下，因为这些事件仍然需要通过 I/O 操作从生产者发送。</sub>

Reactive Streams 中的背压是通过以下方式实现的。为了开始从生产者接收事件，消费者 _拉取_ 它想要接收的项目数量。只有在此之后，生产者才会 _推送_ 事件给消费者；生产者永远不会主动发送它们。在消费者处理完所有它请求的事件后，整个周期重复。在特定情况下，如果已知消费者比生产者快，则可以在 _push_ 通信模型中工作，并在订阅后立即请求所有项目。或者相反，如果已知消费者比生产者慢，则可以在 _pull_ 通信模型中工作，并且仅在处理完前一批项目后才请求下一批。因此，反应式流操作的模型可以描述为 _动态 推/拉_ 通信模型。无论生产者比消费者快或慢，甚至当这种比例随时间变化时，它都能有效地工作。

使用背压时，生产者有更多的解决方案来处理过多的事件：

* 缓冲事件
* 丢弃事件
* 暂停生成事件
* 阻止生产者
* 取消事件流

使用哪个解决方案来处理特定的反应式流取决于事件的性质。但背压并不是一个 _银弹_ 。它只是将性能不匹配的问题转移到了生产者端，在那里它应该更容易解决。然而，在某些情况下，有比背压更好的解决方案，比如简单地在消费者端丢弃过多的事件。

## Reactive Streams 规范

Reactive Streams 是一个 [规范](https://www.reactive-streams.org/)，旨在为各种运行时环境（JVM、.NET 和 JavaScript）和网络协议提供具有非阻塞背压功能的异步流处理标准。Reactive Streams 规范由 Kaazing、Lightbend、Netflix、Pivotal、Red Hat、Twitter 等公司的工程师创建。

该规范描述了具有以下特性的 _反应式流（reactive streams）_ 的概念：

* 反应式流可以是 _单播（unicast）_ 或 _多播（multicast）_ 的：发布者可以向一个或多个消费者发送事件。
* 反应式流可能是 _无限的_ ：它们可以处理零个、一个、多个或无限数量的事件。
* 反应式流是 _顺序的_ ：消费者按发布者发送事件的顺序处理事件。
* 反应式流可以是 _同步_ 或 _异步_ 的：它们可以在不同阶段使用计算资源进行并行处理。
* 反应式流是 _非阻塞的_ ：如果生产者和消费者的性能不同，它们不会浪费计算资源。
* 反应式流使用 _强制背压_ ：消费者可以根据其处理速率从生产者请求事件。
* 反应式流使用 _有界缓冲区_ ：它们可以在没有无界缓冲区的情况下实现，从而避免内存溢出错误。

Reactive Streams [JVM 规范](https://github.com/reactive-streams/reactive-streams-jvm)（最新版本 1.0.4 于 2022 年 5 月 26 日发布）包含文本规范和 Java API，其中包含四个必须根据此规范实现的接口。它还包括技术兼容性套件（Technology Compatibility Kit, TCK），这是用于实现一致性测试的标准测试套件。

值得注意的是，Reactive Streams 规范是在已经存在多个成熟但不兼容的 Reactive Streams 实现之后创建的。因此，该规范目前是有限的，仅包含低级 API。应用程序开发人员应使用此规范在现有实现之间提供互操作性。要获得高级功能 API（过滤、转换、组合等），应用程序开发人员应使用此规范的实现（Lightbend Akka Streams、Pivotal Project Reactor、Netflix RxJava 等）所提供的原生 API。

## Reactive Streams API

Reactive Streams API 由四个接口组成，这些接口位于 _org.reactivestreams_ 包中：

* Publisher&lt;T> 接口表示数据和控制事件的生产者。
* Subscriber&lt;T> 接口表示事件的消费者。
* Subscription 接口表示发布者和订阅者之间的连接。
* Processor&lt;T,R> 接口表示一个事件处理器，它既是订阅者又是发布者。

![Reactive Streams API](https://alphahinex.github.io/contents/reactive-streams-specification-in-java/Reactive_Streams_API.png)

### Publisher

Publisher 接口表示潜在无限的有序数据和控制事件的生产者。发布者根据从一个或多个订阅者接收到的需求（demand）来生产事件。

<sub><em>需求（Demand）</em> 是订阅者请求但尚未由发布者交付的项目总数。</sub>

发布者对于订阅者是否接收在其订阅之前产生的事件可能会有所不同。_冷（Cold）_ 发布者可以重复，并且直到被订阅时才开始产生事件（如内存迭代器、文件读取、数据库查询等）。_热（Hot）_ 发布者无法重复，并且立即开始，无论是否存在订阅者（如键盘和鼠标事件、传感器事件、网络请求等）。

```java
public interface Publisher<T> {
    public void subscribe(Subscriber<? super T> s);
}
```

这个接口有以下方法：

* _subscribe(Subscriber)_ 方法请求发布者开始向订阅者（Subscriber）发送事件。

### Subscriber

Subscriber 接口表示事件的消费者。多个订阅者可以在不同时间订阅和取消订阅生产者。

```java
public interface Subscriber<T> {
    public void onSubscribe(Subscription s);
    public void onNext(T item);
    public void onError(Throwable t);
    public void onComplete();
}
```

这个接口有以下方法：

* _onSubscribe(Subscription)_ 方法在生产者接受新的订阅时调用。
* _onNext(T)_ 方法在接收到每个项目时调用。
* _onError(Throwable)_ 方法在发生错误时调用。
* _onComplete()_ 方法在成功完成时调用。

### Subscription

Subscription 接口表示发布者和订阅者之间的连接。通过 Subscription，订阅者可以从发布者请求项目或取消连接。

```java
public interface Subscription {
    public void request(long n);
    public void cancel();
}
```

这个接口包括下列方法：

* _request(long)_ 方法将给定数量的项目添加到此订阅的未完成的需求中。
* _cancel()_ 方法请求发布者 _最终（eventually）_ 停止发送项目。

### Processor

Processor 接口表示一个事件处理阶段，它同时继承了 Subscriber 和 Publisher 接口，并且受两者的约束。它作为反应式流的前一阶段的订阅者，同时作为下一阶段的发布者。

```java
public interface Processor<T, R> extends Subscriber<T>, Publisher<R> {
}
```

## Reactive Streams 工作流程

Reactive Streams 工作流程包括三个步骤：建立连接、交换数据和控制事件，以及成功或异常地终止连接。

![Reactive Streams workflow](https://alphahinex.github.io/contents/reactive-streams-specification-in-java/Reactive_Streams_workflow.png)

当订阅者想要开始从发布者接收事件时，它调用 _Publisher.subscribe(Subscriber)_ 方法。如果发布者接受请求，它会创建一个新的 Subscription 实例并调用 _Subscriber.onSubscribe(Subscription)_ 方法。如果发布者拒绝请求或以其他方式失败，它会调用 _Subscriber.onError(Throwable)_ 方法。

一旦发布者和订阅者通过 Subscription 实例建立了连接，订阅者就可以请求事件，发布者也可以发送事件。当订阅者想要接收事件时，它调用 _Subscription#request(long)_ 方法，传入请求的项目数量。通常，第一次请求调用发生在 _Subscriber.onSubscribe(Subscription)_ 方法中。发布者仅在响应先前的请求时，通过调用 _Subscriber.onNext(T)_ 方法发送每个请求的项目。如果反应式流结束，发布者可以发送少于请求数量的事件，但随后必须调用 _Subscriber.onComplete()_ 或 _Subscriber.onError(Throwable)_ 方法。

如果订阅者想要停止接收事件，它会调用 _Subscription.cancel()_ 方法。调用此方法后，订阅者仍然可以接收事件以满足先前请求的需求。已取消的订阅不会接收 _Subscriber.onComplete()_ 或 _Subscriber.onError(Throwable)_ 事件。

当没有更多事件时，发布者通过调用 _Subscriber.onComplete()_ 方法成功完成订阅。当发布者发生不可恢复的异常时，它通过调用 _Subscriber.onError(Throwable)_ 方法异常完成订阅。在调用 _Subscriber.onComplete()_ 或 _Subscriber.onError(Throwable)_ 事件后，当前订阅将不再向订阅者发送任何其他事件。

## JDK Flow API

JDK 从版本 9 开始以 Flow API 的形式支持 Reactive Streams 规范。[Flow](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/Flow.html) 类包含嵌套的静态 Publisher、Subscriber、Subscription、Processor 接口，这些接口与 Reactive Streams 规范中对应接口在语义上完全等价。Reactive Streams 规范包含 [FlowAdapters](https://github.com/reactive-streams/reactive-streams-jvm/blob/master/api/src/main/java9/org/reactivestreams/FlowAdapters.java) 类，这是 Reactive Streams API（_org.reactivestreams_ 包）和 JDK Flow API（_java.util.concurrent.Flow_ 类）之间的桥梁。JDK 目前提供的唯一 Reactive Streams 规范实现是 [SubmissionPublisher](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/SubmissionPublisher.html) 类，它实现了 Publisher 接口。

## 示例代码

### 同步冷反应式流

这个 [文档](https://github.com/aliakh/demo-java-reactive-streams/blob/master/src/main/java/demo/reactivestreams/part1/readme.md) 描述了一个同步生产者、同步消费者的实现，以及由它们创建的 _冷_ 反应式流。

### 异步冷反应式流

这个 [文档](https://github.com/aliakh/demo-java-reactive-streams/blob/master/src/main/java/demo/reactivestreams/part2/readme.md) 描述了一个异步生产者、异步消费者的实现，以及由它们创建的 _冷_ 反应式流。

### 异步热反应式流

这个 [文档](https://github.com/aliakh/demo-java-reactive-streams/blob/master/src/main/java/demo/reactivestreams/part5/readme.md) 描述了一个异步生产者、一个继承自 SubmissionPublisher 类的异步处理器的实现，以及由它们创建的 _热_ 反应式流。

## 结论

在 JDK 中出现 Reactive Streams 之前，已经存在相关的 CompletableFuture 和 Stream API。CompletableFuture API 使用 _push_ 通信模型，但支持单值的异步计算。Stream API 支持多值的同步或异步计算，但使用 _pull_ 通信模型。Reactive Streams 填补了这一空白，支持多值的同步或异步计算，并且可以在 _push_ 和 _pull_ 计算模型之间动态切换。因此，Reactive Streams 适用于处理速率不可预测的事件序列，例如鼠标和键盘事件、传感器事件以及来自文件或网络的延迟受限的 I/O 事件（latency-bound I/O events）。

至关重要的是，应用程序开发人员不应自己实现 Reactive Streams 规范的接口。首先，该规范足够复杂，特别是在异步契约方面，无法轻松地正确实现。其次，该规范不包含中间流操作的 API。相反，应用程序开发人员应使用现有框架（Lightbend Akka Streams、Pivotal Project Reactor、Netflix RxJava）及其更丰富的原生 API 来实现反应式流阶段（生产者、处理器、消费者）。他们应仅使用 Reactive Streams API 将异构阶段组合成单个反应式流。

完整的代码示例可在 [GitHub 仓库](https://github.com/aliakh/demo-java-reactive-streams) 中找到。
