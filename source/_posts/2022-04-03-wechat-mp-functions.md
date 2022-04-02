---
id: wechat-mp-functions
title: "微信公众号功能介绍"
description: "个人公号当前已有功能介绍"
date: 2022.04.03 10:34
categories:
    - Others
tags: [Others]
keywords: 微信, 微信公众号, 自动回复, 服务配置, 自定义菜单
cover: /contents/wechat-mp-services/menu.jpeg
---

公众号里积累了一些由用户主动发送消息触发的实用功能，因为都需要特定关键词触发，对记忆力有一定的考验，汇总如下，以便使用。

![WeChat](https://alphahinex.github.io/slides/topics/tdd-from-entry-to-abandon/resources/public.jpg)

![menu](/contents/wechat-mp-services/menu.jpeg)


源远流长
=======

字帖
---

关键字：`字帖`、`字帖1`

发送关键字 + 空格 + 文字内容，可将文字内容（去标点符号）生成一个楷体的 pdf 字帖，可用来临摹或描红使用。

关键字 `字帖1` 与 `字帖` 的区别是会隔行输出一行文字内容。

字帖由 https://tools.yunzitie.cn/ 提供。

![字帖](/contents/wechat-mp-services/zitie.jpeg)

笔顺
----

向公众号发送单个汉字，回复该汉字的笔顺。如：

发送 `何`

得到：

![he](/contents/wechat-mp-services/4F55.gif)

笔顺由 http://bishun.shufaji.com/ 提供。

聚宝盆
=====

谷歌搜索
-------

发送 `g <content>`，得到使用 Google 搜索的前 5 条记录。如：

![g](/contents/wechat-mp-services/g.png)

转换工具
-------

使用 `base64` 及 `unicode` 关键字，加 `encode` 和 `decode`，进行对应的编解码：

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

生成二维码
--------

发送 `qr <content>`，会得到 `<content>` 内容对应的二维码图片。如：

发送 `qr https://alphahinex.github.io`

得到：

![qr](/contents/wechat-mp-services/qr.png)

简书阅读量
---------

关键字：`简书`

直接发送 `简书`，可查看我的简书阅读量报告，由于格式和字数限制，需到钉钉群（`33005170`）中接收消息。

发送 `简书 <简书用户 ID>`，可查看指定用户的简书阅读量报告。

![简书阅读量报告](/contents/jianshu-reading-report/report.jpeg)

更详细的用法可参见：[简书阅读量报告](https://alphahinex.github.io/2022/03/13/jianshu-reading-report/) 。

钉钉推送
-------

关键字：`钉钉`

发送 `钉钉 文字内容`，会将文字内容直接发送至钉钉群（`33005170`）。


借力而行
=======

HSA FAQ
-------

关键字：`hsa-faq`

发送 `hsa-faq 文字内容`，会按 `文字内容` 搜索内部知识库内容，并将相关结果，发送至钉钉群（`34796091`）。

![HSA FAQ](/contents/hsa-faq/result.png)

更详细的用法可参见：[新医保系统开发常见问题自助搜索](https://alphahinex.github.io/2022/03/27/hsa-faq/) 。

全文检索
-------

关键字：`blog`

发送 `blog 文字内容`，会按 `文字内容` 全文检索本博客中内容，回复相关文章名及链接：

![blog](/contents/wechat-mp-services/blog.jpeg)

小抄
----

关键字：`cs`

目前仅有 `ssh` 的小抄，发送 `cs ssh` 获得：

![cheat-sheet](/contents/wechat-mp-services/cheat-sheet.jpeg)

Hacker News
-----------

发送 `hn`，获得实时十大 Hacker News，可直接在公众号中查看回复的消息，也可以到钉钉群（`33005170`）中查看。

![hn](/contents/wechat-mp-services/hn.jpeg)

年度抽奖
-------

每年过年期间会开启抽红包活动，根据关注公众号时间长短，随机生成红包金额，通过支付宝红包发放。


同时启用回调 URL 及页面配置的自定义菜单
==================================

最后吐槽一下微信公众号的认证吧。

未认证的公众号，能够使用的接口非常有限，其中就包括自定义菜单和个性化菜单的接口，而个人公众号根本无法开通微信认证，所以当启用了公众号的回调 URL 后，无法通过页面进行公众号菜单的定义，也无法通过接口进行调用，WTF。

虽然不被官方所支持，但也不是完全无路可走，可通过如下步骤，实现同时使用：

1. 在公众号管理端 `设置与开发` - `基本配置` 中，停用服务器配置
1. 通过 `自定义菜单` 功能，从页面进行自定义菜单配置
1. 回到 `基本配置` 中，重新启用服务器配置
1. 再到公众号管理端左下角 `新的功能` 中，从 `已开通` 的功能中找到 `自定义菜单`，点击 `详情`，之后将自定义菜单功能重新开启

这样就可以同时启用这两个功能了。

更多信息可参考 [微信公众号自定义菜单消失？](https://wyiyi.github.io/amber/2021/07/31/GZH/)。

另外，自定义菜单只支持最多三个一级菜单，最多五个二级菜单，菜单名称的字数也是受限的，并且点击菜单后，只能回复公众号中已有的内容（图文消息、图片、视频等），想简单的回复几个字，是无法实现的……