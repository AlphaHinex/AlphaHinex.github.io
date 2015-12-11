---
layout: post
title:  "使用 HTML5 技术播放视频"
description: "HTML5 定义了通过 video 元素在网页中嵌入视频的标准方式。尽管这种方式仍在不断进化中，也暂时不能做到在任何浏览器下都运转良好，但现代浏览器对其支持的趋势及程度还是很值得期待的，即便在一些不支持的环境下，也有替代方案可供选择。本文主要基于 Dive Into HTML5 # Video on the Web，并对一些内容有更新和补充。"
headline: "Hex"
date:   2015-12-11 10:34:47
categories: Web
tags: [HTML5, Video]
comments: true
---

随着 [HTML5 标准](https://html.spec.whatwg.org/multipage/) 的定稿以及在线视频巨头 `YouTube` 在 `2015` 年初宣布[默认使用 HTML5 视频播放器](http://youtube-eng.blogspot.jp/2015/01/youtube-now-defaults-to-html5_27.html)，主流的在线视频播放技术正在逐步由 `flash` 播放器向 `HTML5` 播放器过渡。国内主流的在线视频网站，如优酷、土豆、爱奇艺、网易公开课等，依然在使用 `flash player`，而国内一些先进的视频直播网站，如 [Shou.tv](https://shou.tv/) 已试水 HTML5 技术。

HTML5 定义了通过 `<video>` 元素在网页中嵌入视频的标准方式。尽管这种方式仍在不断进化中，也暂时不能做到在任何浏览器下都运转良好，但现代浏览器对其支持的趋势及程度还是很值得期待的，即便在一些不支持的环境下，也有替代方案可供选择。

让我们先来看看当前各类浏览器对 video 元素的支持情况：

![video-element](/archives/html5-video/video-element.png)
[数据来源](http://caniuse.com/#feat=video)

同是支持 `<video>` 元素，不同的浏览器所支持的视频格式还是有差异的。让我们先来了解一下常见的视频格式。

视频容器
-------

我们常见的视频格式有 `avi` 或 `mp4` 等，这些所谓的视频格式，实际上指的只是视频容器的格式。就像 `zip` 格式的压缩包里面可以放置任意类型的文件一样，视频容器格式可以简单理解为只定义了如何将视频及音频流数据存储在容器文件中。实际情况会比这更复杂一些，因为不是所有的视频流都可以兼容存入任意视频容器中。

一个视频文件通常包含多个轨道（track）—— 一个视频轨道（不包含声音），叠加一个或多个音频轨道（没有图像）。轨道之间通常是相互关联的。一个音频轨道中会包含一些标记，用来同步声音和图像。每个轨道可以有自己的元数据信息，如视频轨道的画面比例或音频轨道的语言。视频容器同样可以有元数据，如视频的标题、封面等等。

视频容器的格式有很多，常见的包括：

* [MPEG 4](http://en.wikipedia.org/wiki/MPEG-4_Part_14)，通常是扩展名为 `.mp4` 或 `.m4v` 的文件。`MPEG 4` 容器是基于苹果之前的 `QuickTime` 容器格式（`.mov`）而来的。
* [Ogg](http://en.wikipedia.org/wiki/Ogg)，扩展名通常为 `.ogg` 或 `.ogv`。 Ogg 是一个开放的标准，开源友好，不受任何已知的专利限制。Firefox 3.5+，Chrome 4+ 以及 Opera 10.5+ 无需插件原生支持。Ogg 容器格式，包含 Ogg 视频（名为 `Theora`）和 Ogg 音频（名为 `Vorbis`）。Ogg 格式是大多数 Linux 发行版的开箱即用视频格式，并可以通过著名的 [VLC](http://www.videolan.org/vlc/) 播放器在各个平台上进行播放。
* [WebM](http://www.webmproject.org/)，扩展名 `.webm`。WebM 是一种无版税，开源友好的，专为 HTML5 设计的视频压缩格式，使用 `VP8` 视频编码和 `Vorbis` 音频编码。在技术上类似 [Matroska](https://en.wikipedia.org/wiki/Matroska) 格式（`.mkv`）。同样无需插件，在当前版本的 Chromium，Chrome，Firefox 和 Opera 上原生支持。
* [Flash Video](http://en.wikipedia.org/wiki/Flash_Video) (`.flv`) 是 Adobe Flash Player 所使用的格式。在近期的 Flash Player 版本中也加入了对 MPEG 4 容器的支持。
* [ASF](http://en.wikipedia.org/wiki/Advanced_Systems_Format) (`.asf`) 和 [Audio Video Interleave](http://en.wikipedia.org/wiki/AVI) (`.avi`) 是微软发明的格式，早期使用较多。

视频编解码器
----------

当我们观看视频时，视频播放器至少同时做了三件事：

1. 解析视频容器格式，找到可用的视频及音频轨道，以及他们是如何存放在容器内的，以便获得解码所需数据
2. 解码视频流，在屏幕上显示一系列的图像
3. 解码音频流，在扬声器中播放声音

编解码器是指对视频进行编码和解码的算法。视频按照编码算法被转换成二进制流文件进行存储和分发，视频播放器按照解码算法对视频流进行解码，并将一系列图像或帧显示在屏幕上。大多数现代视频编解码器都竭尽其能地减少播放下一帧所需的信息。例如，为了避免保存每一帧图像（类似截屏），编码时将只会存储没帧之间的差异内容。多数视频也不是每一帧都与上一帧完全不同，这边使得更高的压缩率和更小的文件尺寸成为可能。

编解码器分为有损和无损两种类型。无损类型的视频尺寸对于互联网来说还是太大了，所以我们这里只关注有损类型的视频编码。有损类型的视频编解码器，意味着对视频编码总会伴随着不可挽回的原始数据丢失。就像翻录卡带一样，每次视频编码都会造成源视频信息的丢失以及视频质量的下降。多次编码后视频可能会有明显的卡顿，尤其是动作很多的视频（如动作片）。然而好的方面是，有损的视频编码格式能够提供惊人的压缩比例，并通过一些播放时的优化技术，使肉眼很难察觉到这些信息的损失。

常见的视频编解码器有 `H.264`、`Theora` 和 `VP8`。

### H.264

[H.264](http://en.wikipedia.org/wiki/H.264)，即 `MEPG-4 part 10`、`MPEG-4 AVC`、`MPEG-4 Advanced Video Coding`。 H.264 是 [MPEG 组织](http://en.wikipedia.org/wiki/Moving_Picture_Experts_Group) 开发并于 2003 年标准化的编码格式。它致力于为低带宽、低性能 CPU 设备（如手机），高带宽和高性能 CPU 设备（如现代桌面电脑），以及所有在此之间的设备，提供单独的一种编解码器。为了实现这个目标， H.264 标准区分了不同的 [profiles](http://en.wikipedia.org/wiki/H.264#Profiles)，每个配置（`profile`）都定义了不同的文件大小和可选特性。更高的配置在尽可能小的文件尺寸上使用更多的可选特性，提供更好的视频质量，更长的编码时间以及在实时播放时需要更强劲的 CPU 来解码。

概括来说，`iPhone` 支持 `Baseline` 配置，`AppleTV` 支持 `Baseline` 和 `Main` 配置，Flash 和台式机支持 `Baseline`、`Main` 和 `High` 配置。`H.264` 同时也是蓝光标准授权的编解码器，蓝光光盘通常使用 `High` 配置。

大多数的非 PC 设备（如 `iPhone` 和蓝光播放器）在播放 `H.264` 视频时，实际是由专用芯片负责解码，因为他们的 CPU 并没有足够的性能以支持视频的实时播放。目前甚至一些低端的桌面显卡也能够支持硬件解码 `H.264`。有很多 `H.264` 的编码器，包括开源的 [x264 library](http://www.videolan.org/developers/x264.html)。`H.264` 视频可以嵌入到大多数流行视频容器格式中，包括 `MP4` 和 `MKV`。

**H.264 标准是需要支付专利许可费用的**，专利许可的主要来源是 [MPEG LA 组织](http://www.mpegla.com/)。[2010年8月26日，`MPEG LA` 组织宣布使用 `H.264` 编码的网络视频对**最终用户永久免费**](https://en.wikipedia.org/wiki/H.264/MPEG-4_AVC#Patent_licensing)。但是离开网络使用到有关 `H.264` 的产品或服务，还是需要支付费用的。

![MPEG-4/H.264 video format](/archives/html5-video/h264.png)
[数据来源](http://caniuse.com/#feat=mpeg4)

### Theora

[Theora](http://en.wikipedia.org/wiki/Theora) 由 [VP3 编解码器](http://en.wikipedia.org/wiki/Theora#History) 演化而来，随后由 [Xiph.org 基金会](http://xiph.org/) 开发维护。**Theora 开源且免费**，不过这套标准于 `2004` 年即处于“冻结”状态，`Theora` 项目（包含开源的视频编码及解码）只在 `2008` 年发布了初版，`2009` 年发布了 `1.1.1` 稳定版，最近一次发布的 `1.2.0 Alpha 1` 预览版也已是 5 年前的事情了。

`Theora` 视频可以嵌入到任何视频容器格式内，不过最常见的还是 `Ogg` 容器。所有主流的 Linux 发行版都默认支持 `Theora` 格式，Firefox、Chrome 和 Opera 的当前版本都对其提供了原生支持。在安装了 Xiph.org 提供的开源解码软件后，在 [Windows](http://www.xiph.org/dshow/) 和 [Max OS X](http://xiph.org/quicktime/) 也可以播放 `Theora` 视频。

![Ogg/Theora video format](/archives/html5-video/theora.png)
[数据来源](http://caniuse.com/#feat=ogv)

### VP8

[VP8](http://en.wikipedia.org/wiki/VP8) 最早由 `On2` 开发，2010 年，Google 收购 `On2` 后发布了这个视频编解码器的规范和开源的编码解码示例。在经过一些争论之后，最终 VP8 的授权确认为一个**开放源代码授权**。

`WebM` 项目和 `VP8` 同时在 2010 年 5 月发表，Mozilla、Opera、Google 和其他 40 多家厂商共同协助发展，目的是让 VP8 成为 HTML5 的视频格式。 WebM 为一个容器格式，视频部分使用 VP8，声音格式则是使用 `Vorbis`。

![WebM video format](/archives/html5-video/vp8.png)
[数据来源](http://caniuse.com/#feat=webm)

音频编解码器
----------

同视频编解码器一样，音频编解码器是指对音频流编码和解码的算法。音频编解码器也分为有损和无损两种。无损的音频对互联网来说同样太大，所以我们只关注有损音频编解码。

在播放视频时，音频编解码器起到的作用是解码音频数据流，并将其通过扬声器播放出来。同有损编码视频一样，有很多办法来减小音频流的尺寸。在 `录音 - 编码 - 解码 - 播放` 的过程中，有大量信息被丢弃。不同的音频编解码器丢弃的内容不同，但他们都能做到欺骗你的耳朵，让你察觉不到这些损失。

有一个只有在音频中才存在的概念：`声道`。声音通过扬声器来播放，普通的桌面电脑可能拥有左右两个扬声器。环绕立体声系统拥有 6 个甚至更多的扬声器。一个扬声器可以用来播放原始音轨中的一个特定声道。当你坐在 6 个扬声器之中，被 6 个独立声道播放出的声音所环绕，你的大脑会同步它们并使你产生出一种身临其境的感觉。

大部分通用性的音频编解码器能够处理两个声道。在录音时，声音被切分成左右两个声道；在编码时，两个声道被存储在同一个音频流中；解码时，两个声道解译后被送至不同的扬声器来播放。一些音频解码器能够处理两个以上的声道，并且加以区分，以便在播放时能够通过恰当的扬声器来播放。

常用的音频编解码器有：`MP3`、`AAC` 和 `Vorbis`。

### MPEG-1 Audio Layer 3

[MPEG-1 Audio Layer 3](http://en.wikipedia.org/wiki/MPEG-1_Audio_Layer_3) 即 `MP3`。MP3 **最多能容纳两个声道**，可以编码为不同比特率：64 kbps, 128 kbps, 192 kbps, 甚至从 32 到 320 的各种速率。更高的比特率意味着更大的文件尺寸和更好的音频质量，不过音频质量和比特速率不是正比关系。128 kbps 要比 64 kbps 的音质水平提升两倍以上，但 256 kbps 并不能达到 128 kbps 的两倍音质。MP3 支持**可变比特率编码**，这意味着一个音频流的某一部分可能会比另一部分的压缩率高。例如交响乐在演奏时使用高比特率，而在章节间的静默阶段使用低比特率。MP3 同样也支持**固定比特率编码**。

MP3 标准没有确切定义如何编码，但却明确定义了如何解码；不同的编码器使用不同方式导致编码结果大相径庭，但它们需要保证编码结果都可以使用同一个播放器来解码并播放。开源的 [LAME 项目](http://lame.sourceforge.net/) 是免费编码器的首选。

MP3 格式（于 1991 年标准化）是**受版权约束**的，这也解释了为什么 `Linux` 系统不能直接播放 MP3 文件。官方是要求 MP3 编解码器购买授权的，但 MP3 的版权非常混乱和碎片化，这也导致 MP3 成为**事实上的免费格式**。到 2015 ~ 2017 年， MP3 的专利也基本都到期了，也将成为公共领域的东西。所有随身听都可以播放 MP3 文件，MP3 音频流也可以嵌入至任意视频容器中。Adobe Flash 可以播放独立的 MP3 文件，也可以播放在 MP4 视频容器中的 MP3 音频流。

![MP3 audio format](/archives/html5-video/mp3.png)
[数据来源](http://caniuse.com/#search=mp3%20audio)

### Advanced Audio Coding

[Advanced Audio Coding](http://en.wikipedia.org/wiki/Advanced_Audio_Coding) 通常简称为 `AAC`。标准化于 1997 年的这个规范，因苹果选择其作为 `iTunes Store` 的默认格式而声名鹊起。`AAC` 格式是**需要收取版权费用**的，收费标准可在 [这里](http://www.vialicensing.com/licensing/aac-fees.aspx) 查看。**终端用户编码器和/或译码器产品制造商或开放商需要获得 AAC 专利授权。以 AAC 格式编码发布的比特流 —— 无论是通过广播、网络数据流或是通过物理媒体提供 —— 都没有专利授权费**。

`AAC` 被设计为在使用与 MP3 相同的比特率时提供更好的音质，并且可以使用任意比特率来编码（MP3 被限定在最高 320 kbps）。`AAC` 编码的音频**最多可支持 48 个声道**，虽然实际中并没有人需要使用这么多声道。`AAC` 格式还有一个区别于 MP3 的地方时，它同 `H.264` 一样，定义了多种**配置**（`profile`）。低端配置用以在计算资源有限的设备上实时播放，高端配置提供更好的音质，同时需要更长的编解码时间。

当前所有的苹果产品，包括 `iPod`、`AppleTV` 和 `QuickTime` 都支持播放在 MP4 视频容器中的 `ACC` 格式的固定配置音频流。`Adobe Flash` 通开源的 `MPlayer` 和 `VLC` 播放器一样，支持 MP4 容器中的任意配置的 `AAC` 格式音频。编码方面，`FAAC` 类库是一个可选的开源类库，同时还有 `mencoder` 和 `ffmpeg`。

![AAC audio file format](/archives/html5-video/aac.png)
[数据来源](http://caniuse.com/#search=AAC%20audio)

### Vorbis

[Vorbis](http://en.wikipedia.org/wiki/Vorbis) 通常被称作 `Ogg Vorbis`，不过从技术角度来说这个称呼是有误的。`Ogg` 只是一个视频容器格式，`Voribs` 音频流也可以被嵌入到其他视频容器中。`Vorbis` 是**开放、免费且无专利限制**的，因此所有主要的 `Linux` 发行版及移动设备都可以通过开源的 [Rockbox](http://www.rockbox.org/) 固件为其提供支持。`Vorbis` 格式音频流通常被嵌入在 `Ogg` 或 `WebM` 容器中，但它们同时也可以被嵌入在 `MP4` 或 `MKV` 容器里（甚至经过一些改动后，也可以嵌入在 [AVI](http://www.alexander-noe.com/video/amg/) 中）。`Vorbis` 支持**任意数量的声道**。

开源的 `Vorbis` 编码器和解码器有很多，包括 [OggConvert](http://oggconvert.tristanb.net/)（编码）、[ffmpeg](http://www.ffmpeg.org/)（解码）、[aoTuV](http://www.geocities.jp/aoyoume/aotuv/)（编码）和 [libvorbis](http://downloads.xiph.org/releases/vorbis/)（解码）。

![Ogg Vorbis audio format](/archives/html5-video/vorbis.png)
[数据来源](http://caniuse.com/#search=vorbis)

那么问题来了：我们该用哪个？
-----------------------

看了上面的介绍我们发现：

* 没有任何一种容器和编解码器的组合能够在所有的 HTML5 浏览器中播放。
* 并且这种情况在可预见的未来并不会有明显的改善。

要想让你的视频在任意设备和平台上播放，你需要对视频**编码**，**并且不止一次**。

针对不支持 `<video>` 元素的“上古”浏览器，可以继续沿用当前国内主流的 `Adobe Flash Player` 方案。在 Adobe 的 [帮助文档](https://helpx.adobe.com/flash/kb/supported-codecs-flash-player.html) 中我们能够找到 `Flash Player` 支持的音视频编解码器：

![Supported codecs](/archives/html5-video/flash-player.png)

仔细观察之前各主流浏览器对音视频编码格式及容器格式的支持情况可以发现，`MP4(H.264+AAC)` 或 `MP4(H.264+MP3)` 已经可以覆盖 `90%` 以上的浏览器用户。而剩余的用户使用的浏览器又以 `IE9` 之前版本的 `IE` 及老版本的 Firefox 和 Opera 居多。这恰巧又是 `Flash Player` 的“势力范围”。支持 `MP4(H.264+AAC)` 的最低版本 `Flash Player v9.0.115.0` 于 2007 年底发布，距今也已近 **8 年**。

**有理由相信，使用 `MP4(H.264 + MP3/AAC)` 的容器和编码组合，与 `HTML5 播放器 + Adobe Flash Player` 的播放组合，可以满足现今绝大多数桌面及移动终端视频播放的需求。这样便可以只编码出一种视频格式（MP4），节省大量视频编码的耗时以及存储空间。**

怎么用？
------

HTML5 提供了两种使用 `<video>` 元素的方式。在只有一个视频文件的时候，可以像 `<img src="...">` 一样，直接使用 `<video>` 元素的 `src` 属性，如：

    <video src="mov.mp4"></video>
    
这就是你要做的全部。不过就像 `<img>` 元素一样，你应该总是在 `<video>` 元素中指定视频的宽高属性。这个宽高属性值应该与你在进行视频编码时指定的值一致。不用担心视频的某一维度会比指定值小，你的浏览器能够将其自动居中，并保证不会超出指定区域。

    <video src="mov.mp4" width="480" height="640"></video>
    
默认情况下，`<video>` 元素不会显示任何播放控制器。你可以通过 `HTML`、`CSS` 和 `JavaScript` 创建属于你自己的播放控制器。`<video>` 元素包含 [播放和暂停](http://www.whatwg.org/specs/web-apps/current-work/multipage/video.html#playing-the-media-resource) 方法，可读写的 [当前时间](http://www.whatwg.org/specs/web-apps/current-work/multipage/video.html#dom-media-currenttime)、[音量](http://www.whatwg.org/specs/web-apps/current-work/multipage/video.html#dom-media-volume) 和 [静音](http://www.whatwg.org/specs/web-apps/current-work/multipage/video.html#dom-media-muted) 属性。所以你拥有了创建一个自己的播放界面的所有内容。

如果你不想自己构建一个播放器界面，也可以让浏览器显示其内置的控制器。只要增加一个 `controls` 属性即可：

    <video src="mov.mp4" width="480" height="640" controls></video>
    
还有两个有用的属性：`preload` 和 `autoplay`。设置 `preload` 属性后浏览器会在页面加载完成后自动开始下载视频文件。当视频文件只是一个附加材料并不会有很多人观看时，还可以将 `preload` 设置为 `none` 以告知浏览器减轻网络压力。

`autoplay` 属性会在页面加载后自动开始视频文件的下载，并尽快地开始播放视频。这是个有人爱有人恨的特性，但 HTML5 定义这样一个属性是很重要的。一些人希望他们的视频自动播放，即便这样会使访问者感到反感。如果 HTML5 没有定义一个标准的方式来自动播放视频，他们则会通过 JS 来达到目的（例如在 `window` 的 `load` 事件中直接调用 `play()` 方法）。这会使访问者难以应对。而现在则可以通过简单的浏览器插件或脚本告诉浏览器“忽略 `autoplay` 属性，我不想视频自动播放”。

当存在多个视频文件以满足浏览器兼容性问题时，HTML5 也提供了一种方式来添加所有这些视频：`<source>` 元素。每个 `<video>` 元素可以包含多个 `<source>` 元素。浏览器会在视频源列表中从上之下，选择第一个能够播放的视频。

这同时带来了另一个问题：浏览器如何知道哪个视频是它所支持的？在最坏的情况下，浏览器会加载每个视频并且尝试播放。这是非常浪费带宽资源的。但如果你能够直接告诉浏览器每个视频的编码信息，浏览器则可以通过该信息进行判断，以此节省大量网络带宽资源。可以通过 `<source>` 元素的 `type` 属性来设置视频编码信息：

    <video width="480" height="640" controls>
      <source src="mov.mp4" type="video/mp4; codecs=avc1.42E01E, mp4a.40.2">
      <source src="mov.webm" type="video/webm; codecs=vp8,vorbis">
      <source src="mov.ogv" type="video/ogg; codecs=theora,vorbis">
    </video>
    
`type` 属性的值看起来很复杂。它是由三部分组成的：视频容器格式，视频编码和音频编码。例如 `video/mp4` 代表视频容器格式是 MP4 格式。不过严格来说，这里使用的是视频容器格式的 `MIME` 类型（`video/mp4`、`video/webm`、`video/ogg`）。`mov.mp4` 的编解码器设置也很复杂，它代表了 `H.264` 使用的是 `baseline` 配置，`AAC` 使用的也是低复杂度的配置。更多的 `type` 属性参数可以在 [这里](https://wiki.whatwg.org/wiki/Video_type_parameters) 找到。

还有一点需要注意：**视频文件必须在服务端设置恰当的 MIME 类型**，否则你可能会经常遇到类似视频文件在你本地环境一切正常，但在实际产品中无法播放的情况。仅在 `<source>` 元素的 `type` 属性中设置是不够的，你还需要为 web 服务器 HTTP 头中的 Content-Type 设置上 MIME 类型。

当遇到不支持 `<video>` 标签的那不足一成的浏览器时，只要你已经编码好了 `H.264` 格式的视频，即可通过基于 Flash 技术的视频播放器来将视频播放出来。可选的开源播放器有很多，`CC` 协议的 [jwplayer](https://github.com/jwplayer/jwplayer)、`GPL` 协议的 [flowplayer](https://github.com/flowplayer/flowplayer) 和 `Apache` 协议的 [video-js-swf](https://github.com/videojs/video-js-swf) 等。

`Flash Player` 不认识 `<video>` 元素，也不会自动将 `<video>` 标签转换成 `Flash object`。但 HTML5 在设计时已经考虑到了这一点，你可以在 `<video>` 元素内部嵌入一个 `<object>` 元素。那些不支持 HTML5 视频播放的浏览器会忽略 `<video>` 标签，并直接渲染其中的 `<object>` 元素，借此调用 `Flash` 插件来播放视频。而支持 HTML5 视频播放的浏览器会在 `<video>` 元素中找到可播放的视频，并忽略其中的 `<object>` 元素。这些都是由 HTML5 规范和浏览器所支持的，无需额外的 `JS` 代码。

DEMO
----

下面是一段示例代码：

    <video width="480" height="640" preload controls>
      <source src="/archives/html5-video/mov.m4v" type="video/mp4; codecs=avc1.42E01E, mp4a.40.2">
      <object width="480" height="640" type="application/x-shockwave-flash" data="http://releases.flowplayer.org/swf/flowplayer-3.2.16.swf">
        <param name="movie" value="http://releases.flowplayer.org/swf/flowplayer-3.2.16.swf">
        <param name="allowfullscreen" value="true">
        <param name="flashvars" value="config={'clip': {'url': 'http://alphahinex.github.io/archives/html5-video/mov.m4v', 'autoPlay': false, 'autoBuffering': ture}}">
      </object>
    </video>

<video width="480" height="640" preload controls>
  <source src="/archives/html5-video/mov.m4v" type="video/mp4; codecs=avc1.42E01E, mp4a.40.2">
  <object width="480" height="640" type="application/x-shockwave-flash" data="http://releases.flowplayer.org/swf/flowplayer-3.2.16.swf">
    <param name="movie" value="http://releases.flowplayer.org/swf/flowplayer-3.2.16.swf">
    <param name="allowfullscreen" value="true">
    <param name="flashvars" value="config={'clip': {'url': 'http://alphahinex.github.io/archives/html5-video/mov.m4v', 'autoPlay': false, 'autoBuffering': ture}}">
  </object>
</video>

参考资料
-------

* [Video on the web](http://diveintohtml5.info/video.html)
* [HTML5 Specification](https://html.spec.whatwg.org/multipage/)
* [Dive into HTML5](http://diveintohtml5.info/index.html)
* [The Technology Behind Shou.TV](https://blog.shou.tv/the-technology-behind-shoutv)