---
id: replay-to-rtmp-on-mac
title: "Mac 录播推流 RTMP 方案"
description: "Mac 上利用 QuickTime Player 和 ffmpeg 实现录播推流方案"
date: 2020.03.20 19:34
categories:
    - Mac
tags: [Mac, RTMP]
keywords: Mac, RTMP, 录播, QuickTime Player, ffmpeg
cover: /contents/replay-to-rtmp-on-mac/cover.jpeg
---

有时我们可能希望提前录制一些内容，在进行直播时推流至 RTMP 服务。本文提供了一个在 Mac 环境上实现此需求的方案。

## 屏幕录制

屏幕录制可以利用 [Mac RTMP 直播方案](https://alphahinex.github.io/2020/02/20/live-show-on-mac/) 中提到的 `OBS`，
也可以直接使用系统自带的 `QuickTime Player`，占用的资源（主要是 CPU）更少，还提供了鼠标点击的可视化效果。

选择 `新建屏幕录制`，并选择 `内置麦克风` 即可，完成录制后，保存为 `.mov` 格式的视频。

![recording](/contents/replay-to-rtmp-on-mac/recording.png)

## 推流

> the RTMP encapsulates MP3 or AAC audio and FLV1 video multimedia streams —— [Wikipedia](https://en.wikipedia.org/wiki/Real-Time_Messaging_Protocol)

RTMP 协议包含 MP3 或 AAC 格式的音频和 FLV1 格式的音频，所以需要将 `mov` 格式视频文件进行转换之后再进行推流。我们常说的视频格式（如 mp4、avi 等），更准确的说法应该是视频容器格式，在视频容器中，可以包含视频流、音频流等，详细信息可参见 [使用 HTML5 技术播放视频](https://alphahinex.github.io/2015/12/11/play-video-with-html5/) 中相关内容。

格式转换及推流使用强大的 [FFmpeg](http://ffmpeg.org/)。可以提前将视频容器格式转换好，也可以在推流的同时进行转换。

### 格式转换

```bash
$ ffmpeg -i test.mov test.flv
```

### 推流转换后格式

```bash
$ ffmpeg -i test.flv -f flv rtmp://127.0.0.1/live/B11m2KPN8
```

> 先转换，再推流的好处是，可以在推流时节省一些视频转换所需的资源（如 CPU、时间）。

### 边转换边推流

```bash
$ ffmpeg -i test.mov -f flv rtmp://127.0.0.1/live/B11m2KPN8
```

## 效果验证

开始推流后，可以通过直播方案中提到的 VLC 进行效果验证。
