---
id: dingtalk-custom-robot
title: "钉钉自定义机器人"
description: "像发手机短信一样方便"
date: 2022.03.06 10:34
categories:
    - DevOps
tags: [Dingtalk, Robot]
keywords: dingtalk, robot, 钉钉, 机器人, 聊天机器人
cover: /contents/covers/dingtalk-custom-robot.png
---

## 聊天机器人

从 [hubot](https://hubot.github.com/) 起接触到聊天机器人，其使用场景还是非常丰富的：

1. 群管理：新人入群欢迎、关键字自动回复、同类消息汇总 ……
2. 结合 SaaS 服务：翻译、生成二维码、编解码、智能客服 ……
3. 定时通知：天气预报、股市行情、监控信息 ……

简单归纳一下，需要机器人具备的能力主要包括：主动发送消息（单聊、群聊）和 被动响应消息（单聊、群聊）。

相关的开源实现也有很多，如上面提到的 hubot 和其与各种聊天工具的 [适配](https://hubot.github.com/docs/adapters/)、基于微信的 chatbot —— [Wechaty](https://wechaty.js.org/) 等。

不过因为众所周知的原因，国外的聊天工具各种水土不服；微信作为目前的国民即时通讯工具，能力越大责任越大，对机器发送消息的限制一直都很严格。

[微信机器人的曲线实现](https://alphahinex.github.io/2021/02/21/wechat-mp-services/) 提供了一种借助微信公众号实现被动响应消息的方式，但不能主动发送消息；直到被迫使用钉钉后，发现钉钉也支持机器人，并且可以像给手机号发送短信一样方便的主动发送消息，可以结合公众号被动回复消息的功能，获得一个免费可用且较为稳定的，能够主动发消息和被动响应消息的，聊天机器人方案。

## 钉钉机器人

从钉钉机器人的 [官方文档](https://open.dingtalk.com/document/robots/robot-overview) 中，可以了解到，钉钉机器人分为很多种类型，不同类型的机器人拥有不同的能力，接入方式也各不相同。其中最简单的，要数自定义类型的机器人了。

## 钉钉自定义类型机器人

按照 [自定义机器人接入](https://open.dingtalk.com/document/robots/custom-robot-access) 文档，在钉钉客户端中，即可完成自定义类型机器人的添加，之后会获得机器人的 Webhook 地址，如：

```text
https://oapi.dingtalk.com/robot/send?access_token=XXXXXX
```

其中的 `access_token`，就相当于这个机器人的手机号，只要使用这个 token 用 POST 方式调用上面接口，就可以在钉钉中收到发送的消息了。例如使用下面的 curl 命令：

```bash
$ curl 'https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxx' \
 -H 'Content-Type: application/json' \
 -d '{"msgtype": "text","text": {"content":"我就是我, 是不一样的烟火"}}'
```

> 注意，目前自定义机器人必须从 [安全方式](https://open.dingtalk.com/document/robots/customize-robot-security-settings) 中选择一种，不满足安全设置的消息发送动作不允许被执行。

钉钉支持的 [消息类型和数据格式][msg-type] 比微信要丰富，可以获得更好的展示效果和用户体验。

## 使用 RunKit 从浏览器给钉钉机器人发送消息

[RunKit](https://runkit.com/) 是一个可在线运行 nodejs 代码的环境，可在 https://npm.runkit.com/ 直接运行下面代码片段，直接通过浏览器给钉钉机器人发送消息：

```js
const axios = require('axios').default;
const https = require('https');

const DINGTALK_TOKEN = 'XXXXXX';

let dingtalk = (msg, callback) => {
    axios({
        url: 'https://oapi.dingtalk.com/robot/send?access_token=' + DINGTALK_TOKEN,
        headers: {
            'Content-Type': 'application/json;charset=utf-8'
        },
        method: 'POST',
        httpsAgent: new https.Agent({
            rejectUnauthorized: false
        }),
        data: msg
    }).then(callback);
};

dingtalk({"markdown": {"title":"Hello World","text": 'hinex send msg from runkit:\n\n' + '[钉钉自定义机器人](https://alphahinex.github.io/2022/03/06/dingtalk-custom-robot/)\n\n[微信机器人的曲线实现](https://alphahinex.github.io/2021/02/21/wechat-mp-services/)'}, "msgtype": "markdown"});
```

上面 `dingtalk` 方法可以直接使用 [消息类型和数据格式][msg-type] 中的各类型消息 json 对象。

![ding-bot](/contents/covers/dingtalk-custom-robot.png)

> 注意：要想成功发送消息，需替换上面代码中的 `XXXXXX`，安全设置使用 `自定义关键词` 方式，并且在发送的消息内容中，包含定义的关键词。

## 代理 Webhook 地址

某些情况下，可能无法直接访问上面钉钉的 Webhook 地址，通过一个可以访问的地址进行请求转发也是可以的，例如在一个可以访问的地址上，为 Nginx 添加如下配置：

```nginx.conf
location /dingtalk/ {
    proxy_pass https://oapi.dingtalk.com/;
}
```

之后就可以向这个 Nginx 发送 POST 请求以发送消息了，例如：

```bash
$ curl -H "Content-Type:application/json;charset=utf-8" -X POST -d '{"at":{"isAtAll":false},"text":{"content":"我就是我, 是不一样的烟火"},"msgtype":"text"}' http://54.92.69.158/dingtalk/robot/send?access_token=XXXXXX
```

[msg-type]:https://open.dingtalk.com/document/robots/message-types-and-data-format