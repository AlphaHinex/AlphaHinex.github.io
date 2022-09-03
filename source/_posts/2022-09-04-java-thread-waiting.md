---
id: java-thread-waiting
title: "【转】Java 线程状态之 WAITING"
description: "深入探讨了 Java 线程的 WAITING 状态，特别是对 wait/notify 的情形进行了深入分析。"
date: 2022.09.04 10:34
categories:
    - Java
tags: [Java]
keywords: java, waiting, thread.state, 线程, 线程状态
cover: /contents/java-thread-states/cover.png
---

原文地址：[https://xiaogd.net/md/java-线程状态之-wating](https://xiaogd.net/md/java-%e7%ba%bf%e7%a8%8b%e7%8a%b6%e6%80%81%e4%b9%8b-waiting)

在[上一篇][blocked]里我们讲了一个重要状态：BLOCKED，在这一篇章里，我们来看另一个重要的状态：WAITING（等待）。

![](/contents/java-thread-states/state-waiting.png)

定义
====

一个正在无限期等待另一个线程执行一个特别的动作的线程处于这一状态。

> A thread that is waiting indefinitely for another thread to perform a particular action is in this state.

然而这里并没有详细说明这个“特别的动作”到底是什么，详细定义还是看 javadoc（jdk8）：

一个线程进入 WAITING 状态是因为调用了以下方法：

* 不带时限的 Object.wait 方法
* 不带时限的 Thread.join 方法
* LockSupport.park

然后会等其它线程执行一个特别的动作，比如：

* 一个调用了某个对象的 Object.wait 方法的线程会等待另一个线程调用此对象的 Object.notify() 或 Object.notifyAll()。
* 一个调用了 Thread.join 方法的线程会等待指定的线程结束。

对应的英文原文如下：

> A thread is in the waiting state due to calling one of the following methods:
> * Object.wait with no timeout
> * Thread.join with no timeout
> * LockSupport.park
>
> A thread in the waiting state is waiting for another thread to perform a particular action. For example, a thread that has called Object.wait() on an object is waiting for another thread to call Object.notify() or Object.notifyAll() on that object. A thread that has called Thread.join() is waiting for a specified thread to terminate.


线程间的协作（cooperate）机制
==========================

显然，WAITING 状态所涉及的不是一个线程的独角戏，相反，它涉及多个线程，具体地讲，这是多个线程间的一种协作机制。谈到线程我们经常想到的是线程间的竞争（race），比如去争夺锁，但这并不是故事的全部，线程间也会有协作机制。

> 就好比在公司里你和你的同事们，你们可能存在在晋升时的竞争，但更多时候你们更多是一起合作以完成某些任务。

wait/notify 就是线程间的一种协作机制，那么首先，为什么 wait？什么时候 wait？它为什么要等其它线程执行“特别的动作”？它到底解决了什么问题？

wait 的场景
==========

首先，为什么要 wait 呢？简单讲，是因为条件（condition）不满足。那么什么是条件呢？为方便理解，我们设想一个场景：

> 有一节列车车厢，有很多乘客，每个乘客相当于一个线程；里面有个厕所，这是一个公共资源，且一次只允许一个线程进去访问（毕竟没人希望在上厕所期间还与他人共享~）。
> ![](/contents/java-thread-states/toilet.png)

竞争关系
-------

假如有多个乘客想同时上厕所，那么这里首先存在的是竞争的关系。

> 如果将厕所视为一个对象，它有一把锁，想上厕所的乘客线程需要先获取到锁，然后才能进入厕所。
> ![](/contents/java-thread-states/race.png)

Java 在语言级直接提供了同步的机制，也即是 synchronized 关键字：

> synchronized(expression) {……}

它的机制是这样的：对表达式（expresssion）求值（值的类型须是引用类型（reference type）），获取它所代表的对象，然后尝试获取这个对象的锁：
* 如果能获取锁，则进入同步块执行，执行完后退出同步块，并归还对象的锁（异常退出也会归还）；
* 如果不能获取锁，则阻塞在这里，直到能够获取锁。

在一个线程还在厕所期间，其它同时想上厕所的线程被阻塞，处在该厕所对象的 entry set 中，处于 BLOCKED 状态。

![](/contents/java-thread-states/entry-set.png)

完事之后，退出厕所，归还锁。

![](/contents/java-thread-states/release-lock.png)

之后，系统再在 entry set 中挑选一个线程，将锁给到它。

![](/contents/java-thread-states/obtain-lock.png)

对于以上过程，以下为一个 gif 动图演示：

![](/contents/java-thread-states/toilet.gif)

当然，这就是我们所熟悉的锁的竞争过程。以下为演示的代码：

```java
@Test
public void testBlockedState() throws Exception {
    class Toilet { // 厕所类
        public void pee() { // 尿尿方法
            try {
                Thread.sleep(21000);// 研究表明，动物无论大小尿尿时间都在21秒左右
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }

    Toilet toilet = new Toilet();

    Thread passenger1 = new Thread(new Runnable() {
        public void run() {
            synchronized (toilet) {
                toilet.pee();
            }
        }
    });

    Thread passenger2 = new Thread(new Runnable() {
        public void run() {
            synchronized (toilet) {
                toilet.pee();
            }
        }
    });

    passenger1.start();

    // 确保乘客1先启动
    Thread.sleep(100);

    passenger2.start();

    // 确保已经执行了 run 方法
    Thread.sleep(100);

    // 在乘客1在厕所期间，乘客2处于 BLOCKED 状态
    assertThat(passenger2.getState()).isEqualTo(Thread.State.BLOCKED);
}
```

条件
----

现在，假设有个女乘客，她抢到了锁，进去之后裤子脱了一半，发现马桶的垫圈纸没了，于是拒绝尿。

> 或许是因为她比较讲究卫生，怕直接坐上去会弄脏她白花花的屁股~

现在，条件出现了：有纸没纸，这就是某种条件。

![](/contents/java-thread-states/no-paper.png)

那么，现在条件不满足，这位女线程该怎么办呢？如果只是在里面干等，显然是不行的。

> 这不就是人民群众所深恶痛绝的“占着茅坑不拉尿”吗？

* 一方面，外面 entry set 中可能好多群众还嗷嗷待尿呢（其中可能有很多大老爷线程，他们才不在乎有没有马桶垫圈纸~）
* 另一方面，假定外面同时有“乘务员线程”，准备进去增加垫圈纸，可你在里面霸占着不出来，别人也没法进去，也就没法加纸。

所以，当条件不满足时，需要出来，要把锁还回去，以使得诸如“乘务员线程”的能进去增加纸张。

等待是必要的吗？
-------------

那么出来之后是否一定需要等待呢？当然也未必。

> 这里所谓“等待”，指的是使线程处于不再活动的状态，即是从调度队列中剔除。

如果不等待，只是简单归还锁，用一个反复的循环来判断条件是否满足，那么还是可以再次回到调度队列，然后期待在下一次被调度到的时候，可能条件已经发生变化：

> 比如某个“乘务员线程”已经在之前被调度并增加了里面的垫圈纸。自然，也可能再次调度到的时候，条件依旧是不满足的。

现在让我们考虑一种比较极端的情况：厕所外一大堆的“女乘客线程”想进去方便，同时还有一个焦急的“乘务员线程”想进去增加厕纸。

![](/contents/java-thread-states/conductor.png)

如果线程都不等待，而厕所又是一个公共资源，无法并发访问。调度器每次挑一个线程进去，挑中“乘务员线程”的几率反而降低了，entry set 中很可能越聚越多无法完成方便的“女乘客线程”，“乘务员线程”被选中执行的几率越发下降。

> 当然，同步机制会防止产生所谓的“饥饿（starvation）”现象，“乘务员线程”最终还是有机会执行的，只是系统运行的效率下降了。

所以，这会干扰正常工作的线程，挤占了资源，反而影响了自身条件的满足。另外，“乘务员线程”可能这段时间根本没有启动，此时，不愿等待的“女乘客线程”不过是徒劳地进进出出，占用了 CPU 资源却没有办成正事。

> 效果上还是在这种没有进展的进进出出中等待，这种情形类似于所谓的忙等待 （busy waiting）。

协作关系
-------

综上，等待还是有必要的，我们需要一种更高效的机制，也即是 wait/notify 的协作机制。

当条件不满足时，应该调用 wait()方法，这时线程释放锁，并进入所谓的 wait set 中，具体的讲，是进入这个厕所对象的 wait set 中：

![](/contents/java-thread-states/wait-set.png)

这时，线程不再活动，不再参与调度，因此不会浪费 CPU 资源，也不会去竞争锁了，这时的线程状态即是 WAITING。

> 现在的问题是：她们什么时候才能再次活动呢？显然，最佳的时机是当条件满足的时候。

之后，“乘务员线程”进去增加厕纸，当然，此时，它也不能只是简单加完厕纸就完了，它还要执行一个特别的动作，也即是“通知（notify）”在这个对象上等待的女乘客线程：

> 大概就是向她们喊一声：“有纸啦！赶紧去尿吧！”显然，如果只是“女乘客线程”方面一厢情愿地等待，她们将没有机会再执行。

所谓“通知”，也即是把她们从 wait set 中释放出来，重新进入到调度队列（ready queue）中。
* 如果是 notify，则选取所通知对象的 wait set 中的一个线程释放；
* 如果是 notifyAll，则释放所通知对象的 wait set 上的全部线程。

整个过程如下图所示：

![](/contents/java-thread-states/notify.png)

对于上述过程，我们也给出以下 gif 动图演示：

![](/contents/java-thread-states/notify.gif)

**注意**：哪怕只通知了一个等待的线程，被通知线程也不能立即恢复执行，因为她当初中断的地方是在同步块内，而此刻她已经不持有锁，所以她需要再次尝试去获取锁（很可能面临其它线程的竞争），成功后才能在当初调用 wait 方法之后的地方恢复执行。（这也即是所谓的 “reenter after calling Object.wait”，在[上一个篇章][blocked]中也曾详细的讨论了这一过程。）

* 如果能获取锁，线程就从 WAITING 状态变成 RUNNABLE 状态；
* 否则，从 wait set 出来，又进入 entry set，线程就从 WAITING 状态又变成 BLOCKED 状态。

综上，这是一个协作机制，“女乘客线程”和“乘务员线程”间存在一个协作关系。显然，这种协作关系的存在，“女乘客线程”可以避免在条件不满足时的盲目尝试，也为“乘务员线程”的顺利执行腾出了资源；同时，在条件满足时，又能及时得到通知。协作关系的存在使得彼此都能受益。

生产者与消费者问题
---------------

不难发现，以上实质上也就是经典的“生产者与消费者”的问题：

> 乘务员线程生产厕纸，女乘客线程消费厕纸。当厕纸没有时（条件不满足），女乘客线程等待，乘务员线程添加厕纸（使条件满足），并通知女乘客线程（解除她们的等待状态）。接下来，女乘客线程能否进一步执行则取决于锁的获取情况。

代码的演示：
---------

在以下代码中，演示了上述的 wait/notify 的过程：

```java
@Test
public void testWaitingState() throws Exception {
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

    // 两乘客线程
    Thread[] passengers = new Thread[2];
    for (int i = 0; i < passengers.length; i++) {
        passengers[i] = new Thread(new Runnable() {
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
    }

    // 乘务员线程
    Thread steward = new Thread(new Runnable() {
        public void run() {
            synchronized (toilet) {
                toilet.paperCount += 10;// 增加十张纸
                toilet.notifyAll();// 通知所有在此对象上等待的线程
            }
        }
    });

    passengers[0].start();
    passengers[1].start();

    // 确保已经执行了 run 方法
    Thread.sleep(100);

    // 没有纸，两线程均进入等待状态
    assertThat(passengers[0].getState()).isEqualTo(Thread.State.WAITING);
    assertThat(passengers[1].getState()).isEqualTo(Thread.State.WAITING);

    // 乘务员线程启动，救星来了
    steward.start();

    // 确保已经增加纸张并已通知
    Thread.sleep(100);

    // 其中之一会得到锁，并执行 pee，但无法确定是哪个，所以用 "或 ||"
    // 注：因为 pee 方法中实际调用是 sleep， 所以很快就从 RUNNABLE 转入 TIMED_WAITING(sleep 时对应的状态)
    assertTrue(Thread.State.TIMED_WAITING.equals(passengers[0].getState())
            || Thread.State.TIMED_WAITING.equals(passengers[1].getState()));

    // 其中之一则被阻塞，但无法确定是哪个，所以用 "或 ||"
    assertTrue(Thread.State.BLOCKED.equals(passengers[0].getState()) || Thread.State.BLOCKED.equals(passengers[1].getState()));

}
```

join 的场景及其它
===============

从定义中可知，除了 wait/notify 外，调用 join 方法也会让线程处于 WAITING 状态。

join 的机制中并没有显式的 wait/notify 的调用，但可以视作是一种特殊的，隐式的 wait/notify 机制。

假如有 a，b 两个线程，在 a 线程中执行 b.join()，相当于让 a 去等待 b，此时 a 停止执行，等 b 执行完了，系统内部会隐式地通知 a，使 a 解除等待状态，恢复执行。

> 换言之，a 等待的条件是 “b 执行完毕”，b 完成后，系统会自动通知 a。

关于 LockSupport.park 的情况则由读者自行分析。

与传统 waiting 状态的关系
======================

Thread.State.WAITING 状态与传统的 waiting 状态类似：

![](/contents/java-thread-states/os-jvm-thread-state-waiting.png)

不过，Java 中还细分出了 TIMED_WAITING 状态，由于篇幅关系，我们在下一篇中再分析最后一个 TIMED_WAITING 状态。

[blocked]: https://xiaogd.net/md/java-%e7%ba%bf%e7%a8%8b%e7%8a%b6%e6%80%81%e4%b9%8b-blocked