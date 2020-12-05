---
id: which-class-is-loaded
title: "如何确定装载了哪个类"
description: "假如存在全名相同的类时"
date: 2020.12.06 10:34
categories:
    - Java
tags: [Java, DevOps]
keywords: Java, Class, ClassLoader, verbose, load class
cover: /contents/covers/java-classloader.jpg
---

某些时候，我们可能希望知道 ClassLoader 里到底装载的是哪个 class，比如当两个 jar 包中存在 package 和 Class 名完全相同的两个类时。

## java -verbose

在 java 命令的帮助信息中，有如下内容（部分）：

```bash
$ java -help
用法: java [-options] class [args...]
           (执行类)
   或  java [-options] -jar jarfile [args...]
           (执行 jar 文件)
其中选项包括:
    -d32	  使用 32 位数据模型 (如果可用)
    -d64	  使用 64 位数据模型 (如果可用)
    -server	  选择 "server" VM
                  默认 VM 是 server,
                  因为您是在服务器类计算机上运行。


    -cp <目录和 zip/jar 文件的类搜索路径>
    -classpath <目录和 zip/jar 文件的类搜索路径>
                  用 : 分隔的目录, JAR 档案
                  和 ZIP 档案列表, 用于搜索类文件。
    -D<名称>=<值>
                  设置系统属性
    -verbose:[class|gc|jni]
                  启用详细输出
```

可以直接使用 `java -verbose` 来查看运行此命令时装载了哪些类（部分）：

```bash
$ java -verbose
...
[Loaded java.lang.CharSequence from /Library/Java/JavaVirtualMachines/jdk1.8.0_121.jdk/Contents/Home/jre/lib/rt.jar]
[Loaded java.lang.String from /Library/Java/JavaVirtualMachines/jdk1.8.0_121.jdk/Contents/Home/jre/lib/rt.jar]
[Loaded java.lang.reflect.AnnotatedElement from /Library/Java/JavaVirtualMachines/jdk1.8.0_121.jdk/Contents/Home/jre/lib/rt.jar]
[Loaded java.lang.reflect.GenericDeclaration from /Library/Java/JavaVirtualMachines/jdk1.8.0_121.jdk/Contents/Home/jre/lib/rt.jar]
[Loaded java.lang.reflect.Type from /Library/Java/JavaVirtualMachines/jdk1.8.0_121.jdk/Contents/Home/jre/lib/rt.jar]
[Loaded java.lang.Class from /Library/Java/JavaVirtualMachines/jdk1.8.0_121.jdk/Contents/Home/jre/lib/rt.jar]
[Loaded java.lang.Cloneable from /Library/Java/JavaVirtualMachines/jdk1.8.0_121.jdk/Contents/Home/jre/lib/rt.jar]
[Loaded java.lang.ClassLoader from /Library/Java/JavaVirtualMachines/jdk1.8.0_121.jdk/Contents/Home/jre/lib/rt.jar]
[Loaded java.lang.System from /Library/Java/JavaVirtualMachines/jdk1.8.0_121.jdk/Contents/Home/jre/lib/rt.jar]
[Loaded java.lang.Throwable from /Library/Java/JavaVirtualMachines/jdk1.8.0_121.jdk/Contents/Home/jre/lib/rt.jar]
[Loaded java.lang.Error from /Library/Java/JavaVirtualMachines/jdk1.8.0_121.jdk/Contents/Home/jre/lib/rt.jar]
[Loaded java.lang.ThreadDeath from /Library/Java/JavaVirtualMachines/jdk1.8.0_121.jdk/Contents/Home/jre/lib/rt.jar]
[Loaded java.lang.Exception from /Library/Java/JavaVirtualMachines/jdk1.8.0_121.jdk/Contents/Home/jre/lib/rt.jar]
...
```

也可以限定详细输出的类型，比如 `java -verbose:jni`，或组合使用 `java -verbose:class -verbose:jni`。

在运行一个 Spring Boot 应用时，可以通过此参数观察类的装载情况，以确定装载的 class 的来源是哪个 jar 包，进而解决上面提到的问题：

```bash
$ java -verbose -jar app.jar
...
[Loaded org.springframework.cglib.core.EmitUtils$5 from jar:file:/Users/alphahinex/github/origin/spring-roll/app.jar!/BOOT-INF/lib/spring-core-5.2.2.RELEASE.jar!/]
[Loaded java.util.DualPivotQuicksort from /Library/Java/JavaVirtualMachines/jdk1.8.0_121.jdk/Contents/Home/jre/lib/rt.jar]
[Loaded org.springframework.cglib.core.EmitUtils$6 from jar:file:/Users/alphahinex/github/origin/spring-roll/app.jar!/BOOT-INF/lib/spring-core-5.2.2.RELEASE.jar!/]
[Loaded io.github.springroll.RollWebApplication$$EnhancerBySpringCGLIB$$d2db2c71 from jar:file:/Users/alphahinex/github/origin/spring-roll/app.jar!/BOOT-INF/classes!/]
[Loaded org.springframework.cglib.proxy.MethodProxy from jar:file:/Users/alphahinex/github/origin/spring-roll/app.jar!/BOOT-INF/lib/spring-core-5.2.2.RELEASE.jar!/]
[Loaded org.springframework.cglib.proxy.MethodProxy$CreateInfo from jar:file:/Users/alphahinex/github/origin/spring-roll/app.jar!/BOOT-INF/lib/spring-core-5.2.2.RELEASE.jar!/]
[Loaded org.springframework.cglib.proxy.Enhancer$EnhancerFactoryData from jar:file:/Users/alphahinex/github/origin/spring-roll/app.jar!/BOOT-INF/lib/spring-core-5.2.2.RELEASE.jar!/]
[Loaded io.github.springroll.swagger.ApplicationSwaggerConfiguration$$EnhancerBySpringCGLIB$$8e0e540e from jar:file:/Users/alphahinex/github/origin/spring-roll/app.jar!/BOOT-INF/lib/roll-swagger-0.0.9-SNAPSHOT.jar!/]
[Loaded io.github.springroll.export.excel.ExportExcelConfiguration$$EnhancerBySpringCGLIB$$d150201a from jar:file:/Users/alphahinex/github/origin/spring-roll/app.jar!/BOOT-INF/lib/roll-export-0.0.9-SNAPSHOT.jar!/]
...
```
