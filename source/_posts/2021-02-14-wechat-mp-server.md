---
id: wechat-mp-server
title: "微信公众号服务"
description: "抽奖开启"
date: 2021.02.14 10:34
categories:
    - Others
tags: [Others]
keywords: 微信, 微信公众号, 牛年
cover: /contents/covers/wechat-mp-server.jpg
---

辛丑年大年初三（2021年2月14日）抽支付宝口令红包活动已开启，仅此一天！

发送带 `牛` 字的四字消息，根据关注时间，抽取随机金额支付宝口令红包。

除了抽奖功能外，公众号自动回复服务还包括一些其他功能哟，比如：

1. 能够正确响应微信公众平台发送的 Token 验证（此处仅正确响应，并未对 Token 进行验证）
1. 关注时回复欢迎消息
1. 回声功能：对任何发送给公众号的文本消息，回复 `<发送内容>, you said.`；其他类型的消息回复 `Not support yet.`。
1. 十大 Hacker News：发送 `hn` 关键字，不区分大小写，回复当时 Hacker News RSS 中的前十条内容。
1. 抽奖：发送带 `牛` 字的四字消息，根据关注时间（通过接口获得用户信息需公众号主体不能为个人），抽取随机数额。

微信公众号限定某些接口需通过微信认证才可调用，而个人主体不能通过认证 orz，所以目前获取用户关注时间是手动添加的。。。

源码可见：https://github.com/AlphaHinex/wechat-mp

本地运行
-------

1. 安装依赖
    ```bash
    $ npm i
    ```
2. 运行，服务启动在本地 8080 端口
    ```bash
    $ node wechat-mp-server.js
    ```
    
调试时，可参照 [内网穿透？试试 ngrok][ngrok] 中内容，使用 ngrok 将本地 8080 端口映射至外网地址，即可在 微信公众平台接口调试工具 中，调试本地服务。

服务端运行
---------

可将此服务通过 `nohup` 或 `screen` 等方式后台运行，启动后，通过 NGINX 等反向代理将服务器的 80 或 443 端口代理至此服务，并将 IP 或域名配置到微信公众号的服务器配置页，即可由此服务响应公众号收到的消息。

没有服务器？看看 [这里][aws]。

[ngrok]:https://alphahinex.github.io/2021/02/06/ngrok/
[aws]:https://alphahinex.github.io/2021/01/17/aws-free-tier/