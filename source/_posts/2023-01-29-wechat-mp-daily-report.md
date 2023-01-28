---
id: wechat-mp-daily-report
title: "想知道你的公众号昨日都有哪些文章被阅读了吗？"
description: "微信公众平台命令行工具，帮您了解每日阅读、点赞、在看增长情况"
date: 2023.01.29 10:34
categories:
    - Go
    - Wechat
tags: [Go, Golang, Wechat]
keywords: Wechat, 微信公众平台, 公众号, 阅读, 点赞, 在看, Linux, cli
cover: /contents/wechat-mp-daily-report/cover.png
---

在微信公众平台中，提供了前一日 00:00 ~ 24:00 的阅读、分享、关注数统计，如：

![](/contents/wechat-mp-daily-report/lastday.png)

但当我们想知道这个昨日阅读的次数，分别是由哪些文章产生的，每篇文章新增了多少阅读量时，无论桌面端的微信公众平台还是移动端的订阅号助手，都无法给出我们这个明细数据。

如果能有这样一个统计每天推送过来就好了：

![](/contents/wechat-mp-daily-report/cover.png)

# 快速体验

## 加入钉钉群

使用钉钉扫描下方二维码，申请加入钉钉群，以便接收阅读量统计消息。

![](/contents/wechat-mp-daily-report/dingtalk.png)

## 向 `周拱壹卒` 公众号发送消息

扫描下方二维码关注 `周拱壹卒` 公众号，并发送 `公众号` 关键字，加空格，再加要统计的公众号的 Cookie 值（获取 Cookie 方式可见下文），如 `公众号 appmsglist_...`，稍等片刻即可在钉钉群中接收到阅读量统计消息了。

![](https://alphahinex.github.io/slides/topics/tdd-from-entry-to-abandon/resources/public.jpg)

首次交互将进行数据初始化，会认为所有阅读量都是新增的阅读量。间隔一段时间后再次向公众号发送消息，可统计两次发送间隔时间内的增量数据。

> 注意：安全起见，在向公众号发送过 Cookie 值并接收到统计消息之后，请退出公众平台登录状态使此 Cookie 失效。

# 所需材料

1. 登录微信公众平台后生成的 Cookie
1. https://github.com/AlphaHinex/go-toolkit/tree/main/wechat-mp 中提供的命令行工具
1. 钉钉接收推送消息（可选）
1. 一台能够执行计划任务的电脑

# 操作步骤

## 获取公众号 Cookie

访问 https://mp.weixin.qq.com/ 并登录公众号后，打开浏览器调试工具（按 F12），切换至 Network 选项卡，点击公众号图标刷新页面，找一个请求头中带有 `cookie` 的请求，如下图：

![](/contents/wechat-mp-daily-report/cookie.png)

将 `cookie` 的值完整的复制出来，存放到任意文件中备用。

> 注意：公众平台的 Cookie 有效期大约为三天半。

## 获得命令行工具

选择任意版本下载：

1. [wechat-mp Windows AMD64 版本](/contents/wechat-mp-daily-report/wechat-mp_win_amd64.exe)
1. [wechat-mp Linux AMD64 版本](/contents/wechat-mp-daily-report/wechat-mp_linux_amd64)
1. [wechat-mp MacOS AMD64 版本](/contents/wechat-mp-daily-report/wechat-mp_darwin_amd64)

或按照 https://github.com/AlphaHinex/go-toolkit/tree/main/wechat-mp 中文档描述，源码编译获得 wechat-mp 命令行工具可执行文件。

### 使用示例

使用 `/path/to/foobar.cookie` 文件中的 cookie，
统计对应公众号中的文章数据，
并将中间结果（作为基线，供再次执行命令时进行增长统计）输出至 `/foo/bar` 路径。
统计结果以 markdown 格式输出至控制台，
也可通过 `--dingtalk-token` 参数指定钉钉机器人的 token 将统计结果发送给钉钉机器人。

```bash
$ ./wechat-mp_linux_amd64 \
--cookie-file /path/to/foobar.cookie \
-o /foo/bar --dingtalk-token XXXXXX
```

## 钉钉接收消息（可选）

希望将统计消息发送给自己的钉钉机器人时，可参照 [钉钉自定义机器人](https://alphahinex.github.io/2022/03/06/dingtalk-custom-robot/) 中的方式，创建好接收消息的群并在群众添加钉钉自定义机器人后，从获得的机器人 Webhook 地址的 `access_token` 参数中，获得命令行工具所需的 `--dingtalk-token` 参数值。

## 配置计划任务

按上面使用示例调整好命令行工具所需参数后，可将命令存储至对应操作系统支持的脚本文件中，如 `wechat-mp.sh` 或 `wechat-mp.bat`，并按照操作系统支持的计划任务设定方式，将脚本文件配置成每天执行，即可获得微信公众号每日阅读量增长明细。