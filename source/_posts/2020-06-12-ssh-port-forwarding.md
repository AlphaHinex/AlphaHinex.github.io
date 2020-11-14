---
id: ssh-port-forwarding
title: "SSH Port Forwarding, aka SSH Tunneling"
description: ""
date: 2020.06.12 19:26
categories:
    - Others
tags: [Linux, SSH]
keywords: Linux, SSH, SSH Port Forwarding, SSH Tunneling, ssh_config, sshd_config, man
cover: /contents/ssh-port-forwarding/cover.jpg
---

SSH（Secure Shell）端口转发（SSH Port Forwarding），也叫 SSH 隧道（SSH Tunneling），是 SSH 中的一种机制，可以在 SSH 客户端与服务端之间，建立一条隧道，将客户端端口转发至服务端，也可将服务端端口转发至客户端。利用这种机制，可以为老式应用，提供加密通讯的途径，以及其他一些更广泛的用途。

![Securing applications with ssh tunneling/port forwarding](/contents/ssh-port-forwarding/Securing_applications_with_ssh_tunneling___port_forwarding.png)


## 怎么端口转发/创建隧道？

利用 SSH 客户端，即可完成隧道的创建，创建隧道时，需指定隧道两端的端口，故也叫端口转发。

端口转发分为两种：
1. 本地端口转发
1. 远程端口转发

下面以 [OpenSSH](https://en.wikipedia.org/wiki/OpenSSH) 为例，进行具体实例说明。

### 本地端口转发（Local Port Forwarding）

假如有这样一个场景：

本地可以通过 `2426` 端口 ssh 连接到 `remote-host`。
在 remote-host 上的 `3306` 端口有一个 MySQL 服务。
受各种因素所限，本地无法连接 remote-host 的 3306 端口，但想要使用 remote-host 上的 MySQL 服务，且不能修改其端口号。

此时本地端口转发就可以派上用场了：

```bash
$ ssh -L 4406:remote-host:3306 user@remote-host -p 2426
```

`-L` 意为使用本地端口转发。`4406` 为使用的本地端口。`remote-host:3306` 需为所登录的 SSH 服务端可访问的地址及端口。
`user@remote-host` 为登录 SSH 服务端的用户和地址，`-p` 为指定 SSH 服务所在端口，如使用默认端口（`22`)，此部分内容可省略。

此例意为将对本地 4406 端口的访问，通过 SSH 客户端所创建的隧道，转发至 remote-host 的 3306 端口。此时便可通过访问本地 4406 端口，连接至 remote-host 中 3306 的 MySQL 了。

默认情况下，任何可以连接到本地（此 SSH 客户端所在）4406 端口的机器，都可以使用此隧道。需限定仅本机可使用此隧道时，可绑定具体地址，如：

```bash
$ ssh -L 127.0.0.1:4406:remote-host:3306 user@remote-host -p 2426
```

### 远程端口转发（Remote Port Forwarding）

远程端口转发，可适用于如下场景：

内网环境有一个 MySQL 服务，外网无法直接访问到此服务，但内网可连接至外网一 SSH 服务（remote-host）。
通过远程端口转发，可以在内网建立一条与 remote-host 的隧道，并将外网端口（如 5506）转发至内网 MySQL 的 3306 端口。
此时连接 remote-host 的 5506，即可访问内网 MySQL 3306 的服务。

在内网 MySQL 服务所在机器中执行：

```bash
$ ssh -R 5506:localhost:3306 remote-host
```

意为使用本地 SSH 客户端相同用户，默认端口（22）连接 remote-host，并将 remote-host 的 5506 端口，转发至本地 localhost 3306 端口。

默认情况下，此时仅可在 remote-host 服务器自身，通过 5506 端口访问到内网的 3306 服务。

在 SSH 服务端的 `sshd_config` 文件（`/etc/ssh/sshd_config`）中，可通过 `GatewayPorts` 参数控制此行为。


```doc
GatewayPorts
        是否允许远程主机连接本地的转发端口。默认值是"no"。
        sshd(8) 默认将远程端口转发绑定到loopback地址。这样将阻止其它远程主机连接到转发端口。
        GatewayPorts 指令可以让 sshd 将远程端口转发绑定到非loopback地址，这样就可以允许远程主机连接了。
        "no"表示仅允许本地连接，"yes"表示强制将远程端口转发绑定到统配地址(wildcard address)，
        "clientspecified"表示允许客户端选择将远程端口转发绑定到哪个地址。
```

