---
id: mac-route-settings
title: "macOS 路由设置"
description: "临时路由及永久路由配置"
date: 2022.02.27 10:26
categories:
    - Mac
tags: [Network]
keywords: macOS, route, networksetup, netstat
cover: /contents/covers/mac-route-settings.png
---

经常会有需要连接多个网络环境的需求，比如通过网线连接内网，通过无线连接外网，想要同时连接内外网时，需要进行路由的配置，以通过不同的网卡访问不同的地址。

macOS 下可通过如下方式，配置临时（重启后失效）或永久（重启仍有效）路由。

## 注意网络顺序

在配置路由之前，先说一下网络顺序的问题。在同时连接内外网时，可能会有能上内网不能上外网的情况，也可能会有能上外网不能上内网的情况，这是什么原因呢？

在 `系统偏好设置` => `网络` 中，我们可以看到 Mac 当前连接的网络，如下图：

![network](/contents/covers/mac-route-settings.png)

`Wi-Fi` 是外网连接，`USB 10/100/1000 LAN 2` 是内网连接，`Wi-Fi` 在上面，表示优先使用外部网络进行连接，此时默认可以访问外网，无法访问内网地址。

可通过上图中高亮的 `设定服务顺序...` 来调整网络顺序，当将内网连接的顺序设定到外网连接之前时，默认可访问内网，无法访问外网地址。

可通过终端中的 `route` 工具，监控调整网络顺序并点上图右下角 `应用` 按钮后路由的变化：

```bash
$ route monitor
```

为简单起见，我们将外网的顺序放在内网之前，通过为内网地址添加路由的方式，实现同时访问内外网。


## 临时路由配置

临时路由在系统重启后会失效，可通过 `route` 命令进行配置，详细用法可通过 `man route` 查看说明，相关操作如下：

```bash
# 添加临时路由
$ sudo route add -net 192.168.0.0 -netmask 255.255.0.0 192.168.129.1

# 查看路由表
$ netstat -rn

# 删除临时路由
$ sudo route -v delete -net 192.168.0.0 -gateway 192.168.129.1
```

其中 `192.168.0.0` 为内网网段，`255.255.0.0` 为 [子网掩码](https://alphahinex.github.io/2020/08/23/subnet-mask/)，`192.168.129.1` 为内网网关。


## 永久路由配置

永久路由是指系统重启后仍然有效的路由配置，使用 `networksetup` 命令完成。

以本文环境为例，外网网络顺序优先内网网络，需要配置内网地址的路由，此时应选择为内网网络添加路由，网络名称可通过如下方式获得：

```bash
# 查看当前连接的设备
$ networksetup -listallnetworkservices
An asterisk (*) denotes that a network service is disabled.
USB 10/100/1000 LAN
iPad USB
Wi-Fi
Thunderbolt Bridge
Bluetooth PAN
Thunderbolt Ethernet
USB 10/100/1000 LAN 2
iPhone USB
VPN (L2TP)
```

之后可为内网网络（即 `USB 10/100/1000 LAN 2`）配置路由，相关操作如下：

```bash
# 添加永久路由
$ networksetup -setadditionalroutes "USB 10/100/1000 LAN 2" 192.168.0.0 255.255.0.0 192.168.129.1 10.0.0.0 255.0.0.0 192.168.129.1

# 查看永久路由
$ networksetup -getadditionalroutes "USB 10/100/1000 LAN 2"
192.168.0.0 255.255.0.0 192.168.129.1
10.0.0.0 255.0.0.0 192.168.129.1

# 删除永久路由
$ networksetup -setadditionalroutes "USB 10/100/1000 LAN 2"
```

注意：`-setadditionalroutes` 命令的格式为 `-setadditionalroutes networkservice [dest1 mask1 gate1] [dest2 mask2 gate2] ... [destN maskN gateN]`，即多组 [目标地址 子网掩码 网关地址] 的组合。有多个目标地址需要设定路由时，需一次性设置。如果使用该命令多次设置时，后面的配置会覆盖掉之前的配置。