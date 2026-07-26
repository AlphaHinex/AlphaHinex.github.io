---
id: tch-material-downloader
title: "中小学英语教材及听力下载"
description: "国家中小学智慧教育平台教材及配套音频资源下载"
date: 2026.07.26 10:26
categories:
    - Others
tags: [Others]
keywords: 教材, 小学, 初中, 高中, 电子版教材, 国家中小学智慧教育平台, 开发者工具, MAC id, course id
cover: /contents/tch-material-downloader/tch-material.png
---

工具
----

在 https://github.com/AlphaHinex/go-toolkit/releases 下载对应操作系统的 `tch-material-downloader` 可执行文件，如：

- Windows: [tch-material-downloader_win_amd64.exe](https://github.com/AlphaHinex/go-toolkit/releases/download/v2.6.3/tch-material-downloader_win_amd64.exe)
- Linux: [tch-material-downloader_linux_amd64](https://github.com/AlphaHinex/go-toolkit/releases/download/v2.6.3/tch-material-downloader_linux_amd64)
- MacOS: [tch-material-downloader_darwin_amd64](https://github.com/AlphaHinex/go-toolkit/releases/download/v2.6.3/tch-material-downloader_darwin_amd64)

该工具可下载国家中小学智慧教育平台（ https://basic.smartedu.cn/tchMaterial ）教材资源及配套音频文件，如英语教材和听力音频。

前置条件
--------

注册国家中小学智慧教育平台账号并登录，选定某个教材打开页面，如初中英语北师大版七年级上，
对应链接为：https://basic.smartedu.cn/tchMaterial/detail?contentType=assets_document&contentId=331959b8-d722-eac6-5466-4bac34806136&catalogType=tchMaterial&subCatalog=tchMaterial

![](https://alphahinex.github.io/contents/tch-material-downloader/tch-material.png)

### 获取 MAC id

打开浏览器开发者工具（一般按 F12），切换到 Network（网络）选项卡，刷新页面，找到包含 `pdf` 的 `GET` 请求，查看请求头 `X-Nd-Auth` 中包含的 MAC id 值：

![ids](https://alphahinex.github.io/contents/tch-material-downloader/ids.png)

### 获取课程 ID

从教材页面 URL 中的 `contentId=xxx` 获得课程 ID，如上面链接中 `contentId=331959b8-d722-eac6-5466-4bac34806136`，则课程 ID 为 `331959b8-d722-eac6-5466-4bac34806136`。

用法
----

```bash
./tch-material-downloader \
  --mac-id '<x-nd-auth-value>' \
  --course-id '<course-id>' \
  --output ./downloads

# 或直接运行后按提示输入 mac-id 和 course-id
./tch-material-downloader
```

常用参数：

- `--mac-id`, `-m`: 下载鉴权头 `x-nd-auth` 的值（必填）
- `--course-id`, `-c`: 课程 ID（必填）
- `--output`, `-o`: 输出目录（可选，默认 `./output/{course-name}`）
- `--timeout`: 请求超时秒数，默认 45

输出说明
--------

下载完成后，输出目录下会有：

- 按顺序命名的音频文件：`001_*.mp3`, `002_*.mp3`, ...
- 课本 PDF
- `manifest.json`：包含成功/失败、源 URL、保存路径、大小等信息

示例
-----

```bash
# macOS x86_64 示例
$ ./tch-material-downloader_darwin_amd64 \
  --mac-id 7F938B205xxxD2F6CB3B \
  --course-id 331959b8-d722-eac6-5466-4bac34806136
2026/07/25 17:54:40 Course name: （根据2022年版课程标准修订）义务教育教科书 英语 七年级上册
2026/07/25 17:54:41 Found 90 audio item(s)
2026/07/25 17:54:42 [audio][1/90] done: 1 Starter Section 2 Making New Friends Activity 2 (703505 bytes)
2026/07/25 17:54:42 [audio][2/90] done: 2 Starter Section 2 Activity 4 Talk Builder (480942 bytes)
2026/07/25 17:54:42 [audio][3/90] done: 3 Starter Section 3 Saying Hello Activity 1 Talk Builder (517304 bytes)
...
2026/07/25 17:55:58 [audio][89/90] done: 05.Proper Nouns (487174 bytes)
2026/07/25 17:55:59 [audio][90/90] done: 06.Countries and Places (1658296 bytes)
2026/07/25 17:55:59 Found 1 textbook PDF item(s)
2026/07/25 17:56:33 [pdf][1/1] done: textbook (60796211 bytes)
2026/07/25 17:56:33 Completed. audio=90/90, pdf=1/1, failed=0, bytes=158956060
2026/07/25 17:56:33 Manifest saved to output/（根据2022年版课程标准修订）义务教育教科书 英语 七年级上册/manifest.json
$ tree -N output
output
└── （根据2022年版课程标准修订）义务教育教科书 英语 七年级上册
    ├── 001_1 Starter Section 2 Making New Friends Activity 2.mp3
    ├── 002_2 Starter Section 2 Activity 4 Talk Builder.mp3
    ├── 003_3 Starter Section 3 Saying Hello Activity 1 Talk Builder.mp3
    ...
    ├── 089_05.Proper Nouns.mp3
    ├── 090_06.Countries and Places.mp3
    ├── manifest.json
    └── （根据2022年版课程标准修订）义务教育教科书 英语 七年级上册.pdf

1 directory, 92 files
```