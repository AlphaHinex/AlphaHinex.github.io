---
id: item2-open-ssh-with-pwd
title: "【转】iTerm2快速SSH连接并保存密码"
description: "不能 ssh-copy-id 时的替代方案"
date: 2026.04.05 10:34
categories:
    - Mac
tags: [Mac, SSH]
keywords: iterm2, macOS, sshpass, ssh, profile, scp
cover: /contents/item2-open-ssh-with-pwd/cover.png
---

- 原文地址：https://cloud.tencent.com/developer/article/1424423
- 原文作者：[汪志宾](https://cloud.tencent.com/developer/user/1433640)

---

## 背景

Mac自带terminal，以及比较好用的iTerm2命令行工具，都缺乏一个功能，就是远程SSH连接，无法保存密码。

一种方法是将本机的ssh_key放到远程服务器中实现无密码登录。这种方法在很多情况下无法实现，因为远程服务器大多是客户的。

本文介绍一个简单、轻量级的命令行工具——sshpass，通过它我们能够向命令提示符本身提供密码（非交互式密码验证），这样就可以实现自动连接远程服务器，而且能自动执行远程命令。

## 安装sshpass

1. 下载sshpass：https://sourceforge.net/projects/sshpass/files/
1. 进入 sshpass目录
1. 运行【./configure】
1. 运行【sudo make install】
1. 运行【sshpass 】 来测试是否安装成功

## sshpass使用

```bash
Usage: sshpass [-f|-d|-p|-e] [-hV] command parameters
-f filename   Take password to use from file
-d number     Use number as file descriptor for getting password
-p password   Provide password as argument (security unwise)
-e            Password is passed as env-var "SSHPASS"
With no parameters - password will be taken from stdin
-h            Show help (this screen)
-V            Print version information
At most one of -f, -d, -p or -e should be used
```

使用用户名和密码登录到远程Linux ssh服务器（192.168.129.116），并检查文件系统磁盘使用情况，如图所示。

```bash
$ sshpass -p 'password' ssh root@192.168.129.116 'df -h' 
```

也可以使用sshpass 通过scp传输文件或者rsync备份/同步文件，如下所示：

```bash
------- Transfer Files Using SCP ------- 
$ scp -r /var/www/html/example.com --rsh="sshpass -p 'password' ssh -l root" 192.168.129.116:/var/www/html
------- Backup or Sync Files Using Rsync -------
$ rsync --rsh="sshpass -p 'password' ssh -l root" 192.168.129.116:/data/backup/ /backup/
```

## iTerm2集成sshpass实现快速SSH连接

- 打开iTerm2的Profiles菜单，进入Profiles设置。

![Profiles设置](https://alphahinex.github.io/contents/item2-open-ssh-with-pwd/iterm2.png)

- 点击Edit Profiles。

![Edit Profiles](https://alphahinex.github.io/contents/item2-open-ssh-with-pwd/profiles.png)

- 增加SSH连接。
	- Name：名称
	- Tags：分组或者标签名称
	- Title：设置窗口名称
	- Command：`/usr/local/bin/sshpass -p 'xxxx' ssh root@192.168.129.116`

![增加SSH连接](https://alphahinex.github.io/contents/item2-open-ssh-with-pwd/sshpass.png)

- 快速连接

![快速连接](https://alphahinex.github.io/contents/item2-open-ssh-with-pwd/connect.png)

## 参考资料

1. sshpass：一个很棒的免交互SSH登录工具，但不要用在生产服务器上
1. [iTerm2 保存ssh用户名密码](https://cloud.tencent.com/developer/tools/blog-entry?target=https%3A%2F%2Fwww.jianshu.com%2Fp%2F7a7584dcee2b&objectId=1424423&objectType=1&contentType=undefined)