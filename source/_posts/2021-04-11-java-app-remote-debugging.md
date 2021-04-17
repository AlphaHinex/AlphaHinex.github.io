---
id: java-app-remote-debugging
title: "Java 应用远程调试"
description: "本地环境无法重现问题？试试远程调试"
date: 2021.04.11 10:26
categories:
    - Java
tags: [Java, Debug]
keywords: Java, Remote Debugging, JPDA, JDWP, 远程调试, IEEE, SCI, IDEA, JDB
cover: /contents/java-app-remote-debugging/cover.png
---

软件开发会时经常会遇到这样的场景：

* 现场反馈的问题，在本地环境无法重现，可能需要将现场数据库导回来才能重现问题
* 生产环境中的服务无法直接从本地开发环境进行连接，进而无法使用本地代码进行调试

在上面的场景中，无论是将现场库导出，还是开通生产环境服务的访问权限，都是非常困难且不安全的。

本文将介绍一种由 Java 平台提供的，远程调试 Java 应用的方法。

## JPDA

JPDA（Java Platform Debugging Architecture）是一个多层调试架构，支持在不同操作系统、虚拟机及 JDK 版本中创建调试程序。

JPDA 的 [架构图][jpda] 如下：

```text
           Components                          Debugger Interfaces

                /    |--------------|
               /     |     VM       |
 debuggee ----(      |--------------|  <------- JVM TI - Java VM Tool Interface
               \     |   back-end   |
                \    |--------------|
                /           |
 comm channel -(            |  <--------------- JDWP - Java Debug Wire Protocol
                \           |
                     |--------------|
                     | front-end    |
                     |--------------|  <------- JDI - Java Debug Interface
                     |      UI      |
                     |--------------|
```

架构由三层组成：

1. JVM TI - Java VM Tool Interface：定义了由虚拟机提供的调试服务
1. JDWP - Java Debug Wire Protocol：定义了 debuggee（调试应用服务端）和 debugger（调试服务客户端）进程之间的通讯协议
1. JDI - Java Debug Interface：定义了高层次的 Java 语言接口，使得工具开发者可以方便的编写远程调试应用

由上可知，Java 应用远程调试时，需先开启服务端的远程调试服务，再通过 debugger 应用进行连接，实现远程调试。

## 服务端

服务端开启远程调试功能时，需在启动时增加启动参数，不同 JDK 版本的启动参数略有不同：

```bash
# JDK 1.3.x or earlier
-Xnoagent -Djava.compiler=NONE -Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=5005

# JDK 1.4.x
-Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=5005

# JDK 5 - 8
-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=5005

# JDK 9 or later
-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:5005
```

注意，上述启动参数要加到 java 命令参数的最前面，即可以直接加到 java 命令后面，之后再加其他参数。以 JDK 8 为例，启动命令如下所示：

```bash
$ java -agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=5005 -jar demo.jar
```

以 JDK 8 的启动参数为例，`-agentlib:jdwp` 表明使用 JDWP 协议，后面包括了 JDWP 的几个重要参数：

* transport：有两个内置类型，`dt_socket`（使用 socket 接口）和 `dt_shmem`（使用共享内存）。共享内存类型仅在本机调试时使用
* server：`y` 表明此虚拟机在调试中扮演服务端角色
* suspend：是否在客户端连接前挂起主进程。为不影响服务正常使用，通常可以设置为 `n`；当需要调试启动过程时，可设置为 `y`
* address：指定远程调试端口

服务端调试模式启用时，日志中会多出一行类似如下内容：

```text
Listening for transport dt_socket at address: 5005
```

> Tomcat 需要开启远程调试时，可以通过设置环境变量 `CATALINA_OPTS` 为上述对应 JDK 版本的启动参数；或在启动时，直接使用 `./catalina.sh jpda start` 以 jpda 模式启动即可。

## 客户端

### IDEA

服务端开启调试模式后，可通过 IDEA 方便的进行远程连接及调试。

首先 `Edit Configurations...`：

![Edit Configurations...](/contents/java-app-remote-debugging/edit-configurations.png)

然后在 `Run/Debug Configurations` 中创建 `Remote JVM Debug`：

![Remote JVM Debug](/contents/java-app-remote-debugging/remote.png)

填写 Host、Port，选择 `Use module classpath`：

![Configuration](/contents/java-app-remote-debugging/configuration.png)

配置完成后，以 debug 方式启动此服务：

![Debug](/contents/java-app-remote-debugging/debug.png)

连接后可以看到类似提示：

![Connected](/contents/java-app-remote-debugging/connected.png)

之后即可使用与本地调试一样的方式，调试远程服务。

> 注意：添加断点时，可以多试几个位置，remote 的 class 和本地的源码可能不完全一致，所以断点位置可能也不完全一致

> 再注意：同时只能接受一个客户端进行 remote debugging，无法多人同时以此方式进行远程调试

### JDB

一般离岸开发的项目，开发人员不在项目实施地，现场可能仅有实施运维人员。现场人员能连到线上环境但没有源码及 IDEA 等开发工具；开发人员有调试环境，但与线上环境网络不通，此种情况下，还有没有其他的远程调试方法呢？

JDK 中，提供了一个名为 `jdb` 的 Java Debugger，可以以命令行的方式连接至 debuggee 进行调试。

由下面的 [架构图][jdb] 可知，JDB 是 JDI 的一种实现。

![JDB](/contents/java-app-remote-debugging/jdb_architecture.jpg)

下面列举一些 JDB 的常用操作，更多操作方式可参考帮助文档或 [JDB - Quick Guide][jdb]。

#### 连接 Debuggee

