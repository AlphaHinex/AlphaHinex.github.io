---
layout: post
title:  "MongoDB GridFS 读写性能提升关键点"
description: "提升 GridFS 读写性能的关键，就在于分散对 GridFS 的读写请求至集群内的所有分片上，即不能使用 `{files_id:1}` 来分片。这与官方文档内容完全相悖的矛盾如何能调和呢？"
headline: "Hex"
date:   2014-10-27 11:19:47
categories: NOSQL
tags: [MongoDB, GridFS]
comments: true
---

Content of post post