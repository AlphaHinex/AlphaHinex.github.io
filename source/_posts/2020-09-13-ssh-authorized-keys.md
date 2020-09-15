---
id: ssh-authorized-keys
title: "SSH 免密登录"
description: "Authorized_keys File in SSH"
date: 2020.09.13 10:34
categories:
    - Others
tags: [Linux, SSH]
keywords: ssh, authorized_keys, rsa, 免密登录, 无密码登录
cover: /contents/covers/ssh-certificate-authentication.png
---

假设 local 需要 ssh 连接到 remote，且不希望每次连接的时候都输入密码（比如从服务器 A 连到 服务器 B）。

## 本地生成公钥私钥对

```bash
# 在本地（local 主机）.ssh 路径生成公钥和私钥文件
$ ssh-keygen -t rsa
# 一路回车即可
```


## 将公钥复制到远程主机

### scp

local

```bash
$ cd ~/.ssh
# 查看该路径下是否有 authorized_keys 文件，如果没有：
$ cp id_rsa.pub authorized_keys
# 如果有：
$ cat id_rsa.pub >> authorized_keys

# 将公钥传输到 remote
$ scp id_rsa.pub user@remote:/path/to/a.pub
```

remote

```bash
# 将公钥文件追加至 authorized_keys
$ cat /paht/to/a.pub >> ~/.ssh/authorized_keys
```

### 或 ssh-copy-id

```bash
$ ssh-copy-id -i ~/.ssh/id_rsa.pub user@remote
```
