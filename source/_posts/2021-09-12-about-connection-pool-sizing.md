---
id: about-connection-pool-sizing
title: "关于数据库连接池，你可能做错了"
description: "两大误区，中招了吗？"
date: 2021.09.12 10:26
categories:
    - Database
tags: [Database, Connection Pools]
keywords: fixed size, HikariCP, minimumIdle, maximumPoolSize, 静态连接池, 动态连接池
cover: /contents/about-connection-pool-sizing/cover.png
---

误区1：动态连接池
===============

## [Real-World Performance - 13 - Large Dynamic Connection Pools - Part 1](https://alphahinex.github.io/2021/08/29/connection-pools-1/)

Oracle RWP（Real World Performance） 团队：
1. 不能添加无数个连接至数据库
1. 数据库的连接数在理想情况下应该是静态的，无论何时都应该是相同的值

不幸的是，如今的应用大多数建立在中间件之上，这些中间件倾向于指定动态连接池，通常是一个最小值和一个最大值。这给人们一种错觉，应用可以按需持续创建连接，并在负载消失后削减它们。事实上，这是最糟糕的事。你有能力快速创建大量连接，我们有能力破坏掉数据库的稳定性。

## [minimumIdle](https://github.com/brettwooldridge/HikariCP#frequently-used)

HikariCP 堪称上面提到的中间件界的一道光，他们建议：为了获得最好的性能和峰值需求的响应，我们建议不要设置 `minimumIdle`，而是允许 HikariCP 充当固定大小的连接池。

结论
---

使用静态连接池，即将连接池中间件的最小连接数和最大连接数设置为相同的值。


误区2：连接池数量随缘
==================

基础理论
-------

1. 一个 CPU core，同一时间只能支持一个线程执行
1. 操作系统通过时间切片（time-slicing，多个任务短时间内交替执行），使 CPU core 支持“同时”执行多个线程
1. 单个 CPU 资源，在不存在线程阻塞时，顺序执行 A 和 B 两个线程，总是会比通过时间切片方式“同时”执行 A 和 B 两个线程，要快
1. 只有存在线程阻塞时（如 I/O 等待），多线程才能带来更好的性能表现

在面向数据库的场景中，最主要的两个受限的资源，是硬盘和网络。

机械硬盘在磁盘读写时，会产生 I/O 等待（盘片旋转、磁头寻道等），这时就会阻塞住线程，在这种情况下，将 CPU 资源释放出来，用来执行其他的线程，才能带来更好的性能。

SSD 不存在盘片旋转等寻找时间，所以速度更快，但不要认为“SSD 更快了，所以我可以用更多线程了”，恰恰相反，因为 I/O 等待时间更短了，应该减少而不是增加线程数量。

网络的情况与硬盘基本类似。

公式
----

PostgreSQL 在 [How to Find the Optimal Database Connection Pool Size](https://wiki.postgresql.org/wiki/Number_Of_Database_Connections) 中给出了一个连接池数量的建议公式：

```formula
((core_count * 2) + effective_spindle_count)
```

其中，`core_count` 代表 CPU 核心数量，这个数量不应该包括超线程的数量，即使超线程是可用的；`effective_spindle_count` 是指机械硬盘有效的中心主轴（[spindle](https://www.computerhope.com/jargon/s/spindle.htm)）数量。

![spindle](/contents/about-connection-pool-sizing/harddrive.jpg)

> 注意：这个公式在 SSD 环境下表现如何尚无具体的数据支撑

这意味着，一个四核单硬盘的 i7 服务器，应该设定的连接池个数为 `((4 * 2) + 1) = 9`，也可以凑整设置为 10。

感觉很低是吧？

> 可以实际试一下，这样的配置应对 3000 个前端用户的简单查询，可以轻松达到 6000 TPS。—— [HikariCP](https://github.com/brettwooldridge/HikariCP/wiki/About-Pool-Sizing#connections--core_count--2--effective_spindle_count)

pool locking
------------

当一个线程需要持有多个连接时，出现池锁（pool locking）的概率就会增加。比如连接池个数为 2，A、B 两个线程每个线程需要持有两个连接，A、B 先各获得一个，再获取第二个连接时陷入等待，之后便是永远的等待。

固然，增大连接池尺寸能够缓解这类场景下的锁定情况，但在扩大连接池之前，最好还是先检查一下在应用级别是否能做些什么。

为避免死锁，可以采用如下公式计算连接池尺寸：

```formula
pool size = Tn x (Cm - 1) + 1
```

`Tn` 是“最大”线程数，结合上面的情况，可以使用 `((core_count * 2) + effective_spindle_count)` 这个公式作为 `Tn`；`Cm` 是每个线程最大同时持有的连接数。

这个公式可以这样理解：每个线程都比实际需求少一个连接，再增加一个连接，就可以保证不会出现死锁。

> 注意：这个公式只是避免死锁的最小值，不一定是最优解

长事务
-----

当系统中存在长时间运行的事务时，可以考虑为运行长事务的线程单独创建一个连接池，这时连接池的大小还会收到另一个因素约束 —— 长事务任务的运行队列所支持的最大并行任务数量。

结论
---

根据具体环境及公式，计算得出静态连接池的大小。