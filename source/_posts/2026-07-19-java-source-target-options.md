---
id: java-source-target-options
title: "【译】Java Source 和 Target 选项指南"
description: "用 release 选项简化交叉编译参数设置"
date: 2026.07.19 10:34
categories:
    - Java
tags: [Java, Maven]
keywords: javac, source, target, release, cross-compilation, backward compatibility, bootstrap classpath
cover: /contents/covers/java-source-target-options.png
---

- 原文地址：https://www.baeldung.com/java-source-target-options
- 原文作者：[Sachin Kumar](https://www.baeldung.com/author/sachinkumar)

---

## 1. 概述

在本教程中，我们将探讨 Java 提供的 `-source` 和 `-target` 选项。此外，我们还将了解这些选项在 Java 8 中的工作方式，以及从 Java 9 开始它们是如何演变的。

## 2. 与旧版 Java 的向后兼容性

由于 Java 版本发布和更新频繁，应用程序可能无法每次都迁移到新版本。**有时应用程序需要确保其代码与旧版 Java 保持向后兼容。`javac` 中的 `target` 和 `source` 选项可以轻松实现这一点。**

为了深入理解，我们先创建一个示例类，并使用 Java 9 中引入但 Java 8 中不存在的 `List.of()` 方法：

```java
public class TestForSourceAndTarget {
    public static void main(String[] args) {
        System.out.println(List.of("Hello", "Baeldung"));
    }
}
```

假设我们使用 Java 9 编译代码，但希望兼容 Java 8。我们可以使用 `-source` 和 `-target` 来实现：

```bash
/jdk9path/bin/javac TestForSourceAndTarget.java -source 8 -target 8
```

编译时会收到一个警告，但编译是成功的：

```text
warning: [options] bootstrap class path not set in conjunction with -source 8
1 warning
```

用 Java 8 运行这段代码，会看到报错信息：

```bash
$ /jdk8path/bin/java TestForSourceAndTarget
Exception in thread "main" java.lang.NoSuchMethodError:
  java.util.List.of(Ljava/lang/Object;Ljava/lang/Object;)Ljava/util/List;
  at com.baeldung.TestForSourceAndTarget.main(TestForSourceAndTarget.java:7)
```

在 Java 8 中，`List.of()` 是不存在的。理想情况下，Java 应该在编译时就抛出这个错误。然而，在编译期间我们只收到了一个警告。

让我们看看编译时收到的那个警告。`javac` 告诉我们，bootstrap 类没有与 `-source 8` 一起使用。事实证明，**我们必须提供 bootstrap 类文件路径，以便 `javac` 能够为交叉编译选择正确的文件。** 在我们的例子中，我们希望兼容 Java 8，但默认选择了 Java 9 的 bootstrap 类。

为了使其正常工作，**我们必须使用 `-Xbootclasspath` 来指向我们希望进行交叉编译的 Java 版本的路径：**

```bash
/jdk9path/bin/javac TestForSourceAndTarget.java -source 8 -target 8 -Xbootclasspath ${jdk8path}/jre/lib/rt.jar
```

现在我们编译代码，会在编译时看到错误信息：

```text
TestForSourceAndTarget.java:7: error: cannot find symbol
        System.out.println(List.of("Hello", "Baeldung"));
                          ^
  symbol:   method of(String, String)
  location: interface List
1 error
```

## 3. Source 选项

**`-source` 选项指定编译器接受的 Java 源代码版本：**

```bash
/jdk9path/bin/javac TestForSourceAndTarget.java -source 8 -target 8
```

如果不提供 `-source` 选项，编译器将根据所使用的 Java 版本来编译源代码。

在我们的示例中，如果不提供 `-source 8`，编译器将按照 Java 9 规范编译源代码。

`-source` 值为 8 也意味着我们不能使用任何 Java 9 特有的 API。为了使用 Java 9 中引入的任何 API，如 `List.of()`，我们必须将 source 选项的值设置为 9。

## 4. Target 选项

**`target` 选项指定要生成的 class 文件的 Java 版本。target 选项值必须等于或高于 source 选项：**

```bash
/jdk9path/bin/javac TestForSourceAndTarget.java -source 8 -target 8
```

这里， **`-target` 值为 8 意味着这将生成一个需要 Java 8 或更高版本才能运行的类文件。** 如果在 Java 7 中运行上述 class 文件，我们会收到报错信息。

## 5. Java 8 及更早版本中的 Source 和 Target

**从我们的示例中可以看出，要在直到 Java 8 的版本中正确进行交叉编译，我们需要提供三个选项，即 `-source`、`-target` 和 `-Xbootclasspath`。**
例如，如果需要用 Java 9 构建代码，但需要兼容 Java 8：

```bash
/jdk9path/bin/javac TestForSourceAndTarget.java -source 8 -target 8 -Xbootclasspath ${jdk8path}/jre/lib/rt.jar
```

从 JDK 8 开始，使用 1.5 或更早版本的 source 或 target 已被弃用，在 JDK 9 中，对 1.5 或更早版本的 source 或 target 的支持已被完全移除。

## 6. Java 9 及更高版本中的 Source 和 Target

**尽管交叉编译在 Java 8 中工作正常，但需要三个命令行选项。当有三个选项时，要保证它们都保持最新可能会很困难。**

**作为 Java 9 的一部分，[`-release` 选项](https://www.baeldung.com/java-compiler-release-option) 被引入用来简化交叉编译过程。**
使用 `-release` 选项，我们可以完成与之前选项相同的交叉编译。

让我们使用 `-release` 选项来编译之前的示例类：

```bash
/jdk9path/bin/javac TestForSourceAndTarget.java -release 8
```

```text
TestForSourceAndTarget.java:7: error: cannot find symbol
        System.out.println(List.of("Hello", "Baeldung"));
                          ^
  symbol:   method of(String, String)
  location: interface List
1 error
```

很明显，编译时只需要一个选项 `-release`，报错信息表明 `javac` 已在内部为 `-source`、`-target` 和 `-Xbootclasspath` 分配了正确的值。

## 7. 结论

在本文中，我们了解了 `javac` 的 `-source` 和 `-target` 选项及其与交叉编译的关系。此外，我们还发现了它们在 Java 8 及更高版本中的使用方式。同时，我们也了解了 Java 9 中引入的 `-release` 选项。