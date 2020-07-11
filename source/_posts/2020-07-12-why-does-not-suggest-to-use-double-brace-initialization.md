---
id: why-does-not-suggest-to-use-double-brace-initialization
title: "为什么不建议使用双括号初始化？"
description: "Double Brace Initialization in Java"
date: 2020.07.12 19:26
categories:
    - Java
tags: [Java]
keywords: Java, HashMap, Map, Java Collections, Double Brace Initialization
cover: /contents/covers/DoubleBraceInitialization.jpg
---


## 什么是双括号初始化？

```java
Map<String, Object> map = new HashMap<String, Object>() {{
    put("name", "Alpha");
    put("age", 8);
}};
```


## 为什么能这样写？

以下内容引自 [The Java™ Tutorials - Initializing Fields](https://docs.oracle.com/javase/tutorial/java/javaOO/initial.html)：

> Initializing Instance Members
>
> Normally, you would put code to initialize an instance variable in a constructor. There are two alternatives to using a constructor to initialize instance variables: initializer blocks and final methods.
>
> Initializer blocks for instance variables look just like static initializer blocks, but without the static keyword:
>
>     {
>        // whatever code is needed for initialization goes here
>     }
>
> The Java compiler copies initializer blocks into every constructor. Therefore, this approach can be used to share a block of code between multiple constructors.


## 为什么不建议使用？

### 参考资料

* [Initialize a HashMap in Java](https://www.baeldung.com/java-initialize-hashmap)
* [Java 隐藏特性：双括号初始化（Double Brace Initialization）](https://blog.csdn.net/wuxianjiezh/article/details/90267142)
* [Efficiency of Java “Double Brace Initialization”?](https://stackoverflow.com/questions/924285/efficiency-of-java-double-brace-initialization)
* [Java Double Brace Initialization](https://www.baeldung.com/java-double-brace-initialization)

### 总结一下

* 不支持钻石操作符，即不可以这样写：`Map<String, Object> map = new HashMap<>() { {  } };`
* 因为相当于是通过内部类实现的，每次使用这种写法都会新创建一个内部类，如：`MainClass$InnerClass.class`
* 存在性能问题，可能会导致内存溢出。


## 难道只能从了？

虽然双括号初始化看上去还算美，但却不建议使用。
Java 8、9 也提供了一些其他的初始化方式，还有各种三方类库也提供了很多其他方式（详见上节中的参考资料）。

什么？还不满意？

忍一时风平浪静，退一步海阔天空。

有能耐你别用 Java 啊！

比如 Groovy 了解一下：

```groovy
Map emptyMap = [:]
Map map = [name: 'Alpha', age: 8]
```
