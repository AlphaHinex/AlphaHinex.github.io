---
id: httrack-plus-wget
title: "HTTrack + Wget 克隆网站至本地"
description: "HTTrack 打头阵，Wget 查缺补漏"
date: 2023.03.19 10:34
categories:
    - Web
tags: [Web]
keywords: HTTrack, Mirror Site, Wget, recursive, Axure
cover: /contents/covers/httrack-plus-wget.jpeg
---

可能有时我们会希望将整个静态网站克隆至本地，比如在一个纯内网或离线环境中阅读当前最新的 Spring Framework v6.0.6 的 [官方文档](https://docs.spring.io/spring-framework/docs/6.0.6/reference/html/)。

## HTTrack

[HTTrack](https://www.httrack.com/) 就是这样一个工具，能够以一个 URL 为入口，将其中包含的几乎全部（深度 `9999`）静态资源都抓取回来，并将包含该站点的链接修改为相对链接，以便于在本地进行导航浏览。

完成首次克隆后，还可以再次执行进行更新，实现对站点的定时镜像。

在 HTTrack 的 [Download](https://www.httrack.com/page/2/en/index.html) 页面选择适合的版本安装后，即可在命令行中使用。

## Quick Start

HTTrack 有丰富的参数以支持强大的功能，最简单的用法为 `httrack url`，如：

```bash
$ httrack https://www.httrack.com/
```

便可将 HTTrack 的官方网站克隆至本地当前路径下。

> 默认情况下只镜像给出的 URL 站点内的链接，并将站内链接修改为相对路径，便于本地导航。跳转至其他域名的地址不会克隆。

## 基本语法

HTTrack 的基本语法为：

`httrack <url> [-<option>] [+] [-]`

`-<option>` 指定选项，`+`/`-` 过滤需要和不需要的内容。选项和过滤器均可根据需要添加多个。

### 选项

不指定任何选项时，会使用默认配置。在 `man httrack` 中所有标 `*` 的选项均为默认配置：

```txt
  w *mirror web sites
 %f *use proxy for ftp (f0 don't use)
  cN number of multiple connections (*c8)
  RN number of retries, in case of timeout or non-fatal errors (*R1)
 %P *extended parsing, attempt to parse all links, even in unknown tags or Javascript (%P0 don't use)
  NN  name conversion type (0 *original structure, 1+: see below)
  LN  long names (L1 *long names / L0 8-3 conversion)
  K   keep original links (e.g. http://www.adr/link) (K0 *relative link)
  o *generate output html file in case of error (404..) (o0 don't generate)
  X *purge old files after update (X0 keep delete)
  bN  accept cookies in cookies.txt (0=do not accept,* 1=accept)
  u check document type if unknown (cgi,asp..) (u0 don't check, * u1 check but /, u2 check always)
  j *parse Java Classes (j0 don't parse)
  sN  follow robots.txt and meta robots tags (0=never,1=sometimes,* 2=always)
  C  create/use a cache for updates and retries (C0 no cache,C1 cache is prioritary,* C2 test update before)
  f *log file mode
  I *make an index (I0 don't make)
  pN priority mode: (* p3)  *3 save all files
  D  *can only go down into subdirs
  a  *stay on the same address
  --mirror       *make a mirror of site(s) (default)
```

> —— 引自 [Httrack Users Guide (3.10)](https://www.httrack.com/html/fcguide.html)

例：

```bash
# 镜像 http://www.shoesizes.com 至本地 /tmp/shoesizes 路径，镜像深度为 50（默认深度 9999）
$ httrack http://www.shoesizes.com -O /tmp/shoesizes -r50
```

### 过滤器

过滤器一般放在命令的尾部，但也可以与选项混在一起使用，但注意不要放在需要参数的选项和参数中间。

以使用 `www.all.net/test/a.html` 为例，所有 `www.all.net/test/` 开头的链接都会被克隆，其他如 `www.all.net/anything-else` 则不会，因为这是更高一级的目录结构，默认情况下，只会镜像给定路径的下级目录结构中的内容。

在默认情况之外，想要包含（`+`）或排除（`-`）指定链接或特定类型文件时，可使用下列语法：

|语法|含义|
|:--|:---|
|`*`|任意字符|
|`*[file]` or `*[name]`|任意文件或任意名称|
|`*[path]`|任意路径（及文件名）|
|`*[a,z,e,r,t,y]`|a,z,e,r,t,y 中任意字母|
|`*[a-z]`|任意字母|
|`*[0-9,a,z,e,r,t,y]`|0 至 9 及 a,z,e,r,t,y 中任意字母|
|`*[]`|之后没有任意字符|
|`*[< NN]`|大小小于 NN Kbytes|
|`*[> PP]`|大小大于 PP Kbytes|
|`*[< NN > PP]`|小于 NN Kbytes 并且大于 PP Kbytes|

越靠后的过滤条件具有越高的优先级。

例：

|过滤条件|含义|
|:------|:--|
|`+*.com/*`|包含所有带有 `.com` 的链接|
|`+*.com/*[path].zip`|包含 `.com` 地址下的所有 zip 文件|
|`+*.html*[]`|包含 *.html，但不包含如 `www.all.net/index.html?page=10` 的地址|
|`-*.gif*[> 5] -*.zip +*.zip*[< 10]`|排除所有大于 5KB 的 gif 文件，排除所有 zip 文件，但包含小于 10KB 的 zip 文件|

## 动态生成的元素中的链接

HTTrack 功能强大，但对于动态生成的内容中的链接也没什么好方法。

当克隆至本地的内容与源站差异较大时，需要结合实际情况进行分析，可以查看执行 `httrack` 命令后生成的 `hts-log.txt` 及 `hts-err.txt` 文件，或直接查看入口地址文件源码，查找问题原因。

比如使用 Axure 制作的原型导出的 html 格式内容，是由脚本在指定元素中动态创建的目录结构，每个节点对应一个 html 页面。

这时可以先使用 `httrack` 将站点框架克隆下来，获得那些未自动探测到的页面链接后，再使用 HTTrack 或 [Wget](https://www.gnu.org/software/wget/) 将这部分内容下载回来作为补充。

> `wget -r <url>` 同样可以将指定路径及相关链接内容下载至本地，默认最大深度为 `5`。

下面这段神秘代码，在 Axure 生成的 html 页面的 Console 中执行，可以获得到目录中所有页面的链接相对路径：

```js
let links='';$('.sitemapPageLink').each((i,e) => {links += e.getAttribute('nodeurl') + '\r\n';});console.info(links);
```