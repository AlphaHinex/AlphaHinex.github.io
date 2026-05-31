---
id: accountsd
title: "【译】Accountsd：如何解决 Mac 上的高 CPU 占用问题"
description: "风扇超负荷运转的元凶"
date: 2026.05.31 10:34
categories:
    - Mac
tags: [Mac]
keywords: macOS, accountsd, Spotlight, cpu usage, SMC, NVRAM
cover: /contents/covers/accountsd.jpg
---

- 原文地址：https://www.macrumors.com/guide/accountsd/
- 原文作者：[Joe Rossignol](https://www.macrumors.com/author/joe-rossignol/)

---

在 [macOS Catalina 10.15.7](https://www.macrumors.com/2020/09/24/apple-releases-macos-catalina-10-15-7/) 版本发布后，越来越多的用户遇到了一个名为 “**accountsd**” 的系统进程在活动监视器中占用 CPU 过高的问题，导致 Mac 运行变慢。

Apple 支持社区的一位用户分享了一张 “accountsd” CPU 占用率超过 400% 的截图，并表示这导致了他 2018 款 MacBook Pro “无法使用”。

![](https://alphahinex.github.io/contents/covers/accountsd.jpg)

虽然这个问题多年来偶尔会出现，但在 macOS Catalina 10.15.7 发布后，[Apple 支持社区](https://discussions.apple.com/thread/251846520?page=1)、[MacRumors 论坛](https://forums.macrumors.com/threads/accountsd-mail-process-and-cpu-usage.2212236/page-3)、[Twitter](https://twitter.com/search?q=%22accountsd%22%2010.15.7&src=typed_query&f=live)、[Reddit](https://www.reddit.com/r/mac/comments/j05c8e/user_reports_show_that_macos_10157_clogs_up_the/)、[Stack Exchange](https://apple.stackexchange.com/questions/182059/why-is-the-accountsd-process-eating-so-much-cpu/402322#402322) 等平台上的相关抱怨明显增多，用户们都在尝试排查这个问题。

## accountsd 是什么？

Accountsd 是一个守护进程，属于 [Accounts 框架](https://developer.apple.com/documentation/accounts) 的一部分。Apple 的开发者文档指出，该框架帮助用户从应用程序内部访问和管理他们的外部账户，而无需输入登录凭证。

> Accounts 框架提供对存储在 Accounts 数据库中的用户账户的访问权限，该数据库由系统管理。一个账户存储了某个特定服务（如 Twitter）的登录凭证，你可以使用这些凭证向该服务进行身份验证。当你将 Accounts 框架集成到你的应用程序中时，你无需自行存储账户登录信息。而是由用户授权你的应用程序使用他们的账户登录凭证，从而无需输入用户名和密码。如果用户的 Accounts 数据库中不存在某个特定服务的账户，你可以让用户在你的应用程序内创建并保存一个账户。

## 如何解决 accountsd 的 CPU 占用问题？

受影响的用户提供了各种可能的解决方案，但效果可能因人而异。

有些用户通过在 系统偏好设置 > Apple ID > 概览 > 退出登录 他们的 Apple ID 账户，重启 Mac，然后重新登录账户来解决该问题，但这并非对所有人都有效。

一些用户通过 [重置 Mac 的 SMC](https://support.apple.com/en-us/HT201295) 和/或 [NVRAM](https://support.apple.com/en-us/HT204063) 解决了该问题。

Stack Exchange 上的一位用户认为该问题与 Mac 上文件索引的一个 bug 有关。他们的解决方案是通过进入 系统偏好设置 > Spotlight > 隐私 ，添加（+）你的存储驱动器（默认为“Macintosh HD”）到 “防止 Spotlight 在这些位置中搜索” 列表中，然后从列表中移除（-）该驱动器，Mac 便会开始重新索引。重新索引过程可能会暂时拖慢你的 Mac，因此建议在夜间执行这些步骤。

还有些更进一步的故障分析，一些用户成功解决问题的方式是导航到 “~/Library/Accounts” 路径并将文件 “Accounts4.sqlite” 重命名为 “Accounts4.sqlite.testbackup”，或者使用更复杂的终端命令，但需小心执行，因为这些解决方案都可能会对你的 iCloud 账户或同步造成冲击。

苹果尚未承认此问题。如果发布了修复该问题的软件更新，我们将相应更新本文。

相关论坛：[macOS Catalina](https://forums.macrumors.com/forums/macos-catalina.208)
