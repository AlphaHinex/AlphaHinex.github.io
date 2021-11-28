---
id: iterm2-ssh-via-ssh
title: "iTerm2 快速通过跳板机 ssh 远程登录"
description: "提供几种需通过跳板机才能访问的远程主机的快速 ssh 登录方式"
date: 2021.11.28 10:26
categories:
    - Mac
tags: [SSH, Linux]
keywords: ssh, sshpass, iTerm2, expect
cover: /contents/iterm2-ssh-via-ssh/cover.jpg
---

场景
===

假设有 A、B、C …… 几批主机：

* a0 为跳板机，a1 ~ an 为实际要操作的目标远程主机
* b0 为跳板机，b1 ~ bn 为实际要操作的目标远程主机

以此类推，共有 n 批。

客户端能联通各跳板机，但无法直接联通目标主机，每批主机之间网络隔离。

需通过 ssh 远程登录目标主机时，是比较痛苦的一件事，一堆 ip 和密码不便记忆，从文档里找又效率很低。


解决方案
=======

SSH 免密登录
-----------

首先想到的是配置跳板机和各目标主机之间的 [SSH 免密登录](https://alphahinex.github.io/2020/09/13/ssh-authorized-keys/)，能够起到不用记忆密码的作用，但需要配置客户端和各个跳板机的免密登录，以及各个跳板机和每个网络内目标主机的免密，在目标主机数量庞大时，配置操作量也很大，更重要的是，其他人登录到跳板机后，也能免密直接 ssh 到各目标主机了，安全性较差。

sshpass
-------

理想的状态是将密码保留在客户端，而免密登录，相当于将客户端的公钥，发给了服务端。

ssh 命令，出于安全性的考虑，又不支持在命令中直接明文传入密码。这时可以使用 sshpass，将密码传给 ssh 命令，使用方式如下：

```bash
$ sshpass -p <password> ssh <user>@<remote_host>
```

### MacOS 安装 sshpass

linux 中可以通过包管理工具，安装 sshpass，如 `yum install sshpass`，或者下载对应安装包，进行离线安装，如 CentOS 的 [rpm 包](https://centos.pkgs.org/7/centos-extras-x86_64/sshpass-1.06-2.el7.x86_64.rpm.html)。

MacOS 中安装 sshpass 会稍微复杂一些，因为 `brew` 出于安全考虑也不让直接安装。具体安装方式可以参考 [macOS 安装 sshpass](https://wsgzao.github.io/post/sshpass/)：

```bash
$ brew install https://raw.githubusercontent.com/kadwanev/bigboybrew/master/Library/Formula/sshpass.rb
```

或

```bash
$ wget https://raw.githubusercontent.com/kadwanev/bigboybrew/master/Library/Formula/sshpass.rb
$ brew install sshpass.rb
```

某些原因下载不到这个脚本的话，可以保存下面内容到本地 `sshpass.rb` 文件，之后再执行 `brew install sshpass.rb`：

```ruby
require 'formula'

class Sshpass < Formula
  url 'http://sourceforge.net/projects/sshpass/files/sshpass/1.06/sshpass-1.06.tar.gz'
  homepage 'http://sourceforge.net/projects/sshpass'
  sha256 'c6324fcee608b99a58f9870157dfa754837f8c48be3df0f5e2f3accf145dee60'

  def install
    system "./configure", "--disable-debug", "--disable-dependency-tracking",
                          "--prefix=#{prefix}"
    system "make install"
  end

  def test
    system "sshpass"
  end
end
```

### 通过 iTerm2 执行多条指令

因为需要先登录跳板机，再从跳板机登录到目标主机，故需要两次 ssh 动作。在 iTerm2 中，可以通过 Profile 进行设置。

`⌘+O` 打开 Profiles 设置界面，`Edit Profiles...` => `+` 新增 Profile，按如下方式配置：

![command](/contents/iterm2-ssh-via-ssh/command.png)

`Command` 处选择 `Command`，即可输入两个命令，上面为登录跳板机的命令，下面为从跳板机登录到目标机器的命令，具体内容如下：

```
/usr/local/bin/sshpass -p <pwd> ssh -o StrictHostKeyChecking=no root@a0
```

```
sshpass -p <pwd> ssh -o StrictHostKeyChecking=no root@a1
```

> `-o StrictHostKeyChecking=no` 参数避免进行 host key 确认，导致第二个 ssh 命令失败

配置好的效果如下图：

![sshpass](/contents/iterm2-ssh-via-ssh/sshpass.png)

之后可以在 Profiles 界面中直接点击进行快速登录。

### 使用 iTerm2 的 Profile 组织主机树

当 profile 配置数量增多时，尤其是上面假设场景中的分批次的情况，通过树形方式组织主机，是一个能够快速找到想要连接的主机的方法。

在 iTerm2 中，可以通过 `tag` 来组织 Profile 的层级关系，以达到树形的效果。

例如，在 a1 主机的 tag 中输入 `demo/A`、a2 主机 tag `demo/A`、b1 主机 tag `demo/B` ……

打开 Profiles 时，可看到如下效果：

![profiles](/contents/iterm2-ssh-via-ssh/profiles.png)

expect
------

sshpass 的方案也存在一个问题，即需要在客户端，和各个跳板机中安装 sshpass，无法直接通过包管理工具安装时，还是有些麻烦的，并且直接将密码作为参数传递，多少还是存在一些安全隐患的。

终极方案 —— 使用 [expect 脚本](https://www.php.cn/linux-428101.html)。

主要用到 expect 中的如下命令：

|命令|作用|
|:--|:---|
|send|用于向进程发送字符串|
|expect|从进程接收字符串|
|exp_continue|在expect中多次匹配就需要用到|
|spawn|启动新的进程|
|interact|允许用户交互|

通过脚本，可以实现 ssh 连跳板机，输入跳板机密码，连接至跳板机后，ssh 连接目标主机，并输入目标主机密码，之后将控制权交还给用户的过程。

参照 [iTerm2 结合 Linux expect 实现 ssh 自动登陆, 通过跳板机登录服务器内网功能](https://segmentfault.com/a/1190000009826457) 中内容，假设各跳板机密码是相同的，各目标主机密码也是相同的，使用如下脚本，可将跳板机和目标主机的 ip 作为参数传入，密码填写在脚本中，保存在客户端，以提高安全性。

```sh
#!/usr/bin/expect
# 跳板机 ip
set TERMSERV [lindex $argv 0] 
# 通过跳板机才能访问的目标主机 ip
set host [lindex $argv 1]

# 跳板机用户名及密码
set USER root
set PASSWORD pwd0

# 目标主机用户名及密码
set UATUN root
set UATPWD pwd123

# 登录跳板机
spawn ssh -l $USER $TERMSERV
expect {
    "yes/no" {send "yes\r";exp_continue;}
    "*password:*" { send "$PASSWORD\r" }
}

# 登录内网
expect "*$USER@*" {send "ssh -l $UATUN $host\r"}
expect {
    "yes/no" {send "yes\r";exp_continue;}
    "*password:*" { send "$UATPWD\r" }
}
interact
```

假设上面脚本文件存储为 `/path/to/login_inner.sh`，在 iTerm2 的 Profile 中，`Command` 改为选择 `Login Shell`，在 `Send text at start:` 中输入：`/path/to/login_inner.sh a0 a1`（`a0`、`a1` 分别为 跳板机 和 目标主机的 ip 或 host），即可完成一个 profile 的设置。

享受通过跳板机连接远程主机的极速体验吧！

> `expect` 方案，也可配合 `alias` 命令，自定义连接各个主机的快捷指令，在终端中直接输入自定义指令进行连接，在其他终端模拟器中也可以使用。