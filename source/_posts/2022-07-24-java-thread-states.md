---
id: java-thread-states
title: "Java 线程状态介绍"
description: "理解 java.lang.Thread.State 枚举类中定义的六种状态"
date: 2022.07.24 10:26
categories:
    - Java
tags: [Java]
keywords: JVM, OS, Thread, NEW, RUNNABLE, BLOCKED, WAITING, TIMED_WAITING, TERMINATED
cover: /contents/java-thread-states/cover.png
---

JVM 中的线程，有六种状态，定义在 `java.lang.Thread.State` 枚举类中，从 [1.5](https://docs.oracle.com/javase/1.5.0/docs/api/) 版本开始，至目前最新的 [17](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/lang/Thread.State.html)、[18](https://docs.oracle.com/en/java/javase/18/docs/api/java.base/java/lang/Thread.State.html)，基本没有变化。

先来看一下 Java Doc 中对这六种状态的描述：

![](/contents/java-thread-states/cover.png)

注意下面那句话：

> A thread can be in only one state at a given point in time. These states are virtual machine states which do not reflect any operating system thread states.

这段话提到两点：
1. JVM 中的线程，在某一时间点，只能处于一种状态中；
2. 上面这些状态是 JVM 虚拟机中的线程状态，不对应任何操作系统的线程状态。


六种线程状态的理解
===============

先看两种比较简单的状态。

NEW / TERMINATED
----------------

### NEW

> Thread state for a thread which has not yet started.

线程对象创建后，尚未开始执行时，处于 `NEW` 状态。

### TERMINATED

> Thread state for a terminated thread. The thread has completed execution.

线程对象完成执行或终止退出后，处于 `TERMINATED` 状态。

### 获取线程状态

可以在线程实例上，直接调用 `getState()` 方法，获取此线程的状态，如：

```bash
$ jshell
|  欢迎使用 JShell -- 版本 11.0.3
|  要大致了解该版本, 请键入: /help intro

jshell> Thread t = new Thread()
t ==> Thread[Thread-3,5,main]

jshell> t.getState()
$8 ==> NEW

jshell> t.start()

jshell> t.getState()
$10 ==> TERMINATED
```

可以看到，线程对象刚创建后，查看状态时，为 `NEW` 状态；调用 `start()` 方法并执行完毕后，转换为 `TERMINATED` 状态。

> Java 9 开始提供了 `jshell` 工具，可以用于执行 Java 代码并立即获得执行结果。

RUNNABLE
--------

> Thread state for a runnable thread. A thread in the runnable state is executing in the Java virtual machine but it may be waiting for other resources from the operating system such as processor.

一个正在 Java 虚拟机中执行的线程处于这一状态，但它可能正在等待来自于操作系统的其它资源，比如处理器。

注意上面提到过：这里的状态指的是 JVM 虚拟机中的线程状态，不对应任何操作系统的线程状态。

JVM 将 CPU、硬盘、网络等都视为资源，有资源在为线程服务，它就认为线程是可以执行的，即使此时线程正在等待阻塞式的 IO 或网络操作，线程的状态也是 `RUNNABLE`。

```java
@Test
public void runnableState() {
    Thread t = new Thread(() -> {
        try(Scanner in = new Scanner(System.in)) {
            in.nextLine();
        }
    });
    assert Thread.State.NEW.equals(t.getState());

    t.start();
    assert Thread.State.RUNNABLE.equals(t.getState());
}
```

Java 线程状态的改变通常只与自身显式引入的机制有关，比如 `synchronized` 机制有可能让线程进入 `BLOCKED` 状态，`sleep`、`wait` 等方法则可能让其进入 `WATING` 之类的状态。


BLOCKED / WAITING / TIMED_WAITING
---------------------------------

剩下三种状态，可以先看一下这个视频，通过生活中的例子，对这三种状态进行了解释：

<video width="640" height="360" preload controls>
  <source src="/contents/java-thread-states/video.mp4">
</video>

> 该视频搬运自 [油管](https://www.youtube.com/watch?v=fzYLtYaJ_D0)，使用 https://yt1s.com/ 下载。

### BLOCKED

> Thread state for a thread blocked waiting for a monitor lock. A thread in the blocked state is waiting for a monitor lock to enter a synchronized block/method or reenter a synchronized block/method after calling Object.wait.

视频中，菲利普家的车子是一个同步资源：在车子被其妻子线程使用时，菲利普线程只能处于等待状态，等待车子空闲下来以便为他所用。

`BLOCKED` 状态跟 I/O 的阻塞是不同的，它不是一般意义上的阻塞，而是特指被 `synchronized` 块阻塞，即是跟线程同步有关的一个状态，是由 Java 的同步机制引起的等待状态。

### WAITING

> Thread state for a waiting thread. A thread is in the waiting state due to calling one of the following methods:
> 
> * Object.wait with no timeout
> * Thread.join with no timeout
> * LockSupport.park
> 
> A thread in the waiting state is waiting for another thread to perform a particular action. For example, a thread that has called Object.wait() on an object is waiting for another thread to call Object.notify() or Object.notifyAll() on that object. A thread that has called Thread.join() is waiting for a specified thread to terminate.

视频中，车子这个同步资源，因为超速被交警扣押（`wait`），菲利普线程陷入了 `WATING` 状态。交警线程需要对车子资源进行一系列处理后，才会允许（`notify`）菲利普线程继续使用此资源，进而使菲利普线程恢复为 `RUNNABLE` 状态。

> `Object` 中的 `wait` 方法必须在该线程持有此对象的锁时才能被调用，否则会抛出 `IllegalMonitorStateException` 异常。

除了 `Object.wait` 方法外，`Thread.join` 和 `LockSupport.park` 也会导致线程转换为 `WAITING` 状态。注意，这几个方法都是不带超时时间的。

### TIMED_WAITING

> Thread state for a waiting thread with a specified waiting time. A thread is in the timed waiting state due to calling one of the following methods with a specified positive waiting time:
> 
> * Thread.sleep
> * Object.wait with timeout
> * Thread.join with timeout
> * LockSupport.parkNanos
> * LockSupport.parkUntil

`TIMED_WAITING` 状态与 `WAITING` 状态的区别，是 `TIMED_WAITING` 包含一个超时时间，在到达时限后，即使没有外部通知，也会自我唤醒。

视频中，菲利普线程因不想上班迟到，在等待拼车人线程通知时，设定了超时时间 10 分钟，时间到了，不管拼车人是否出现，都会继续前进。

在该状态的 Java Doc 描述中，也可以看到，触发该状态的五个方法，都是需要设定超时时间的。调用带超时时间的等待方法，可以避免因通知失效导致等待线程陷入无休止的等待。

线程 dump
========

了解了线程状态的含义，在分析 Java 应用的运行状况时会非常有帮助。

要获得一个运行中的 Java 进程的线程栈信息时，可使用 JDK 中自带的 `jstack` 工具，如：

```bash
$ jstack -l <pid>
```

> `<pid>` 需替换为 Java 进程 ID，可通过 `jps` 命令查询。

上面命令会将线程栈信息直接输出到控制台，将其输出内容重定向到文件，即可获得线程 dump 文件：

```bash
$ jstack -l <pid> > thread.dump
```

可通过文本编辑器直接打开线程 dump 文件，里面包含该 Java 进程中每个 Java 线程的栈信息，例如：

```dump
"http-nio-8080-Poller" #19 daemon prio=5 os_prio=31 cpu=77.35ms elapsed=664.82s tid=0x00007ffbd1ea0800 nid=0x6303 runnable  [0x00007000099a2000]
   java.lang.Thread.State: RUNNABLE
	at sun.nio.ch.KQueue.poll(java.base@11.0.3/Native Method)
	at sun.nio.ch.KQueueSelectorImpl.doSelect(java.base@11.0.3/KQueueSelectorImpl.java:122)
	at sun.nio.ch.SelectorImpl.lockAndDoSelect(java.base@11.0.3/SelectorImpl.java:124)
	- locked <0x000000070de1e270> (a sun.nio.ch.Util$2)
	- locked <0x000000070de1def0> (a sun.nio.ch.KQueueSelectorImpl)
	at sun.nio.ch.SelectorImpl.select(java.base@11.0.3/SelectorImpl.java:136)
	at org.apache.tomcat.util.net.NioEndpoint$Poller.run(NioEndpoint.java:787)
	at java.lang.Thread.run(java.base@11.0.3/Thread.java:834)

   Locked ownable synchronizers:
	- None
```

可以看出，该线程处于 `RUNNABLE` 状态中。


可视化工具
=========

VisualVM
--------

[VisualVM](https://visualvm.github.io/) 可以查看本地或远程运行中的 Java 进程的线程状态，在 JDK 6~8 中是 JDK 中自带的工具，JDK 9 之后不再包含在 JDK 中，可从 [VisualVM 下载页面](https://visualvm.github.io/download.html) 下载最新版。

可通过 `jvisualvm` 命令启动 VisualVM：

![](/contents/java-thread-states/jvisualvm.png)

由上图右下角可以看到，VisualVM 中，对线程状态的划分与 JDK 中定义的线程状态不相同，但是有对应关系的。

在 [ThreadMXBeanDataManager.ThreadMonitoredDataResponse#getState](https://github.com/visualvm/visualvm.java.net.backup/blob/master/visualvm/applicationviews/src/com/sun/tools/visualvm/application/views/threads/ThreadMXBeanDataManager.java#L177-L198) 中定义了两种线程状态的映射：

```java
byte getState(ThreadInfo threadInfo) {
    Thread.State state = threadInfo.getThreadState();
    switch (state) {
        case BLOCKED:
            return CommonConstants.THREAD_STATUS_MONITOR;
        case RUNNABLE:
            return CommonConstants.THREAD_STATUS_RUNNING;
        case TIMED_WAITING:
        case WAITING:
            StackTraceElement[] stack = threadInfo.getStackTrace();
            if (stack.length>0) {
                StackTraceElement el = stack[0];
                if (isSleeping(el)) return CommonConstants.THREAD_STATUS_SLEEPING;
                if (isParked(el)) return CommonConstants.THREAD_STATUS_PARK;
            }
            return CommonConstants.THREAD_STATUS_WAIT;
        case TERMINATED:
        case NEW:
            return CommonConstants.THREAD_STATUS_ZOMBIE;
    }
    return CommonConstants.THREAD_STATUS_UNKNOWN;
}
```

即

|JDK |Visual VM|
|:---|:--------|
|BLOCKED | Monitor |
|RUNNABLE | Running |
|WAITING / TIMED_WAITING | Sleeping / Park / Wait |
|TERMINATED / NEW | Zombie |

fastThread
----------

fastThread 网站（ https://fastthread.io/ ）为我们提供了一个免费的，在线分析线程 dump 文件的方案，可以将 dump 文件上传，得到可视化的分析结果：

![](/contents/java-thread-states/fastthread.png)


参考资料
=======

* [关于 Java 的线程状态](https://my.oschina.net/goldenshaw/blog/386788)
* [Java 线程状态之 RUNNABLE](https://my.oschina.net/goldenshaw/blog/705397)
* [Java 线程状态之 BLOCKED](https://my.oschina.net/goldenshaw/blog/706663)
* [Java 线程状态之 WAITING](https://my.oschina.net/goldenshaw/blog/802620)
* [Java 线程状态之 TIMED_WAITING](https://my.oschina.net/goldenshaw/blog/806018)
* [VisualVM - Thread States](https://stackoverflow.com/questions/27406200/visualvm-thread-states/27406503)