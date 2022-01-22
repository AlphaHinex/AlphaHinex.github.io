---
id: bootclasspath-in-action
title: "通过 -Xbootclasspath/a 参数修改 Spring Boot 应用行为实例"
description: "通过两个实例说明 -Xbootclasspath/a 参数的用法"
date: 2022.01.23 10:26
categories:
    - Java
tags: [Spring Boot, Java, MyBatis]
keywords: -Xbootclasspath/a, 覆盖, Spring Boot 应用, 不重新打包, 不修改 jar 包 
cover: /contents/covers/bootclasspath-in-action.png
---

在 [Spring boot 应用不重新打包，添加新类](https://alphahinex.github.io/2022/01/09/bootclasspath/) 中简单介绍了 `-Xbootclasspath/a` 参数的用法，下面用两个实例来进行实际使用场景的说明。


演示项目
=======

[bootclasspath][demo] 为本文使用的演示项目，可通过 `mvn clean package -DskipTests` 命令获得 Spring Boot 应用 JAR 包，并在项目根路径通过 `java -jar app/target/app-0.0.1-SNAPSHOT.jar` 命令启动应用，之后可访问 http://localhost:8080 ，正常情况会得到类似下面的响应：

```bash
$ curl localhost:8080
User count: 3
Country count: 151
```

场景1：覆盖三方 jar 包中的某个类
============================

演示项目中使用 MyBatis 作为持久层框架。假设需要修改 MyBatis 包中的某个类，以 `org.apache.ibatis.executor.statement.PreparedStatementHandler` 为例，可通过 `-Xbootclasspath/a` 参数指定包含这个类的路径，以起到覆盖原版本的效果。

按照演示项目中路径结构，编译后，修改的类路径结构如下所示：

```text
├── hacked
│   └── target
│       ├── classes
│       │   └── org
│       │       └── apache
│       │           └── ibatis
│       │               └── executor
│       │                   └── statement
│       │                       └── PreparedStatementHandler.class
```

可按如下方式启动应用，注意替换 `mybatis-3.5.9.jar` 包的实际路径：

```bash
# Replace /Users/alphahinex/.m2/repository/org/mybatis/mybatis/3.5.9/mybatis-3.5.9.jar to your mybatis-3.5.9.jar file's path
$ java -Xbootclasspath/a:./hacked/target/classes:/Users/alphahinex/.m2/repository/org/mybatis/mybatis/3.5.9/mybatis-3.5.9.jar -jar app/target/app-0.0.1-SNAPSHOT.jar
```

`-Xbootclasspath/a:` 参数后面路径为多个时，路径之间需要以操作系统指定的分隔符进行间隔，分隔符可使用 `java -X` 命令进行查看。

根据 [Override same class](https://alphahinex.github.io/2020/12/27/override-same-class/) 描述的类覆盖机制，需要将修改的 `PreparedStatementHandler` 类所在路径，放在原版本 jar 包路径前，以起到覆盖的作用。

应用启动后，访问 http://localhost:8080 ，正常的话在应用启动的 console 中会看到 `HACKED::PreparedStatementHandler.query` 内容输出，代表修改的类已生效。


场景2：覆盖 MyBatis Mapper 文件
=============================

使用 MyBatis 时，具体的查询语句可能会放到 Mapper 文件中，当我们想修改 Mapper 文件中的 SQL 语句时，也可以使用 `-Xbootclasspath/a:` 参数指定外部的 Mapper 文件路径。

演示项目中，编译后可在 `hacked/target/classes/sql` 路径下获得 Mapper 文件，路径结构如下，其中 `CountryMapper.xml` 修改了 SQL 语句：

```text
├── hacked
│   └── target
│       ├── classes
│       │   └── sql
│       │       └── db
│       │           └── mapper
│       │               ├── CountryMapper.xml
│       │               └── UserMapper.xml
```

通过如下方式启动应用：

```bash
$ java -Xbootclasspath/a:./hacked/target/classes/sql -jar app/target/app-0.0.1-SNAPSHOT.jar
```

之后访问 http://localhost:8080 ，可以看到 `Country count` 的数值，从原版本的 `151`，变成了 `26`。

> 注意：此种方式覆盖 Mapper 文件时，需要将所有 Mapper 文件均放到外部，不论是否需要修改其中的内容，否则只能读取到外部路径的 Mapper 文件，无法读取到原 Spring Boot JAR 包中的 Mapper 文件。仅将变动的文件从外部加载的方式，会另写一篇进行单独说明。


最后
===

虽然 `-Xbootclasspath/a:` 参数可以实现一定程度的修改 Spring Boot 包原本行为，但从上面的实例中可以看出，还是有些麻烦的，并且当需要覆盖 Spring 的类，或添加一些新的依赖 JAR 包时，上面的方式并不可行。

在能够修改 Java 应用的启动命令时，还是推荐使用 [如何给 Spring Boot 外挂 classpath？](https://alphahinex.github.io/2021/03/14/spring-boot-launcher/) 中的方式，本文描述的 `-X` 参数仅作为在无法修改启动命令、只能修改 JVM 参数时的一种有局限性的替代方案使用。

[demo]:https://github.com/AlphaHinex/bootclasspath