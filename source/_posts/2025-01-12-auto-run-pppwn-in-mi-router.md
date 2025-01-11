---
id: auto-run-pppwn-in-mi-router
title: "用小米路由器自动折腾 PS4"
description: ""
date: 2025.01.12 10:26
categories:
    - Others
tags: [PS4, Python]
keywords: OpenWRTInvasion, pppwn_cpp, init.d, mi router
cover: /contents/covers/auto-run-pppwn-in-mi-router.png
---

// TODO 👆

在 [用 PPPwn_cpp 在 Mac 上折腾 PS4](https://alphahinex.github.io/2024/12/15/using-pppwn-cpp-on-mac-with-ps4/) 中，我们介绍了如何使用 PPPwn_cpp 在 Mac 上折腾 PS4。其实不只是 Mac，只要能运行 PPPwn_cpp 的设备，都可以用来折腾 PS4，比如小米路由器。

总共分三步：

1. 使用 OpenWRTInvasion 获取小米路由器 Root Shell 权限
2. 能够在小米路由器中运行 PPPwn_cpp
3. 编写脚本，配置路由器开机自动执行

# 获取小米路由器 Root Shell 权限

获取小米路由器 Root Shell 权限的方式可参考 [小米 4A 千兆版路由器禁 ping](https://alphahinex.github.io/2024/02/25/mir4ag-disable-ping/) 中内容，主要是执行 [OpenWRTInvasion](https://github.com/acecilia/OpenWRTInvasion) 工程中的 `remote_command_execution_vulnerability.py` 脚本，即便不是在 [支持列表](https://github.com/acecilia/OpenWRTInvasion?tab=readme-ov-file#supported-routers-and-firmware-versions) 中标明支持的设备和固件版本，也有可能成功，比如小米 4A 千兆版 `2.28.58` 固件，还有小米 3A 都可以成功获得 Root Shell 权限。

// TODO 小米3A具体型号

```bash
$ cd OpenWRTInvasion
$ conda activate openwrt
$ python remote_command_execution_vulnerability.py
```

成功后可根据提示，通过 SSH 登录到路由器。

# 在小米路由器中运行 PPPwn_cpp

小米路由器是 mipsel 架构的，pppwn_cpp 可以使用 https://github.com/xfangfang/PPPwn_cpp/releases/tag/1.1.0 里的 https://github.com/xfangfang/PPPwn_cpp/releases/download/1.1.0/mipsel-linux-musl.zip 版本。

此处需注意，通过获取 Root Shell 权限后提供的 ftp 方式上传文件，可能存在传输后文件 MD5 不一致的问题，可通过 http + wget 方式解决，即将要上传到路由器中的文件发布到一个 http 服务中，在路由器中通过 wget 命令获得文件。

将 pppwn_cpp、stage1.bin 和 stage2.bin 上传到路由器后，可在路由器中执行 `pppwn list` 查看网络接口，网口使用中间 Lan 口时，网络接口名为 `eth0.1`（不同硬件环境网络接口名可能不同）。

# 配置路由器开机自动执行

依据环境实际情况，编写执行 pppwn 脚本 `pppwn_start.sh`：

// TODO pppwn_start.sh

```bash
./pppwn --interface en8 --fw 960 --stage1 SiSTR0/PPPwn/stage1/stage1.bin --stage2 stage2_v1.03/stage2_9.60.bin --timeout 10 --auto-retry
```

// TODO 是否需要可执行权限？

并将脚本放入 `/etc/init.d` 路径下（小米路由器中放入 `/etc/init.d` 下的文件会同时出现在 `/data/etc/init.d`），即可实现路由器开机自动执行。

pppwn_cpp 启动后会监听配置的网络端口，故可实现开启路由后打开 PS4 无人值守自动折腾。 // TODO 是否存在顺序依赖？