> —— 引自 [sshd_config 中文手册](http://www.jinbuguo.com/openssh/sshd_config.html)

在配置文件中进行 `GatewayPorts yes` 配置后，可通过 `systemctl restart sshd` 重启 ssh 服务使配置生效。


## 如何保持会话？

按上述方式进行端口转发时，会通过 SSH 方式连接到服务端。但按默认设置，客户端在空闲一段时间后可能会中断，需保持会话时，可在 `~/.ssh/config` 中加入：

```config
Host *
  ServerAliveInterval 30
```

* `Host *` 表示连接任意地址均使用此配置。如果需要针对某个主机，可配置为指定 host 或者 IP；
* `ServerAliveInterval 30` 表示 SSH 客户端每隔 `30秒` 给远程主机发送一个 no-op 包，no-op 是无任何操作的意思，这样远程主机就不会关闭这个SSH会话。

参数说明可通过 `man ssh_config` 进行查看，如：

```man
ServerAliveInterval
        Sets a timeout interval in seconds after which if no data has been received from the server, ssh(1) will send a message through the
        encrypted channel to request a response from the server.  The default is 0, indicating that these messages will not be sent to the
        server.
```


## 怎么后台运行

设置了超时时间后，在 SSH 客户端存在期间可以一直使用端口转发。但客户端关闭后就会失效。SSH 提供了后台运行的方式来解决这个问题。

以上面远程端口转发为例，可使用如下方式，使连接在后台运行。

```bash
$ ssh -fNgR 5506:localhost:3306 remote-host
```

各参数含义如下：

```man
-f      Requests ssh to go to background just before command execution.  This is useful if ssh is going to ask for passwords or
        passphrases, but the user wants it in the background.  This implies -n.  The recommended way to start X11 programs at a remote
        site is with something like ssh -f host xterm.

        If the ExitOnForwardFailure configuration option is set to ``yes'', then a client started with -f will wait for all remote port
        forwards to be successfully established before placing itself in the background.

-N      Do not execute a remote command.  This is useful for just forwarding ports.

-g      Allows remote hosts to connect to local forwarded ports.  If used on a multiplexed connection, then this option must be specified
        on the master process.
```

另外，后台运行时，同样也存在服务端断开连接的情况。此时若需保持会话，可通过 `-o` 参数指定客户端参数，如：

```bash
$ ssh -fNgR 5506:localhost:3306 remote-host -o ServerAliveInterval=30
```


## 如何防止滥用 ？

为防止端口转发被滥用，一般需要在服务器配置中（/etc/ssh/sshd_config）明确禁止此行为，如：

```config
AllowTcpForwarding no
AllowStreamLocalForwarding no
GatewayPorts no
PermitTunnel no
```

> 注意：即使禁用了端口转发，依然存在用户运行自己的 SSH 服务等其他可能，不能彻底避免安全性问题。

各参数详细说明，可通过 `man sshd_config` 进行查看：

```man
AllowTcpForwarding
        Specifies whether TCP forwarding is permitted.  The available options are yes (the default) or all to allow TCP forwarding, no to
        prevent all TCP forwarding, local to allow local (from the perspective of ssh(1)) forwarding only or remote to allow remote forward-
        ing only.  Note that disabling TCP forwarding does not improve security unless users are also denied shell access, as they can
        always install their own forwarders.

AllowStreamLocalForwarding
        Specifies whether StreamLocal (Unix-domain socket) forwarding is permitted.  The available options are yes (the default) or all to
        allow StreamLocal forwarding, no to prevent all StreamLocal forwarding, local to allow local (from the perspective of ssh(1)) for-
        warding only or remote to allow remote forwarding only.  Note that disabling StreamLocal forwarding does not improve security unless
        users are also denied shell access, as they can always install their own forwarders.

GatewayPorts
        Specifies whether remote hosts are allowed to connect to ports forwarded for the client.  By default, sshd(8) binds remote port for-
        wardings to the loopback address.  This prevents other remote hosts from connecting to forwarded ports.  GatewayPorts can be used to
        specify that sshd should allow remote port forwardings to bind to non-loopback addresses, thus allowing other hosts to connect.  The
        argument may be no to force remote port forwardings to be available to the local host only, yes to force remote port forwardings to
        bind to the wildcard address, or clientspecified to allow the client to select the address to which the forwarding is bound.  The
        default is no.

PermitTunnel
        Specifies whether tun(4) device forwarding is allowed.  The argument must be yes, point-to-point (layer 3), ethernet (layer 2), or
        no.  Specifying yes permits both point-to-point and ethernet.  The default is no.

        Independent of this setting, the permissions of the selected tun(4) device must allow access to the user.
```

## 示例

```bash
# 将本地 3426 端口映射至 remote 22 端口，此时可 ssh 到此机器的 3426 端口，以实现以此机器作为跳板 ssh 到 remote 主机的效果
$ ssh -fNgL 3426:remote:22 root@remote -o ServerAliveInterval=30
```


## 参考资料

* [SSH Port Forwarding Example](https://www.ssh.com/ssh/tunneling/example)
* [SSH tunnel](https://www.ssh.com/ssh/tunneling/)
* [Iterm2 SSH保持连接方法](https://www.jianshu.com/p/c0f1ef1f01c2)
* [sshd_config 中文手册](http://www.jinbuguo.com/openssh/sshd_config.html)
