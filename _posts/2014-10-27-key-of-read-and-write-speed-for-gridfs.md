---
layout: post
title:  "MongoDB GridFS 读写性能提升关键点"
description: "提升 GridFS 读写性能的关键，就在于分散对 GridFS 的读写请求至集群内的所有分片上，即不能使用 `{files_id:1}` 来分片。这与官方文档内容完全相悖的矛盾如何能调和呢？"
headline: "Hex"
date:   2014-10-27 11:19:47
categories: NOSQL
tags: [MongoDB, GridFS]
comments: true
featured: true
---

MongoDB(v2.6 current) 官方文档中关于 [Shard GridFS Data Store](http://docs.mongodb.org/manual/tutorial/shard-gridfs-data/) 有如下说明：

> **IMPORTANT**
>
> { files\_id : 1 , n : 1 } and {  files\_id : 1 } are the **only** supported shard keys for the chunks collection of a GridFS store.

即 GridFS 的 chunks collection 只支持 `{files_id:1, n:1}` 和 `{files_id:1}` 作为片键。而 `files_id:1` 是按照 files collection 的 `_id` 升序分片。这样的话无论 MongoDB 集群如何部署以及如何分片，GridFS 的读写压力还是会集中在一个分片上。

**所以提升 GridFS 读写性能的关键，就在于分散对 GridFS 的读写请求至集群内的所有分片上，即不能使用 `{files_id:1}` 来分片。**

这与官方文档内容完全相悖的矛盾如何能调和呢？

经过测试发现，虽然 MongoDB 提供的操作 GridFS 的工具 `mongofiles` 和 `python driver` 都如文档所述，只支持按照 `files_id` 升序分片，但 **`java driver` 却没有这个限制，可以任意设置片键**。

在测试环境中（千兆网络），将 chunks collection 的片键设置为 `{files_id: 'hashed'}`，集群中设置 6 个分片，写入数据均匀分布在了所有分片上。**与使用 `files_id` 升序片键相比，读写性能可提升 2~3 倍，100 并发下读写 1mb 大小文件，写速度可达到 `90.75mb/s`，读速度可达到 `110.62mb/s`**。