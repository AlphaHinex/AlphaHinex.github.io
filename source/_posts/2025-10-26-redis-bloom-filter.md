---
id: redis-bloom-filter
title: "【译】Bloom filter"
description: "Redis 8 起，RedisBloom 数据结构已集成到 Redis 中，不再需要单独安装模块"
date: 2025.10.26 10:26
categories:
    - Redis
tags: [Redis, Data Structures]
keywords: Bloom, Bloom Filter, RedisBloom, hash, Cuckoo Filter, False Positive, error rate, sub-filter, stacked filter, total size
cover: /contents/covers/redis-bloom-filter.png
---

- 原文地址：https://redis.io/docs/latest/develop/data-types/probabilistic/bloom-filter/
- 源码：https://github.com/redis/docs/blob/e871df72be1af7a26a23bea62863650d3f648daa/content/develop/data-types/probabilistic/bloom-filter.md

Redis 开源版本中的布隆过滤器是一个基于概率的数据结构，它使用非常小的固定大小内存空间来检查一个元素是否存在于一个集合中。

不同于将所有数据项都存储在集合中，布隆过滤器只存储数据项的哈希表示，因此会牺牲一些精度。这种权衡带来的好处是，布隆过滤器在空间效率和速度上表现优异。

布隆过滤器能够保证一个元素不在集合中，但只能估计它是否存在。因此，当它回答一个元素不在集合中（否定回答）时，你可以确定情况确实如此。但每 N 个肯定回答中会有一个是错误的。
尽管乍一看这种不确定性似乎不寻常，但在计算机科学中仍然有其应用场景。在许多情况下，否定的答案可以避免更昂贵的操作，例如检查用户名是否已被占用、信用卡是否被报告为被盗、用户是否已经看到过广告等等。

## 适用场景

**金融欺诈检测（金融）**

这类应用能够回答“用户是否曾在此位置付款？”之类的问题，从而检查用户购物习惯中的可疑活动。

为每个用户创建一个布隆过滤器，并在每次交易时进行检查。提供极快的响应（本地延迟）。在用户移动时，在不同地区进行复制。防止随着规模扩大而降低性能。

使用 Redis 布隆过滤器可为此类应用提供以下好处：

- 快速完成交易
- 减少网络分区情况下交易中断的可能性（连接需要保持打开的时间更短）
- 为信用卡持有人和零售商提供额外的安全层

在金融行业，布隆过滤器还可以帮助回答其他问题：

- 用户是否曾在此类产品/服务类别中进行过购买？
- 当用户在经过验证的在线商店（如亚马逊、苹果应用商店等）购买商品时，是否需要跳过某些安全步骤？
- 这张信用卡是否被报告为丢失/被盗？在这个场景使用布隆过滤器的另一个好处是，金融机构可以交换被盗/被封锁的信用卡号码列表，而无需透露号码本身。

**广告投放（零售、广告）**

此类应用程序回答以下问题：

- 用户是否已经看过这个广告？
- 用户是否已经购买了这个产品？

使用布隆过滤器为每个用户存储所有购买的产品。推荐引擎建议一个新产品时可检查该产品是否已存在于用户的布隆过滤器中。

- 如果不存在，则向用户展示广告并将其添加到布隆过滤器中。
- 如果存在，则该过程将重新开始并重复，直到找到一个不在过滤器中的产品。

使用 Redis 布隆过滤器可为此类应用提供以下好处：

- 成本效益高，能够提供定制化的近实时体验
- 无需投资昂贵的基础设施

**检查用户名是否被占用（SaaS、内容发布平台）**

此类应用程序回答以下问题：这个用户名/电子邮件/域名/别名是否已经被使用？

使用布隆过滤器来存储每个已注册用户的用户名。新用户输入所需的用户名。应用程序检查该用户名是否存在于布隆过滤器中。

- 如果不存在，则创建用户并将用户名添加到布隆过滤器中。
- 如果存在，则应用程序可以选择检查主数据库或拒绝该用户名。

查询时间在不同数据规模上保持相同级别。

使用 Redis 布隆过滤器可为此类应用提供以下好处：

- 非常快速和高效的方式来执行常见操作
- 无需投资昂贵的基础设施

## 示例

设想有一个制造一百万种不同自行车的制造商，您希望避免在新型号中使用重复的名称。可以使用布隆过滤器来检测重复项。
在接下来的示例中，您将创建一个具有一百万个条目空间和 0.1% 错误率的过滤器。添加一个型号并检查它是否存在。然后添加多个型号并检查它们是否存在。

```>_Redis CLI
> BF.RESERVE bikes:models 0.001 1000000
OK
> BF.ADD bikes:models "Smoky Mountain Striker"
(integer) 1
> BF.EXISTS bikes:models "Smoky Mountain Striker"
(integer) 1
> BF.MADD bikes:models "Rocky Mountain Racer" "Cloudy City Cruiser" "Windy City Wippet"
1) (integer) 1
2) (integer) 1
3) (integer) 1
> BF.MEXISTS bikes:models "Rocky Mountain Racer" "Cloudy City Cruiser" "Windy City Wippet"
1) (integer) 1
2) (integer) 1
3) (integer) 1
```

