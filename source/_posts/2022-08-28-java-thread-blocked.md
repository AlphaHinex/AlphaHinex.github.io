---
id: java-thread-blocked
title: "【转】Java 线程状态之 BLOCKED"
description: "深入探讨了 Java 线程的 BLOCKED 状态，特别是对 enter 及 reenter 两种情形进行了深入分析。"
date: 2022.08.28 10:26
categories:
    - Java
tags: [Java]
keywords: java, blocked, thread.state, 线程, 线程状态
cover: /contents/java-thread-states/cover.png
---

原文地址：[https://xiaogd.net/md/java-线程状态之-blocked](https://xiaogd.net/md/java-%e7%ba%bf%e7%a8%8b%e7%8a%b6%e6%80%81%e4%b9%8b-blocked)

目录
* BLOCKED 状态的定义
* 进入（enter）同步块时阻塞
* wait 之后重进入（reenter）同步块时阻塞
* 总结

在[上一篇](https://xiaogd.net/java-%e7%ba%bf%e7%a8%8b%e7%8a%b6%e6%80%81%e4%b9%8b-runnable/)中，我们强调了 BLOCKED 状态跟 I/O 的阻塞是不同的，它不是一般意义上的阻塞，而是特指被 synchronized 块阻塞，即是跟线程同步有关的一个状态。


BLOCKED 状态的定义
================

[前面](http://my.oschina.net/goldenshaw/blog/386788)已经说过 BLOCKED(阻塞) 的简单定义为：

> 一个正在阻塞等待一个监视器锁的线程处于这一状态。(A thread that is blocked waiting for a monitor lock is in this state.)

更加详细的定义可以参考 Thread.State 中的 javadoc：

```java
/**
 * Thread state for a thread blocked waiting for a monitor lock.
 * A thread in the blocked state is waiting for a monitor lock
 * to enter a synchronized block/method or
 * reenter a synchronized block/method after calling
 * {@link Object#wait() Object.wait}.
 */
BLOCKED,
```

这句话很长，可以拆成两个简单句来理解。

1. A thread in the blocked state is waiting for a monitor lock to enter a synchronized block/method.
    > 一个处于 blocked 状态的线程正在等待一个监视器锁以进入一个同步的块或方法。
1. A thread in the blocked state is waiting for a monitor lock to reenter a synchronized block/method after calling Object.wait.
    > 一个处于 blocked 状态的线程正在等待一个监视器锁，在其调用 Object.wait 方法之后，以再次进入一个同步的块或方法。


进入（enter）同步块时阻塞
======================

先说第一句，这个比较好理解。

监视器锁用于同步访问，以达到多线程间的互斥。所以一旦一个线程获取锁进入同步块，在其出来之前，如果其它线程想进入，就会因为获取不到锁而阻塞在同步块之外，这时的状态就是 BLOCKED。

> 注：这一状态的进入及解除都不受我们控制，当锁可用时，线程即从阻塞状态中恢复。

我们可以用一些代码来演示这一过程：

```java
@Test
public void testBlocked() throws Exception {
    class Counter {
        int counter;
        public synchronized void increase() {
            counter++;
            try {
                Thread.sleep(30000);
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            }
        }
    }
    Counter c = new Counter();

    Thread t1 = new Thread(new Runnable() {
        public void run() {
            c.increase();
        }
    }, "t1线程");
    t1.start();

    Thread t2 = new Thread(new Runnable() {
        public void run() {
            c.increase();
        }
    }, "t2线程");
    t2.start();

    Thread.sleep(100); // 确保 t2 run已经得到执行
    assertThat(t2.getState()).isEqualTo(Thread.State.BLOCKED);
}
```

> 以上定义了一个访问计数器 counter，有一个同步的 increase 方法。t1 线程先进入，然后在同步块里面睡觉，导致锁迟迟无法释放，t2 尝试执行同步方法时就因无法获取锁而被阻塞了。

VisualVM 监控显示了 t2 线程的状态：

![](/contents/java-thread-states/visualvm-blocked.jpg)

> 图上的“监视（monitor）”状态即为 BLOCKED 状态。可以看到在 t1睡眠期间 t2处于 BLOCKED 状态。
BLOCKED 状态可以视作是一种特殊的 WAITING，特指等待锁。


wait 之后重进入（reenter）同步块时阻塞
==================================

现在再次来看第二句：

2. A thread in the blocked state is waiting for a monitor lock to reenter a synchronized block/method after calling Object.wait.

> 一个处于 blocked 状态的线程正在等待一个监视器锁，在其调用 Object.wait 方法之后，以再次进入一个同步的块或方法。

这句话有点绕，也不好翻译成一句简洁的中文。如果没有对 wait 的相关背景有较好的理解，则不容易理解这句话。我们在此把它稍微展开讲一下。既然是 reenter，说明有两次 enter，这个过程是这样的：
1. 调用 wait 方法必须在同步块中，即是要先获取锁并进入同步块，这是第一次 enter。
1. 而调用 wait 之后则会释放该锁，并进入此锁的等待队列（wait set）中。
1. 当收到其它线程的 notify 或 notifyAll 通知之后，等待线程并不能立即恢复执行，因为停止的地方是在同步块内，而锁已经释放了，所以它要重新获取锁才能再次进入（reenter）同步块，然后从上次 wait 的地方恢复执行。这是第二次 enter，所以叫 reenter。
1. 但锁并不会优先给它，该线程还是要与其它线程去竞争锁，这一过程跟 enter 的过程其实是一样的，因此也可能因为锁已经被其它线程据有而导致 BLOCKED。

这一过程就是所谓的 reenter a synchronized block/method after calling Object.wait。

关于这一点，因为也涉及到了 WAITING 的状态，可结合 [Java 线程状态之 WAITING](https://xiaogd.net/java-%e7%ba%bf%e7%a8%8b%e7%8a%b6%e6%80%81%e4%b9%8b-waiting/) 一起来理解，在那里还增加了一些动画的演示来辅助理解。

我们也用一段代码来演示这一过程：

```java
@Test
public void testReenterBlocked() throws Exception {
    class Account {
        int amount = 100; // 账户初始100元
        public synchronized void deposit(int cash) { // 存钱
            amount += cash;
            notify();
            try {
                Thread.sleep(30000); // 通知后却暂时不退出
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            }
        }
        public synchronized void withdraw(int cash) { // 取钱
            while (cash &gt; amount) {
                try {
                    wait();
                } catch (InterruptedException e) {
                    throw new RuntimeException(e);
                }
            }
            amount -= cash;
        }
    }
    Account account = new Account();
    Thread withdrawThread = new Thread(new Runnable() {
        public void run() {
            account.withdraw(200);
        }
    }, "取钱线程");
    withdrawThread.start();

    Thread.sleep(100); // 确保取钱线程已经得到执行

    assertThat(withdrawThread.getState()).isEqualTo(Thread.State.WAITING);

    Thread depositThread = new Thread(new Runnable() {
        public void run() {
            account.deposit(100);
        }
    }, "存钱线程");
    Thread.sleep(10000); // 让取钱线程等待一段时间
    depositThread.start();

    Thread.sleep(300); // 确保取钱线程已经被存钱线程所通知到

    assertThat(withdrawThread.getState()).isEqualTo(Thread.State.BLOCKED);

}
```

简要介绍一下以上代码场景：

1. 有一个账户对象，有存钱（deposit）和取钱（withdraw）方法，初始金额100元。
1. 取钱线程先启动，并进入（enter）同步块，试图取 200 元，发现钱不够，调用 wait，锁释放，线程挂起（WAITING 状态）。
1. 10 秒后存钱线程启动，存入钱并通知（notify）取钱线程，但之后继续在同步块中睡眠，导致锁没有释放。
1. 取钱线程收到通知后，退出 WAITING 状态，但已经不持有锁，当试图重新进入（reenter）同步块以恢复执行时，因锁尚未被存钱线程释放，于是被阻塞（BLOCKED 状态）。

监控的显示：

![](/contents/java-thread-states/visualvm-reenterblocked.jpg)

> 如图，取钱线程先是 WAITING，在收到通知因无法获取锁而阻塞（BLOCKED）。


总结
====

综合来看这两句话，两层意思，其实还是一个意思，简单地讲，就是enter，reenter 也还是 enter，概括地讲：

> 当因为获取不到锁而无法进入同步块时，线程处于 BLOCKED 状态。

如果有线程长时间处于 BLOCKED 状态，要考虑是否发生了死锁（deadlock）的状况。
BLOCKED 状态可以视作为一种特殊的 waiting，是传统 waiting 状态的一个细分：

![](/contents/java-thread-states/os-jvm-thread-state.png)

由于还没有讲到 WAITING 状态，而这里有涉及到了 wait 方法，所以上面对 wait 也稍微做了些分析，在下一章节，会更加详细的分析 WAITING 和 TIMED_WAITING 这两个状态。