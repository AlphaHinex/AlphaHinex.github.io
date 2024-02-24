---
id: mir4ag-disable-ping
title: "小米 4A 千兆版路由器禁 ping"
description: "借助 OpenWRTInvasion 利用 Root Shell 漏洞实现小米 4A 千兆版路由器禁 ping"
date: 2024.02.25 10:26
categories:
    - Python
    - Shell
tags: [Python, Shell, Mac, OpenWRT]
keywords: mir4ag, ping, sysctl, openwrt, OpenWRTInvasion, debrick
cover: /contents/covers/mir4ag-disable-ping.png
---

小米路由器的官方固件中并不支持设置禁 ping。

本文借助 OpenWRTInvasion 利用 Root Shell 漏洞实现小米4A千兆版路由器禁 ping。


OpenWRTInvasion
===============

[OpenWRTInvasion](https://github.com/acecilia/OpenWRTInvasion) 是一个可以获得小米路由器 Root Shell 权限的工具，[支持多种路由型号和固件版本](https://github.com/acecilia/OpenWRTInvasion?tab=readme-ov-file#supported-routers-and-firmware-versions)，也有一些写明 [不支持的型号和固件版本](https://github.com/acecilia/OpenWRTInvasion?tab=readme-ov-file#unsupported-routers-and-firmware-versions)。

以小米4A千兆版路由器为例，分为国内版、国际版，还有 v1、v2 版本，可参照 [这里](https://openwrt.org/inbox/toh/xiaomi/xiaomi_mi_router_4a_gigabit_edition#how_to_tell_the_different_versions_apart) 区分不同版本。

未写明支持或不支持的版本，也有能成功的可能，比如下面的过程是在 小米4A千兆版路由国内 v1 型号，固件版本为 `2.28.58` 上获得的 Root Shell 权限。


环境准备
------

该工具是 python + shell 脚本，如需在 Windows 环境中使用，可参考官方 README 中 [Using Docker (also works on Windows)](https://github.com/acecilia/OpenWRTInvasion?tab=readme-ov-file#using-docker-also-works-on-windows) 部分。

先从 GitHub 克隆仓库：

```bash
$ git clone https://github.com/acecilia/OpenWRTInvasion.git
$ cd OpenWRTInvasion
$ git log
commit fcec03a49d78d700d62f7be82093bd8e349d9a55 (HEAD -> master, origin/master, origin/HEAD)
Author: BugC0der <60848096+BugC0der@users.noreply.github.com>
Date:   Mon Mar 13 01:15:11 2023 +0100

    Ensure correct line ending for script.sh when used from Windows (#171)
```

创建 conda 虚拟环境并安装依赖：

```bash
$ conda create -n openwrt python=3
$ conda activate openwrt
$ pip install -r requirements.txt
```

> conda 工具安装配置可参照 [JupyterLab 实战](https://alphahinex.github.io/2024/01/14/jupyter-lab-in-action/) 。


脚本执行
------

运行环境连接至小米路由器后，获得路由地址，如 `192.168.31.169`。之后执行如下过程：

```bash
$ python remote_command_execution_vulnerability.py
Router IP address [press enter for using the default 'miwifi.com']: 192.168.31.169
Enter router admin password: xxxxxx
There two options to provide the files needed for invasion:
   1. Use a local TCP file server runing on random port to provide files in local directory `script_tools`.
   2. Download needed files from remote github repository. (choose this option only if github is accessable inside router device.)
Which option do you prefer? (default: 1)1
****************
router_ip_address: 192.168.31.169
stok: xxxxxxxxx
file provider: local file server
****************
start uploading config file...
start exec command...
local file server is runing on 0.0.0.0:50423. root='script_tools'
local file server is getting 'busybox-mipsel' for 192.168.31.169.
local file server is getting 'dropbearStaticMipsel.tar.bz2' for 192.168.31.169.
done! Now you can connect to the router using several options: (user: root, password: root)
* telnet 192.168.31.169
* ssh -oKexAlgorithms=+diffie-hellman-group1-sha1 -oHostKeyAlgorithms=+ssh-rsa -c 3des-cbc -o UserKnownHostsFile=/dev/null root@192.168.31.169
* ftp: using a program like cyberduck
```

> 通过本地文件服务将文件传输至路由时，可无需网络连接。

脚本执行成功后，可通过提供的三种方式连接至小米路由器，用户名密码均为 `root`：

```bash
$ ssh -oKexAlgorithms=+diffie-hellman-group1-sha1 -oHostKeyAlgorithms=+ssh-rsa -c 3des-cbc -o UserKnownHostsFile=/dev/null root@192.168.31.169
The authenticity of host '192.168.31.169 (192.168.31.169)' can't be established.
RSA key fingerprint is SHA256:VS1Ef5kgBMO6ghA+PD2lcKYM6cTOnwE/eO4PRUYV6Jg.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '192.168.31.169' (RSA) to the list of known hosts.
root@192.168.31.169's password:


BusyBox v1.19.4 (2019-06-11 03:26:58 UTC) built-in shell (ash)
Enter 'help' for a list of built-in commands.

 -----------------------------------------------------
       Welcome to XiaoQiang!
 -----------------------------------------------------
  $$$$$$\  $$$$$$$\  $$$$$$$$\      $$\      $$\        $$$$$$\  $$\   $$\
 $$  __$$\ $$  __$$\ $$  _____|     $$ |     $$ |      $$  __$$\ $$ | $$  |
 $$ /  $$ |$$ |  $$ |$$ |           $$ |     $$ |      $$ /  $$ |$$ |$$  /
 $$$$$$$$ |$$$$$$$  |$$$$$\         $$ |     $$ |      $$ |  $$ |$$$$$  /
 $$  __$$ |$$  __$$< $$  __|        $$ |     $$ |      $$ |  $$ |$$  $$<
 $$ |  $$ |$$ |  $$ |$$ |           $$ |     $$ |      $$ |  $$ |$$ |\$$\
 $$ |  $$ |$$ |  $$ |$$$$$$$$\       $$$$$$$$$  |       $$$$$$  |$$ | \$$\
 \__|  \__|\__|  \__|\________|      \_________/        \______/ \__|  \__|


root@XiaoQiang:~# 
```


禁 ping
=======

编辑 `/etc/sysctl.conf` 文件，加入或修改 `net.ipv4.icmp_echo_ignore_all` 字段值为 `1`，之后使配置生效即可。路由重启后也是禁 ping 状态。

```bash
root@XiaoQiang:~# cat /etc/sysctl.conf|grep icmp_echo_ignore_all
net.ipv4.icmp_echo_ignore_all=1
root@XiaoQiang:~# sysctl -p
```

后记
===

最初是想通过给小米路由刷 OpenWRT 固件看看能不能设置禁 ping，无奈按照官方 wiki —— [Xiaomi Mi Router 4A Gigabit Edition](https://openwrt.org/inbox/toh/xiaomi/xiaomi_mi_router_4a_gigabit_edition) 尝试多次，每次写入 OpenWRT 官方固件后，路由器都会陷入橙灯常亮时而闪烁的状态。最终退而求其次在获得 Root Shell 权限后直接修改 sysctl 配置实现禁 ping。

将刷 OpenWRT 及变砖后的恢复过程记录如下，以备后续需要。

OpenWRT
-------

- 官方文档：[Xiaomi Mi Router 4A Gigabit Edition](https://openwrt.org/inbox/toh/xiaomi/xiaomi_mi_router_4a_gigabit_edition)
- 设备 SKU: `DVB4218CN`

> 2019 model is shielded

> Warning Xiaomi is currently shipping Mi Router 4A Gigabit Edition devices without proper shielding since 2020. Be aware that those might cause problems due to radio interference. Nevertheless, it's flashable.

在 [Installation](https://openwrt.org/inbox/toh/xiaomi/xiaomi_mi_router_4a_gigabit_edition#installation) 部分下载 [Factory image](https://downloads.openwrt.org/releases/23.05.2/targets/ramips/mt7621/openwrt-23.05.2-ramips-mt7621-xiaomi_mi-router-4a-gigabit-squashfs-sysupgrade.bin)

> 当前文档中，[23.05.2](https://openwrt.org/releases/23.05.2) 版本 `Factory image` 和 `Sysupgrade image` 是相同的镜像

文档中并未给出镜像文件的校验码，可在 [固件选择](https://firmware-selector.openwrt.org/?version=23.05.2&target=ramips%2Fmt7621&id=xiaomi_mi-router-4a-gigabit) 界面选择适合设备的 OpenWRT 版本进行下载，下载后可对比 shasum256 码。

- kernel：https://downloads.openwrt.org/releases/23.05.2/targets/ramips/mt7621/openwrt-23.05.2-ramips-mt7621-xiaomi_mi-router-4a-gigabit-initramfs-kernel.bin
- sha256sum：da95d78bbb590e3f81e078d63bb1a3a129364c0a6a586caab9c5249ede183116

- sysupgrade：https://downloads.openwrt.org/releases/23.05.2/targets/ramips/mt7621/openwrt-23.05.2-ramips-mt7621-xiaomi_mi-router-4a-gigabit-squashfs-sysupgrade.bin
- sha256sum：66c58c3c05d4d43c88cb6f98e831ee0d518f80a248aba3314d7895983b91deff

下载镜像并通过 ftp（账号 `root`/`root`）上传至路由器：

```bash
$ curl https://downloads.openwrt.org/releases/23.05.2/targets/ramips/mt7621/openwrt-23.05.2-ramips-mt7621-xiaomi_mi-router-4a-gigabit-squashfs-sysupgrade.bin --output firmware.bin
$ ftp 192.168.31.169
Connected to 192.168.31.169.
220 Operation successful
Name (192.168.31.169:alphahinex): root
331 Specify password
Password:
230 Operation successful
ftp> cd tmp
250 Operation successful
ftp> put firmware.bin
200 Operation successful
150 Ok to send data
226 Operation successful
6579470 bytes sent in 0.519 seconds (12.1 Mbytes/s)
```

在路由器中校验镜像，并写入：

```bash
root@XiaoQiang:/tmp# /tmp/busybox sha256sum firmware.bin
66c58c3c05d4d43c88cb6f98e831ee0d518f80a248aba3314d7895983b91deff  firmware.bin
root@XiaoQiang:/tmp# mtd -e OS1 -r write firmware.bin OS1
Unlocking OS1 ...
Erasing OS1 ...

Writing from firmware.bin to OS1 ...
Rebooting ...
```

顺利的话，Rebooting 可能需要等待个十几分钟，不顺利可能就一直处于橙灯常亮，偶尔闪烁状态了……

百兆版好像也有类似的情况：[Cannot flash OpenWRT on Mi Router 4A 100M (Chinese version) firmware 2.28.62](https://github.com/acecilia/OpenWRTInvasion/issues/176)

Debrick
-------

路由器变砖后，可使用官方提供的工具和固件进行恢复：

- [【路由刷机教程】适用于小米路由器刷机工具](https://web.vip.miui.com/page/info/mio/mio/detail?postId=19134127&app_version=dev.20051)
- [【客户端下载】小米路由器修复工具](https://web.vip.miui.com/page/info/mio/mio/detail?postId=19156828&app_version=dev.20051)
- [【ROM下载】小米路由器4A千兆版](https://web.vip.miui.com/page/info/mio/mio/detail?postId=19166773&app_version=dev.20051)

下载：

- [Windows 版刷机工具](http://bigota.miwifi.com/xiaoqiang/tools/MIWIFIRepairTool.x86.zip)
- [官方固件 2.28.62 版本（2019年6月30日）](http://bigota.miwifi.com/xiaoqiang/rom/r4a/miwifi_r4a_firmware_72d65_2.28.62.bin)

恢复过程可参考：https://forum.openwrt.org/t/xiaomi-mi-router-4a-gigabit-edition-r4ag-r4a-gigabit-fully-supported-and-flashable-with-openwrtinvasion/36685/747

### Windows 环境设置静态 IP

- IP：`192.168.31.100`
- 子网掩码：`255.255.255.0`

### 连接路由

网线连接电脑及路由 LAN 口（不要连 WAN 口）

### 执行恢复

- 打开修复工具，选镜像、网卡
- 先给路由器断电，之后按住路由器上 reset 键通电，持续按住 8s 左右，路由器橙灯由常亮变成闪烁，修复工具弹出进度条开始写入固件
- 写入完成后等待几分钟，蓝灯闪烁表示完成，断电重启路由即可