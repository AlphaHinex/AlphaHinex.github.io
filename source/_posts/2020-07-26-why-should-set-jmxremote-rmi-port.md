---
id: why-should-set-jmxremote-rmi-port
title: "为什么应该设置 com.sun.management.jmxremote.rmi.port？"
description: "不设置貌似也没问题啊"
date: 2020.07.26 19:26
categories:
    - Java
tags: [Java]
keywords: Java, JMX, RMI, Firewall
cover: /contents/covers/jmx.gif
---

在使用 JMX 对 Java 应用进行监控时，一般会在启动时添加如下参数：

```bash
java \
-Djava.rmi.server.hostname=192.168.16.237 \
-Dcom.sun.management.jmxremote.rmi.port=2909 \
-Dcom.sun.management.jmxremote.port=9009 \
-Dcom.sun.management.jmxremote.authenticate=false \
-Dcom.sun.management.jmxremote.ssl=false \
-jar test.jar
```

后三个参数在 Oracle 官方文档 [Monitoring and Management Using JMX Technology](https://docs.oracle.com/javase/8/docs/technotes/guides/management/agent.html) 中均有描述，但前两个参数直到 [JDK9 版本的文档](https://docs.oracle.com/javase/9/management/monitoring-and-management-using-jmx-technology.htm#JSMGM-GUID-805517EC-2D33-4D61-81D8-4D0FA770D1B8) 中才有所提及。

`java.rmi.server.hostname` 为需要远程连接时必须设置的参数，否则只能从本地对应用进行监控，无法从远程机器进行连接。

那么 `com.sun.management.jmxremote.rmi.port` 这个参数指定的端口是干什么用的呢？

按上面启动命令所示，使用 jmx 进行连接的时候使用的是 `com.sun.management.jmxremote.port` 参数指定的端口，`com.sun.management.jmxremote.rmi.port` 这个参数去掉好像也没什么影响，依然能够进行远程连接，那么为什么还要设置这个参数呢？

先来看一下 [官方文档](https://docs.oracle.com/javase/9/management/monitoring-and-management-using-jmx-technology.htm#JSMGM-GUID-805517EC-2D33-4D61-81D8-4D0FA770D1B8) 中关于这个参数为数不多的描述：

> To enable monitoring and management from remote systems, you must set the following system property when you start the Java VM:
>
>     com.sun.management.jmxremote.port=portNum
> Where, portNum is the port number to enable JMX RMI connections. Ensure that you specify an unused port number. In addition to publishing an RMI connector for local access, setting this property publishes an additional RMI connector in a private read-only registry at the specified port using the name, jmxrmi. The port number to which the RMI connector will be bound using the system property:
>
>     com.sun.management.jmxremote.rmi.port
> Ensure to use an unused port number.

大意为，使用 `com.sun.management.jmxremote.port` 指定端口后，除了在这个端口上会创建一个 RMI 连接器之外，还会额外创建另一个连接器，而这个额外创建的连接器的端口，就可以通过 `com.sun.management.jmxremote.rmi.port` 参数来指定。

这个额外连接器的端口，在我们进行监控的时候并没有使用到，而且不进行指定也会随机使用一个端口，那为什么还要指定呢？

## 一探究竟

让我们使用 docker 来模拟一个网络访问受限的环境，看一看这个参数的影响。

### 准备 Java 应用

先准备一个用来监控的 Java 应用。比如可以从 https://github.com/AlphaHinex/spring-roll 通过 `./gradlew bootJar`，在 `modules/roll-application/build/libs` 路径获得一个 Spring Boot 的 Fat Jar。

### Docker Compose

然后在 Java 应用路径，创建一个 `docker-compose.yml` 文件，内容参考如下：

```yml
jmx:
  image: openjdk:8u171-jre
  volumes:
    - ./roll.jar:/opt/jmx/roll.jar
  command: java -Djava.rmi.server.hostname=192.168.16.237 -Dcom.sun.management.jmxremote.port=9009 -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false -jar /opt/jmx/roll.jar
  ports:
    - "9009:9009"
```

### 仅指定及开放 jmxremote.port

按照上述 `docker-compose.yml` 内容，执行 `docker-compose up jmx`，之后使用 `jvisualvm`、`jconsole` 等工具，连接 9009 端口，会发现无法正常进行连接。

### 指定并开放 rmi.port

将 `docker-compose.yml` 调整为如下内容：

```yml
jmx:
  image: openjdk:8u171-jre
  volumes:
    - ./roll.jar:/opt/jmx/roll.jar
  command: java -Djava.rmi.server.hostname=192.168.16.237 -Dcom.sun.management.jmxremote.rmi.port=2909 -Dcom.sun.management.jmxremote.port=9009 -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false -jar /opt/jmx/roll.jar
  ports:
    - "9009:9009"
    - "2909:2909"
```

此时在通过 JMX 连接 9009 端口，会发现可以正常的进行监控了。

## 总结

当存在防火墙等网络访问限制时，可通过 `com.sun.management.jmxremote.rmi.port` 参数指定 RMI 连接器所使用的端口并进行开放。**在这种场景下，必须设置此参数。**

另外，`com.sun.management.jmxremote.rmi.port` 使用的端口，可以与 `com.sun.management.jmxremote.port` 指定的端口相同，这样仅开放一个端口就可以了，比如：

```yml
jmx:
  image: openjdk:8u171-jre
  volumes:
    - ./roll.jar:/opt/jmx/roll.jar
  command: java -Djava.rmi.server.hostname=192.168.16.237 -Dcom.sun.management.jmxremote.rmi.port=9009 -Dcom.sun.management.jmxremote.port=9009 -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false -jar /opt/jmx/roll.jar
  ports:
    - "9009:9009"
```
