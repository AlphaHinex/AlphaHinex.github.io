---
id: simple-but-powerful
title: "简单，却伟大"
description: "犹如母爱一般"
date: 2021.06.06 10:34
categories:
    - Web
tags: [Web, HTML, DNS]
keywords: DNS, lvh.me, localtest.me, nip.io, sslip.io
cover: /contents/covers/simple-but-powerful.png
---

Web 开发时，会有需要使用域名的时候，比如以下两个场景：

1. 需要模拟跨域访问
1. 由于网络等限制只能有一个可以访问的 ip 和端口，却需要提供多个相同 context path 的服务

使用 `127.0.0.1` 和 `localhost` 可以解决第一个场景的一部分问题，但需要多个域的时候，或者第二个场景，就无能为力了。

虽说可以修改本地的 hosts 文件，将不同域名映射到指定 ip 上，但麻烦不说，在访问非本地服务时，也不容易让所有使用的人都修改 hosts。

下面介绍几个简单，却非常有效的 DNS 解析服务（离线环境无法使用）。

为方便查看效果，可以先在本地启动一个 http 服务，比如地址是 http://localhost:9876 。


## localhost

针对本地开发调试，可以使用如下两个 DNS 解析服务：

### lvh.me

可以设置任意域名前缀，在后面加上 `lvh.me`，即可访问到本地的对应服务，如：

http://alpha.hinex.lvh.me:9876/


### [localtest.me](http://readme.localtest.me/)

除 `lvh.me` 外，还可以使用 `localtest.me`，比如：

http://alpha.hinex.localtest.me:9876/

更多信息可查阅此服务官网 http://readme.localtest.me/ 。


## 其他 ip

上面两个域名后缀仅支持本地服务，如果需要使用域名的服务在远程主机上，并且希望其他人也能访问时，可以使用如下服务：


### [nip.io](https://nip.io/)

相关说明可见官网（https://nip.io/），简单来说，就是使用 `xxx.<ip>.nip.io` 等域名规则，可以将域名解析到对应的 ip 上，如：

http://alpha.hinex.192.168.77.57.nip.io:9876/

不仅内网地址可用，公网地址也可以：

http://test.116.140.154.101.nip.io/


### [sslip.io](https://sslip.io/)

与 `nip.io` 类似，还可以使用 `sslip.io`，详见 https://sslip.io/ 。

http://alpha.hinex.192.168.77.57.sslip.io:9876/ 此地址同样可以访问演示用的服务，并且能访问到 `192.168.77.57` 的人都可以直接通过此域名进行访问，无需额外配置。