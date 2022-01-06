---
id: spring-boot-launcher
title: "如何给 Spring Boot 外挂 classpath？"
description: "无需重新打包，修改 Fat Jar 行为"
date: 2021.03.14 10:26
categories:
    - Spring
    - Java
tags: [Spring Boot, Java, Spring]
keywords: PropertiesLauncher, classpath, classloader
cover: /contents/covers/spring-boot-launcher.jpeg
---

假设使用 Spring Boot 开发了一个可使用不同数据库的应用，每个数据库的 jdbc 驱动包都不同，不想在 Fat Jar 中打入所有的数据库驱动 jar，又不想为每一个确定了具体数据库的场景都打一个对应的 Fat Jar 包，有没有优雅的方式来实现这个需求呢？

我们先来看下 Spring Boot 的 Fat Jar（Executable Jar）是如何运行的。

通常情况下，要启动一个 Spring Boot 应用，可通过如下方式：

```bash
$ java -jar example.jar
```

Spring Boot Jar 包的文件结构如下：

```file
example.jar
 |
 +-META-INF
 |  +-MANIFEST.MF
 +-org
 |  +-springframework
 |     +-boot
 |        +-loader
 |           +-<spring boot loader classes>
 +-BOOT-INF
    +-classes
    |  +-mycompany
    |     +-project
    |        +-YourClasses.class
    +-lib
       +-dependency1.jar
       +-dependency2.jar
```

在 [Launching Executable Jars][launching] 中，介绍了 Spring Boot 的 Jar 包可以直接运行的原因：`org.springframework.boot.loader.Launcher` 类是 Spring Boot Jar 包实际的主类，负责调用应用的 main 方法。`Launcher` 类有三个子类：`JarLauncher`，`WarLauncher` 和 `PropertiesLauncher`，由它们负责从 jar 包或者 war 包中读取内嵌的资源（.class 文件等）。

`JarLauncher` 从 `BOOT-INF/lib/` 固定路径加载资源；`WarLauncher` 是从 `WEB-INF/lib/` 和 `WEB-INF/lib-provided/` 路径。

`PropertiesLauncher` 默认从 `BOOT-INF/lib/` 加载资源，并且支持通过环境变量 `LOADER_PATH` 或 `loader.path` 来指定额外的路径。

具体的 Launcher 和应用的 main 函数所在类，设定在 `MANIFEST.MF` 文件中，一般由 Maven 或 Gradle 打包插件帮我们设定好，例如：

```file
Main-Class: org.springframework.boot.loader.JarLauncher
Start-Class: com.mycompany.project.MyApplication
```

所以通过调整默认 Launcher 及使用环境变量指定额外 classpath 的方式，即可实现添加 Fat Jar 外 jar 包至运行环境的需求。

那么如果不想修改打包配置，或者手动修改 `MANIFEST.MF` 文件内容，该如何操作呢？

比如本文最初提到的场景，可以将数据库的 jdbc 驱动 jar 包放在同级 lib 路径下，然后通过如下方式启动 Fat Jar：

```bash
$ java -cp example.jar -Dloader.path=./lib org.springframework.boot.loader.PropertiesLauncher
```

注意，此时不再是使用 `java -jar` 方式启动，而是使用传统的 Java 应用启动方式，先通过 `-cp` 参数将 Fat Jar 加入 classpath，然后指定运行的主类 `PropertiesLauncher`，并且通过 `-D` 参数，将系统属性传入主类中。

关于 `PropertiesLauncher` 的更多信息，可参见 [官方文档][PropertiesLauncher]。

通过这种方式，结合 [Override same class][override] 中相关内容，还可以实现无需重新打包，覆盖 Fat Jar 中类的某些行为。

参考资料
-------

* [How to configure additional classpath in SpringBoot?][so]
* [Hack – How 2 add jars 2 springboot classpath with JarLauncher ?][hack]

[launching]:https://docs.spring.io/spring-boot/docs/2.4.2/reference/htmlsingle/#executable-jar-launching
[PropertiesLauncher]:https://docs.spring.io/spring-boot/docs/2.4.2/reference/htmlsingle/#executable-jar-property-launcher-features
[override]:https://alphahinex.github.io/2020/12/27/override-same-class/
[so]:https://stackoverflow.com/questions/40499548/how-to-configure-additional-classpath-in-springboot
[hack]:https://mash213.wordpress.com/2017/01/05/hack-how-2-add-jars-2-springboot-classpath-with-jarlauncher/