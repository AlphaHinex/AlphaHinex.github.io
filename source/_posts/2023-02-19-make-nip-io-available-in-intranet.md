---
id: make-nip-io-available-in-intranet
title: "使 nip.io 域名在纯内网环境可用"
description: "比如 K8s 集群内部，或没有 DNS 服务的内网环境"
date: 2023.02.19 10:34
categories:
    - Web
    - Go
tags: [DNS, Web, Go, CoreDNS]
keywords: DNS, lvh.me, localtest.me, nip.io, sslip.io, coredns
cover: /contents/covers/make-nip-io-available-in-intranet.jpg
---

在 [简单，却伟大](https://alphahinex.github.io/2021/06/06/simple-but-powerful/) 中，我们介绍了几个非常简单，但又非常强大的 DNS 解析服务，如 `nip.io`、`sslip.io`、`localtest.me` 等。

然而在 K8s 集群内部，或没有 DNS 服务的纯内网环境中，我们却无法直接使用这些服务。

那就只能回归到挨个域名配置 host 的原始方式了吗？不！有一个能解析这类域名的 DNS 服务就可以了。

CoreDNS
=======

[CoreDNS](https://coredns.io/) 是一个用 [Go](https://golang.org/) 编写的灵活可扩展的 DNS 服务器，是 [CNCF](https://cncf.io/) 的毕业项目。可通过 [Kubernetes 插件](https://coredns.io/plugins/kubernetes/) 集成至 [Kubernetes](https://kubernetes.io/) 中作为 Kubernetes 集群 DNS，[Releases 页面](https://github.com/coredns/coredns/releases) 也有面向各种环境的可执行文件。

CoreDNS 有丰富的 [官方插件](https://coredns.io/plugins/) 及 [三方插件](https://coredns.io/explugins/)，可通过配置文件 [Corefile](https://coredns.io/manual/toc/#configuration) 对 CoreDNS 进行配置。

使用 CoreDNS 解析 `nip.io` 之类的域名，就可以通过 [template](https://coredns.io/plugins/template/) 插件来实现。

template plugin
---------------

在 template 插件的文档页面中，给出了这样一个 [例子](https://coredns.io/plugins/template/#resolve-multiple-ip-patterns)：

```Corefile
. {
    forward . 8.8.8.8

    template IN A example {
      match "^ip-(?P<a>10)-(?P<b>[0-9]*)-(?P<c>[0-9]*)-(?P<d>[0-9]*)[.]dc[.]example[.]$"
      match "^(?P<a>[0-9]*)[.](?P<b>[0-9]*)[.](?P<c>[0-9]*)[.](?P<d>[0-9]*)[.]ext[.]example[.]$"
      answer "{{ .Name }} 60 IN A {{ .Group.a}}.{{ .Group.b }}.{{ .Group.c }}.{{ .Group.d }}"
      fallthrough
    }
}
```

作用是根据输入的包含 IP 的域名，进行正则匹配，并将捕捉到的 IP 作为响应输出。

可以仿照上例，写出使 CoreDNS 支持 `nip.io` 类域名解析的配置：

```Corefile
nip.io {
    template IN A {
      match (?P<a>[0-9]*)[.-](?P<b>[0-9]*)[.-](?P<c>[0-9]*)[.-](?P<d>[0-9]*).nip.io
      answer "{{ .Name }} 3600 IN A {{ .Group.a }}.{{ .Group.b }}.{{ .Group.c }}.{{ .Group.d }}"
    }
}
```

将上面内容保存为 `Corefile` 文件，放置在 CoreDNS 的可执行文件路径下，运行 CoreDNS，即可获得一个能够解析 `nip.io` 域名的 DNS 服务器。

[这里](https://github.com/deskoh/docker-coredns) 有一个可以用 Docker Compose 启动的环境，实现了相同功能，并可按照其 README 中方式进行测试：

```bash
# 10.0.0.1
$ nslookup 10.0.0.1.nip.io 127.0.0.1

# 192.168.1.250
$ nslookup 192-168-1-250.nip.io 127.0.0.1

# 10.8.0.1
$ nslookup app.10.8.0.1.nip.io 127.0.0.1

# 116.203.255.68
$ nslookup app-116-203-255-68.nip.io 127.0.0.1

# 10.0.0.1
$ nslookup customer1.app.10.0.0.1.nip.io 127.0.0.1

# 127.0.0.1
$ nslookup customer2-app-127-0-0-1.nip.io 127.0.0.1
$ nslookup magic.127.0.0.1.nip.io 127.0.0.1
$ nslookup magic-127-0-0-1.nip.io 127.0.0.1
```


K8s 集群内部环境
==============

在 K8s 集群内部，想在容器中能够解析 `nip.io` 域名时，可以参照 [自定义 DNS 服务](https://kubernetes.io/zh-cn/docs/tasks/administer-cluster/dns-custom-nameservers/)，在 ConfigMap 中调整 CoreDNS 的 Corefile 配置。


其他环境
=======

如果已经有了一个 K8s 集群内的，可以解析 `nip.io` 域名的 DNS 服务，那么能否使用这个服务作为 K8s 集群外部的 DNS 服务器呢？

简单来说，很难。

因为在 K8s 中，会使用 [NodeLocal DNSCache](https://kubernetes.io/zh-cn/docs/tasks/administer-cluster/nodelocaldns/) 在集群节点上作为 DaemonSet 运行 DNS 缓存代理来提高集群 DNS 性能，所以 DNS 服务默认的 `53` 端口在集群内各个节点已被占用，这样的话就只能使用非默认端口。

虽然一些工具可以使用非默认端口的 DNS 服务进行域名解析，如：

```bash
# dns 服务监听在本地 54 端口
$ dig test.192.168.1.80.nip.io @127.0.0.1 -p 54
```

但想给 Windows 或 Linux 系统配置使用非默认端口的 DNS 服务，[并不是一件容易的事](https://ilpl.me/2018/08/17/public-DNS-5353-list/)。

所以没必要为难自己，在非 K8s 集群环境，找台机器（比如本地）直接启动一个 CoreDNS 服务就好了。