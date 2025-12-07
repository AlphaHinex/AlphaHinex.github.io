---
id: jetbrains-fully-offline-mode
title: "离线环境 JetBrains 远程开发"
description: "本文以 PyCharm 纯离线模式官方文档为例，对其中一些不太清晰的地方进行补充说明，可作为使用 JetBrains IDE 在离线环境进行远程开发的指引。"
date: 2025.12.07 10:34
categories:
    - IDE
tags: [JetBrains]
keywords: JetBrains, offline mode, remote development, PyCharm, JetBrains GateWay, JetBrains Client Downloader, JetBrains Client, JBR, JetBrains Runtime, IDE Backend, HTTP server, GLIBC
cover: /contents/jetbrains-fully-offline-mode/cover.png
---

本文以 [PyCharm 纯离线模式官方文档](https://www.jetbrains.com/help/pycharm/fully-offline-mode.html) 为例，对其中一些不太清晰的地方进行补充说明，可作为使用 JetBrains IDE 在离线环境进行远程开发的指引。

# 适用场景

![overview](https://alphahinex.github.io/contents/jetbrains-fully-offline-mode/cover.png)

- 服务器均无法连接互联网
- 一台或多台远程开发服务器（拥有本地机器中不具备的源码、运行时环境、GPU 等）
- 一台 HTTP 服务器（可以与远程开发环境使用相同服务器）
- 本地机器（无需安装 IDE，本例中即为无需安装 PyCharm）
- 有可联网环境，能下载必须资源，并传输至离线环境

# 主要组件

|名称                        |描述                                         |最终放置位置  |
|:--------------------------|:--------------------------------------------|:-----------|
|JetBrains Client Downloader|下载器，可用来下载其他组件                       |联网环境      |
|IDE Backend                |IDE 后端，作为服务运行在远程开发环境中            |HTTP 服务器   |
|JetBrains Client           |轻量级 IDE，相当于 PyCharm 等                  |HTTP 服务器   |
|JetBrains Gateway          |用来连接 JetBrains Client 和 IDE Backend 的网关|本地机器      |

# 准备工作

在联网环境下载必需文件：

1. 参照 [全平台可用的 JetBrains Client Downloader](https://alphahinex.github.io/2025/10/19/full-platforms-jetbrains-clients-downloader/) 在联网环境准备 JetBrains Client Downloader。
1. 选择 IDE 一个具体版本，获得 Build 号。例如在 [PyCharm 下载页面](https://www.jetbrains.com/pycharm/download/other.html)，找到 `Version 2025.2.4` 的 `Build` 为 `252.27397.106`。

	![build](https://alphahinex.github.io/contents/jetbrains-fully-offline-mode/build.png)

1. 使用 JetBrains Client Downloader 下载 IDE 后端，例如： `./jetbrains-clients-downloader --products-filter PY --build-filter 252.27397.106 --platforms-filter linux-x64 --download-backends ./remote-dev` 。
1. 使用 JetBrains Client Downloader 下载各平台版本的 JetBrains Client，以满足不同操作系统的本地机器远程开发使用，例如：`./jetbrains-clients-downloader --products-filter PY --build-filter 252.27397.106 ./remote-dev/clients` 。
1. 使用 JetBrains Client Downloader 下载本地机器系统版本的 JetBrains GateWay，GateWay 的 Build 号跟 IDE 的可能不完全对应，可从 https://data.services.jetbrains.com/products 选择最相近的 Build 号下载（GateWay 与 IDE Backend 的主版本号需要一致，否则可能看不到 IDE 后端列表）：`./jetbrains-clients-downloader --products-filter GW --build-filter 252.27397.101 --platforms-filter osx-x64 --download-backends ./remote-dev` 。
1. 从 [JetBrains Client Downloader 包](https://download.jetbrains.com/idea/code-with-me/backend/jetbrains-clients-downloader-linux-x86_64-2149.tar.gz) 中提取 `jbr` 目录，作为 `JRE` 稍后使用。

下载内容清单供参考：

```text
remote-dev
├── KEYS
├── backends
│   ├── GW
│   │   ├── JetBrainsGateway-2025.2.4.dmg
│   │   └── products.json
│   ├── PY
│   │   ├── products.json
│   │   └── pycharm-2025.2.4.tar.gz
│   └── products.json
├── clients
│   ├── JetBrainsClient-252.27397.106-aarch64.jbr.win.zip
│   ├── JetBrainsClient-252.27397.106-aarch64.jbr.win.zip.sha256
│   ├── JetBrainsClient-252.27397.106-aarch64.jbr.win.zip.sha256.asc
│   ├── JetBrainsClient-252.27397.106-aarch64.sit
│   ├── JetBrainsClient-252.27397.106-aarch64.sit.sha256
│   ├── JetBrainsClient-252.27397.106-aarch64.sit.sha256.asc
│   ├── JetBrainsClient-252.27397.106-aarch64.tar.gz
│   ├── JetBrainsClient-252.27397.106-aarch64.tar.gz.sha256
│   ├── JetBrainsClient-252.27397.106-aarch64.tar.gz.sha256.asc
│   ├── JetBrainsClient-252.27397.106.jbr.win.zip
│   ├── JetBrainsClient-252.27397.106.jbr.win.zip.sha256
│   ├── JetBrainsClient-252.27397.106.jbr.win.zip.sha256.asc
│   ├── JetBrainsClient-252.27397.106.sit
│   ├── JetBrainsClient-252.27397.106.sit.sha256
│   ├── JetBrainsClient-252.27397.106.sit.sha256.asc
│   ├── JetBrainsClient-252.27397.106.tar.gz
│   ├── JetBrainsClient-252.27397.106.tar.gz.sha256
│   ├── JetBrainsClient-252.27397.106.tar.gz.sha256.asc
│   ├── KEYS
│   ├── force_mirror_unix_timestamp_ms
│   └── minimal_clients_downloader_version
├── force_mirror_unix_timestamp_ms
├── jbr
│   ├── bin
│   ├── conf
│   ├── legal
│   ├── lib
│   └── release
└── minimal_clients_downloader_version
```

除 JetBrains GateWay 安装包放置到本地机器之外，其余内容需传输至 HTTP 服务器。

# HTTP 服务器

以将 `remote-dev` 目录上传至服务器 `/resources/jetbrains/remote-dev` 路径为例，
在远程开发环境服务器中，通过 HTTP 服务（如 Nginx）将 `/resources/jetbrains/remote-dev` 路径发布至 http://192.168.1.16/resources/jetbrains/remote-dev ，获得四个 URL：

1. `productsInfoUrl`：http://192.168.1.16/resources/jetbrains/remote-dev/backends/products.json
2. `clientDownloadUrl`: http://192.168.1.16/resources/jetbrains/remote-dev/clients/
3. `jreDownloadUrl`: http://192.168.1.16/resources/jetbrains/remote-dev/jbr/
4. `pgpPublicKeyUrl`: http://192.168.1.16/resources/jetbrains/remote-dev/KEYS

# 本地机器

## 配置

### macOS

创建四个文件 `productsInfoUrl`、`clientDownloadUrl`、`jreDownloadUrl`、`pgpPublicKeyUrl`，每个文件中存放对应 URL，如：

```bash
$ pwd
/Users/alphahinex/Library/Application Support/JetBrains/RemoteDev
$ ls
clientDownloadUrl jreDownloadUrl    pgpPublicKeyUrl   productsInfoUrl
$ cat clientDownloadUrl
http://192.168.1.16/resources/jetbrains/remote-dev/clients/
```

- 用户级配置，将四个文件放到 `/Users/UserName/Library/Application Support/JetBrains/RemoteDev/` 路径；
- 系统级配置，将四个文件放到 `/Library/Application Support/JetBrains/RemoteDev/`。

> 路径不存在直接创建即可。

### Linux

与 macOS 创建文件相同。

- 用户级配置，将四个文件放到 `$HOME/.config/JetBrains/RemoteDev/`；
- 系统级配置，将四个文件放到 `/etc/xdg/JetBrains/RemoteDev/`。

### Windows

用注册表替代文件。用户级在 `HKEY_CURRENT_USER`，系统级在 `HKEY_LOCAL_MACHINE` 中的 `SOFTWARE\JetBrains\RemoteDev` 下创建字符串值，Name 对应文件名，Data 对应 URL：

![regedit](https://alphahinex.github.io/contents/jetbrains-fully-offline-mode/offline_mode.png)

## 使用

本地机器安装并打开 JetBrains GateWay，配置 SSH 连接至远程开发环境，选择 IDE 版本及工程路径后，等待从 HTTP 服务下载对应资源并上传至远程开发环境 `~/.cache/JetBrains/`。一切顺利的话即可看到由 GateWay 打开的 JetBrains Client 已连接至远程开发环境中启动的 IDE Backend 服务，之后就可以远程开发了。

![gateway](https://alphahinex.github.io/contents/jetbrains-fully-offline-mode/gateway.png)


# Troubleshooting

## 社区版不支持远程开发

IDEA 和 PyCharm 社区版不支持远程开发，需要升级到 Ultimate 或 Pro 等版本，详情见：

https://www.jetbrains.com.cn/remote-development/

> 我可以获得 IntelliJ IDEA Community 和 PyCharm Community 版本的远程开发许可证吗？
>
> IntelliJ IDEA Community Edition 或 PyCharm 不支持远程开发。您需要将订阅升级到 IntelliJ IDEA Ultimate 或 PyCharm Pro。

## Deploy Failed

![failed](https://alphahinex.github.io/contents/jetbrains-fully-offline-mode/failed.png)

在 Linux 环境运行 JetBrains IDE 对于 [GLIBC](https://ftp.gnu.org/gnu/libc/) 有最低版本要求，例如 [PyCharm 2025.2 要求 GLIBC 不低于 2.28](https://www.jetbrains.com/help/pycharm/2025.2/installation-guide.html#requirements)，[IDEA 2023.1 要求 GLIBC 不低于 2.27](https://www.jetbrains.com/help/idea/2023.1/installation-guide.html#requirements)。

当出现类似上图的报错时，可以到远程开发环境检查一下 GLIBC 版本：

```bash
# 检查 GLIBC 版本
$ ldd --version
ldd (GNU libc) 2.17
Copyright (C) 2012 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
由 Roland McGrath 和 Ulrich Drepper 编写。
# 找到 IDE Backend 绑定的 JetBrains Runtime 目录，检查 libjvm.so 依赖的 GLIBC 版本
$ cd ~/.cache/JetBrains/RemoteDev/dist/0915790bcd0d3_pycharm-2025.2.4/jbr/bin/
$ ./java
Error: dl failure on line 582
Error: failed /root/.cache/JetBrains/RemoteDev/dist/0915790bcd0d3_pycharm-2025.2.4/jbr/lib/server/libjvm.so, because /lib64/libm.so.6: version `GLIBC_2.27' not found (required by /root/.cache/JetBrains/RemoteDev/dist/0915790bcd0d3_pycharm-2025.2.4/jbr/lib/server/libjvm.so)
```

此时可降低 IDE Backend 至支持当前 GLIBC 的版本。

## GateWay 中看不到 IDE 列表

以下为推测内容，未经完全验证，仅供参考。

推测 GateWay 是在 `productsInfoUrl` 中从自身版本号往上查找 IDE Backend 的。

`productsInfoUrl` 中包含多个版本的 IDE Backend 时：

- 如果有与 GateWay 版本相匹配的 IDE Backend 版本，IDE 列表显示匹配的版本，否则：
- 如果远程开发环境已经安装了某个版本的 IDE Backend，那么 GateWay 会显示已安装版本；如有更新版本的 IDE Backend 也会显示；
- 如果远程开发环境没有安装任何版本的 IDE Backend，那么 GateWay 只会显示从自身版本号往上查找到的 IDE Backend 最新版本。

所以如果 GateWay 版本高于 `productsInfoUrl` 中 IDE Backend 最高版本时，IDE 列表显示为空。

如出现 IDE 列表为空的情况，可尝试降低 GateWay 版本至与 `productsInfoUrl` 中 IDE Backend 相匹配版本（大版本号相同，Build 号可不同）。

本地机器也可以安装多个版本的 GateWay 来连接不同远程开发环境中不同版本的 IDE Backend。
