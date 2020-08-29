---
id: gitee-pages
title: "联通 4G 访问 GitHub Pages 受阻肿么办？"
description: "要不要试试给联通客服打电话？"
date: 2020.08.30 10:34
categories:
    - Git
tags: [Git, GitHub]
keywords: Git, GitHub, GitHub Pages, gitee, 码云，Gitee Pages
cover: /contents/gitee-pages/cover.png
---

联通 4G 抽风性的无法正常访问 GitHub Pages，GitHub 有时候也抽，哥俩抽的频率还不同步。

这时候有域名和主机的朋友可以考虑架个 Nginx 反向代理一下，那没有条件的朋友们如何创造条件也要上呢？

Gitee（https://gitee.com/），是一个不错的选择，可以同步 GitHub Pages 仓库，并提供 Gitee Pages 功能。

注册账号后新建仓库，选择 `导入已有仓库`，点击创建，即可将 GitHub Pages 的仓库迁移到 Gitee 上来。

导入仓库之后，在服务下拉栏下选择 `Gitee Pages` 可进行相关配置。完成后即可访问 Gitee Pages 对应地址，如：https://alphahinex.gitee.io/acp

![service](/contents/gitee-pages/service.png)

### 注意

1. Gitee 上的仓库若要与 GitHub 上的仓库内容保持一致，需 **手动** 点击 Gitee 仓库首页上的强制同步按钮
1. 不同于 GitHub，Gitee Pages 的发布过程没找到可以查询的地方，只能跟着感觉走，页面手动刷到天长地久。经验证，在手动更新代码仓库内容之后，**会** 自动触发 Gitee Pages 的刷新。

![GitHub Pages Deployments](/contents/gitee-pages/github-pages-deployments.png)