注意：即使只有少量项目，也总有可能出现误报，这意味着某个项目可能被认为是“存在”的，即使它并未被明确添加到布隆过滤器中。有关布隆过滤器概率性质的更深入理解，请查看本文底部链接的博客文章。

## 创建布隆过滤器

使用 Redis Bloom 过滤器时，大部分的大小调整工作都已为您完成：

```cli
BF.RESERVE {key} {error_rate} {capacity} [EXPANSION expansion] [NONSCALING]
```

#### 1. 假正例率（`error_rate`）

这是一个 0 到 1 之间的小数值。例如，对于 0.1%（千分之一）的假正例率，error_rate 应设置为 0.001。

#### 2. 预期容量（`capacity`）

这是您期望在过滤器中总共拥有的项目数量，当您拥有静态集合时，这个数字是微不足道的，但当您的集合随着时间的推移而增长时，它变得更加具有挑战性。正确获取这个数字非常重要，因为如果设置 **过大** —— 您将浪费内存。如果 **过小**，过滤器将很快被填满，致使新的过滤器将不得不堆叠在其上（子过滤器堆叠）。在过滤器由多个子过滤器堆叠在一起的情况下，添加的延迟保持不变，但存在性检查的延迟会增加。原因在于检查的工作方式：常规检查将首先在顶部（最新）过滤器上执行，如果返回否定答案，则检查下一个过滤器，依此类推。这就是增加的延迟来源。

#### 3. 扩展（`EXPANSION`）

向布隆过滤器添加项目永远不会因为数据结构“填满”而失败。相反，错误率会开始增长。为了保持错误率接近在过滤器初始化时设置的值，布隆过滤器将自动扩展，这意味着当达到预期容量时，将创建一个额外的子过滤器。

新的子过滤器的大小是最后一个子过滤器大小乘以 `EXPANSION` 扩展值。如果要存储在过滤器中的项目数量未知，我们建议您使用 2 或更高的扩展率以减少子过滤器的数量。否则，我们建议您使用 1 的扩展率以减少内存消耗。默认的扩展值为 2。

过滤器将继续为每个新的子过滤器添加更多的哈希函数，以维持所预期的错误率。

也需你会想 “如果我知道我将要扩展，为什么还要创建一个较小的过滤器并使用高扩展率？”；答案是：是为了需要保持许多过滤器的情况（比如每个用户或每个产品一个过滤器），其中大多数过滤器将保持较小规模，但一些活动较多的过滤器将需要扩展。

#### 4. `NONSCALING`

如果您确定不需要扩展过滤器，请使用 `NONSCALING` 标志，因为这样过滤器将少使用一个哈希函数。只要记住，如果您最终达到了最初分配的容量，错误率将开始增长。

### 布隆过滤器的总大小

布隆过滤器的实际内存使用量是所选错误率的函数：

最优哈希函数数量为 `ceil(-ln(error_rate) / ln(2))`。

给定所需的 `error_rate` 和最优哈希函数数量时，每个项目所需的 bit 数为 `-ln(error_rate) / ln(2)^2`。因此，过滤器所需总 bit 数为 `capacity * -ln(error_rate) / ln(2)^2`。

* **1%** 错误率需要 7 个哈希函数，每个项目占 9.585 bit。
* **0.1%** 错误率需要 10 个哈希函数，每个项目占 14.378 bit。
* **0.01%** 错误率需要 14 个哈希函数，每个项目占 19.170 bit。

作为比较，当使用 Redis 集合进行成员存在性校验时，所需的内存为：

```text
memory_with_sets = capacity*(192b + value)
```

例如，对于一组 IP 地址，每个项目大约需要 40 字节（320 bit）—— 远高于我们在 0.01% 假正例率的布隆过滤器中所需的 19.170 bit。

## 布隆过滤器 vs. 布谷鸟过滤器

布隆过滤器通常在插入项目时表现出更好的性能和可扩展性（因此，如果您经常向数据集中添加项目，那么布隆过滤器可能是理想的选择）。布谷鸟过滤器在检查操作上更快，并且还允许删除操作。

## 性能

布隆过滤器的插入操作时间复杂度为 O(K)，其中 `k` 是哈希函数的数量。

检查某个项目是否存在的时间复杂度为 O(K) ，对于堆叠的过滤器则为 O(K*n)，其中 n 是堆叠过滤器的数量。

## 学术文献

- [Space/Time Trade-offs in Hash Coding with Allowable Errors](http://www.dragonwins.com/domains/getteched/bbc/literature/Bloom70.pdf) by Burton H. Bloom.
- [Scalable Bloom Filters](https://gsd.di.uminho.pt/members/cbm/ps/dbloom.pdf)

## 参考资料

### 网络研讨会

1. [Probabilistic Data Structures - The most useful thing in Redis you probably aren't using](https://youtu.be/dq-0xagF7v8?t=102)

### 博客文章

1. [RedisBloom Quick Start Tutorial](https://docs.redis.com/latest/modules/redisbloom/redisbloom-quickstart/)
1. [Developing with Bloom Filters](https://redis.io/blog/bloom-filter/)
1. [RedisBloom on Redis Enterprise](https://redis.com/redis-enterprise/redis-bloom/)
1. [Probably and No: Redis, RedisBloom, and Bloom Filters](https://redis.com/blog/redis-redisbloom-bloom-filters/)