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

虽然 EME 没有定义 DRM 功能，但规范中要求所有支持 EME 的浏览器**必须实现** `Clear Key`。使用这套系统，媒体资源可以使用一个 `key` 来加密，在播放时只需简单的提供这个 `key` 即可。Clear Key 可以构建至浏览器中：它甚至不需要一个单独的解密模块。

尽管不容易被用于许多类型的商业内容，Clear Key 可以与所有支持 EME 的浏览器完全兼容。它也可以用来测试 EME 的实现和应用，甚至可以直接提供 key 以免去授权服务器。在 [simpl.info/ck](http://simpl.info/eme/clearkey) 有一个简单的演示。演示中的视频使用的是加密过的 `WebM` 格式。

要加密 WebM 视频并非易事，目前的一个可用方案是使用 `webm-crypt` 模块。按照 [How to build and use webm_crypt](https://docs.google.com/document/d/17d6_KX5jX0gY1ygYbjqOEdVzuUGkPO53wL8t40dMGeQ/edit?usp=sharing) 中的步骤来看，为了使用这个模块你需要编译整个 `chrome`，[Docker Hub](https://hub.docker.com/) 上的编译好的 chrome 镜像体积有 **20G+** 的规模。

相比之下，[Cable Labs](http://www.cablelabs.com/) 提供的针对 `MP4` 的解决方案则简便许多。

用 Clear Key 加密 MP4 并在浏览器中播放
----------------------------------

终于到了今天的重头戏，先来看下 [Cable Labs MSE-EME Overview](https://html5.cablelabs.com/mse-eme/doc/overview.html) 中的方案总览：

![EME Tools Overview](https://html5.cablelabs.com/mse-eme/doc/images/EMETools.png)

总体方案分为两部分：加密内容的创建和内容播放。

* [加密内容的创建](https://html5.cablelabs.com/mse-eme/doc/creation.html)：包括对原始视频的转码以获得 `MP4(H.264/AAC)` 格式视频；视频内容加密；DASH 分割及打包。
* [内容播放](https://html5.cablelabs.com/mse-eme/doc/playback.html)：在浏览器中播放加密并 DASH 视频。

### Dynamic Adaptive Streaming over HTTP (DASH)

`DASH`（即 `MPEG-DASH`）设计用来最大限度的满足在实际环境中的媒体内容流播放及下载需求。很多其他技术也在做着类似的实行 —— 例如苹果的 [HTTP Live Streaming(HLS)](https://en.wikipedia.org/wiki/HTTP_Live_Streaming) 和微软的 [Smooth Streaming](https://en.wikipedia.org/wiki/Adaptive_bitrate_streaming#Microsoft_Smooth_Streaming) —— 但 DASH 是唯一的一个基于开放标准的使用 HTTP 提供可变比特率流技术。DASH 已经应用在 YouTube 等网站上。

这与 EME 和 MSE 有什么关系？基于 MSE 的 DASH 实现能够解析清单（`mpd` 文件），下载恰当比特率的视频片段，并将其提供给 `<video>` 元素，这些都是在现有的 HTTP 之上完成的。换句话说，DASH 使商用内容提供商能够提供可变比特率的受保护内容。

### 所需工具

* [ffmpeg](https://github.com/FFmpeg/FFmpeg)：视频转码，将源视频格式转换为 MP4(H.264/AAC)。
* [mse-eme](https://github.com/cablelabs/mse-eme)：Cable Labs 提供的相关工具集合，使用其中的 Clear Key 加密文件生成器来生成加密用文件。
* [MP4Box](https://github.com/gpac/gpac)：GPAC 项目中的 MP4Box 工具可用来对 MP4 视频进行加密及 DASH。
* [dash.js](https://github.com/Dash-Industry-Forum/dash.js)：用来在浏览器中播放 DASH 视频。

上述工具除 `dash.js` 外，基本都需要安装，可以自行按照官网的说明来安装，也可以直接使用我组装好的这个 [docker 镜像](https://hub.docker.com/r/alphahinex/try-docker/)，使用方式为：
    
    # 拉取镜像
    $ docker pull alphahinex/try-docker:vc
    # 交互模式运行镜像，并将容器命名为 vc
    $ docker run --name vc -v /local/folder:/docker/folder -t -i alphahinex/try-docker:vc /bin/bash
    # 查看 ffmpeg 信息
    root@57ec3690605c:/usr/local# ffmpeg -version
    # 查看 MP4Box 信息
    root@57ec3690605c:/usr/local# MP4Box -version
    # 查看 clearkey 加密文件生成工具信息
    root@57ec3690605c:/usr/local# java -jar mse-eme/create/encrypt/clearkey/cryptgen/clearkey.jar -help
    # 退出容器
    root@57ec3690605c:/usr/local# exit
    
各个工具的具体参数请参考其帮助手册。好，让我们找个视频来试一下。

### 实际例子

引用 [html5rocks](http://www.html5rocks.com) 上的这个 [WebM 视频](http://www.html5rocks.com/en/tutorials/video/basics/devstories.webm) 作为源视频，将其转换为 `MP4` 并使用 `Clear Key` 加密，之后使用 HTML5 播放。

    # 交互模式启动之前创建的容器 vc
    $ docker start -i vc
    # 假定源文件在容器中的路径为 /usr/local/video/devstories.webm
    root@57ec3690605c:/usr/local/video# ffmpeg -i devstories.webm -codec:v libx264 -x264opts keyint=48:min-keyint=48:no-scenecut -codec:a aac -strict -2 devstories.mp4
    # 可通过 ffprobe 或 MP4Box 查看转换后的视频信息
    root@57ec3690605c:/usr/local/video# ffprobe -i devstories.mp4
    root@57ec3690605c:/usr/local/video# MP4Box -info devstories.mp4
    # 生成加密文件，key id 和 key 随便写，都是 16 位的 16 进制数，需要记住其转换成的 Base64 字符串
    root@57ec3690605c:/usr/local/video# java -jar /usr/local/mse-eme/create/encrypt/clearkey/cryptgen/clearkey.jar 1:20212223-2425-2627-2829-2A2B2C2D2E2F=15161718191A1B1C1D1E1F2021222324 2:12131415-1617-1819-1A1B-1C1D1E1F2021=25262728292A2B2C2D2E2F3031323334 -out devstories_drm.xml
    Ensure the following keys are available to the client:
    	202122232425262728292a2b2c2d2e2f : 15161718191a1b1c1d1e1f2021222324 (ICEiIyQlJicoKSorLC0uLw : FRYXGBkaGxwdHh8gISIjJA)
    	12131415161718191a1b1c1d1e1f2021 : 25262728292a2b2c2d2e2f3031323334 (EhMUFRYXGBkaGxwdHh8gIQ : JSYnKCkqKywtLi8wMTIzNA)
    # 使用上一步生成的 devstories_drm.xml 加密 MP4
    root@57ec3690605c:/usr/local/video# MP4Box -crypt devstories_drm.xml devstories.mp4 -out devstories_enc.mp4
    # 可再次通过 MP4Box -info devstories_enc.mp4 看到两个轨道都已被加密
    # dash
    root@57ec3690605c:/usr/local/video# MP4Box -dash 10000 -profile onDemand -out devstories_enc.mpd devstories_enc.mp4#video devstories_enc.mp4#audio
    
完成上述步骤后，会得到三个文件：`devstories_enc.mpd`、`devstories_enc_track1_dashinit.mp4`、`devstories_enc_track2_dashinit.mp4`。从 `mpd` 中可以看到视频清单和加密使用的 `key id`。

<script src="http://127.0.0.1:4000/archives/html5-video/dash.all-1.5.1.js"></script>
<script>
function init() {
  var video,context,player;
  video = document.querySelector("video");
  context = new Dash.di.DashContext();
  player = new MediaPlayer(context);
  player.startup();
  player.attachView(video);
  player.setAutoPlay(true);
  player.attachSource("/archives/html5-video/devstories_enc.mpd", null, {
    "org.w3.clearkey": {
      "clearkeys": {
        "ICEiIyQlJicoKSorLC0uLw": "FRYXGBkaGxwdHh8gISIjJA",
        "EhMUFRYXGBkaGxwdHh8gIQ": "JSYnKCkqKywtLi8wMTIzNA"
      }
    }
  });
}
</script>

<div>
  <button onclick="init()">初始化并播放</button>
  <video width="640" height="360" controls="true" poster="/archives/html5-video/poster.png"></video>
</div>


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
* [Working with MP4Box](https://www.radiantmediaplayer.com/working-with-mp4box.html)