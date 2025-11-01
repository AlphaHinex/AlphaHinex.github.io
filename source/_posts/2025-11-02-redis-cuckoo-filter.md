---
id: redis-cuckoo-filter
title: "【译】Cuckoo filter"
description: "RedisBloom 为 Redis 添加了一组概率数据结构，包括布隆过滤器，布谷鸟过滤器等"
date: 2025.11.02 10:34
categories:
    - Redis
tags: [Redis, Data Structures]
keywords: Cuckoo Filter, RedisBloom, hash, False Positive, error rate, sub-filter, capacity, bucket, fingerprint, expansion factor, max iterations, Bloom, Bloom Filter
cover: /contents/covers/redis-bloom-filter.png
---

- 原文地址：https://redis.io/docs/latest/develop/data-types/probabilistic/cuckoo-filter/
- 源码：https://github.com/redis/docs/blob/64c3a82545b6a441a8b0ccfcc568f5141a5c0523/content/develop/data-types/probabilistic/cuckoo-filter.md

布谷鸟过滤器，与布隆过滤器类似，是 Redis Open Source 中的一种概率数据结构，可让您以非常快速且节省空间的方式检查元素是否存在于集合中，同时还允许删除，并在某些场景下显示出比布隆过滤器更好的性能。

布隆过滤器是一个由哈希函数来决定置真位置的位数组，而布谷鸟过滤器是一个存储元素指纹的桶数组，指纹通过两个哈希函数计算桶位置后存储在其中一个之中。判断元素 `x` 是否存在时，会根据 `x` 的指纹搜索所有可能的桶位置，如果找到相同的指纹则返回 true。布谷鸟过滤器的指纹大小将直接决定误报率。

## 适用场景

**定向广告活动（广告，零售）**

此类应用程序回答了这个问题：用户是否已注册此活动？

为每个活动使用一个布谷鸟过滤器，填充目标用户的 ID。在每次访问时，用户 ID 会被检查是否在其中一个布谷鸟过滤器中。

- 如果是，用户尚未注册该活动。显示广告。
- 如果用户点击广告并注册，则从该布谷鸟过滤器中删除用户 ID。
- 如果否，用户已注册该活动。尝试下一个广告/布谷鸟过滤器。

**折扣码/优惠券验证（零售，在线商店）**

此类应用程序回答了这个问题：此折扣码/优惠券是否已被使用？

使用一个填充所有折扣码/优惠券的布谷鸟过滤器。在每次尝试时，输入的代码会被检查是否在过滤器中。

- 如果否，则优惠券无效。
- 如果是，则优惠券可能有效。检查主数据库。如果有效，则从布谷鸟过滤器中删除为“已使用”。

> 注意：除了这两种场景，布谷鸟过滤器还非常适用于所有布隆过滤器的使用场景。

## 示例

