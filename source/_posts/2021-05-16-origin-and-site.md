---
id: origin-and-site
title: "Origin 和 Site"
description: "同源一定同站"
date: 2021.05.16 10:34
categories:
    - Web
tags: [Web, HTML]
keywords: origin, site, same origin, cross-origin, same origin-domain, same site, corss site, domain, host
cover: /contents/covers/origin-and-site.jpg
---

## Origin

在 Web 中，origin（源）是指 `协议（scheme）+ 主机名（host）+ 端口号（port）`。

如：https://alphahinex.github.io/2021/05/16/origin-and-site/ 

源即为：https://alphahinex.github.io

同源（Same origin），意味着 `scheme/host/port` 三元组完全相同。任意一部分不同，即为跨源（cross-origin，或称为跨域）。

未明确指定端口时，使用协议默认端口（http 为 80，https 为 443）进行同源判定。

仍以 https://alphahinex.github.io/2021/05/16/origin-and-site/ 为例，下表列出各 URL 与之是否同源的判定：

|URL|是否同源|原因|
|:--|:------|:--|
|https://alphahinex.github.io/tags/|是|仅路径不同|
|http://alphahinex.github.io/|否|协议不同|
|https://alphahinex.github.io:443/archives/|是|https 默认端口即为 443|
|https://github.com/AlphaHinex|否|host 不同|

## Site

Top-level domain (TLD)，顶级域，如 `.com`、`.org` 等，收录在根域名数据库 [Root Zone Database][db] 中。TLD 以及 TLD 前面的一部分（TLD + 1）连在一起即为 Site（站）。如 https://www.foo.com/bar 的 site 是 `foo.com`。

然而对于一些域，如 `.github.io`，仅使用 TLD（`.io`）+ 1 不足以区分不同的站，故一个 **有效顶级域**（effective TLD，eTLD）的列表 —— 公共后缀列表（[Public Suffix List][psld]）被创建了出来，并可以在 [这里][psl] 进行查询。

站（Site）的定义，也演变为了 `eTLD + 1` 。如 https://alphahinex.github.io ，eTLD 为 `.github.io`，eTLD + 1 为 `alphahinex.github.io`。

不考虑 scheme 的 site 定义，使得 HTTP 可能会成为一个安全薄弱环节所被利用，故 site 正在演变为包括 scheme 部分。在最新的 [HTML 标准][html] 中，也已将 scheme 和 eTLD + 1 同时相同，作为同站（same site）的判定条件。仅 eTLD + 1 相同，scheme 不同，被称为 `schemelessly same site`。

例如，已知 `wildlife.museum`、`museum` 和 `com` 是公共后缀（Public Suffix），`example.com` 不是公共后缀：

|A|B|schemelessly same site|same site|
|:--|:--|:-----------------|:--------|
|https://example.com|https://sub.example.com|√|√|
|https://example.com|https://sub.other.example.com|√|√|
|https://example.com|http://non-secure.example.com|√|X|
|https://r.wildlife.museum|https://sub.r.wildlife.musemum|√|√|
|https://r.wildlife.museum|https://sub.other.r.wildlife.museum|√|√|
|https://r.wildlife.museum|https://other.wildlife.museum|X|X|
|https://r.wildlife.museum|https://wildlife.museum|X|X|
|https://wildlife.museum|https://wildlife.museum|√|√|

## 参考资料

* [Understanding "same-site" and "same-origin"][ssso]
* [HTML spec][html]

[ssso]:https://web.dev/same-site-same-origin/
[db]:https://www.iana.org/domains/root/db
[psld]:https://wiki.mozilla.org/Public_Suffix_List
[psl]:https://publicsuffix.org/list/
[html]:https://html.spec.whatwg.org/multipage/origin.html#sites