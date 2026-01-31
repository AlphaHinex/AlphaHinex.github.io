---
id: tch-material-download
title: "中小学教材下载"
description: "从国家中小学智慧教育平台可免费下载电子版教材"
date: 2026.02.01 10:34
categories:
    - Others
tags: [Others]
keywords: 教材, 小学, 初中, 高中, 电子版教材, 国家中小学智慧教育平台, 开发者工具, curl, PowerShell, accessToken
cover: /contents/tch-material-download/cover.png
---

在 国家中小学智慧教育平台（ https://basic.smartedu.cn/tchMaterial ）注册登录后，可以在线查看国内中小学的各科多版本的电子教材，但网站内并未提供下载方式：

![](https://alphahinex.github.io/contents/tch-material-download/cover.png)

只需借助浏览器的开发者工具，即可获取电子教材的下载链接及权限，从而实现免费下载电子版教材。

通常可通过 `F12` 打开浏览器的开发者工具，切换到 `网络`（Network）选项卡，然后在网站内点击某本教材进行查看，筛选 `Fetch/XHR` 类型包含 `.pdf` 的请求，右键点击请求，选择拷贝，即可获取下载教材必需的内容：

![dev-tools](https://alphahinex.github.io/contents/tch-material-download/dev-tools.png)

## MacOS

MacOS 或其他可使用 `curl` 命令的系统，可以在浏览器中选择复制 curl 脚本，添加 ` -O` 参数后直接在终端中执行，例如：

![curl](https://alphahinex.github.io/contents/tch-material-download/curl.png)

```bash
<从浏览器网络请求中复制出来的 curl 脚本> -O
```

```bash
curl 'https://r1-ndr-private.ykt.cbern.com.cn/edu_product/esp/assets/c3e06fe4-c6b3-49cb-8727-4f8ff69bbfbc.pkg/%E4%B9%89%E5%8A%A1%E6%95%99%E8%82%B2%E6%95%99%E7%A7%91%E4%B9%A6%20%E6%95%B0%E5%AD%A6%20%E4%B8%80%E5%B9%B4%E7%BA%A7%20%E4%B8%8A%E5%86%8C_1756191664314.pdf' \
  -H 'Accept: */*' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Cache-Control: no-cache' \
  -H 'Connection: keep-alive' \
  -H 'Origin: https://basic.smartedu.cn' \
  -H 'Pragma: no-cache' \
  -H 'Referer: https://basic.smartedu.cn/' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: cross-site' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'x-nd-auth: MAC id="7F938B205F876FC3C7550081F114A1A4E86984B1B128A080C1C265F441648C11807F351A86125303937E549D054B402BCE97E759869B3935",nonce="1769667338265:4Z8LXG3U",mac="JCede9B5wOMc2NNugF7xXrB/jeTbT5LuGXV3iKMbdGs="' -O
```

## Windows

![powershell](https://alphahinex.github.io/contents/tch-material-download/powershell.png)

复制出来的 PowerShell 脚本，需要在中间添加一个变量，接收响应内容，之后再保存至文件中：

```powershell
<从浏览器网络请求中复制出来的 PowerShell 脚本 - $seesion 开头的两行>
$response = <从浏览器网络请求中复制出来的 PowerShell 脚本 - Invoke-WebRequest 开始>
Set-Content -Path ".\output.pdf" -Value $response.Content -Encoding Byte
```

例如，复制得到的原始脚本如下：

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0"
Invoke-WebRequest -UseBasicParsing -Uri "https://r1-ndr-private.ykt.cbern.com.cn/edu_product/esp/assets/bdc00134-465d-454b-a541-dcd0cec4d86e.pkg/%E4%B9%89%E5%8A%A1%E6%95%99%E8%82%B2%E6%95%99%E7%A7%91%E4%B9%A6%20%E9%81%93%E5%BE%B7%E4%B8%8E%E6%B3%95%E6%B2%BB%20%E4%B8%80%E5%B9%B4%E7%BA%A7%20%E4%B8%8A%E5%86%8C_1756191804648.pdf" `
-WebSession $session `
-Headers @{
"Accept"="*/*"
  "Accept-Encoding"="gzip, deflate, br, zstd"
  "Accept-Language"="zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6"
  "Origin"="https://basic.smartedu.cn"
  "Referer"="https://basic.smartedu.cn/"
  "Sec-Fetch-Dest"="empty"
  "Sec-Fetch-Mode"="cors"
  "Sec-Fetch-Site"="cross-site"
  "sec-ch-ua"="`"Not(A:Brand`";v=`"8`", `"Chromium`";v=`"144`", `"Microsoft Edge`";v=`"144`""
  "sec-ch-ua-mobile"="?0"
  "sec-ch-ua-platform"="`"Windows`""
  "x-nd-auth"="MAC id=`"7F938B205F876FC3C7550081F114A1A4E86984B1B128A08069DDB0CCD16E82AED7BFBF6EFEB4C139A06C89003DB372C19BCCABACE87F8B7F`",nonce=`"1769668885174:FLJWZYK7`",mac=`"w70gvg0jR9VTjYEwfR0KSEw3oYi/eKrzQj/JI0evC/Y=`""
}
```

在 PowerShell 中执行的脚本如下：

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0"
$response = Invoke-WebRequest -UseBasicParsing -Uri "https://r1-ndr-private.ykt.cbern.com.cn/edu_product/esp/assets/bdc00134-465d-454b-a541-dcd0cec4d86e.pkg/%E4%B9%89%E5%8A%A1%E6%95%99%E8%82%B2%E6%95%99%E7%A7%91%E4%B9%A6%20%E9%81%93%E5%BE%B7%E4%B8%8E%E6%B3%95%E6%B2%BB%20%E4%B8%80%E5%B9%B4%E7%BA%A7%20%E4%B8%8A%E5%86%8C_1756191804648.pdf" `
-WebSession $session `
-Headers @{
"Accept"="*/*"
  "Accept-Encoding"="gzip, deflate, br, zstd"
  "Accept-Language"="zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6"
  "Origin"="https://basic.smartedu.cn"
  "Referer"="https://basic.smartedu.cn/"
  "Sec-Fetch-Dest"="empty"
  "Sec-Fetch-Mode"="cors"
  "Sec-Fetch-Site"="cross-site"
  "sec-ch-ua"="`"Not(A:Brand`";v=`"8`", `"Chromium`";v=`"144`", `"Microsoft Edge`";v=`"144`""
  "sec-ch-ua-mobile"="?0"
  "sec-ch-ua-platform"="`"Windows`""
  "x-nd-auth"="MAC id=`"7F938B205F876FC3C7550081F114A1A4E86984B1B128A08069DDB0CCD16E82AED7BFBF6EFEB4C139A06C89003DB372C19BCCABACE87F8B7F`",nonce=`"1769668885174:FLJWZYK7`",mac=`"w70gvg0jR9VTjYEwfR0KSEw3oYi/eKrzQj/JI0evC/Y=`""
}
Set-Content -Path ".\output.pdf" -Value $response.Content -Encoding Byte
```

![windows](https://alphahinex.github.io/contents/tch-material-download/windows.png)

## 浏览器直接下载

在复制了 `curl` 或 PowerShell 脚本后，也可以直接在浏览器中直接进行下载，但需要在 URL 后面添加 `?accessToken=xxxx` ，否则会提示无权限访问。

以上面复制出的 `curl` 脚本为例：

- URL 为 `curl` 命令后面跟着的一串单引号中内容：`https://r1-ndr-private.ykt.cbern.com.cn/edu_product/esp/assets/c3e06fe4-c6b3-49cb-8727-4f8ff69bbfbc.pkg/%E4%B9%89%E5%8A%A1%E6%95%99%E8%82%B2%E6%95%99%E7%A7%91%E4%B9%A6%20%E6%95%B0%E5%AD%A6%20%E4%B8%80%E5%B9%B4%E7%BA%A7%20%E4%B8%8A%E5%86%8C_1756191664314.pdf`
- `xxxx` 为 `MAC id="xxxx"` 中的内容：`7F938B205F876FC3C7550081F114A1A4E86984B1B128A080C1C265F441648C11807F351A86125303937E549D054B402BCE97E759869B3935`

> `MAC id` 中的 token 具有时效性，失效后需重新获取。

使用浏览器直接访问：https://r1-ndr-private.ykt.cbern.com.cn/edu_product/esp/assets/c3e06fe4-c6b3-49cb-8727-4f8ff69bbfbc.pkg/%E4%B9%89%E5%8A%A1%E6%95%99%E8%82%B2%E6%95%99%E7%A7%91%E4%B9%A6%20%E6%95%B0%E5%AD%A6%20%E4%B8%80%E5%B9%B4%E7%BA%A7%20%E4%B8%8A%E5%86%8C_1756191664314.pdf?accessToken=7F938B205F876FC3C7550081F114A1A4E86984B1B128A080C1C265F441648C11807F351A86125303937E549D054B402BCE97E759869B3935

即可看到页面中有了下载按钮：

![download](https://alphahinex.github.io/contents/tch-material-download/download.png)
