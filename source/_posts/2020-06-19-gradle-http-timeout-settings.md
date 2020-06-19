---
id: gradle-http-timeout-settings
title: "Gradle HTTP 超时设置"
description: "The Missing Guide"
date: 2020.06.19 19:34
categories:
    - Java
tags: [Java, Gradle]
keywords: Java, Gradle, timeout, Maven, dependency
cover: /contents/covers/gradle-http-timeout-settings.jpeg
---

在使用 Nexus 时，很罕见的遇到了超时问题：

```log
> Unable to load Maven meta-data from http://localhost:8081/repository/test/io/github/alphahinex/example/0.1.2-SNAPSHOT/maven-metadata.xml.
   > Could not HEAD 'http://localhost:8081/repository/test/io/github/alphahinex/example/0.1.2-SNAPSHOT/maven-metadata.xml'.
      > Read timed out
```

经确认，http://localhost:8081/repository/test/io/github/alphahinex/example/0.1.2-SNAPSHOT/maven-metadata.xml 是可以得到正确的响应的，但是响应时间比较长。

类似问题，在使用 [JitPack 真香](https://alphahinex.github.io/2020/05/29/jitpack-in-action/) 中提到的，需要 JitPack 先进行构建才能下载的依赖时，也可能会遇到。

增加超时时间就可以解决这个问题了，但现在 Gradle 的 [文档](https://docs.gradle.org/current/userguide/userguide.html) 实在有点无力吐槽，啥也找不着。

下面就是缺失的 ——

# Gradle HTTP 超时设置文档

以 [Gradle v6.0.1](https://github.com/gradle/gradle/tree/v6.0.1) 为例：

超时属性及默认超时时间在 [JavaSystemPropertiesHttpTimeoutSettings.java#L26-L29](https://github.com/gradle/gradle/blob/v6.0.1/subprojects/resources-http/src/main/java/org/gradle/internal/resource/transport/http/JavaSystemPropertiesHttpTimeoutSettings.java#L26-L29) 中：

```java
public static final String CONNECTION_TIMEOUT_SYSTEM_PROPERTY = "org.gradle.internal.http.connectionTimeout";
public static final String SOCKET_TIMEOUT_SYSTEM_PROPERTY = "org.gradle.internal.http.socketTimeout";
public static final int DEFAULT_CONNECTION_TIMEOUT = 30000;
public static final int DEFAULT_SOCKET_TIMEOUT = 30000;
```

设置方式为：

## 命令行

```bash
$ ./gradlew build -Dorg.gradle.internal.http.socketTimeout=200000 -Dorg.gradle.internal.http.connectionTimeout=200000
```

## 配置文件

可在 `gradle.properties` 文件中，通过如下属性进行配置：

```gradle.properties
systemProp.org.gradle.internal.http.socketTimeout=200000
systemProp.org.gradle.internal.http.connectionTimeout=200000
```


参考资料
-------

* [Increase timeout for gradle to get a maven dependency](https://stackoverflow.com/questions/37156568/increase-timeout-for-gradle-to-get-a-maven-dependency)
* [#3041 Introduce HTTP timeout](https://github.com/gradle/gradle/pull/3041)
* [#3371 Increase timeout for HTTP timeouts and assign system properties to internal namespace](https://github.com/gradle/gradle/pull/3371)
