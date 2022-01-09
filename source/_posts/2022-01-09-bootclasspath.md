---
id: bootclasspath
title: "Spring boot 应用不重新打包，添加新类"
description: "PropertiesLauncher 和 -Xbootclasspath"
date: 2022.01.09 10:26
categories:
    - Spring
    - Java
tags: [Spring Boot, Java, Spring]
keywords: PropertiesLauncher, -Xbootclasspath, -Xbootclasspath/a, -Xbootclasspath/p
cover: /contents/covers/bootclasspath.png
---

问题描述
========

因为某些约束，我们可能不希望对 Spring Boot 应用重新打包，却又需要调整其中的某些行为（如：添加新类），有没有办法？


解决方案
=======

### 1. PropertiesLauncher

修改启动命令，不再是使用 `java -jar` 方式启动，而是使用传统的 Java 应用启动方式，先通过 `-cp` 参数将 Fat Jar （`example.jar`）加入 classpath，然后指定运行的主类 `PropertiesLauncher`，并且通过 `-D` 参数，将系统属性传入主类中。

```bash
$ java -cp example.jar -Dloader.path=./lib org.springframework.boot.loader.PropertiesLauncher
```

详细可参考 [如何给 Spring Boot 外挂 classpath？](https://alphahinex.github.io/2021/03/14/spring-boot-launcher/)

### 2. -Xbootclasspath

某些场景下，修改 Java 应用的启动命令可能会受限，但添加参数是可以的。这时候可以通过添加 `-Xbootclasspath` 相关参数，来实现类似的功能。

JDK [文档](https://docs.oracle.com/javase/8/docs/technotes/tools/unix/java.html) 中关于 -Xbootclasspath 相关的参数，描述如下： 

```text
-Xbootclasspath:path
    Specifies a list of directories, JAR files, and ZIP archives separated by colons (:) to search for boot class 
    files. These are used in place of the boot class files included in the JDK.

    Do not deploy applications that use this option to override a class in rt.jar, because this violates the JRE 
    binary code license.

-Xbootclasspath/a:path
    Specifies a list of directories, JAR files, and ZIP archives separated by colons (:) to append to the end of the 
    default bootstrap class path.

    Do not deploy applications that use this option to override a class in rt.jar, because this violates the JRE 
    binary code license.

-Xbootclasspath/p:path
    Specifies a list of directories, JAR files, and ZIP archives separated by colons (:) to prepend to the front of 
    the default bootstrap class path.

    Do not deploy applications that use this option to override a class in rt.jar, because this violates the JRE 
    binary code license.
```

因为我们是希望为已有的 Spring Boot 应用添加新类，所以采用 `-Xbootclasspath/a:path` 的形式，即在默认的启动 class path 后，追加新的目录或 Jar 包等。命令的参考形式如下，`/path/to/a.jar` 和 `/path/to/b.jar` 是需要追加的 Jar 包路径，多个 Jar 包之间通过分隔符间隔：

```bash
$ java -Xbootclasspath/a:/path/to/a.jar:/path/to/b.jar -jar /path/app.jar
```

> 使用这种方式追加 Jar 包时，可能会遇到找不到 Spring Boot 应用里原本就存在的类的情况（例如 Spring Boot 应用中原本包含 `commons-pool2` 的 Jar 包，但追加 jedis 的 Jar 包后，提示找不到 `commons-pool2` 中的类），此时在 `-Xbootclasspath/a` 参数中再追加一下包含找不到的类的 Jar 包即可。