> 你会了解到如何创建一个初始容量为 1,000 个元素的空布谷鸟过滤器，添加元素，检查它们的存在性，再删除它们。尽管 [`CF.ADD`](https://redis.io/docs/latest/commands/cf.add/) 命令可以在过滤器不存在时自动创建一个新的过滤器，但它可能并不适合您的容量需求。最好使用 [`CF.RESERVE`](https://redis.io/docs/latest/commands/cf.reserve/) 命令来设置具有您首选容量的过滤器。

```>_Redis CLI
> CF.RESERVE bikes:models 1000
OK
> CF.ADD bikes:models "Smoky Mountain Striker"
(integer) 1
> CF.EXISTS bikes:models "Smoky Mountain Striker"
(integer) 1
> CF.EXISTS bikes:models "Terrible Bike Name"
(integer) 0
> CF.DEL bikes:models "Smoky Mountain Striker"
(integer) 1
```

## 布隆过滤器 vs. 布谷鸟过滤器

布隆过滤器通常在插入元素时表现出更好的性能和可扩展性（因此，如果您经常向数据集中添加元素，那么布隆过滤器可能是理想的选择）。布谷鸟过滤器在检查操作上更快，并且还允许删除操作。

## 布谷鸟过滤器容量分析

以下是布谷鸟过滤器的主要参数和特性：

- `p` 目标错误率
- `f` 指纹长度（单位：比特）
- `α` 填充率或负载因子 (0≤α≤1)
- `b` 每个桶中的条目数
- `m` 桶的数量
- `n` 存储的元素数量
- `C` 每个元素的平均比特数

让我们从记住布谷鸟过滤器的每个桶可以有多个条目（每个条目存储一个指纹）开始。如果我们最终用指纹占满所有条目，那么我们将没有空槽位来保存新元素，过滤器将被声明为已被填满，因此我们应该始终保持布谷鸟过滤器有一定比例的空闲空间。

由上可知，每个元素的“真实”内存占用，除指纹的大小外，还包括由于保持一定比例的空闲空间而产生的开销。如果 `α` 是负载因子（指纹大小 / 过滤器总大小），`f` 是每个条目存储的指纹比特位数，则均摊后每个元素的空间占用位 `f/α` 比特。

当初始化一个新的布谷鸟过滤器时，您需要选择其容量和桶的数量。

```cli
CF.RESERVE {key} {capacity} [BUCKETSIZE bucketSize] [MAXITERATIONS maxIterations]
[EXPANSION expansion]
``` 

### 选择容量  (`capacity`)

布谷鸟过滤器的容量可通过以下公式计算：

```formula
capacity = n*f/α
```

`n` 是您期望在过滤器中存储的元素数量，`f` 是以比特为单位的指纹长度，一般设置为 `8`，`α` 是填充因子。因此，为了获得过滤器容量，您必须首先选择一个填充因子。填充因子将决定数据的密度，当然也决定内存用量。

容量的数值将被向上取整至最接近的“2 的幂 (2<sup>n</sup>)”。

> 请注意，在布谷鸟过滤器中重复插入相同元素会导致多次添加这些元素，从而使过滤器被填满。

由于布谷鸟过滤器的工作原理，过滤器可能会在达到容量之前就声明自己已满，因此填充率可能永远不会达到 100%。

### 选择桶大小 (`BUCKETSIZE`)

每个桶中的条目数。较高的桶大小值可以提高填充率，但也会导致更高的错误率和稍慢的性能。

```formula
error_rate = (buckets * hash_functions)/2^fingerprint_size = (buckets*2)/256
```

当桶大小为 1 时，填充率为 55%，假阳性错误率为 2/256 ≈ 0.78% **这是您可以实现的最小假阳性率**。更大的桶将线性增加错误率，但也会提高过滤器的填充率。例如，桶大小为 3 时，错误率为 2.34%，填充率为 80%。桶大小为 4 时，错误率为 3.12%，填充率为 95%。

### 选择扩展因子 (`EXPANSION`)

当过滤器自我声明已满时，它将通过生成额外的子过滤器进行自动扩展，这会导致性能下降和错误率增加。新的子过滤器的大小是上一个子过滤器的大小乘以 `EXPANSION`（在过滤器创建时选择）。与桶大小一样，额外的子过滤器线性增加错误率（复合错误率是所有子过滤器错误率的总和）。新子过滤器的大小是最后一个子过滤器的大小乘以扩展因子，这一点非常重要。如果您知道将来必须扩展，最好选择更高的扩展值。默认值是 [`cf-expansion-factor`](https://redis.io/docs/latest/develop/data-types/probabilistic/configuration/#cf-expansion-factor)。

也许您会想：“如果我知道将来会扩展，为什么还要创建一个较小的过滤器并设置较高的扩展率？”答案是：对于需要保留多个过滤器的情况（例如每个用户或每个产品一个过滤器），大多数过滤器将保持较小，但某些活动较多的过滤器将需要扩展。

扩展因子的数值将被向上取整至最接近的“2 的幂 (2<sup>n</sup>)”。

### 选择最大迭代次数 (`MAXITERATIONS`)

`MAXITERATIONS` 决定了为传入指纹找到插槽的尝试次数。一旦过滤器变满，高 `MAXITERATIONS` 值将减慢插入速度。默认值是 [`cf-max-iterations`](https://redis.io/docs/latest/develop/data-types/probabilistic/configuration/#cf-max-iterations)。

### 有趣的事实：

- 先前子过滤器中未使用的容量会在可能的情况下自动使用。
- 过滤器最多可以增长 [`cf-max-expansions`](https://redis.io/docs/latest/develop/data-types/probabilistic/configuration/#cf-max-expansions) 次。
- 您可以删除元素以保持在过滤器限制内，而不是重建过滤器。
- 多次添加相同元素将创建多个条目，从而填满过滤器。

## 性能

向布谷鸟过滤器添加元素的时间复杂度为 O(1)。

同样，检查元素和删除元素的时间复杂度也为 O(1)。

## 学术文献

- [Cuckoo Filter: Practically Better Than Bloom](https://www.cs.cmu.edu/~dga/papers/cuckoo-conext2014.pdf)