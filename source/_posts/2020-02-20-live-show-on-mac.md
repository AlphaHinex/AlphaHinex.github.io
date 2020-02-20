---
id: live-show-on-mac
title: "Mac RTMP 直播方案"
description: "Mac 下直播推流及效果验证完整方案"
date: 2020.02.20 19:43
categories:
    - Mac
tags: [Mac, RTMP]
keywords: Mac, RTMP, 直播, OBS, 降噪, VLC
cover: /contents/live-show-on-mac/cover.png
---

Mac 直播软件
----------

[OBS](https://obsproject.com/) 为 Mac 下可用的直播软件。上手简单，网上教程也很多。
不过因为 RMBP 的分辨率太高，直播画面必须进行缩小，否则 Mac 不一定能吃得消。`MacBook Pro (Retina, 15-inch, Mid 2015)` 播一会就提示资源不足，需降低分辨率之类的了。最后使用的如下配置，观看直播的分辨率基本可接受，录制起来也不会提示需要降低输出质量。

![video settings](/contents/live-show-on-mac/video.png)

不过风扇还是会疯了一样响，如果使用 Mac 内置麦克风，可能会产生比较大噪音，影响直播效果。可以接入耳机，并且为声音添加降噪滤镜。

![audio settings 1](/contents/live-show-on-mac/audio-1.png)

![audio settings 2](/contents/live-show-on-mac/audio-2.png)

在 OBS 的 `设置` 中，有 `推流` 设置，里面可以设置将直播流推送的地址。


本地 RTMP 服务器
--------------

在本地环境，可以使用 [mac-local-rtmp-server](https://github.com/sallar/mac-local-rtmp-server) 搭建一个本地 RTMP 服务器。运行后可获得一个 `RTMP URL` 和 `STREAM KEY`，分别填入 OBS 推流设置的 `服务器` 和 `串流密钥` 中即可。


查看效果
-------

可使用 [VLC 播放器](https://www.videolan.org/vlc/) 观看流视频，以 iOS 版本为例，在 `网络` tab 页中，选择 `打开网络串流`，填入从本地 RTMP 服务器获得的 RTMP URL 和 STREAM KEY（斜线间隔）即可，如：`rtmp://127.0.0.1/live/r1hkK8cXU`。

> 注意流媒体播放器需与服务器在相同网络内。
