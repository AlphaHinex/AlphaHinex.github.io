---
id: unable-to-open-socket-file
title: "无法动态附加到 Java 进程？"
description: "导致 jmap、jstack 等命令无法正常使用"
date: 2021.12.19 10:34
categories:
    - Java
tags: [Java, JDK]
keywords: socket file, .java_pid, java.io.tmpdir, Dynamic Attach, /tmp, systemd
cover: /contents/covers/unable-to-open-socket-file.png
---

现象
====

[找出 Java 应用频繁 Full GC 的原因](https://alphahinex.github.io/2021/12/12/find-the-reason-of-full-gc/) 中介绍了一些 JDK 中自带的命令，
如：`jmap`、`jstat` 等，但在实际使用时，可能会遇到类似如下的问题：

```bash
$ jmap -histo 2867
2867: Unable to open socket file: target process not responding or HotSpot VM not loaded
The -F option can be used when the target process is not responding
```

出现这种情况时，如果不是 Java 进程所属的用户和执行命令的用户不一致导致，那么按照提示使用 `-F` 参数可能也无济于事，重启 Java 应用后才可正常使用。


原因
===

出现这种情况时，基本是 socket file（`.java_pid<pid>` 文件）被删除导致，其中 `<pid>` 为对应 Java 进程的 ID。

这个文件在哪？
-----------

这个文件，会被生成到操作系统临时路径下，如 linux 下为 `/tmp` 。

默认情况下，可以通过 `System.getproperty("java.io.tmpdir")`（Java 应用的临时路径）来获取操作系统临时路径，但 `java.io.tmpdir` 这个属性可以通过环境变量、启动参数等进行改变，而操作系统的临时路径是没有办法被修改的，因为是硬编码到 [对应操作系统的 JVM 代码](https://github.com/openjdk/jdk/blob/master/src/hotspot/os/linux/os_linux.cpp) 中的，如：

```cpp
// This must be hard coded because it's the system's temporary
// directory not the java application's temp directory, ala java.io.tmpdir.
const char* os::get_temp_directory() { return "/tmp"; }
```

以现象中的 pid（2867）为例，对应 Linux 操作系统下该 Java 进程的 socket file 全路径为：`/tmp/.java_pid2867`

为什么需要这个文件？
----------------

这是由 JVM 的 [Dynamic Attach 机制](http://openjdk.java.net/groups/hotspot/docs/Serviceability.html#battach) 决定的。

`jmap`、`jstack` 等命令，都是通过这个机制来实现的。该机制的作用是，在 Java 进程运行过程中，为其动态附加一个外部进程，使外部进程可以与 Java 进程进行通信，实现例如 dump 等交互。

`jmap -histo`、`jmap -dump`、`jstack` 等命令执行时，都需要指定一个 Java 进程的 PID，作用即为向目标 JVM 发送一个 attach 请求。

通过 Java 代码，也可以发起这个附加请求，如：

```java
import com.sun.tools.attach.VirtualMachine;

...

String pid = "2867";
VirtualMachine jvm = VirtualMachine.attach(pid);
...
jvm.detach();

...
```

在第一次发生附加请求时，Dynamic attach 会在目标 JVM 中运行一个 Attach Listener 线程，可通过如下方式观察：

```bash
# 前台运行一个 java 应用，观察 console 输出内容
$ java -jar hello.jar

# 新开一个终端窗口，获得 java 进程 id
$ jps
22480 jar
23032 Jps

# 发送一个 QUIT 信号
$ kill -3 22480
```

此时会在 Java 应用的 console 中，输出线程相关信息。在未进行过 Dynamic attach 时，Java 应用的线程栈中是没有 `Attach Listener` 线程的。

```bash
# 触发一个附加请求
$ jstack -l 22480
...
"Attach Listener" #20 daemon prio=9 os_prio=31 tid=0x00007fd113814000 nid=0x450b waiting on condition [0x0000000000000000]
   java.lang.Thread.State: RUNNABLE

   Locked ownable synchronizers:
	- None
...
```

可以看到线程栈中多出了一个名为 `Attach Listener` 的线程。

随后，这个线程会与发起附加请求的源 JVM，以依赖操作系统的方式进行通信：

```text
* On Solaris, the Doors IPC mechanism is used. The door is attached to a file in the file system so that clients can access it.
* On Linux, a Unix domain socket is used. This socket is bound to a file in the filesystem so that clients can access it.
* On Windows, the created thread is given the name of a pipe which is served by the client. The result of the operations are written to this pipe by the target JVM.
```

在 Linux 中，上面文档所指的 `This socket is bound to a file in the filesystem`，即为前面提到的 `.java_pid<pid>` 文件。

这个文件为什么会被删除？
--------------------

因为这个 socket file 生成在操作系统的临时路径，如 Linux 下的 `/tmp`，而 Linux 的 `/tmp` 路径下的文件，默认在重启，或者超过 10 天的情况下会被删除。

能不能让这个文件生成到别的路径？
--------------------------

如上所述，操作系统的临时路径是在 JVM 源代码中硬编码的，并且与 `java.io.tmpdir` 等属性不同，无法通过环境变量等形式进行更改。


解决方案
=======

分析完原因，让这个问题不再发生的解决方案，就只剩下让这个生成在操作系统临时路径下的 socket 文件不被删除了。

以 CentOS7 为例，临时文件夹下文件的删除，是由 Systemd Cleanup 任务完成的，可在其配置文件 `/usr/lib/tmpfiles.d/tmp.conf` 中，添加如下内容，以排除对 socket 文件的删除：

```conf
x /tmp/.java_pid*
```

其中，`x` 代表在清理任务中，排除符合的文件。


参考资料
=======

* [Java Attach机制](https://www.jianshu.com/p/542e50edc8e3)
* [JVM源码分析之Attach机制实现完全解读](https://mp.weixin.qq.com/s?__biz=MzIzNjI1ODc2OA==&mid=2650886799&idx=1&sn=108c5fdfcd2695594d4f80ff02fc9a70&mpshare=1&scene=21&srcid=0114WsKpUmDXhRtqy8x7JX5w#wechat_redirect)
* [Serviceability in HotSpot](http://openjdk.java.net/groups/hotspot/docs/Serviceability.html)
* [Fixing Bugs in Running Java Code with Dynamic Attach](https://www.sitepoint.com/fixing-bugs-in-running-java-code-with-dynamic-attach/)
* [JVM is not reachable with jstat and jstack](https://confluence.atlassian.com/kb/jvm-is-not-reachable-with-jstat-and-jstack-1031281491.html)