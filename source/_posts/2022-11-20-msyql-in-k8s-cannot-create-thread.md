---
id: msyql-in-k8s-cannot-create-thread
title: "K8s 中的 MySQL 频繁重启问题调查"
description: "健康检查失败导致频繁重启，无法稳定提供服务"
date: 2022.11.20 10:34
categories:
    - K8s
    - Cloud Native
tags: [MySQL, Kubernetes, Linux, cgroup]
keywords: MySQL, K8s, cgroup, pids.max, pids.current, ulimit
cover: /contents/covers/msyql-in-k8s-cannot-create-thread.png
---

现象
===

K8s 集群中部署了一个 MySQL 实例，使用过程中发现，由于配置了健康检查，健康检查频繁失败，导致容器被频繁重启，无法提供稳定的 MySQL 服务。

MySQL 日志中的相关报错信息如下：

```log
[ERROR] Can't create thread to handle new connection(errno= 11)
```

在重新启动后，能够正常使用一小段时间，之后就会报出这个错误，并陆续关闭客户端连接，直至关闭服务，重启容器。如此反复，每天能重启近百次。


调查
===

通过 `kubectl describe pod` 查看问题容器组的最后状态：

```text
    Last State:     Terminated
      Reason:       ContainerCannotRun
      Message:      OCI runtime create failed: container_linux.go:380: starting container process caused: process_linux.go:402: getting the final child's pid from pipe caused: EOF: unknown
      Exit Code:    128
```

查看 Message 中涉及的报错代码位置：[container_linux.go:380](https://github.com/opencontainers/runc/blob/v1.0.1/libcontainer/container_linux.go#L380)、[process_linux.go:402](https://github.com/opencontainers/runc/blob/v1.0.1/libcontainer/process_linux.go#L402)，均是与创建进程相关的内容，以为是打开文件数受到了限制，到容器及宿主机中使用 `ulimit -n` 进行查看，都是非常大的数，应该不是这个问题导致的。

受到 [docker exec 失败问题排查之旅](https://plpan.github.io/docker-exec-%E5%A4%B1%E8%B4%A5%E9%97%AE%E9%A2%98%E6%8E%92%E6%9F%A5%E4%B9%8B%E6%97%85/) 的启发，查找一下问题容器组的 `pids.max` 值：

```bash
$ kubectl get pod -n demo|grep mysql
mysql-5578d79785-wnjcl                                           2/2     Running             1          2d
$ kubectl edit pod mysql-5578d79785-wnjcl -n demo
apiVersion: v1
kind: Pod
metadata:
  ...
  ownerReferences;
  - apiVersion: apps/v1
    ...
    uid: fd41c180-5ddf-4baa-94f8-68d01c999136
  resourceVersion: "111331159"
  uid: 1c178021-5860-4495-a1ab-f9ac17877672
  ...
$ cat /sys/fs/cgroup/pids/kubepods.slice/kubepods-burstable.slice/kubepods-burstable-pod1c178021_5860_4495_a1ab_f9ac17877672.slice/pids.max
1000
```

随即监控了一下 `pids.current` 与 `pids.max` 的数值关系，以及与重启次数是否有关联。

当时 pids.max=1000，pids.current=352，restart count=14。pids.current 的值在不断增长，达到设定的 pids.max(1000) 后 MySQL 容器被重启。重启后 pids.current 降低，再逐步增加，不断循环。

重启两次后，将 `pids.max` 文件内容修改为 `max`，继续观察 pids.current 数量及是否还会重启。

一段时间后，pids.current 达到一个稳定的范围，健康检查没在发生失败的情况，容器也没有再被重启。

那么这个 `pids.max` 最初的 `1000` 是怎么来的呢？如何调整这个默认值呢？


[Pod 级别 PID 限制][pod-pid]
==========================

> Kubernetes 允许你限制 Pod 中运行的进程个数。你可以在节点级别设置这一限制，而不是为特定的 Pod 来将其设置为资源限制。每个节点都可以有不同的 PID 限制设置。 要设置限制值，你可以设置 kubelet 的命令行参数 `--pod-max-pids`，或者 在 kubelet 的 [配置文件](https://kubernetes.io/zh-cn/docs/tasks/administer-cluster/kubelet-config-file/) 中设置 `PodPidsLimit`。

例如：

```bash
$ cat /var/lib/kubelet/config.yaml |grep podPidsLimit
podPidsLimit: 1000
```

> 你需要将其设置到 kubelet 上而不是在 Pod 的 `.spec` 中为 Pod 设置资源限制。 目前还不支持在 Pod 级别设置 PID 限制。

`pids.max` 的值只与 kubelet 的配置有关，更高的 QoS 级别（如 `Guaranteed`）并不会对其造成影响。

比如：

```bash
$ kubectl describe pod test-ui-79d7c9bd8c-49msk -n demo|grep QoS
QoS Class:                   Guaranteed
```

```bash
$ kubectl get pods test-ui-79d7c9bd8c-49msk -n demo -o jsonpath='{.metadata.uid}'
1ec564f6-d7ef-40fb-8550-a8e71c37aced
```

```bash
$ cat /sys/fs/cgroup/pids/kubepods.slice/kubepods-pod1ec564f6_d7ef_40fb_8550_a8e71c37aced.slice/pids.max
1000
```


参考资料
=======

* [源码逐层分析k8s中的 Cgroup](https://blog.csdn.net/chengyinwu/article/details/120881182)
* [Linux Namespace和Cgroup](https://segmentfault.com/a/1190000009732550)
* [Linux Cgroup系列（01）：Cgroup概述](https://segmentfault.com/a/1190000006917884)
* [Linux Cgroup系列（02）：创建并管理cgroup](https://segmentfault.com/a/1190000007241437)
* [Linux Cgroup系列（03）：限制cgroup的进程数（subsystem之pids）](https://segmentfault.com/a/1190000007468509)
* [Linux Cgroup系列（04）：限制cgroup的内存使用（subsystem之memory）](https://segmentfault.com/a/1190000008125359)
* [Linux Cgroup系列（05）：限制cgroup的CPU使用（subsystem之cpu）](https://segmentfault.com/a/1190000008323952)
* https://www.kernel.org/doc/Documentation/cgroup-v1/pids.txt
* https://www.kernel.org/doc/Documentation/cgroup-v2.txt
* [linux系统pid的最大值研究](https://www.cnblogs.com/ZhaoKevin/p/12310662.html)
* [重学容器30: 容器资源限制之限制容器的进程数量](https://blog.frognew.com/2021/07/relearning-container-30.html)
* [Process ID Limits And Reservations](https://kubernetes.io/docs/concepts/policy/pid-limiting/)

[pod-pid]:https://kubernetes.io/zh-cn/docs/concepts/policy/pid-limiting/#pod-pid-limits