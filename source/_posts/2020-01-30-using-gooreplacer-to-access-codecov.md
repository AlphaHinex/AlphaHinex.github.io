---
id: using-gooreplacer-to-access-codecov
title: "利用 Gooreplacer 科学访问 Codecov"
description: "在 GFW 内科学访问 Codecov 的页面"
date: 2020.01.30
categories:
    - GFW
tags: [GFW, Codecov, Gooreplacer]
keywords: Codecov, GFW, Gooreplacer
cover: /contents/codecov/welcome.png
---

[Codecov](https://codecov.io/) 是一个测试覆盖率结果可视化展现网站，并与 GitHub 和 Pull Request 有较好的集成，可以在 Pull Request 中展现覆盖率变化结果，协助保证代码质量。

不过在 GFW 环境下访问 Codecov 不是很稳定，因为网站使用了一些 Google 的 CDN 资源（主要是 js 和 css）。利用 [Gooreplacer](https://liujiacai.net/gooreplacer/) 可以将这些资源重定向到可访问的地址，科学使用 Codecov 提供的服务。


安装 Gooreplacer Chrome 插件
---------------------------

因无法直接在线安装 Chrome 插件，可以从 Gooreplacer 的 [Releases](https://github.com/jiacai2050/gooreplacer/releases) 页面直接下载作者打好的 zip 包，如：https://github.com/jiacai2050/gooreplacer/releases/download/v3.11.0/chrome_gooreplacer_1574507740.zip 。在 Chrome 的 `扩展程序` 中打开 `开发者模式`，直接加载解压出的内容即可。


配置
---

### 配置在线规则

可参照 [README](https://github.com/jiacai2050/gooreplacer/blob/master/README.md) 中内容配置好在线规则，即可完成大部分 Google 资源的重定向。

### 去掉 content-security-policy 限制

由于 Codecov 网站安全限制，浏览器会拒绝加载重定向的资源。可参照 [#13](https://github.com/jiacai2050/gooreplacer/issues/13) 中方式，在 `请求/响应头` 中，新增一个响应头，填写如下信息：

|key|value|
|:--|:--|
|匹配模式|codecov.io|
|匹配类型|通配符|
|动作类型|拦截|
|键名|content-security-policy|
|键值|空|
|是否开启|是|

### 重定向 codecov 资源

|匹配模式|目标地址|
|:---|:---|
|https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js|https://cdn.bootcss.com/jquery/2.1.3/jquery.min.js|
|https://codecov-cdn.storage.googleapis.com/4.4.11-95184d8/bower/deps.min.css|https://alphahinex.github.io/proxy/codecov/deps.min.css|
|https://codecov-cdn.storage.googleapis.com/4.4.11-95184d8/media/css/style.css|https://alphahinex.github.io/proxy/codecov/style.css|
|https://codecov-cdn.storage.googleapis.com/4.4.11-95184d8/bower/deps.min.js|https://alphahinex.github.io/proxy/codecov/deps.min.js|
|https://codecov-cdn.storage.googleapis.com/4.4.11-95184d8/media/js/script.min.js|https://alphahinex.github.io/proxy/codecov/script.min.js|
