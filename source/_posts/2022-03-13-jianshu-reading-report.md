---
id: jianshu-reading-report
title: "简书阅读量报告"
description: "简书阅读总量、增量阶段性报告"
date: 2022.03.13 10:26
categories:
    - DevOps
tags: [Jianshu, Dingtalk]
keywords: jianshu, 简书, dingtalk, 钉钉, 阅读量, 增量
cover: /contents/jianshu-reading-report/report.jpeg
---

[博客](https://alphahinex.github.io/) 上的文章，会同步发布到 公众号 和 [简书](https://www.jianshu.com/) 平台上，简书对 markdown 格式的支持、展现效果，以及文章的 SEO 和阅读量都非常不错，在有点赞和评论时，app 也会有即时通知。但当我们想知道自己的哪些文章阅读量最多，哪些文章阅读量增长较快以及近期哪些文章的阅读量有增加时，无论官网还是官方 app 上都缺少可用的工具。

我们可以借助一些简单的、免费的工具和脚本，来实现一个《简书阅读量报告》。 

## 效果

先来看下效果：

![简书阅读量报告](/contents/jianshu-reading-report/report.jpeg)

上面消息，为使用 NodeJS 脚本，在 [AWS](https://alphahinex.github.io/2021/01/17/aws-free-tier/) 上定时执行，并将 markdown 格式报告，通过 [钉钉自定义机器人](https://alphahinex.github.io/2022/03/06/dingtalk-custom-robot/) 的 Webhook 发送至钉钉中。

## 快速体验

如果对上面提到的这些名词比较陌生，只想将阅读量报告统计的数据换成是自己的或者是关注的简书作者的，可以按照下述步骤快速体验一下。

### 获得简书作者 ID

* 网页版可直接从作者主页的 url 中获取，如下图中作者主页地址为：https://www.jianshu.com/u/618c59928f3b ，最后面的 `618c59928f3b` 即为简书作者 ID。

![简书作者主页-web](/contents/jianshu-reading-report/jianshu-web.png)

* 使用简书移动端 app 的话，可以从作者主页点击右上角分享按钮，选择复制链接，同样可以获得上面的 url。

![简书作者主页-app](/contents/jianshu-reading-report/jianshu-app.png)

### 加入钉钉群

邀请你加入钉钉群聊钉钉机器人测试，点击进入查看详情 https://h5.dingtalk.com/circle/healthCheckin.html?corpId=ding0e53bcdadc9542fcd182e90532597458&48bad=98b1c&cbdbhh=qwertyuiop&origin=1

可以用钉钉打开上述链接，申请加入钉钉群，以便接收阅读量报告。

### 向 AlphaHinex 公众号发送消息

关注 `AlphaHinex` 公众号，并发送 `简书` 关键字，加空格和简书作者 ID，如 `简书 618c59928f3b`，稍等片刻即可在钉钉群中接收到阅读量报告了。

![公众号](https://alphahinex.github.io/slides/topics/tdd-from-entry-to-abandon/resources/public.jpg)

![公众号发送消息](/contents/jianshu-reading-report/wechat-mp.jpeg)

## 源码

主要源码可见 https://github.com/AlphaHinex/wechat-mp/blob/main/scripts/jianshu.js 。
