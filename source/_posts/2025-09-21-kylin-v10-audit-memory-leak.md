---
id: kylin-v10-audit-memory-leak
title: "【转】麒麟v10操作系统audit内存溢出引发的k8s灾难性雪崩"
description: "大模型金牌辅助"
date: 2025.09.21 10:34
categories:
    - Linux
tags: [Linux]
keywords: Kylin, audit, memory leak, Kubernetes, k8s
cover: /contents/covers/kylin-v10-audit-memory-leak.png
---

- 作者：[微凉哇](https://www.jianshu.com/u/d682f8cbe064)
- 原文：[麒麟v10操作系统audit内存溢出引发的k8s灾难性雪崩](https://www.jianshu.com/p/486f443d05d6)

笔者最近在国产化操作系统部署了一套k8s服务，今天发现好多应用都出现无法调度的问题。原因均指向：节点内存不足。

环境信息

```bash
[root@localhost ~]# rpm -qa|grep audit
audit-libs-3.0-5.se.06.ky10.x86_64
python3-audit-3.0-5.se.06.ky10.x86_64
audit-3.0-5.se.06.ky10.x86_64
[root@localhost ~]# cat /etc/system-release
Kylin Linux Advanced Server release V10 (Sword)
[root@localhost  ~]# uname -a
Linux localhost  4.19.90-24.4.v2101.ky10.x86_64 #1 SMP Mon May 24 12:14:55 CST 2021 x86_64 x86_64 x86_64 GNU/Linux
```

查看节点负载，发现确实爆了。

```bash
[root@node1 ~]# kubectl top nodes
NAME     CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%
node1    266m         3%     6254Mi          46%
node10   350m         4%     13521Mi         100%
node11   195m         2%     13332Mi         98%
node2    105m         1%     13410Mi         99%
node3    321m         4%     13280Mi         98%
node4    543m         1%     53915Mi         90%
node5    326m         1%     47163Mi         79%
node6    175m         2%     13393Mi         99%
node7    92m          1%     13656Mi         101%
node8    65m          0%     13499Mi         99%
node9    3641m        47%    13671Mi         101%
```

不禁疑惑起来：最近也没部署新的服务上去啊，为什么内存会爆满？

于是选取了一个计算节点登入查看内存使用情况

```bash
[root@node7 ~]# free -g
              total        used        free      shared  buff/cache   available
Mem:             14          12           0           0           2           1
Swap:             0           0           0
```

查看内存占用排名靠前的进程

```bash
[root@localhost ~]# top -o %MEM -b -n 1 | head -n 12
top - 13:46:08 up 25 days,  2:40,  1 user,  load average: 0.00, 0.03, 0.06
Tasks: 174 total,   1 running, 173 sleeping,   0 stopped,   0 zombie
%Cpu(s):  0.8 us,  0.0 sy,  0.0 ni, 99.2 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
MiB Mem :  14753.7 total,    283.2 free,  12475.4 used,   1995.0 buff/cache
MiB Swap:      0.0 total,      0.0 free,      0.0 used.   1060.9 avail Mem

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
  782 root      16  -4   11.6g  11.5g   1120 S   0.0  80.1   8:19.34 auditd
  568 root      20   0  378080 250064 248740 S   0.0   1.7   5:49.80 systemd-journal
36652 root      20   0 2304684 129648  65600 S   6.7   0.9   2:56.32 kubelet
37206 root      20   0 1949520  91460  42348 S   0.0   0.6   1:09.16 dockerd
38224 root      20   0 1905792  78332  47480 S   0.0   0.5   1:18.58 calico-node
```

好家伙，`auditd`进程占用了11G。由于是系统级服务，笔者首先想到了是不是内核/操作系统的Bug导致的内存溢出。于是求证大模型

![](https://alphahinex.github.io/contents/covers/kylin-v10-audit-memory-leak.png)

竟然是软件本身的问题，于是按照大模型的指导升级了`audit`版本，并重启服务。

再次查看节点负载，恢复正常。

```bash
[root@node1 ~]# kubectl top nodes
NAME     CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%
node1    232m         3%     3910Mi          28%
node10   363m         4%     2466Mi          18%
node11   140m         1%     2262Mi          16%
node2    410m         5%     2668Mi          19%
node3    209m         2%     3875Mi          28%
node4    633m         2%     40443Mi         68%
node5    282m         0%     33690Mi         56%
node6    247m         3%     2689Mi          19%
node7    83m          1%     2173Mi          16%
node8    105m         1%     2013Mi          14%
node9    158m         2%     5146Mi          38%
```

持续关住...