---
id: full-platforms-jetbrains-clients-downloader
title: "全平台可用的 JetBrains Client Downloader"
description: "官方仅提供了 Linux 下可用的脚本，稍加调整即可在全平台下使用"
date: 2025.10.19 10:34
categories:
    - Java
tags: [Java, Linux]
keywords: JetBrains, JetBrains Client Downloader, jetbrains-clients-downloader, JetBrains Client, JBR, JetBrains Runtime, JDK, OpenJDK, JRE
cover: /contents/full-platforms-jetbrains-clients-downloader/cover.png
---

# JetBrains Client Downloader

JetBrains Client Downloader 是由 JetBrains 官方提供的从 JetBrains 服务器下载所需文件的脚本，可以用来下载 JetBrains 提供的各类产品。

> JetBrains Client Downloader
>
> Use this script to download the required files from JetBrains servers and to place them on end-users’ workstations in air-gapped environments.
> 
> [Linux x86-64 .tar.gz](https://download.jetbrains.com/idea/code-with-me/backend/jetbrains-clients-downloader-linux-x86_64-2149.tar.gz)
> 
> —— https://www.jetbrains.com/code-with-me/on-prem/#downloads

在 [Offline (local storage) mode](https://www.jetbrains.com/help/cwm/guest-local-storage-setup.html) 中介绍了这个脚本的来历和目标使用场景：

> Lobby Guests Local Storage is an on-premises lobby server feature that lets you download required Code With Me guest files from JetBrains to a dedicated local storage in your network and distribute them among users.

> Since version 1698, the "mirror-guests" script has been renamed to `jetbrains-clients-downloader` and comes as a separate file from [distributive page](https://www.jetbrains.com/code-with-me/on-prem).

该脚本最初是为了镜像在离线环境中使用的 Code With Me 客户端文件而设计的，后续更名并独立出来。

**JetBrains Client 与 IDE Backend 对应，分别代表 [远程开发](https://www.jetbrains.com.cn/remote-development/) 时，用户本地运行的 JetBrains IDE 瘦客户端以及在远程服务端运行的 IDE 后端服务。**

## The script supports Linux only

在 [Fully offline mode|PyCharm](https://www.jetbrains.com/help/pycharm/fully-offline-mode.html) 等文档中提到 JetBrains Client Downloader 时，均强调了该脚本仅支持 Linux 平台：

> The script supports Linux only.
> 
> It accepts product code, version, build number, platform, and EAP builds as the filtering parameters.

下载 `Linux x86-64 .tar.gz` 并解压后，可以看到由官方提供的这个仅支持 Linux 环境的脚本中，包含的主要内容如下：

```text
├── LICENSE.txt
├── bin
│   └── jetbrains-clients-downloader
├── jbr
├── lib
│   ├── ... .jar
│   ├── jetbrains-clients-downloader-2149.jar
│   └── ... .jar
└── third-party-licenses
```

其中 `bin/jetbrains-clients-downloader` 是 `Shell` 脚本，其主要作用是拼接实际执行的 Java 命令：

```sh
#!/bin/sh

set -e -f -u

APP_HOME="$(cd "$(dirname "$0")/.."; pwd)"

# Determine the Java command to use to start the JVM.
if [ -n "${JETBRAINS_CLIENTS_DOWNLOADER_JAVA_HOME:-}" ] ; then
    if [ -x "$JETBRAINS_CLIENTS_DOWNLOADER_JAVA_HOME/jre/sh/java" ] ; then
        # IBM's JDK on AIX uses strange locations for the executables
        JAVACMD="$JETBRAINS_CLIENTS_DOWNLOADER_JAVA_HOME/jre/sh/java"
    else
        JAVACMD="$JETBRAINS_CLIENTS_DOWNLOADER_JAVA_HOME/bin/java"
    fi
    if [ ! -x "$JAVACMD" ] ; then
        die "ERROR: JETBRAINS_CLIENTS_DOWNLOADER_JAVA_HOME is set to an invalid directory: $JETBRAINS_CLIENTS_DOWNLOADER_JAVA_HOME

Please set the JETBRAINS_CLIENTS_DOWNLOADER_JAVA_HOME variable in your environment to match the
location of your Java installation."
    fi
    echo "Using $JAVACMD"
else
    JAVACMD="$APP_HOME/jbr/bin/java"
fi

# shellcheck disable=SC2086
exec "$JAVACMD" ${JETBRAINS_CLIENTS_DOWNLOADER_JVM_OPTS:-} -cp "$APP_HOME/lib/*" "com.jetbrains.codeWithMe.lobby.DownloaderMainKt" "$@"
```

所以只要我们使用合适的 JDK 或 JRE，就可以用 `java -cp "./lib/*" "com.jetbrains.codeWithMe.lobby.DownloaderMainKt"` 来替换 `jetbrains-clients-downloader` 命令了。

# 通过 Java 环境在其他平台使用 JetBrains Client Downloader

`jetbrains-clients-downloader-2149.jar` 中 class 文件的版本是 `61`，即需要 Java 17 及以上版本运行。

> 从自带的 `jbr/release` 中也可以查看到打包的 Java 环境版本为 `17.0.6`。

可从 Oracle、OpenJDK 或其他三方网站下载 Java 运行环境，如：

- https://www.oracle.com/cn/java/technologies/downloads/
- https://jdk.java.net/archive/
- https://www.openlogic.com/openjdk-downloads

也可以直接下载 JBR 的其他系统版本。

## JBR

JBR 是 [JetBrains Runtime](https://github.com/JetBrains/JetBrainsRuntime)，即 JetBrains 基于 [OpenJDK](https://github.com/openjdk/jdk) 为在 Windows、macOS 及 Linux 上运行 IntelliJ 平台产品构建的运行时环境。

JetBrains Client Downloader `Linux x86-64 .tar.gz` 包中打包的是 Linux 版本的 JBR，可以在 [Releases](https://github.com/JetBrains/JetBrainsRuntime/releases) 页面选择目标环境可用的版本下载，如：[17.0.11-b1312.2](https://github.com/JetBrains/JetBrainsRuntime/releases/tag/jbr-release-17.0.11b1312.2)、[17.0.6-b653.34](https://github.com/JetBrains/JetBrainsRuntime/releases/tag/jbr-release-17.0.6b653.34) 等（`Platform` 选择目标操作系统，`Flavour` 任意）。

## 总结

在非 Linux 平台使用 JetBrains Client Downloader 步骤：

1. 准备目标平台可用的 Java 17 及以上运行环境，如；`./jbr-17.0.11-osx-x64-b1312.2/Contents/Home/bin/java`；
1. 从官方提供的 JetBrains Client Downloader 下载包中提取 `lib` 路径；
1. 使用 `./jbr-17.0.11-osx-x64-b1312.2/Contents/Home/bin/java -cp "./lib/*" "com.jetbrains.codeWithMe.lobby.DownloaderMainKt" -h` 命令即可查看 JetBrains Client Downloader 帮助信息。

# 使用 JetBrains Client Downloader 下载

基本用法：

```bash
java -cp "./lib/*" "com.jetbrains.codeWithMe.lobby.DownloaderMainKt" [FILTERS] OUTPUT-DIRECTORY
```

## 查看产品代码

在 `--products-filter` 参数中传入非法值查看所有产品编码：

```bash
java -cp "./lib/*" "com.jetbrains.codeWithMe.lobby.DownloaderMainKt" --products-filter showall ./test
```

```text
Available product codes:
  OC (AppCode)
  CL (CLion)
  CL (CLion Nova)
  DB (DataGrip)
  DS (DataSpell)
  FLIJ (Fleet Backend)
  GO (GoLand)
  GW (Gateway)
  IC (IntelliJ IDEA Community Edition)
  IU (IntelliJ IDEA Ultimate)
  PC (PyCharm Community Edition)
  PY (PyCharm)
  PS (PhpStorm)
  RM (RubyMine)
  RR (RustRover)
  VSCAI (JetBrains AI Assistant for Visual Studio Code)
  VSCRS (ReSharper for Visual Studio Code)
  WS (WebStorm)
```

所有产品信息可从 https://data.services.jetbrains.com/products 获取。

## 下载

以下载 RustRover 253.25908.32 mac 版本为例：

```bash
java -cp "./lib/*" "com.jetbrains.codeWithMe.lobby.DownloaderMainKt" \
--products-filter RR \
--build-filter 253.25908.32 \
--include-eap-builds \
--platforms-filter osx-x64 \
--download-backends \
./backend
```

```text
├── KEYS
├── backends
│   ├── RR
│   │   ├── RustRover-253.25908.32.dmg
│   │   └── products.json
│   └── products.json
├── force_mirror_unix_timestamp_ms
└── minimal_clients_downloader_version
```

不添加 `--download-backends` 时会下载对应的 JetBrains Client：

```bash
java -cp "./lib/*" "com.jetbrains.codeWithMe.lobby.DownloaderMainKt" \
--products-filter RR \
--build-filter 253.25908.32 \
--include-eap-builds \
--platforms-filter osx-x64 \
./client
```

```text
├── JetBrainsClient-253.25908.32.sit
├── JetBrainsClient-253.25908.32.sit.sha256
├── JetBrainsClient-253.25908.32.sit.sha256.asc
├── KEYS
├── force_mirror_unix_timestamp_ms
└── minimal_clients_downloader_version
```

> 访问 https://data.services.jetbrains.com/products 不稳定时，可以先将其下载保存至本地（如 `products.json`），再添加 `--products-json-location=http://localhost:8080/products.json` 参数即可使用本地产品列表进行下载。

# 附录

- `2149` 版 JetBrains Client Downloader 中的 [lib.zip](https://github.com/AlphaHinex/AlphaHinex.github.io/raw/refs/heads/develop/source/contents/full-platforms-jetbrains-clients-downloader/lib.zip)
- 20251017 [products.json.zip](https://github.com/AlphaHinex/AlphaHinex.github.io/raw/refs/heads/develop/source/contents/full-platforms-jetbrains-clients-downloader/products.json.zip)