```bash
$ jdb -attach remote:32738 -sourcepath ./src/main/java
设置未捕获的java.lang.Throwable
设置延迟的未捕获的java.lang.Throwable
正在初始化jdb...
> 
```

不通过 `-sourcepath` 指定源码路径也可以进行调试，只是不会显示出断点行对应的源码内容。

#### 设置断点（方法上）

```bash
> stop in cn.hinex.xxx.demo.DemoController.demo()
设置断点cn.hinex.xxx.demo.DemoController.demo()
> 
```

运行至此方法时，JDB 中会提示

```bash
断点命中: "线程=http-nio-8888-exec-4", cn.hinex.xxx.demo.DemoController.demo(), 行=16 bci=0
16            StringBuffer msg = new StringBuffer("hello");
http-nio-8888-exec-4[1] 
```

#### 列出当前断点所在位置

```bash
http-nio-8888-exec-4[1] list
12        RedisTemplate redisTemplate;
13
14        @GetMapping
15        public String demo() {
16 =>         StringBuffer msg = new StringBuffer("hello");
17            for (Object clientInfo : redisTemplate.getClientList()) {
18                msg.append(clientInfo.toString()).append("\r\n");
19            }
20            for (Object key : redisTemplate.keys("*")) {
21                msg.append(key.toString()).append("\r\n");
```

#### 显示堆栈

```bash
http-nio-8888-exec-4[1] where
  [1] cn.hinex.xxx.demo.DemoController.demo (DemoController.java:16)
  [2] sun.reflect.NativeMethodAccessorImpl.invoke0 (本机方法)
  [3] sun.reflect.NativeMethodAccessorImpl.invoke (NativeMethodAccessorImpl.java:62)
  [4] sun.reflect.DelegatingMethodAccessorImpl.invoke (DelegatingMethodAccessorImpl.java:43)
  [5] java.lang.reflect.Method.invoke (Method.java:498)
  [6] org.springframework.web.method.support.InvocableHandlerMethod.doInvoke (InvocableHandlerMethod.java:209)
  [7] org.springframework.web.method.support.InvocableHandlerMethod.invokeForRequest (InvocableHandlerMethod.java:136)
  [8] org.springframework.web.servlet.mvc.method.annotation.ServletInvocableHandlerMethod.invokeAndHandle (ServletInvocableHandlerMethod.java:102)
  [9] org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerAdapter.invokeHandlerMethod (RequestMappingHandlerAdapter.java:894)
  [10] org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerAdapter.handleInternal (RequestMappingHandlerAdapter.java:800)
  ……
```

#### 运行至下一步

```bash
http-nio-8888-exec-4[1] step
>
已完成的步骤: "线程=http-nio-8888-exec-4", cn.hinex.xxx.demo.DemoController.demo(), 行=17 bci=10
17            for (Object clientInfo : redisTemplate.getClientList()) {
```

#### 在指定行设置断点

```bash
http-nio-8888-exec-4[1] stop at cn.hinex.xxx.demo.DemoController:24
设置断点cn.hinex.xxx.demo.DemoController:24
```

#### 继续运行

```bash
http-nio-8888-exec-4[1] cont
>
断点命中: "线程=http-nio-8888-exec-4", cn.hinex.xxx.demo.DemoController.demo(), 行=24 bci=109
24            return str;
```

可通过 `list` 命令观察此时断点位置：

```bash
http-nio-8888-exec-4[1] list
20            for (Object key : redisTemplate.keys("*")) {
21                msg.append(key.toString()).append("\r\n");
22            }
23            String str = msg.toString();
24 =>         return str;
25        }
26
27    }
```

#### 打印变量值

```bash
http-nio-8888-exec-4[1] print str
 str = "hello"
```

#### 修改变量值

```bash
http-nio-8888-exec-4[1] set str = "hinex"
 str = "hinex" = "hinex"
```

## 其他

### 安全性问题

在使用远程调试时，不能忽略由此所带来的的性能影响及安全性问题。

有兴趣的读者可以阅读一下 [Hacking the Java Debug Wire Protocol – or – “How I met your Java debugger”][hack]，文中伪造了一个调试程序的客户端，并通过 `java.lang.Runtime` 类获取到 `getRuntime()` 方法的实例，之后便可执行运行此 java 应用的用户所拥有权限执行的命令。

也可以进行一下简单的验证，在得知一个服务的 remote debugging 端口后，在一个会被频繁调用的类上（如 `java.net.ServerSocket.accept()`）设置断点，进入断点后在 jdb 中执行 `print java.lang.Runtime.getRuntime().exec("touch /home/testfile")`，如果运行此 java 应用的用户拥有在 /home 路径下创建文件的权限，即可在服务器上完成此文件的创建。

故通常情况下，不应该开启调试模式。必须要开启时，也应尽快完成调试，之后将调试模式关闭，并不要使用常用的端口，如 `5005` 等。

### 下载 IEEE 论文

查询资料时，如需查看 IEEE 中的论文，如 [Multi-party collaborative debug service for Java application][ieee]，可以试试 [这个][gfsoso]，得到 [这个][sci-hub]。

## 参考资料

[A Practical Guide to Java Remote Debugging][guide]

[jpda]:https://docs.oracle.com/javase/8/docs/technotes/guides/jpda/architecture.html
[jdb]:https://www.tutorialspoint.com/jdb/jdb_quick_guide.htm
[hack]:https://ioactive.com/hacking-java-debug-wire-protocol-or-how/
[guide]:https://stackify.com/java-remote-debugging/
[ieee]:https://ieeexplore.ieee.org/document/5986571/
[gfsoso]:https://gfsoso.99lb.net/sci-hub.html
[sci-hub]:https://sci-hub.mksa.top/10.1109/soli.2011.5986571