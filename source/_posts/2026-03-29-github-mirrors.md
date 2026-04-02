---
id: github-mirrors
title: "【转】【2026最新收集】github国内镜像站，高速访问"
description: "科学访问 GitHub"
date: 2026.03.29 10:34
categories:
    - GFW
tags: [GFW, GitHub]
keywords: GitHub, proxy, mirror, release, raw
cover: /contents/github-mirrors/cover.png
---

- 原文地址：https://blog.csdn.net/qq_38238956/article/details/156717907
- 原文作者：[程序员大龙虾](https://sgdygb.blog.csdn.net/?type=blog)

---

# 一、最新可用GitHub镜像站汇总

以下镜像站经实测验证，按“直接访问型”“文件加速型”“知名项目专属型”分类，标注实时可用性，方便按需选择。

## 1. 直接访问型镜像站（可浏览仓库、查看代码）

此类镜像站完全复刻GitHub界面，支持搜索、浏览仓库、查看代码文件，操作逻辑与官网一致，适合日常代码查阅。

|镜像站序号	|访问方式	|镜像站链接	|当前状态	|备注   |
|:--------|:---------|:--------|:---------|:-------|
|1	|直接访问	|https://bgithub.xyz	|✅ 可用	|界面简洁，响应速度快，支持仓库搜索|
|2	|直接访问	|https://gitclone.com	|✅ 可用	|附带Git Clone加速命令，适合开发者使用|
|3	|直接访问	|https://github.ur1.fun	|✅ 可用	|加载速度快，支持Markdown文档渲染|

**推荐场景**：需在线浏览仓库结构、查看代码细节、复制代码片段时，优先选择`bgithub.xyz`或`kkgithub.com`，加载速度和稳定性最优。

## 2. 文件加速型镜像站（专用于下载Release、压缩包）

此类镜像站主打文件下载加速，无需浏览完整仓库，只需粘贴GitHub文件链接，即可生成高速下载地址，解决大文件下载超时问题。

| 镜像站序号 | 功能类型 | 镜像站链接 | 当前状态 | 使用方法 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | 文件加速 | https://gh-proxy.com/ | ✅ 可用 | 支持批量文件加速，粘贴多个链接可批量生成下载地址 |
| 2 | 文件加速 | https://ghproxy.net/ | ✅ 可用 | 自动识别文件类型，支持断点续传 |
| 3 | 文件加速 | https://ghproxy.homeboyc.cn/ | ✅ 可用 | 适合下载大体积Release包（1GB以上文件稳定） |
| 4 | 文件加速 | http://toolwa.com/github/ | ✅ 可用 | 附带文件大小显示，支持GitHub仓库压缩包一键下载 |
| 5 | 文件加速 | https://github.akams.cn/ | ✅ 可用 | 支持 API、Git Clone、Releases、Archive、Gist、Raw 等资源加速下载，提升 GitHub 文件下载体验。 |

**推荐场景**：下载Release安装包、仓库压缩包（.zip/.tar.gz）时，用`ghp.ci`（简单快捷）或`moeyy.cn/gh-proxy/`（功能全面），下载速度可达10-50MB/s。

## 3. 知名项目专属镜像站（稳定同步热门仓库）

针对GitHub上高人气的项目（如Google、GitHub官方仓库），国内平台提供专属镜像，同步频率更高、稳定性更强，适合长期依赖特定项目的开发者。

| 序号 | 镜像项目范围 | 访问方式 | 镜像站链接 | 当前状态 | 优势 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | GitHub Release文件（全量） | 直接访问 | https://mirrors.tuna.tsinghua.edu.cn/github-release | ✅ 可用 | 清华镜像源，学术场景优先选择，支持按项目名检索Release |
| 2 | GitHub热门项目镜像集合 | 直接访问 | https://gitee.com/organizations/mirrors/projects | ✅ 可用 | 码云（Gitee）官方镜像库，包含 thousands+ 热门开源项目，支持Git Clone |

# 二、Git Clone加速：一行命令配置全局镜像

除了网页端访问，开发者通过Git命令Clone仓库时，可配置全局镜像，无需每次手动修改链接，实现“一次配置，永久加速”。

**方法：配置gitclone.com全局镜像**

1. 打开命令提示符（Windows：Win+R输入`cmd`；Mac/Linux：打开终端）；
1. 输入以下命令并回车：
    ```bash
    git config --global url."https://gitclone.com/".insteadOf https://
    ```
1. 配置完成后，直接用原GitHub链接Clone，Git会自动通过镜像站加速：
    ```bash
    # 示例：Clone TensorFlow仓库，自动走镜像加速
    git clone https://github.com/tensorflow/tensorflow.git
    ```

# 三、使用DNS加速

这个方法测试下来不太稳定，还是镜像站稳定点，当然如果前面的镜像站你都没法使用，可以尝试下这个方式

## 第一步：查询GitHub有效IP地址

1. 打开浏览器，访问站长工具DNS查询页面：http://tool.chinaz.com/dns/

![chinaz](https://alphahinex.github.io/contents/github-mirrors/chinaz.png)

选出可用的ip后，接着下一步

## 第二步：修改系统Hosts文件

1. 打开电脑本地文件夹，路径为：C:\Windows\System32\drivers\etc
1. 找到名为“hosts”的文件（无后缀名），右键选择“用记事本打开”（如果提示权限不足，可先右键选择“属性”-“安全”-“编辑”，赋予当前用户修改权限）
1. 滚动到hosts文件的最后一行，另起一行输入以下内容（IP地址和域名之间用至少一个空格隔开）：
`20.205.243.166 github.com`
1. 输入完成后，按Ctrl+S保存文件，然后关闭记事本

## 第三步：刷新DNS解析缓存

1. 按下键盘上的“Win+R”组合键，打开运行窗口
1. 在输入框中输入“cmd”，按下回车键，打开命令提示符窗口
1. 在命令窗口中输入命令：`ipconfig/flushdns`
1. 按下回车键执行命令，当出现“Windows IP配置 已成功刷新DNS解析缓存”的提示时，说明操作成功

> 发现一款加速专用的开源工具，如果以上都用不了，可以试试https://github.com/docmirror/dev-sidecar

# 参考链接

- https://docs.suanlix.cn/github.html
- https://freevaults.com/category/mirror
- https://ineo6.github.io/hosts/
