---
layout: post
title:  "使用 Clear Key 加密 MP4 视频并播放"
description: "使用 HTML5 技术播放视频简单方便，但同时也将视频源直接暴露了出去。针对一些需要保护以避免用户随意下载的视频，有没有鱼和熊掌兼得之策呢？"
headline: "Hex"
date:   2015-12-25 08:55:47
categories: Web
tags: [HTML5, Video]
comments: true
---

在现代浏览器中，使用 HTML5 技术在线播放视频已不是难事，只需浏览器支持和视频格式兼容即可（参见 [使用 HTML5 技术播放视频](http://alphahinex.github.io/2015/12/11/play-video-with-html5/)）。`<video>` 标签带给我们便利的同时，也将视频源地址直接暴露了出去。虽然 `开放` 是互联网精神之一，但总会有些内容需要限制传播或独家提供。在 HTML5 视频播放技术中，有没有一些可用的版权保护策略呢？

既然 YouTube 已经将默认的播放器切换成了 HTML5，那么答案一定是**肯定的**。让我们从 YouTube 的这篇 [博文](http://youtube-eng.blogspot.jp/2015/01/youtube-now-defaults-to-html5_27.html) 中来找找线索。

YouTube 提到了在这一重大进步中的一些关键技术：

* [Media Source Extensions](https://w3c.github.io/media-source/)：可变比特流（`Adaptive Bitrate(ABR) streaming`）在为用户提供高质量的视频体验中非常重要，它允许我们在面对多变的网络环境时快速且无缝的调整视频分辨率和比特率。`ABR` 能够在总体上减少超过 `50%` 的缓冲，在某些极度拥挤的网络环境下甚至能达到 `80%`。`MediaSource Extensions` 不仅可以在浏览器中使用，还可以在如 `XBox` 和 `PS4` 等游戏终端的直播中使用。

* [Encrypted Media Extensions](https://w3c.github.io/encrypted-media/) 和 `Common Encryption`：过去，视频分发平台（Flash、Silverlight 等）和版权保护技术（Access，PlayReady）是紧密连接的，内容保护深入集成在分发平台甚至文件格式中。`Encrypted Media Extensions` 将内容保护技术与分发平台分离，使得如 YouTube 的内容提供商可以使用同一个 HTML5 视频播放器覆盖大量不同平台。与 `Common Encryption` 技术联合使用可以针对不同平台提供不同的版权保护技术，这使得 YouTube 的视频播放更加平稳快速。

Encrypted Media Extensions
--------------------------
[EME(Encrypted Media Extensions) WTF?](http://www.html5rocks.com/en/tutorials/eme/basics) 简单来说，EME 提供了一套 API 以允许 web 应用能够与内容保护系统进行交互，并使播放加密过的视频和音频成为可能。从 `Extensions` 可以看出，EME 是 `HTMLMediaElement` 标准的扩展，这意味着**浏览器对其的支持不是必须的**。从 `jwplayer` 的网站上我们能够找到[一些浏览器对 `MSE` 和 `EME` 的支持情况](http://www.jwplayer.com/html5/mediasource/)：

![JW Player MSE and EME test](/archives/html5-video/jwplayer-test.png)

不过实际测试中发现这份数据**并不完全准确**，例如在 `win7` 下的 `Chrome41` 就无法播放使用 `Clear Key` 加密的 `MP4` 视频。

EME 实现需要使用下列外部组件：

* **Key System**：一种内容保护（DRM）机制。EME 并没有定义 `Key System` 本身，除了 `Clear Key`。常见的 `Key System` 有 `Clear Key`、`Playready`、`Widevine` 等。
* **Content Decryption Module**：用来播放加密媒体资源的客户端软件或硬件机制。同 `Key System` 一样，EME 也没有定义任何内容解密模块（CDM），但为应用提供了一个接口用来与可用的 CDM 模块交互。
* **License（Key） server**：与 CDM 模块交互并提供解密媒体资源所需的 `key`。与 `license server` 通信是由应用本身负责的。
* **Packaging service**：编码并加密媒体资源以供发布和播放使用。

Common Encryption
-----------------

`Common Encryption` 允许内容提供商按 `容器/编码` 加密并打包内容一次，而后在各种支持的 `Key System`、`CDM` 和 客户端中使用。例如一个使用 `Playready` 加密的视频可以在使用 `Widevine` 内容解密模块从 `Widevine license server` 获得解密 `key` 的浏览器中播放。

Clear Key
---------

 


参考资料
-------

* [YouTube now defaults to HTML5](http://youtube-eng.blogspot.jp/2015/01/youtube-now-defaults-to-html5_27.html)
* [Media Source Extensions](https://w3c.github.io/media-source/)
* [Encrypted Media Extensions](https://w3c.github.io/encrypted-media/)
* [EME WTF?](http://www.html5rocks.com/en/tutorials/eme/basics)
* [Common Encryption](https://gpac.wp.mines-telecom.fr/mp4box/encryption/common-encryption/)
* [Content Creation](https://html5.cablelabs.com/mse-eme/doc/creation.html)
* [Clear Key demo](http://simpl.info/eme/clearkey/)
* [Client Player Applications](https://html5.cablelabs.com/mse-eme/doc/playback.html)