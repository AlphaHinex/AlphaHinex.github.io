---
id: windows-sshd-in-git-bash
title: "Windows Git Bash 中使用 sshd 服务"
description: "可以 ssh 到 Windows 终端"
date: 2023.11.26 10:26
categories:
    - Git
    - Linux
tags: [Git, Linux, SSH]
keywords: Windows, Git Bash, sshd, ssh
cover: /contents/covers/windows-sshd-in-git-bash.png
---

Windows 环境下，可以通过 [Git](https://git-scm.com/) 中的 `Git Bash` 启动 sshd 服务。

进入 Git Bash 后，先生成 `ssh_host_rsa_key`：

```bash
ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key
```

之后会在 Git 安装路径下的 `/etc/ssh` 中生成 `ssh_host_rsa_key`、`ssh_host_rsa_key.pub` 两个文件：

```bash
# /etc/ssh 下的文件实际路径在 git 安装路径下的 /etc/ssh 中
$ ls -l /etc/ssh
total 569
-rw-r--r-- 1 Administrator 197121 565252 12月  4  2018 moduli
-rw-r--r-- 1 Administrator 197121   1589 8月  24  2018 ssh_config
-rw-r--r-- 1 Administrator 197121   1831 11月 25 16:51 ssh_host_rsa_key
-rw-r--r-- 1 Administrator 197121    409 11月 25 16:51 ssh_host_rsa_key.pub
-rw-r--r-- 1 Administrator 197121   3122 12月  4  2018 sshd_config
```

用全路径启动 `sshd` 服务：

```bash
$ /usr/bin/sshd
Could not load host key: /etc/ssh/ssh_host_ecdsa_key
Could not load host key: /etc/ssh/ssh_host_ed25519_key
```

此时可通过其他终端使用 Windows 环境的登录账号进行 ssh 连接：

```bash
ssh Administrator@xxx.xxx.xxx.xxx
```

结束 sshd 服务可以直接 kill 进程：

```bash
$ ps -ef|grep sshd
Administ    5292       1 ?        16:54:51 /usr/bin/sshd
$ kill 5292
```