---
id: wechat-mp-services
title: "微信机器人的曲线实现"
description: "基于未认证订阅号的功能受限版本"
date: 2021.02.21 10:36
categories:
    - Others
tags: [Others]
keywords: 微信, 微信公众号, 自动回复, 订阅号, 机器人, hubot
cover: /contents/wechat-mp-services/cover.jpg
---

在知道了 [Hubot][hubot] 之后，就一直想在微信里也有一个类似的机器人。虽然也有不少微信的 hubot adapter，但基本都是基于网页版微信实现的，而微信对网页版微信的态度，让人深刻的感受到，作为国内的超级 App 所承担的责任。

之后在 [Slack][slack] 中用了一段 Hubot，还是挺不错的，但是在国内使用 Slack，无论是桌面端还是移动端，还都是有些难度和不稳定的。

[微信公众平台][mp]，给出了一个微信官方支持的，微信机器人的实现方式，公众平台提供的接口比较有限，尤其是对未认证的订阅号，提供的接口更少，但基本的被动回复消息的功能还是有的，这就给出了一定的空间来让我们在微信中，实现一个问答方式的机器人。

实例
===

先看看实例，可以关注公众号进行体验。

![WeChat](https://alphahinex.github.io/slides/topics/tdd-from-entry-to-abandon/resources/public.jpg)

查询汉字笔顺
----------

向公众号发送单个汉字，回复该汉字的笔顺。如：

发送 `何`

得到：

![he](/contents/wechat-mp-services/4F55.gif)

生成二维码
---------

发送 `qr <content>`，会得到 `<content>` 内容对应的二维码图片。如：

发送 `qr https://alphahinex.github.io`

得到：

![qr](/contents/wechat-mp-services/qr.png)

Google 搜索
-----------

发送 `g <content>`，得到使用 Google 搜索的前 10 条记录。如：

![g](/contents/wechat-mp-services/g.png)

实时十大 Hacker News
-------------------

发送 `hn`，得到类似如下内容：

>Top 10 Hacker News
>
>UK Supreme Court rules Uber drivers are workers
>https://www.bbc.co.uk/news/business-56123668
>
>Monolith First
>https://martinfowler.com/bliki/MonolithFirst.html
>
>Perseverance Rover lands on Mars [video]
>https://www.youtube.com/watch?v=gm0b_ijaYMQ
>
>12 requests per second: A realistic look at Python web frameworks
>https://suade.org/dev/12-requests-per-second-with-python/
>
>Why is it so hard to see code from 5 minutes ago?
>https://web.eecs.utk.edu/~azh/blog/yestercode.html
>
>Checked C
>https://github.com/microsoft/checkedc
>
>Where Everything Went Wrong: Error Handling and Error Messages in Rust
>https://msirringhaus.github.io/Where-everything-went-wrong/
>
>Reflections on Using Haskell for My Startup
>https://alistairb.dev/reflections-on-haskell-for-startup/
>
>A Follow-Up to “Location-Based Pay”
>https://blackshaw.substack.com/p/pay-2
>
>Designing a RISC-V CPU, Part 1: Learning hardware design as a software engineer
>https://mcla.ug/blog/risc-v-cpu-part-1.html

base64/unicode 编解码
--------------------

使用 base64 及 unicode 关键字，加 encode 和 decode，进行对应的编解码：

> base64 encode hinex
> 
> aGluZXg=

> base64 decode aGluZXg=
> 
> hinex

> unicode encode 何
> 
> %u4F55

> unicode decode 4F55
> 
> 何

抽奖
---

发送带 `牛` 四字消息，得到抽奖结果演示文字：

> 旺仔牛奶
>
> 【演示文字】恭喜您获得 1476.10 元红包！祝您 2021 年牛年如意!

回声
---

发送其他无特定含义的消息内容，会将内容原封不动的返回，并增加 `, you said.` 后缀，如：

> hello
> 
> hello, you said.

源码
===

[源码][src] 仿照 Hubot 的目录结构，将每类回复的脚本作为一个单独的文件，放在了 `scripts` 路径下。入口文件为 `wechat-mp-server.js`。

受限于订阅号的 [被动回复用户消息][reply] 机制，只能被动响应用户发送过来的消息，并且只能回复一次；回复消息的类型、内容及长度，也都是有一定的限制的；回复图片等内容时，还需要先上传到公众号的素材库……

不过这种 `请求 - 响应` 的模式，也是能够实现一些好玩的功能的，比如 [ChatOps][chatops] 等。您有什么有趣的想法吗？或者，直接提个 PR 也是欢迎的！

[hubot]:https://github.com/hubotio/hubot
[slack]:https://slack.com/intl/en-cn/
[mp]:https://mp.weixin.qq.com/
[src]:https://github.com/AlphaHinex/wechat-mp
[reply]:https://developers.weixin.qq.com/doc/offiaccount/Message_Management/Passive_user_reply_message.html
[chatops]:https://cn.bing.com/search?q=chatops&rdr=1&rdrig=B6FA0334135242B0B1B0A6B4C6C78A04