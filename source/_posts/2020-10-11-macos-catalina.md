---
id: macos-catalina
title: "macOS Catalina 飞不起来了？"
description: "拢共分四步"
date: 2020.10.11 10:34
categories:
    - Mac
tags: [Mac]
keywords: Mac, macOS, macOS Catalina, 慢
cover: /contents/macos-catalina/cover.jpeg
---

自 macOS Catalina（10.15）发布之日（2019.10.08）起，便听到了不少负面反馈，迟迟没敢进行升级。

一年之后 Catalina 已经迎来了 `10.15.7` 版本，心想也差不多稳定了，就趁国庆假期更新了一下，没想到还是

## 翻车了！

升级过程还算顺利，但升级完之后，明显的感到了系统的卡顿，不再有起飞的感觉了，仿佛眼前的 Mac 已不再是 Mac ……

虽然我的 Mac 已经服役了五年，中间经历了电池鼓包不在召回范围，MagSafe 2 磁性接口烫得能退毛，风扇声音戴耳机都盖不住，连 U 口时 iPhone 像钟摆一样连上又断开、断开又连上无法充电，但在使用 macOS Mojave 时，起码还是不用我等它的。

升级个系统就把飞机改成在地上开有点不能接受，折腾起来。

## Round 1

先通过系统自带的活动监视器（Activity monitor）查看 CPU 使用情况，占用 CPU 最多的是一个叫做 mdworker 的进程，有的时候是 mds 或 mds_stores 等，从进程后面的用户可以发现，mdworker 的用户是 `_spotlight`，也就是系统自带的 `聚焦搜索`。这些进程就是在为聚焦搜索进行索引，这个过程可能会持续几小时甚至一天半天，等索引完毕后，进程的 CPU 使用率会下降，卡顿现象也会有所缓解。对待此问题，采取的对策就是：死等！

## Round 2

另外一个明显的不适来自 [Alfred](https://www.alfredapp.com/)，首先是不能通过 Alfred 直接打开日历、计算器等系统应用了，其次是打开应用时特别慢。开始以为是我用的 Alfred 版本比较旧，不适应新系统，更新到最新的 v4 版之后问题依旧。查看 Alfred 的 Preferences，发现在 `Search Scope` 中没有系统应用所在路径了，添加进去就可以找到了。

![alfred](/contents/macos-catalina/alfred.jpg)

但是打开应用慢的问题依旧存在，现象是选择应用后在 Dock 中应用图标跳啊跳，跳啊跳，跳啊跳，等它跳够了心情好了的时候才会打开界面 ……

## Round 3

偶然发现在不联网的时候，打开应用并不慢，在代理软件中也发现了应用在 Dock 里跳动时会有一些奇怪的请求发往 ocsp.apple.com 。在 `/etc/hosts` 里增加一条：

```hosts
0.0.0.0 ocsp.apple.com
```

之后再打开应用，迅雷不及掩耳盗铃之势！至此，Mac 又恢复了昔日指哪打哪飞一般的感觉。

## Round 4

除了上述问题之外，新系统还带来了一些变化，比如：

* 打开终端时会提示 `The default interactive shell is now zsh.`
* 之前连接 Windows 远程桌面的应用 Remote Desktop Connection 已无法使用，可使用 Microsoft Remote Desktop 替代
* Catalina 的亮点 `随航` 需要 [2016 年以后的 MBP](https://support.apple.com/en-us/HT210380#systemrequirements)，洗洗睡吧

## 参考资料

* [Mac刚升级以后会变慢是正常现象](https://codechina.org/2020/05/mac-update-slow/)
* [终于解决 Catalina 打开 app 缓慢的问题](https://v2ex.com/t/622672)
* [终极 Shell](http://macshuo.com/?p=676)
* [老款的macbook 如何使用随航（sidecar)](https://zhuanlan.zhihu.com/p/87527750)
* [「Microsoft Remote Desktop 10 」适用于 Mac 的 Windows 远程桌面连接客户端](https://www.maczd.com/post/microsoft-remote-desktop-mac.html)
