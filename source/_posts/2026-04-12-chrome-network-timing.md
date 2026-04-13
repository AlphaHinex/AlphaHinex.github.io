---
id: chrome-network-timing
title: "【转】谷歌浏览器network请求时间（stalled，DNS Lookup，Waiting）分析以及解决方案"
description: "https://developer.chrome.com/docs/devtools/network/reference?hl=zh-cn#timing-explanation"
date: 2026.04.12 10:26
categories:
    - Chrome
tags: [Chrome, Web]
keywords: chrome, network, stalled, initial connection, tcp, wireshark
cover: /contents/chrome-network-timing/cover.png
---

- 原文地址：https://blog.csdn.net/u010633266/article/details/88722980
- 原文作者：[_双眸](https://blog.csdn.net/u010633266)

---

network工具功能强大，能够让我看到网页加载的信息，比如加载时间，和先后顺序，是否是并行加载，还是堵塞加载。

![network](https://alphahinex.github.io/contents/chrome-network-timing/network.jpeg)

默认情况下有八列:
1. Name:表示加载的文件名。
2. Method:表示请求的方式。
3. Status:表示状态码（200为请求成功，304表示从缓存读取）。
4. Type:表示文件的MIME Type的类型。
5. Initiator:表示发出这个文件请求的发出者。
6. Size:表示文件大小。
7. Time:表示每个请求的总时长。
8. Timeline:以图表的形式显示元素的请求和加载情况。

　　当然内容不仅仅先于以上8个，右击上面八个任意一个选项卡可以弹出一个菜单，可以查看更多内容:

![more](https://alphahinex.github.io/contents/chrome-network-timing/more.jpeg)

## （1）Stalled（阻塞）

一般常规的优化包括：css、js合并压缩、图片压缩、雪碧图、静态资源全部上CDN，一般这些都做了但是慢的话，这是时候问题一般出在Stalled阻塞了，如下图:

![stalled](https://alphahinex.github.io/contents/chrome-network-timing/stalled.jpeg)

**什么是stalled呢？下面是一段比较容易懂的解释：**

> Time the request spent waiting before it could be sent. This time is
> inclusive of any time spent in proxy negotiation.Additionally, this
> time will include when the browser is waiting for an already
> established connection to become available for re-use, obeying
> Chrome’s maximum six TCP connection per origin rule.

也即是从TCP连接建立完成，到真正可以传输数据之间的时间差。先让我们要分析TCP连接为什么要等待这么久才能用？用Wireshark抓包发现(如下图)，TCP连接过程中有多次重传，直到达到最大重传次数后连接被客户端重置。

![wireshark](https://alphahinex.github.io/contents/chrome-network-timing/wireshark.png)

**为什么会发生重传呢？**

> The sender waits for an ACK for the byte-range sent to the client and
> when not received, resends the packets, after a particular interval.
> After a certain number of retries, the host is considered to be “down”
> and the sender gives up and tears down the TCP connection.

TCP三次握手后，发送端发送数据后，一段时间内（不同的操作系统时间段不同）接收不到服务端ACK包，就会以 某一时间间隔(时间间隔一般为指数型增长)重新发送，从重传开始到接收端正确响应的时间就是stalled阶段。而重传超过一定的次数（windows系统是5次），发送端就认为本次TCP连接已经down掉了，需要重新建立连接。 对比以下，没有重传的http请求过程。如下图：

![no-resend](https://alphahinex.github.io/contents/chrome-network-timing/no-resend.jpeg)

stalled阶段是TCP连接的检测过程，如果检测成功就会继续使用该TCP连接发送数据，如果检测失败就会重新建立TCP连接。所以出现stalled阶段过长，往往是丢包所致，这也意味着网络或服务端有问题。

另外，需要注意的是：浏览器对同一个主机域名的并发连接数有限制，因此如果当前的连接数已经超过上限，那么其余请求就会被阻塞，等待新的可用连接；此外脚本也会阻塞其他组件的下载，被阻塞的请求的stalled也会很长。

**总结一下：**
**1. 单一服务发送时候stalled过长，往往是丢包所致，这也意味着网络或服务端有问题。**
**2. 多个服务并发导致stalled过长，是浏览器对同一个主机域名的并发连接数有限制，过长的请求是被阻塞了，处在队列中等待tcp连接**

所以，stalled阶段是浏览器**得到要发出这个请求的指令，到请求可以发出的等待时间**，一般是代理协商、以及等待可复用的TCP连接释放的时间，不包括DNS查询、建立TCP连接等时间等。

> 优化措施：
> 1. 将资源合理分布到多台主机上，可以提高并发数，但是增加并行下载数量也会增大 开销，这取决于带宽和CPU速度，过多的并行下载会降低性能；
> 2. 脚本置于页面底部；

## （2）DNS Lookup（域名解析）

请求某域名下的资源，浏览器需要先通过DNS解析器得到该域名服务器的IP地址。在DNS查找完成之前，浏览器不能从主机名那里下载到任何东西。

> 优化措施： 　　
> 1. 利用DNS缓存（设置TTL时间）；
> 2. 利用Connection:keep-alive特性建立持久连接，可以在当前连接上进行多个请求，无需再进行域名解析；

## （3）Initial connection（初始化连接）

TCP建立连接的三次握手时间

## （4）Request sent（发送请求）

请求第一个字节发出前到最后一个字节发出后的时间，也就是上传时间。

发送HTTP请求的时间（从第一个bit到最后一个bit）

> 优化措施： 　　
> 1. 减少HTTP请求，可以使用CSS Sprites、内联图片、合并脚本和样式表等；
> 2. 对不常变化的组件添加长久的Expires头（相当于设置久远的过期时间），在后续的页面浏览中可以避免不必要的HTTP请求；

## （5）Waiting（等待响应）

请求发出后，到收到响应的第一个字节所花费的时间(Time To First Byte)。

通常是耗费时间最长的。从发送请求到收到响应之间的空隙，会受到线路、服务器距离等因素的影响。

> 优化措施： 　　
> 1. 使用CDN，将用户的访问指向距离最近的工作正常的缓存服务器上，由缓存服务器直接响应用户请求，提高响应速度；

## （6）Content Download（下载）

收到响应的第一个字节，到接受完最后一个字节的时间，就是下载时间。

下载HTTP响应的时间（包含头部和响应体）

> 优化措施：
> 1. 通过条件Get请求，对比If-Modified-Since和Last-Modified时间，确定是否使用缓存中的组件，服务器会返回“304Not Modified”状态码，减小响应的大小； 　　
> 2. 移除重复脚本，精简和压缩代码，如借助自动化构建工具grunt、gulp等；
> 3. 压缩响应内容，服务器端启用gzip压缩，可以减少下载时间；
