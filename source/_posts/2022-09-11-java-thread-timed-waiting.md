---
id: java-thread-timed-waiting
title: "【转】Java 线程状态之 TIMED_WAITING"
description: "深入探讨了 Java 线程的 TIMED_WAITING 状态"
date: 2022.09.11 10:26
categories:
    - Java
tags: [Java]
keywords: java, timed waiting, thread.state, 线程, 线程状态
cover: /contents/java-thread-states/cover.png
---

原文地址：[https://xiaogd.net/md/java-线程状态之-timed_waiting](https://xiaogd.net/md/java-%e7%ba%bf%e7%a8%8b%e7%8a%b6%e6%80%81%e4%b9%8b-timed_waiting)

目录
* 定义
* timed_waiting 的场景
* 虚假唤醒（spurious wakeup）
* sleep 时的线程状态
* BLOCKED 和 WAITING 状态的区别和联系
* 总结

在[上一篇章][waiting]中我们谈论了 WAITING 状态，在这一篇章里，我们来看剩余的最后的一个状态：TIMED_WAITING（限时等待）。

![](/contents/java-thread-states/state-timed-waiting.png)

定义
====

一个正在限时等待另一个线程执行一个动作的线程处于这一状态。

> A thread that is waiting for another thread to perform an action for up to a specified waiting time is in this state.

更详细的定义还是看 javadoc（jdk8）：

带指定的等待时间的等待线程所处的状态。一个线程处于这一状态是因为用一个指定的正的等待时间（为参数）调用了以下方法中的其一：

* Thread.sleep
* 带时限（timeout）的 Object.wait
* 带时限（timeout）的 Thread.join
* LockSupport.parkNanos
* LockSupport.parkUntil

对应的英文原文如下：

> Thread state for a waiting thread with a specified waiting time. A thread is in the timed waiting state due to calling one of the following methods with a specified positive waiting time:
> * Thread.sleep
> * Object.wait with timeout
> * Thread.join with timeout
> * LockSupport.parkNanos
> * LockSupport.parkUntil

不难看出，TIMED_WAITING 与 WAITING 间的联系还是很紧密的，主要差异在时限（timeout）参数上。

> 另外则是 sleep 这一点上的不同。

timed_waiting 的场景
===================

实际上，在上一篇章中谈到的没有参数的 wait() 等价于 wait(0)，而 wait(0) 它不是等0毫秒，恰恰相反，它的意思是永久的等下去，到天荒地老，除非收到通知。

> 具体可见 java 的源代码及相应 javadoc，注意：同时又还存在一种特殊的情况，所谓的“spurious wakeup”（虚假唤醒），我们在下面再讨论。

即是把自己再次活动的命运完全交给了别人（通知者），那么这样会存在什么问题呢？

> 在这里，我们还是继续上一篇章中的谈到的车厢场景，如不清楚的参见 [Java 线程状态之 WAITING][waiting]。

设想一种情况，乘务员线程增加了厕纸，正当它准备执行 notify 时，这个线程因某种原因被杀死了（持有的锁也随之释放）。这种情况下，条件已经满足了，但等待的线程却没有收到通知，还在傻乎乎地等待。
简而言之，就是存在通知失效的情况。这时，如果有个心机婊线程，她考虑得比较周全，她不是调用 wait()，而是调用 wait(1000），如果把进入 wait set 比喻成在里面睡觉等待。那么 wait(1000）相当于自带设有倒计时 1000 毫秒的闹钟，换言之，她在同时等待两个通知，并取决于哪个先到：

* 如果在1000毫秒内，她就收到了乘务员线程的通知从而唤醒，闹钟也随之失效；
* 反之，超过1000毫秒，还没收到通知，则闹钟响起，此时她则被闹钟唤醒。

这种情况类似于双保险。下面是一个动态的 gif 示意图（空的电池代表条件不满足，粉色的乘务员线程负责增加纸张，带有闹钟的乘客线程代表限时等待）：

![](/contents/java-thread-states/thread_timed_waiting.gif)

这样，在通知失效的情况下，她还是有机会自我唤醒的，进而完成尿尿动作。

> 可见，一个线程，她带不带表（闹钟），差别还是有的。其它死心眼的线程则等呀等，等到下面都湿了却依旧可能等不来通知。用本山大叔的话来说：那憋得是相当难受。

以下代码模拟了上述情形，这次，没有让乘务员线程执行通知动作，但限时等待的线程2还是自我唤醒了：

```java
@Test
public void testTimedWaitingState() throws Exception {
    class Toilet { // 厕所类
        int paperCount = 0; // 纸张

        public void pee() { // 尿尿方法
            try {
                Thread.sleep(21000);// 研究表明，动物无论大小尿尿时间都在21秒左右
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }

    Toilet toilet = new Toilet();

    // 一直等待的线程1
    Thread passenger1 = new Thread(new Runnable() {
        public void run() {
            synchronized (toilet) {
                while (toilet.paperCount < 1) {
                    try {
                        toilet.wait(); // 条件不满足，等待
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                }
                toilet.paperCount--; // 使用一张纸
                toilet.pee();
            }
        }
    });

    // 只等待1000毫秒的线程2
    Thread passenger2 = new Thread(new Runnable() {
        public void run() {
            synchronized (toilet) {
                while (toilet.paperCount < 1) {
                    try {
                        toilet.wait(1000); // 条件不满足，但只等待1000毫秒
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                }
                toilet.paperCount--; // 使用一张纸
                toilet.pee();
            }
        }
    });

    // 乘务员线程
    Thread steward = new Thread(new Runnable() {
        public void run() {
            synchronized (toilet) {
                toilet.paperCount += 10;// 增加十张纸
                // 粗心的乘务员线程，没有通知到，（这里简单把代码注释掉来模拟）
                // toilet.notifyAll();// 通知所有在此对象上等待的线程
            }
        }
    });

    passenger1.start();
    passenger2.start();

    // 确保已经执行了 run 方法
    Thread.sleep(100);

    // 没有纸，两线程均进入等待状态，其中，线程2进入 TIMED_WAITING
    assertThat(passenger1.getState()).isEqualTo(Thread.State.WAITING);
    assertThat(passenger2.getState()).isEqualTo(Thread.State.TIMED_WAITING);

    // 此时的纸张数应为0
    assertThat(toilet.paperCount).isEqualTo(0);

    // 乘务员线程启动
    steward.start();

    // 确保已经增加纸张
    Thread.sleep(100);

    // 此时的纸张数应为10
    assertThat(toilet.paperCount).isEqualTo(10);

    // 确保线程2已经自我唤醒
    Thread.sleep(1000);

    // 如果纸张已经被消耗一张，说明线程2已经成功自我唤醒
    assertThat(toilet.paperCount).isEqualTo(9);

}
```

虚假唤醒（spurious wakeup）
========================

虽然，前面说到没有参数的 wait() 等价于 wait(0)，意思是永久的等下去直到被通知到。但事实上存在所谓的 “spurious wakeup”，也即是“虚假唤醒”的情况，具体可见 Object.wait(long timeout) 中的 javadoc 说明：

> A thread can also wake up without being notified, interrupted, or timing out, a so-called spurious wakeup. While this will rarely occur in practice, applications must guard against it by testing for the condition that should have caused the thread to be awakened, and continuing to wait if the condition is not satisfied.
> 
> 一个线程也能在没有被通知、中断或超时的情况下唤醒，也即所谓的“虚假唤醒”，虽然这点在实践中很少发生，应用应该检测导致线程唤醒的条件，并在条件不满足的情况下继续等待，以此来防止这一点。

换言之，wait 应该总是在循环中调用（waits should always occur in loops），javadoc 中给出了样板代码：

```java
synchronized (obj) {
    while (<condition does not hold>)
        obj.wait(timeout);
    ... // Perform action appropriate to condition
}
```

简单讲，要避免使用 if 的方式来判断条件，否则一旦线程恢复，就继续往下执行，不会再次检测条件。由于可能存在的“虚假唤醒”，并不意味着条件是满足的，这点甚至对简单的“二人转”的两个线程的 wait/notify 情况也需要注意。

> 另外，如果对于更多线程的情况，比如“生产者和消费者”问题，一个生产者，两个消费者，更加不能简单用 if 判断。因为可能用的是 notifyAll，两个消费者同时起来，其中一个先抢到了锁，进行了消费，等另一个也抢到锁时，可能条件又不满足了，所以还是要继续判断，不能简单认为被唤醒了就是条件满足了。

关于此话题的更多信息，可参考：
* Doug Lea 的 《Concurrent Programming in Java (Second Edition)》3.2.3 节。
* Joshua Bloch 的 《Effective Java Programming Language Guide》，“Prefer concurrency utilities to  wait and  notify”章节。

sleep 时的线程状态
================

进入 TIMED_WAITING 状态的另一种常见情形是调用的 sleep 方法，单独的线程也可以调用，不一定非要有协作关系，当然，依旧可以将它视作为一种特殊的 wait/notify 情形。

> 这种情况下就是完全靠“自带闹钟”来通知了。
另：sleep(0) 跟 wait(0) 是不一样的，sleep 不存在无限等待的情况，sleep(0) 相当于几乎不等待。

需要注意，sleep 方法没有任何同步语义。通常，我们会说，sleep 方法不会释放锁。

> javadoc中的确切说法是：The thread does not lose ownership of any monitors.（线程不会失去任何 monitor 的所有权）

而较为夸张的说法则是说 sleep 时会抱住锁不放，这种说法不能说说错了，但不是很恰当。

> 打个不太确切的比方，就好比你指着一个大老爷们说：“他下个月不会来大姨妈”，那么，我们能说你说错了吗？但是，显得很怪异。

就锁这个问题而言，确切的讲法是 sleep 是跟锁无关的。

> JLS 中的说法是“It is important to note that neither  Thread.sleep nor  Thread.yield have any synchronization semantics”。（sleep 和 yield 均无任何同步语义），另一个影响是，在它们调用的前后都无需关心寄存器缓存与内存数据的一致性（no flush or reload）
> 
> 见《The Java Language Specification Java SE 7 Edition》17.3 Sleep and Yield

所以，如果线程调用 sleep 时是带了锁，sleep 期间则锁还为线程锁拥有。

> 比如在同步块中调用 sleep（需要特别注意，或许你需要的是 wait 的方法！）

反之，如果线程调用 sleep 时没有带锁（这也是可以的，这点与 wait 不同，不是非得要在同步块中调用），那么自然也不会在sleep 期间“抱住锁不放”。

> 压根就没有锁，你让它抱啥呢？而 sleep 君则完全是一脸懵逼：“锁？啥是锁？我没听过这玩意！”

带 timeout 的 join 的情景与 wait(timeout) 原理类似，这里不再展开叙述。

> LockSupport.parkNanos 和 parkUnitl 也交由读者自行分析。

BLOCKED 和 WAITING 状态的区别和联系
================================

在说完了 BLOCKED，WAITING 和 TIMED_WAITING 后，我们可以综合来看看它们，比如，阻塞与等待到底有什么本质的区别呢？

显然，BLOCKED 同样可以视作是一种特殊的，隐式的 wait/nofity 机制。等待的条件就是“有锁还是没锁”。

> 不过，这是一个不确定的等待，可能等待（无法获取锁时），也可能不等待（能获取锁）。陷入这种阻塞后也没有自主退出的机制。
> 
> 有一点需要注意的是，BLOCKED 状态是与 Java 语言级别的 synchronized 机制相关的，我们知道在 Java 5.0 之后引入了更多的机制（java.util.concurrent），除了可以用 synchronized 这种内部锁，也可以使用外部的显式锁。
> 
> 显式锁有一些更好的特性，如能中断，能设置获取锁的超时，能够有多个条件等，尽管从表面上说，当显式锁无法获取时，我们还是说，线程被“阻塞”了，但却未必是 BLOCKED 状态。

当锁可用时，其中的一个线程会被系统隐式通知，并被赋予锁，从而获得在同步块中的执行权。

> 显然，等待锁的线程与系统同步机制形成了一个协作关系。

对比来看， WAITING 状态属于主动地显式地申请的阻塞，BLOCKED 则属于被动的阻塞，但无论从字面意义还是从根本上来看，并无本质的区别。

> 在前面我们也已经说过，这三个状态可以认为是传统 waiting 状态在 JVM 层面的一个细分。

总结
====

最后，跟传统进（线）程状态划分的一个最终对比：

![](/contents/java-thread-states/os-jvm-thread-state-all.png)

关于 Java 线程状态的所有分析就到此为止。


[waiting]:https://xiaogd.net/md/java-%e7%ba%bf%e7%a8%8b%e7%8a%b6%e6%80%81%e4%b9%8b-waiting