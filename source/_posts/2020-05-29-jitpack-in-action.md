---
id: jitpack-in-action
title: "JitPack 真香"
description: "拳打 GPR，脚踹 JCenter"
date: 2020.05.29 19:26
categories:
    - Git
tags: [Maven, Git]
keywords: Git, GitHub, GitHub Packages, GitHub Packages Registry, GPR, JitPack, JCenter, Maven Central, GitLab, Gitee, BitBucket
cover: /contents/jitpack-in-action/cover.png
---

在 [GitHub Packages in Action](https://alphahinex.github.io/2020/01/17/github-packages-in-action/) 中，我们介绍了 GitHub Packages Registry（GPR）的用法。GPR 有其应用场景，但也经常会有蹩手的感觉，尤其是在传错了包，需要邮件联系客服进行删除，而客服又迟迟没有回复的时候……

直到发现了 [JitPack](https://jitpack.io/)，除了真香，找不到别的词来形容了。

## 如何接入 JitPack

只要代码仓库是使用 GitHub，或者 [其他几种常见的 Git 仓库托管服务](https://jitpack.io/docs/#other-git-hosts)，就可以立即接入 JitPack。

以 https://github.com/AlphaHinex/checkstyle-checkers 仓库为例，只需在 https://jitpack.io/ 页面的输入框中，填写 `AlphaHinex/checkstyle-checkers` 并点击 `Look up` 按钮，即可完成接入。

在 JitPack 完成构建之后，可通过 `Release`、`Branch` 甚至 `Commit` 获得不同版本的 jar 包，页面上提供了各种构建工具的接入方式，照着一顿操作就好了。

## 如何从 JitPack 下载依赖

以 Gradle 为例，需要在 `build.gradle` 中添加 JitPack 的仓库地址即可。

```build.gradle
allprojects {
	repositories {
		...
		maven { url 'https://jitpack.io' }
	}
}
```

## 能否从没主动接入的 Git 库直接下载依赖

按照 JitPack 支持的版本规则（Release、Commit、Branch），可直接获得任意公开库的 jar 包，无论该仓库是否进行过主动接入。

## 关于 tag 中的 `v` 前缀

有一个需要注意的点是，在 GitHub 上，推荐使用的 tag 为使用 `v` 前缀的形式：

> Tagging suggestions
>
> It’s common practice to prefix your version names with the letter v. Some good tag names might be v1.0 or v2.3.4.

但在版本号中，一般都使用不带 `v` 的形式。

当未主动在 JitPack 网站上面点击过 Release 版本的 `Get it` 按钮之前，在依赖时，version 只能使用带 `v` 前缀的形式。

![get it](/contents/jitpack-in-action/get-it.jpg)

**如果想要使用不带 v 前缀的格式作为 version，可以找到相应版本，并点击 `Get it` 按钮之后，等待 JitPack 的构建完成（可以从 `Log` 中查看构建日志）。**

## Nexus 能否代理 JitPack 仓库

没问题，注意选择 `Mixed` 类型即可。

![nexus](/contents/jitpack-in-action/nexus-jitpack.png)
