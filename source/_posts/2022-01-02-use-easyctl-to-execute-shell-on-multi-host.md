---
id: use-easyctl-to-execute-shell-on-multi-host
title: "使用 easyctl 在多主机上并行执行脚本"
description: "Linux, Mac 均可使用"
date: 2022.01.02 10:34
categories:
    - DevOps
tags: [Go, DevOps, Shell, Linux, Mac]
keywords: easyctl, ssh, multi-host
cover: /contents/covers/use-easyctl-to-execute-shell-on-multi-host.png
---

当有大批量主机，需要进行类似的操作时，推荐一个不需要配置 [SSH 免密登录](https://alphahinex.github.io/2020/09/13/ssh-authorized-keys/) 的简单工具 —— [easyctl][ec]。


easyctl
=======

上面这个场景，主要使用到了 easyctl 中的 [执行指令集 - 跨主机并行执行shell](https://weiliang-ms.github.io/easyctl/%E6%89%A7%E8%A1%8C%E6%8C%87%E4%BB%A4%E9%9B%86/01%E8%B7%A8%E4%B8%BB%E6%9C%BA%E5%B9%B6%E8%A1%8C%E6%89%A7%E8%A1%8Cshell.html)，easyctl 提供的其他功能及使用方式，可见 [源码][ec] 或文档中的其他部分。

因为 `跨主机并行执行 shell` 这个功能实际就是通过 ssh 连接到各主机，并行执行指定命令，并将最终直接结果汇总，所以理论上只要支持 ssh 的环境，都可以使用 easyctl 的这个功能。


获取 easyctl 可执行文件
=====================

例如，在 Mac 环境下，可以按照 [README](https://github.com/weiliang-ms/easyctl/blob/master/README.md) 中提供的链接，下载 [Release](https://github.com/weiliang-ms/easyctl/releases/v0.7.13-alpha/) 中编译好的 [Mac OS v0.7.13-alpha](https://github.com/weiliang-ms/easyctl/releases/download/v0.7.13-alpha/easyctl-v0.7.13-alpha-darwin-amd64.tar.gz) 版本，也可以参照 [Mac 编译](https://github.com/weiliang-ms/easyctl#mac-%E7%BC%96%E8%AF%91) 部分的内容，使用源码编译最新版，或者直接使用 [mac-build](https://github.com/AlphaHinex/easyctl) 分支源码进行编译。

编译时需注意：

1. [Go](https://golang.google.cn/dl/) 版本不得低于 v1.16
1. 需要设置代理时，可参照 https://goproxy.cn/

可编译为可执行文件（不需要 Go 运行环境），如：

```bash
# 编译为可在当前环境运行的可执行文件
$ go build
# 编译为可在其他环境运行的可执行文件
$ GOOS=windows GOARCH=amd64 go build
```

> 可用的 GOOS 和 GOARCH 可参照 https://golang.google.cn/doc/install/source#environment 。


批量执行脚本
==========

准备配置文件
----------

可先通过如下命令生成一份配置文件模板：

```bash
$ ./easyctl exec shell
INFO[0000] 生成配置文件样例, 请携带 -c 参数重新执行 -> config.yaml
```

下面是一个复杂一些的配置文件：

```yaml
server:
  - host: "/path/to/server-list.txt"
    username: root
    password: 123456
    port: 22
  - host:
    - 192.168.69.175
    - 192.168.71.[159-162]
    - 10.10.10.1-3
    - "server-list2.txt"
    username: root
    password: 123456
    port: 22
  - host: 192.168.0.1
    username: root
    password: 123456
    port: 22
  - host:
    - 192.168.1.1-3
    - 192.168.1.4
    - 192.168.1.4
    username: root
    password: 123456
    port: 22
  - host: 10.10.10.[1:3]
    username: root
    privateKeyPath: ~/.ssh/id_rsa
    password: ""
    port: 22
excludes:
  - 192.168.235.132
#script: "1.sh"
script: "date"
```

`server` 是一个数组，包含 ssh 到一个远程 host 所必须的参数；`server.host` 可以是单个 IP、地址段、IP 地址列表文件，或他们的数组；`script` 命令，或脚本文件。

当配置中需要使用地址列表文件或脚本文件时，可使用相对于执行 easyctl 命令时所在的路径的相对路径，或文件的绝对路径。


执行及检查结果
------------

传入配置文件，即可批量执行，并获得执行结果：

```bash
$ ./easyctl exec shell -c config.yaml
...
|   IP ADDRESS   | CMD  | EXIT CODE | RESULT | OUTPUT |           EXCEPTION            |
|----------------|------|-----------|--------|--------|--------------------------------|
|   10.10.10.1   | date |    -1     |  fail  |        |           10.10.10.1           |
|                |      |           |        |        |   ssh会话建立失败->dial tcp    |
|                |      |           |        |        |   10.10.10.1:22: i/o timeout   |
|   10.10.10.2   | date |    -1     |  fail  |        |           10.10.10.2           |
|                |      |           |        |        |   ssh会话建立失败->dial tcp    |
|                |      |           |        |        |   10.10.10.2:22: i/o timeout   |
|   10.10.10.3   | date |    -1     |  fail  |        |           10.10.10.3           |
|                |      |           |        |        |   ssh会话建立失败->dial tcp    |
|                |      |           |        |        |   10.10.10.3:22: i/o timeout   |
|  192.168.0.1   | date |    -1     |  fail  |        |          192.168.0.1           |
|                |      |           |        |        |   ssh会话建立失败->dial tcp    |
|                |      |           |        |        |  192.168.0.1:22: i/o timeout   |
|  192.168.1.1   | date |    -1     |  fail  |        |          192.168.1.1           |
|                |      |           |        |        |   ssh会话建立失败->dial tcp    |
|                |      |           |        |        |    192.168.1.1:22: connect:    |
|                |      |           |        |        |       connection refused       |
```

[ec]:https://github.com/weiliang-ms/easyctl