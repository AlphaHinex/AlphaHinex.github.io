---
id: using-pppwn-cpp-on-mac-with-ps4
title: "用 PPPwn_cpp 在 Mac 上折腾 PS4"
description: "Mac，Linux，盒子，路由等都能折腾"
date: 2024.12.15 10:34
categories:
    - Others
tags: [PS4, Python, Mac]
keywords: pppwn, goldhen, PS4, pkg, stage1, stage2, pppwn_cpp
cover: /contents/using-pppwn-cpp-on-mac-with-ps4/cover.png
---

PS4 能不能用 [PPPwn](https://github.com/TheOfficialFloW/PPPwn) 方式折腾，主要取决于 [GoldHEN](https://github.com/GoldHEN/GoldHEN) 和 [SiSTR0/PPPwn](https://github.com/SiSTR0/PPPwn) stage2 支持的固件版本。

目前最新的 [GoldHEN v2.4b18](https://github.com/GoldHEN/GoldHEN/releases/tag/2.4b18) 版本和 [GoldHEN stage2 v1.03](https://github.com/SiSTR0/PPPwn/releases/tag/1.03) 支持的固件版本交集如下：

> **Supported Firmware**
> - 9.00
> - 9.60
> - 10.00 / 10.01
> - 10.50
> - 10.70 / 10.71
> - 11.00

主要折腾两件事：

1. 把 PS4 系统版本升级到上面支持的固件版本
2. 通过 PPPwn 扫描到漏洞并加载 `stage2.bin` 及 `goldhen.bin`

# 所需工具

1. 系统版本不高于支持固件版本的 PS4
1. 网线
1. Mac 及网口转换器（或其他能执行 PPPwn 的电脑、设备）

# 离线升级固件版本

[这里](http://caicai.zicp.vip:1100/) 提供了一些支持的固件版本的离线升级系统文件下载，可选择升级至离当前版本最近的固件版本（保持最低可用的固件版本，避免需要降级）。

从百度网盘下载后，拷入格式化为 `FAT32` 或 `exFAT` 格式的 U 盘：`/PS4/UPDATE/PS4UPDATE.PUP`，将 U 盘插入 PS4。

- 升级方式一：关机状态下的 PS4 主机，长长长长长按电源键，刚按的时候会听到第一次哔声，约 8 秒后听到第二次哔声后松开，主机会进入安全模式，**此模式下需要 USB 线连接手柄才能控制**。依次选择：3.升级系统软件 => 1.使用USB储存装置更新 => OK => 等待升级完成
- 升级方式二：若用方法一进入安全模式后，USB 线连接手柄无反应，可尝试直接 [使用U盘给PS4进行系统升级](https://www.wikimoe.com/post/193) —— 在【设定】中选择【系统软件升级】=> 检测到新版本后选择【继续】=>【升级】=> 等待升级完成

等待升级完成会自动重启，重启后进入设置看下系统版本，升级完成。

# PPPwn_cpp

Python 版本的 PPPwn 需手工执行，且并不是每次都能执行成功（尝试几十次都有可能，效率很低），可使用 C++ 重写版 [PPPwn_cpp](https://github.com/xfangfang/PPPwn_cpp)，能够在失败时自动重试且无需依赖 Python 环境，效率大大提升。

在 [Releases](https://github.com/xfangfang/PPPwn_cpp/releases) 页面直接下载编译好的可执行版本，如 [x86_64-macos-none.zip
](https://github.com/xfangfang/PPPwn_cpp/releases/download/1.1.0/x86_64-macos-none.zip)。

在 macOS 上，下载后需要执行 `sudo xattr -rd com.apple.quarantine <path-to-pppwn>`。[#10](https://github.com/xfangfang/PPPwn_cpp/issues/10) 里有更多相关信息。

> Windows 环境需要提前安装 [npcap](https://npcap.com/)。

在命令行执行 `pppwn` 查看帮助，`pppwn list` 列出所有网卡。

## stage1.bin

可以使用 [PPPwn](https://github.com/TheOfficialFloW/PPPwn) 或 [SiSTR0/PPPwn](https://github.com/SiSTR0/PPPwn) 项目源码编译 `stage1.bin`，或直接使用编译好的版本 [stage1.bin](/contents/using-pppwn-cpp-on-mac-with-ps4/stage1.bin)（MD5：`87e198da92a4c8e53abd7be6d8e7ce02`）。

## stage2.bin

下载 [stage2_v1.03.7z](https://github.com/SiSTR0/PPPwn/releases/download/1.03/stage2_v1.03.7z)，解压后得到对应固件版本的 `stage2.bin`，如：`stage2_9.60.bin`。

## goldhen.bin

下载 [GoldHEN_v2.4b18.7z
](https://github.com/GoldHEN/GoldHEN/releases/download/2.4b18/GoldHEN_v2.4b18.7z)，解压后得到 `goldhen.bin`。将 `goldhen.bin` 拷贝至之前离线升级系统的 U 盘根路径，插入 PS4 等待后续使用。

SiSTR0 定制版本的 stage2 会先在 U 盘根路径寻找 `goldhen.bin`，找到后将其拷贝至 PS4 内部存储的 `/data/GoldHEN/payloads/goldhen.bin`。首次折腾成功之后即可使用内部存储中的 `goldhen.bin`，不再需要将 U 盘插入 PS4。

**首次折腾时须确保根路径下放有 `goldhen.bin` 文件的 U 盘已插入 PS4。后续折腾不再需要。**

## PS4

在 PS4 中进行如下操作：

- 进入【设定】=>【网络】=>【设定互联网连接】=>【使用LAN连接线】=>【定制】=>【PPPoE】
- 输入任意 PPPoE 用户ID 和 密码，点【继续】
- DNS 设定和 MTU 设定均选择【自动】
- 选择【不使用】Proxy服务器
- 最后一步【测试互联网连接】先不点

## 终端

准备好 `stage1.bin`、`stage2.bin` 和 `goldhen.bin` 之后，先将 PS4 与 Mac 通过网线连接。首次执行时确保根路径下放有 `goldhen.bin` 文件的 U 盘已插入 PS4。

在终端中准备好如下命令（**先不执行**），需根据实际环境网卡名、`stage1.bin` 和 `stage2.bin` 的路径及文件名进行调整，如：

```bash
./pppwn --interface en8 --fw 960 --stage1 SiSTR0/PPPwn/stage1/stage1.bin --stage2 stage2_v1.03/stage2_9.60.bin --timeout 10 --auto-retry
```

> 其他固件版本需修改 `fw` 值，如 `11.00` 传入 `--fw 1100`。

## 折腾

在终端执行准备好的命令，之后会出现类似下面的日志：

```text
[+] PPPwn - PlayStation 4 PPPoE RCE by theflow
[+] args: interface=enp0s3 fw=1100 stage1=stage1/stage1.bin stage2=stage2/stage2.bin

[+] STAGE 0: Initialization
[*] Waiting for PADI...
```

此时在 PS4 上操作点击【测试互联网连接】。

顺利的话稍后会在 PS4 界面看到 `获取IP地址 成功`、`互联网连接 失败` 字样，一般不会一次就直接成功，失败时 PS4 界面左侧会弹出 `NW-31274-7` 的错误提示，此时无需任何操作，会自动重试。一般三五分钟内即可成功（运气不好半个多小时也有可能），耐心等待执行成功即可。

失败一般会出现在 STAGE 1 的最后一步，最后一行出现类似 `found fe80::0fdf:4141:4141:4141` 的内容即为成功。

```text
[+] STAGE 1: Memory corruption
[+] Pinning to CPU 0...done
[*] Sending malicious LCP configure request...
[*] Waiting for LCP configure request...
[*] Sending LCP configure ACK...
[*] Sending LCP configure request...
[*] Waiting for LCP configure ACK...
[*] Waiting for IPCP configure request...
[*] Sending IPCP configure NAK...
[*] Waiting for IPCP configure request...
[*] Sending IPCP configure ACK...
[*] Sending IPCP configure request...
[*] Waiting for IPCP configure ACK...
[+] Scanning for corrupted object...found fe80::0fdf:4141:4141:4141
```

完整的成功日志类似下面情况：

```text
[+] PPPwn - PlayStation 4 PPPoE RCE by theflow
[+] args: interface=enp0s3 fw=1100 stage1=stage1/stage1.bin stage2=stage2/stage2.bin

[+] STAGE 0: Initialization
[*] Waiting for PADI...
[+] pppoe_softc: 0xffffabd634beba00
[+] Target MAC: xx:xx:xx:xx:xx:xx
[+] Source MAC: 07:ba:be:34:d6:ab
[+] AC cookie length: 0x4e0
[*] Sending PADO...
[*] Waiting for PADR...
[*] Sending PADS...
[*] Waiting for LCP configure request...
[*] Sending LCP configure ACK...
[*] Sending LCP configure request...
[*] Waiting for LCP configure ACK...
[*] Waiting for IPCP configure request...
[*] Sending IPCP configure NAK...
[*] Waiting for IPCP configure request...
[*] Sending IPCP configure ACK...
[*] Sending IPCP configure request...
[*] Waiting for IPCP configure ACK...
[*] Waiting for interface to be ready...
[+] Target IPv6: fe80::2d9:d1ff:febc:83e4
[+] Heap grooming...done

[+] STAGE 1: Memory corruption
[+] Pinning to CPU 0...done
[*] Sending malicious LCP configure request...
[*] Waiting for LCP configure request...
[*] Sending LCP configure ACK...
[*] Sending LCP configure request...
[*] Waiting for LCP configure ACK...
[*] Waiting for IPCP configure request...
[*] Sending IPCP configure NAK...
[*] Waiting for IPCP configure request...
[*] Sending IPCP configure ACK...
[*] Sending IPCP configure request...
[*] Waiting for IPCP configure ACK...
[+] Scanning for corrupted object...found fe80::0fdf:4141:4141:4141

[+] STAGE 2: KASLR defeat
[*] Defeating KASLR...
[+] pppoe_softc_list: 0xffffffff884de578
[+] kaslr_offset: 0x3ffc000

[+] STAGE 3: Remote code execution
[*] Sending LCP terminate request...
[*] Waiting for PADI...
[+] pppoe_softc: 0xffffabd634beba00
[+] Target MAC: xx:xx:xx:xx:xx:xx
[+] Source MAC: 97:df:ea:86:ff:ff
[+] AC cookie length: 0x511
[*] Sending PADO...
[*] Waiting for PADR...
[*] Sending PADS...
[*] Triggering code execution...
[*] Waiting for stage1 to resume...
[*] Sending PADT...
[*] Waiting for PADI...
[+] pppoe_softc: 0xffffabd634be9200
[+] Target MAC: xx:xx:xx:xx:xx:xx
[+] AC cookie length: 0x0
[*] Sending PADO...
[*] Waiting for PADR...
[*] Sending PADS...
[*] Waiting for LCP configure request...
[*] Sending LCP configure ACK...
[*] Sending LCP configure request...
[*] Waiting for LCP configure ACK...
[*] Waiting for IPCP configure request...
[*] Sending IPCP configure NAK...
[*] Waiting for IPCP configure request...
[*] Sending IPCP configure ACK...
[*] Sending IPCP configure request...
[*] Waiting for IPCP configure ACK...

[+] STAGE 4: Arbitrary payload execution
[*] Sending stage2 payload...
[+] Done!
```

# 安装游戏

`pkg` 格式的游戏文件拷贝至 `exFAT` 格式的移动硬盘根目录后，插入 PS4，进入折腾后的 GoldHEN 界面，选择【Debug Settings】=>【Package Installer】进入后即可选择 U 盘中的 pkg 文件进行安装。

一般游戏文件较大，如需通过百度网盘下载又没有 SVIP，可参考 [百度网盘每天不限速下载](https://alphahinex.github.io/2024/12/08/pan-baidu-svip-per-day/) 中内容。

# 关机后重新折腾

PS4 关机后需重新折腾，连接 PS4 和电脑后，先执行 `pppwn` 命令，然后在 PS4 的网络设置中点击【测试互联网连接】，等待执行成功即可。
