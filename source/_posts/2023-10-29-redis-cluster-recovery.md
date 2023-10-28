---
id: redis-cluster-recovery
title: "Redis 5 集群断电故障处理指北"
description: "整理一些 Redis 5 集群故障的处理方式"
date: 2023.10.29 10:34
categories:
    - Redis
tags: [Redis, K8s]
keywords: Redis CLI, Redis Cluster, nodes.conf, corrupted cluster config file, bitnami
cover: /contents/covers/redis-cluster-recovery.png
---

现象
====

- Redis 版本：5.0.9
- Redis 集群使用 [Bitnami Redis Cluster Chart](https://github.com/bitnami/charts/tree/main/bitnami/redis-cluster)（appVersion: 5.0.9, version: 2.0.14）部署在 K8s 中
- 集群配置：三主三从六节点

集群断电后重启出现故障节点，报错日志 `Unrecoverable error: corrupted cluster config file.`。


故障时集群各节点状态
-----------------

在 [Redis CLI](https://redis.io/docs/connect/cli/) 中可通过 [cluster nodes](https://redis.io/commands/cluster-nodes/)、[cluster info](https://redis.io/commands/cluster-info/)、[info](https://redis.io/commands/info/) 等命令查看集群节点、集群状态及节点主从关系，也可以直接从各节点的 `nodes.conf` 文件中查看。

### redis-cluster-0（主）

- IP：10.0.2.131
- nodes.conf

```conf
cd17f6c6c9808521f23b6f2d35e797f2a62444fc 10.1.59.108:6379@16379 slave e998e0c78ddd89ef7d0989a19ff5dcd11348656c 0 1695612120166 8 connected
e998e0c78ddd89ef7d0989a19ff5dcd11348656c 10.0.2.131:6379@16379 myself,master - 0 1695612121000 8 connected 5461-10922
53e4379e78ed29a16ba752daa244329b16fd4d12 10.0.0.8:6379@16379 master - 0 1695612121603 7 connected 0-5460
008179f63e12ca74cfac49fb305bcdec33d0f988 10.1.61.78:6379@16379 slave,fail 53e4379e78ed29a16ba752daa244329b16fd4d12 1695612044535 1695612044535 7 disconnected
955c9b55ecfb0cee0b2e906db4a5bc8ae227b68a 10.0.0.175:6379@16379 master,fail - 1695612044535 1695612044535 3 disconnected 10923-16383
682b478c0ae0c6a02cecd47a04e8a6c9a53b0a1f 10.0.2.148:6379@16379 slave,fail 955c9b55ecfb0cee0b2e906db4a5bc8ae227b68a 1695612044535 1695612044535 4 disconnected
vars currentEpoch 8 lastVoteEpoch 0
```

### redis-cluster-1（主）

- IP：10.0.0.8
- nodes.conf

```conf
682b478c0ae0c6a02cecd47a04e8a6c9a53b0a1f 10.0.2.76:6379@16379 slave,fail 955c9b55ecfb0cee0b2e906db4a5bc8ae227b68a 1695612121508 1695612121508 3 connected
955c9b55ecfb0cee0b2e906db4a5bc8ae227b68a 10.0.0.175:6379@16379 master,fail - 1695612121508 1695612121508 3 disconnected 10923-16383
e998e0c78ddd89ef7d0989a19ff5dcd11348656c 10.0.2.131:6379@16379 master - 0 1697706582722 8 connected 5461-10922
cd17f6c6c9808521f23b6f2d35e797f2a62444fc 10.1.59.108:6379@16379 slave e998e0c78ddd89ef7d0989a19ff5dcd11348656c 0 1697706582118 8 connected
008179f63e12ca74cfac49fb305bcdec33d0f988 10.1.61.78:6379@16379 slave,fail 53e4379e78ed29a16ba752daa244329b16fd4d12 1695612121508 1695612121508 7 disconnected
53e4379e78ed29a16ba752daa244329b16fd4d12 10.0.0.8:6379@16379 myself,master - 0 1697706582000 7 connected 0-5460
vars currentEpoch 8 lastVoteEpoch 8
```

### redis-cluster-2（从，故障）

- IP：10.0.2.148
- nodes.conf 内容为空

### redis-cluster-3（主，故障）

- IP：10.0.0.175
- nodes.conf 内容为空

### redis-cluster-4（从）

- IP：10.1.59.108
- nodes.conf

```conf
e998e0c78ddd89ef7d0989a19ff5dcd11348656c 10.0.2.131:6379@16379 master - 0 1697706582714 8 connected 5461-10922
682b478c0ae0c6a02cecd47a04e8a6c9a53b0a1f 10.0.2.76:6379@16379 slave,fail 955c9b55ecfb0cee0b2e906db4a5bc8ae227b68a 1695612016917 1695612016917 3 connected
cd17f6c6c9808521f23b6f2d35e797f2a62444fc 10.1.59.108:6379@16379 myself,slave e998e0c78ddd89ef7d0989a19ff5dcd11348656c 0 1697706582000 2 connected
53e4379e78ed29a16ba752daa244329b16fd4d12 10.0.0.8:6379@16379 master - 0 1697706582412 7 connected 0-5460
955c9b55ecfb0cee0b2e906db4a5bc8ae227b68a 10.0.0.175:6379@16379 master,fail - 1695612016917 1695612016917 3 disconnected 10923-16383
008179f63e12ca74cfac49fb305bcdec33d0f988 10.1.61.78:6379@16379 slave,fail 53e4379e78ed29a16ba752daa244329b16fd4d12 1695612016917 1695612016917 7 disconnected
vars currentEpoch 8 lastVoteEpoch 7
```

### redis-cluster-5（从，故障）

- IP：10.1.61.78
- nodes.conf 内容为空


主从关系
-------

根据 `nodes.conf` 中的 `node-id` 整理故障集群节点主从关系如下：

|主|从|
|:--|:--|
|redis-cluster-0（5461-10922）<br>`e998e0c78ddd89ef7d0989a19ff5dcd11348656c`<br>10.0.2.131|redis-cluster-4<br>`cd17f6c6c9808521f23b6f2d35e797f2a62444fc`<br>10.1.59.108|
|redis-cluster-1（0-5460）<br>`53e4379e78ed29a16ba752daa244329b16fd4d12`<br>10.0.0.8|redis-cluster-5（故障）<br>`008179f63e12ca74cfac49fb305bcdec33d0f988`<br>10.1.61.78|
|redis-cluster-3（10923-16383）（故障）<br>`955c9b55ecfb0cee0b2e906db4a5bc8ae227b68a`<br>10.0.0.175|redis-cluster-2（故障）<br>`682b478c0ae0c6a02cecd47a04e8a6c9a53b0a1f`<br>10.0.2.148 / 10.0.2.76|


故障恢复
=======


清理故障节点信息
--------------

在集群健康节点中使用 [cluster forget](https://redis.io/commands/cluster-forget/) 清理故障节点信息。

可创建如下脚本协助自动清理，根据实际情况调整 `host_array` 中 `host`、`-p` 端口和 `-a` 密码：

```shell forget.sh
host_array="10.0.2.131 10.0.0.8 10.1.59.108"
for var in $host_array;
do
    nodeids=`redis-cli -c -h $var -p 6379 -a redis cluster nodes|grep fail|awk '{print $1}'`
    for d in $nodeids
    do
        echo $d
        redis-cli -c -h $var -p 6379 -a redis cluster forget $d
    done
done
```


创建 Sidecar 容器
----------------

创建 [Sidecar](https://github.com/bitnami/charts/tree/main/bitnami/redis-cluster#sidecars-and-init-containers) 容器 `redis-tool` 挂载 Redis 主容器配置文件、数据目录等，以便重建故障节点。可参考如下配置：

```yml
sidecars:
  - name: redis-tool
    image: {{ include "redis-cluster.image" . }}
    imagePullPolicy: Always
    volumeMounts:
      - name: redis-data
        mountPath: {{ .Values.persistence.path }}
        subPath: {{ .Values.persistence.subPath }}
      - name: redis-tmp-conf
        mountPath: /opt/bitnami/redis/etc/
```


修复主节点
---------

优先修复主节点。

在故障主节点 redis-cluster-3 的 `redis-tool` 容器终端中，删除内容为空的 `nodes.conf`，使用 `/opt/bitnami/redis/etc/redis.conf` 配置文件重新启动 Redis 进程：

```shell
redis-server /opt/bitnami/redis/etc/redis.conf
```

启动成功后，在集群任意非故障节点使用 [cluster meet](https://redis.io/commands/cluster-meet/) 将重新启动的主节点添加到集群中：

```redis-cli
127.0.0.1:6379> cluster meet 10.0.0.175 6379
OK
```

完成配置后，可直接移除该 pod，使其自动重建，完成该节点故障恢复。


修复从节点
--------

从节点的修复步骤与修复主节点类似：

1. 清理已损坏的 `nodes.conf`
1. 重新启动 Redis 进程
1. 将重启后的节点加入集群

此外，修复从节点还需一步操作：配置节点的主从关系。

以将 redis-cluster-5 配置为 redis-cluster-1 的从节点为例：在 redis-cluster-5 实例的 Redis CLI 中使用 [cluster replicate](https://redis.io/commands/cluster-replicate/) 指定 redis-cluster-1 节点的 `node-id`（可从 `nodes.conf` 中获得）：

```redis-cli
127.0.0.1:6379> cluster replicate 53e4379e78ed29a16ba752daa244329b16fd4d12
OK
```

完成配置后，可直接移除该 pod，使其自动重建，完成该节点故障恢复。


其他问题
=======

集群节点 IP 错误
---------------

使用 Bitnami 早期版本的 Redis Cluster Chart 时，可能会遇到 Redis 节点的 `nodes.conf` 中出现非法 IP 的情况，如：`10.233.95.2365`。

Chart 所使用的 [Redis Cluster 镜像](https://github.com/bitnami/containers/tree/main/bitnami/redis-cluster) 中有一个 `/opt/bitnami/scripts/librediscluster.sh` 脚本，负责在容器启动时更新 `nodes.conf` 中当前节点的 IP。

出现上述非法 IP 的原因是该脚本的早期版本在使用 `sed` 更新 IP 时存在 bug，可在 git 仓库中找新版脚本，再覆盖镜像中问题脚本即可。


集群状态为 fail
-------------

Redis 集群模式需要将 16384 个 slot 都分配到主节点上，集群状态才会是 ok，否则为 fail，如：

```info
cluster_state:ok
cluster_slots_assigned:16384
cluster_slots_ok:16384
cluster_slots_pfail:0
cluster_slots_fail:0
cluster_known_nodes:6
cluster_size:3
cluster_current_epoch:6
cluster_my_epoch:2
cluster_stats_messages_sent:1483972
cluster_stats_messages_received:1483968
total_cluster_links_buffer_limit_exceeded:0
```

```info
cluster_state:fail
cluster_slots_assigned:10922
cluster_slots_ok:10922
```

可通过 [cluster slots](https://redis.io/commands/cluster-slots/) 查看 Redis 集群各主节点的 slot 分配情况，[cluster addslots](https://redis.io/commands/cluster-addslots/) 为主节点分配 slot，如：

```redis-cli
cluster addslots 10922 10923 10924
```

`cluster addslots` 命令只能逐个 slot 分配，不能像 Redis 7.0 版本引入的 [cluster addslotsrange](https://redis.io/commands/cluster-addslotsrange/) 命令一样分配一个范围的 slot。遇到需要分配大量连续 slot 时，可参考如下 Shell 脚本方式实现批量分配：

```shell
for i in $(seq 10923 16383); do
    echo $i
    redis-cli -c -h localhost -p 6379 -a redis cluster addslots $i
done
```