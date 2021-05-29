---
id: same-origin-and-same-site-of-cookie
title: "Cookie 的同源和同站"
description: "Cookie 中的同源，等价于同站？！"
date: 2021.05.30 10:34
categories:
    - Web
tags: [Web, HTML]
keywords: origin, site, same origin, cross origin, same site, corss site, CSRF, SOP, port, cookie
cover: /contents/covers/same-origin-and-same-site-of-cookie.jpg
---

存储在浏览器中的数据，如 [localStorage][storage] 和 [IndexedDB][indexDB]，是以 [源（origin）][origin] 进行分割的。每个源都拥有自己单独的存储空间，一个源中的 JavaScript 脚本不能对属于其它源的数据进行读写操作，即所谓的 [同源策略（SOP）][SOP]。

## Cookie 的同源

然而 Cookie 在受同源策略约束时，使用不同的源的定义方式。

通常来讲：

> 同源（Same origin），意味着 scheme/host/port 三元组完全相同。任意一部分不同，即为跨源（cross-origin，或称为跨域）。

而根据 Cookie 的现行标准规范 [HTTP State Management Mechanism (rfc6265)][6265] ：

> 1. Introduction
> ...
> For historical reasons, cookies contain a number of security and
   privacy infelicities.  For example, a server can indicate that a
   given cookie is intended for "secure" connections, but the Secure
   attribute does not provide integrity in the presence of an active
   network attacker.  **Similarly, cookies for a given host are shared
   across all the ports on that host, even though the usual "same-origin
   policy" used by web browsers isolates content retrieved via different
   ports.**

**即，相同 host，不同端口的服务之间，cookie 是可以共享的！**

另外：

> 8.5. Weak Confidentiality
> **Cookies do not provide isolation by port.**  If a cookie is readable by
   a service running on one port, the cookie is also readable by a
   service running on another port of the same server.  If a cookie is
   writable by a service on one port, the cookie is also writable by a
   service running on another port of the same server.  For this reason,
   servers SHOULD NOT both run mutually distrusting services on
   different ports of the same host and use cookies to store security-
   sensitive information.
> **Cookies do not provide isolation by scheme.**  Although most commonly
   used with the http and https schemes, the cookies for a given host
   might also be available to other schemes, such as ftp and gopher.
   Although this lack of isolation by scheme is most apparent in non-
   HTTP APIs that permit access to cookies (e.g., HTML's document.cookie
   API), the lack of isolation by scheme is actually present in
   requirements for processing cookies themselves (e.g., consider
   retrieving a URI with the gopher scheme via HTTP).

由上可知，Cookie 不提供根据 `scheme` 和 `port` 的隔离性，也就是说：

**Cookie 中同源的定义，等价于不考虑 scheme 的同站（schemelessly same site）定义!**

**默认情况下，Cookie 可以在 `eTLD + 1` 相同的站点间进行共享！**

**另外，服务端可以通过响应的 `Set-Cookie` Header，对 Cookie 的可用性进行设定，相关的属性包括 `Domain`、`Path`、`Secure` 等。**

比如通过 `Path` 属性，可以指定允许获得 Cookie 的 URL 路径前缀。

> 注意：`Path` 属性意在性能而非安全性。满足同源条件的页面中，依然可以通过 `document.cookie` 对 Cookie 进行访问，即使在 path 属性不匹配的情况下。


## Cookie 的同站

现行的 [rfc6265][6265] 标准是 2011 年 4 月开始实行的，在后续的 rfc6265bis 提案的 [02][02] 版本中，在 `Set-Cookie` 的响应头中增加了 `SameSite` 属性，用来约束对 Cookie 的跨站访问行为，以提升安全性，降低 [CSRF][CSRF] 攻击的风险。

该提案的最新版本为 [draft-ietf-httpbis-rfc6265bis-07][draft]（将于 2021 年 6 月 10 日到期），此版本中 `SameSite` 属性有三个值：

1. Lax：通常情况下不会在跨站请求中携带 Cookie，但用户主动导航至外站时，会携带用户之前访问此外站的 Cookie。在 `SameSite` 属性未被显示设定时，将按照 `SameSite=Lax` 进行对携带 Cookie 的约束（07 版提案之前，未设定 `SameSite` 等价于 `SameSite=None`）。
1. Strict：跨站请求时不会携带 Cookie。
1. None：同站和跨站的请求都会携带 Cookie。当设置了 `SameSite=None` 时，Cookie 的 `Secure` 属性也必须被同时设定（即此时 Cookie 只能通过 https 协议发送），否则 Cookie 会被拦截。

在此版本提案中，对于同站的定义增加了 `scheme` 部分，即与最新的 HTML 标准一致：`scheme` 和 `eTLD + 1` 同时相同，才能够认为是同站（same site）。


## 参考资料

* [跨源数据存储访问](https://developer.mozilla.org/zh-CN/docs/Web/Security/Same-origin_policy#%E8%B7%A8%E6%BA%90%E6%95%B0%E6%8D%AE%E5%AD%98%E5%82%A8%E8%AE%BF%E9%97%AE)
* [Are HTTP cookies port specific?](https://stackoverflow.com/questions/1612177/are-http-cookies-port-specific)
* [SameSite cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite)
* [SameSite cookies explained](https://web.dev/samesite-cookies-explained/)
* [SameSite cookies recipes](https://web.dev/samesite-cookie-recipes/)
* [Schemeful Same-Site](https://web.dev/schemeful-samesite/)
* [網站安全🔒 再探同源政策，談 SameSite 設定對 Cookie 的影響與注意事項](https://medium.com/%E7%A8%8B%E5%BC%8F%E7%8C%BF%E5%90%83%E9%A6%99%E8%95%89/%E5%86%8D%E6%8E%A2%E5%90%8C%E6%BA%90%E6%94%BF%E7%AD%96-%E8%AB%87-samesite-%E8%A8%AD%E5%AE%9A%E5%B0%8D-cookie-%E7%9A%84%E5%BD%B1%E9%9F%BF%E8%88%87%E6%B3%A8%E6%84%8F%E4%BA%8B%E9%A0%85-6195d10d4441)
* [Web Security 1: Same-Origin and Cookie Policy](https://inst.eecs.berkeley.edu/~cs261/fa17/scribe/web-security-1.pdf)

[storage]:https://developer.mozilla.org/zh-CN/docs/Web/Guide/API/DOM/Storage
[indexDB]:https://developer.mozilla.org/zh-CN/docs/IndexedDB
[origin]:https://alphahinex.github.io/2021/05/16/origin-and-site/#Origin
[SOP]:https://alphahinex.github.io/2021/05/23/sop-cors-csrf-xss/#SOP
[6265]:https://datatracker.ietf.org/doc/html/rfc6265
[CSRF]:https://alphahinex.github.io/2021/05/23/sop-cors-csrf-xss/#CSRF
[draft]:https://datatracker.ietf.org/doc/html/draft-ietf-httpbis-rfc6265bis-07
[02]:https://datatracker.ietf.org/doc/html/draft-ietf-httpbis-rfc6265bis-02