---
id: sop-cors-csrf-xss
title: "SOP、CORS 和 CSRF、XSS"
description: "请说出它们的含义"
date: 2021.05.23 10:26
categories:
    - Web
tags: [Web, HTML]
keywords: origin, site, same origin, cross-origin, same site, corss site, SOP, CORS, CSRF, XSS
cover: /contents/sop-cors-csrf-xss/cover.jpeg
---

在 [Origin 和 Site](https://alphahinex.github.io/2021/05/16/origin-and-site/) 中，我们介绍了 `源` 和 `站` 的概念，这两个概念在浏览器的安全策略中有着广泛的应用，接下来再介绍几个与之相关的概念。


## SOP

Same Origin Policy（[SOP][SOP]），同源策略，是浏览器的一个重要安全机制，用来限制从某一 Origin（源）加载的文档或脚本，如何与其他源中的资源进行交互。它能帮助隔离潜在的恶意文档，减少被攻击的可能。

### 跨源网络访问

跨源网络访问，通常分为三类：

1. 跨源**写操作**（Cross-origin writes）：通常是被允许的，例如链接、重定向，以及表单提交。这类操作又分为 `简单请求（simple request）` 及 `预检请求（preflighted request）` 两类，需预检的请求，要求必须首先使用 `OPTIONS` 方法发起一个预检请求到服务器，以获知服务器是否允许该实际请求。
1. 跨源**资源嵌入**（Cross-origin embedding）：一般是被允许的。
1. 跨源**读操作**（Cross-origin reads）：一般是不被允许的，但常可以通过内嵌资源来巧妙的进行读取访问。例如，可以读取嵌入图片的高度和宽度，调用内嵌脚本的方法，或像 [Abusing HTTP Status Codes to Expose Private Information][availability] 中描述的方式，通过嵌入资源的请求的响应状态获得一些信息。

### 源的继承

在页面中通过 `about:blank` 或 `javascript:` URL 执行的脚本会继承打开该 URL 的文档的源，因为这些类型的 URLs 没有包含源服务器的相关信息。


## CORS

Cross-Origin Resource Sharing（[CORS][CORS]），跨源资源共享 或 跨域资源共享，是一种基于 HTTP Header 的机制，用来使服务端指定哪些其他的源可以从这个服务端加载资源。对那些可能对服务器数据产生副作用的 HTTP 请求方法（特别是 GET 以外的 HTTP 请求，或者搭配某些 MIME 类型的 POST 请求），浏览器必须首先使用 OPTIONS 方法发起一个预检请求（preflight request），从而获知服务端是否允许该跨源请求。服务器确认允许之后，才发起实际的 HTTP 请求。在预检请求的返回中，服务器端也可以通知客户端，是否需要携带身份凭证（包括 Cookies 和 HTTP 认证相关数据）。

CORS 请求失败会产生错误，但是为了安全，在 JavaScript 代码层面是无法获知到底具体是哪里出了问题。你只能查看浏览器的控制台以得知具体是哪里出现了错误。

![CORS](/contents/sop-cors-csrf-xss/cors_principle.png)

### HTTP response headers

CORS 响应头字段包括：

* Access-Control-Allow-Origin：指定允许访问该资源的外源 URL，或设定为 `*` 以允许来自所有域的请求
* Access-Control-Expose-Headers：设定除基本的响应头之外，允许浏览器访问的其他响应头
* Access-Control-Max-Age：指定 preflight 请求的结果能被缓存多久
* Access-Control-Allow-Credentials：预检请求的响应通过此 header 控制实际请求发送的时候是否会携带凭证
* Access-Control-Allow-Methods：用于预检请求的响应，指明了实际请求所允许使用的 HTTP 方法
* Access-Control-Allow-Headers：用于预检请求的响应，指明了实际请求中允许携带的 header 字段

### HTTP request headers

* Origin：表明预检请求或实际请求的源站
* Access-Control-Request-Method：用于预检请求，其作用是，将实际请求所使用的 HTTP 方法告诉服务器
* Access-Control-Request-Headers：用于预检请求，将实际请求所携带的 header 字段告诉服务器

### 简单请求（simple request）

若请求满足所有下述条件，则该请求可视为“简单请求”，不会触发“预检请求”：

* 使用下列方法之一：
1. GET
1. HEAD
1. POST
* 除了被用户代理自动设置的 header（如 `Connection`，`User-Agent`）和在 Fetch 规范中定义为 [禁用的 header][forbidden]，允许人为设置的字段为 Fetch 规范定义的 [对 CORS 安全的首部字段集合][safe]：
1. Accept
1. Accept-Language
1. Content-Language
1. Content-Type （需要注意下面的限制）
* Content-Type 的值仅限于下列三者之一：
1. application/x-www-form-urlencoded
1. multipart/form-data
1. text/plain
* 如果请求中使用了 XMLHttpRequest 对象，则需要没有在 XMLHttpRequest.upload 属性返回的对象上注册任何事件监听器，比如给定一个 XMLHttpRequest 实例 `xhr`，没有对 xhr 实例调用过 `xhr.upload.addEventListener()` 来监听上传操作
* 请求中没有使用 [ReadableStream][readable] 对象

![simple request](/contents/sop-cors-csrf-xss/simple-req-updated.png)

### 预检请求（preflight request）

不满足“简单请求”条件的请求，都需要先发送一个 HTTP method 为 `OPTIONS` 的预检请求（preflight request）给外源站点，并根据响应头中的设定，判断是否可以发送实际请求。

![preflight request](/contents/sop-cors-csrf-xss/preflight_correct.png)

### 凭证请求（requests with credentials）

XMLHttpRequest 或 Fetch 与 CORS 的一个有趣的特性是，可以基于 HTTP cookies 和 HTTP 认证信息发送身份凭证。一般而言，对于跨源 XMLHttpRequest 或 Fetch 请求，浏览器不会发送身份凭证信息。如果要发送凭证信息，需要设置 XMLHttpRequest 的某个特殊标志位，或在构造 [Request][request] 对象时指明。

即使是不需要发送预检请求的简单请求，也可以在跨源请求中携带凭证，但如果响应头中没有 `Access-Control-Allow-Credentials: true`，浏览器不会把响应内容返回给请求的发送者。

![with credential](/contents/sop-cors-csrf-xss/cred-req-updated.png)

## CSRF

Cross Site Request Forgery（[CSRF][CSRF]），跨站请求伪造，是指利用用户已经在某网站登录的凭证，在用户不知情的情况下，伪造用户操作此网站的请求。用户在此网站的权限越大，对此网站造成的危害越大。

### 如何阻止跨站访问

大部分框架都提供了内置的 CSRF 支持，如 Joomla，[Spring][spring-csrf]，Struts，Ruby on Rails，.NET 等。

通常的做法是设定一个 CSRF token，一个由服务端生成的随机值，请求需携带这个 token，并由服务端验证请求的合法性。

阻止跨站写操作，可以通过 CSRF token 进行校验。

阻止跨站读操作，需确保该资源是不可嵌入的。阻止跨站嵌入，需确保资源不能通过 [可嵌入资源格式][embed] 使用。浏览器可能不会遵守 Content-Type 头部定义的类型，例如在 HTML 文档外面套上 `<script>` 标签，浏览器会尝试按照 JavaScript 来解析其中的 HTML 内容。当资源不是网站入口时，也可以考虑使用 CSRF token 来防止嵌入。

更多阻止方案，可参考 [Cross-Site Request Forgery Prevention Cheat Sheet][CSRF-cs] 。

## XSS

Cross Site Scripting（[XSS][XSS]），跨站脚本攻击，缩写不使用 CSS 是为了避免与 层叠样式表 混淆。

跨站脚本攻击通常是指对用户通过表单等方式写入的数据未进行合法性校验，导致可能将恶意脚本注入到网站中，并对其他用户造成危害。

通常采取的防范措施是由前端对用户输入内容进行转义等，避免用户上传的恶意脚本能够被直接执行。目前大部分主流的前端框架，也对 XSS 进行了基本的防御。

更多阻止 XSS 的方案，可参考 [Cross Site Scripting Prevention Cheat Sheet][XSS-cs] 。


## 参考资料

* [Same-origin policy][SOP]
* [Cross-Origin Resource Sharing (CORS)][CORS]

[SOP]:https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy
[availability]:https://www.grepular.com/Abusing_HTTP_Status_Codes_to_Expose_Private_Information
[CORS]:https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
[forbidden]:https://fetch.spec.whatwg.org/#forbidden-header-name
[safe]:https://fetch.spec.whatwg.org/#cors-safelisted-request-header
[readable]:https://developer.mozilla.org/zh-CN/docs/Web/API/ReadableStream
[request]:https://developer.mozilla.org/en-US/docs/Web/API/Request
[CSRF]:https://owasp.org/www-community/attacks/csrf
[embed]:https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy#cross-origin_network_access
[XSS]:https://owasp.org/www-community/attacks/xss/
[spring-csrf]:https://docs.spring.io/spring-security/site/docs/current/reference/html5/#csrf
[CSRF-cs]:https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
[XSS-cs]:https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html