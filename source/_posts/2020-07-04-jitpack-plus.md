---
id: jitpack-plus
title: "JitPack 真香 Plus"
description: "冷饭加热水，补充说明一下多模块的用法"
date: 2020.07.04 19:34
categories:
    - Git
tags: [Maven, Git]
keywords: Git, GitHub, GitHub Packages, GitHub Packages Registry, GPR, JitPack, JCenter, Maven Central, GitLab, Gitee, BitBucket
cover: /contents/jitpack-in-action/modules.png
---

在 [JitPack 真香](https://alphahinex.github.io/2020/05/29/jitpack-in-action/) 中，介绍了 JitPack 的基本用法。

当一个仓库中对应多个模块，每个模块需发布成一个独立 jar 包时，依赖的坐标有略微调整：

||单模块|多模块|
|:--|:--|:--|
|groupId|com.github.User|com.github.User.Repo|
|artifactId|Repo|Module|
|version|Tag|Tag|

> 多模块时，依然可以通过单模块的依赖语法形式，获得该项目的所有模块：
>
>     implementation 'com.github.User:Repo:Tag'

相关文档可见 [Multi-module projects](https://jitpack.io/docs/BUILDING/#multi-module-projects)。

在 [JitPack](https://jitpack.io/) 界面完成构建之后，可以直接从界面获得所有模块的依赖坐标：

![modules](/contents/jitpack-in-action/modules.png)
