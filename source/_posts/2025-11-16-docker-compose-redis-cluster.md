---
id: docker-compose-redis-cluster
title: "Docker Compose 单机 Redis Cluster"
description: "三主三从六节点，端口映射，不依赖 host 网络模式。需要有一个 IP（可内网）。"
date: 2025.11.16 10:34
categories:
    - Redis
    - Docker
tags: [Redis, Docker, Mac, Linux]
keywords: Redis, RedisBloom, Redis Cluster, Docker, Docker Compose, docker-compose, Port Mapping, host network mode
cover: /contents/covers/docker-compose-redis-cluster.png
---

# 前置条件

- 安装 Docker 和 Docker Compose
- 有一个可用 IP 地址（可以是内网 IP），以便端口映射后，容器间通过此 IP 进行通讯

> 不依赖 host 网络模式，Mac 可用。

# 配置文件

```bash
$ tree
.
├── cleanup.sh
├── docker-compose.yml
├── redis.conf
└── start.sh
```

> https://github.com/AlphaHinex/compose-docker/tree/master/redis-cluster

## docker-compose.yml

```yml
version: "3.8"

services:
  redis-7000:
    image: redis:8.2.2
    privileged: true
    container_name: redis-7000
    ports:
      - 7000:7000
      - 17000:17000
    volumes:
      - ./redis.conf:/usr/local/etc/redis/redis.conf
      - ./7000/data:/data
    command: redis-server /usr/local/etc/redis/redis.conf --cluster-announce-ip ${LOCALHOST_IP} --port 7000

  redis-7001:
    image: redis:8.2.2
    privileged: true
    container_name: redis-7001
    ports:
      - 7001:7001
      - 17001:17001
    volumes:
      - ./redis.conf:/usr/local/etc/redis/redis.conf
      - ./7001/data:/data
    command: redis-server /usr/local/etc/redis/redis.conf --cluster-announce-ip ${LOCALHOST_IP} --port 7001

  redis-7002:
    image: redis:8.2.2
    privileged: true
    container_name: redis-7002
    ports:
      - 7002:7002
      - 17002:17002
    volumes:
      - ./redis.conf:/usr/local/etc/redis/redis.conf
      - ./7002/data:/data
    command: redis-server /usr/local/etc/redis/redis.conf --cluster-announce-ip ${LOCALHOST_IP} --port 7002

  redis-7003:
    image: redis:8.2.2
    privileged: true
    container_name: redis-7003
    ports:
      - 7003:7003
      - 17003:17003
    volumes:
      - ./redis.conf:/usr/local/etc/redis/redis.conf
      - ./7003/data:/data
    command: redis-server /usr/local/etc/redis/redis.conf --cluster-announce-ip ${LOCALHOST_IP} --port 7003

  redis-7004:
    image: redis:8.2.2
    privileged: true
    container_name: redis-7004
    ports:
      - 7004:7004
      - 17004:17004
    volumes:
      - ./redis.conf:/usr/local/etc/redis/redis.conf
      - ./7004/data:/data
    command: redis-server /usr/local/etc/redis/redis.conf --cluster-announce-ip ${LOCALHOST_IP} --port 7004

  redis-7005:
    image: redis:8.2.2
    privileged: true
    container_name: redis-7005
    ports:
      - 7005:7005
      - 17005:17005
    volumes:
      - ./redis.conf:/usr/local/etc/redis/redis.conf
      - ./7005/data:/data
    command: redis-server /usr/local/etc/redis/redis.conf --cluster-announce-ip ${LOCALHOST_IP} --port 7005

  redis-cluster-creator:
    image: redis:8.2.2
    privileged: true
    depends_on:
      - redis-7000
      - redis-7001
      - redis-7002
      - redis-7003
      - redis-7004
      - redis-7005
    command: |
      redis-cli --cluster create 
      ${LOCALHOST_IP}:7000 ${LOCALHOST_IP}:7001 ${LOCALHOST_IP}:7002 ${LOCALHOST_IP}:7003 ${LOCALHOST_IP}:7004 ${LOCALHOST_IP}:7005 
      --cluster-replicas 1 --cluster-yes
```

## redis.conf

```conf
cluster-enabled yes
cluster-config-file nodes.conf
cluster-node-timeout 5000
appendonly yes
```

## start & cleanup

```start.sh
#!/bin/bash

# Allow LOCALHOST_IP to be set via environment, otherwise detect automatically
if [ -z "$LOCALHOST_IP" ]; then
    OS_TYPE="$(uname)"
    if [ "$OS_TYPE" = "Darwin" ]; then
        LOCALHOST_IP=$(ipconfig getifaddr en0)
    elif [ "$OS_TYPE" = "Linux" ]; then
        LOCALHOST_IP=$(hostname -I | awk '{print $1}')
    else
        echo "Warning: Unknown OS type '$OS_TYPE'. Please set LOCALHOST_IP manually."
        LOCALHOST_IP="127.0.0.1"
    fi
fi
echo $LOCALHOST_IP

COMPOSE_CMD="docker compose"

if docker-compose --version >/dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
fi

LOCALHOST_IP=$LOCALHOST_IP $COMPOSE_CMD up -d
```

```cleanup.sh
#!/bin/bash

COMPOSE_CMD="docker compose"

if docker-compose --version >/dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
fi

$COMPOSE_CMD stop
$COMPOSE_CMD rm -f
rm -rf 700{0..5}
```

# 用法

```bash
# 用脚本启动
# 或手动执行 LOCALHOST_IP=192.168.1.16 docker compose up -d 命令
$ ./start.sh
```

```bash
# 进入容器验证集群状态
$ docker exec -it redis-7000 redis-cli -c -p 7000

127.0.0.1:7000> cluster info
cluster_state:ok
cluster_slots_assigned:16384
cluster_slots_ok:16384
cluster_slots_pfail:0
cluster_slots_fail:0
cluster_known_nodes:6
cluster_size:3
cluster_current_epoch:6
cluster_my_epoch:1
cluster_stats_messages_ping_sent:20
cluster_stats_messages_pong_sent:23
cluster_stats_messages_sent:43
cluster_stats_messages_ping_received:18
cluster_stats_messages_pong_received:20
cluster_stats_messages_meet_received:5
cluster_stats_messages_received:43
total_cluster_links_buffer_limit_exceeded:0

127.0.0.1:7000> cluster nodes
3c8fc7b10e45b3c75ccade532ef8d62f8bb400a0 10.88.37.116:7002@17002 master - 0 1763085993000 3 connected 10923-16383
90c5f72f443342a1ffe48dbd9d4edbcd2432a2f6 10.88.37.116:7001@17001 master - 0 1763085992896 2 connected 5461-10922
399146e000c59895097ab2f281992680ffaa9ae1 10.88.37.116:7005@17005 slave 90c5f72f443342a1ffe48dbd9d4edbcd2432a2f6 0 1763085993604 2 connected
fa6366530ffc50669c51b42e4e4d01a85cdd159a 10.88.37.116:7003@17003 slave 3c8fc7b10e45b3c75ccade532ef8d62f8bb400a0 0 1763085993604 3 connected
e3a8ee89a20d079e84a8195e6170bbf96fda03aa 10.88.37.116:7004@17004 slave 870a912e496ce6528048a681bf95851271b91c48 0 1763085993906 1 connected
870a912e496ce6528048a681bf95851271b91c48 10.88.37.116:7000@17000 myself,master - 0 0 1 connected 0-5460

127.0.0.1:7000> set foo bar
-> Redirected to slot [12182] located at 10.88.37.116:7002
OK
10.88.37.116:7002> bf.reserve t1 0.1 1000000
-> Redirected to slot [8943] located at 10.88.37.116:7001
OK
10.88.37.116:7001> get foo
-> Redirected to slot [12182] located at 10.88.37.116:7002
"bar"
10.88.37.116:7002> bf.info t1
-> Redirected to slot [8943] located at 10.88.37.116:7001
 1) Capacity
 2) (integer) 1000000
 3) Size
 4) (integer) 779504
 5) Number of filters
 6) (integer) 1
 7) Number of items inserted
 8) (integer) 0
 9) Expansion rate
10) (integer) 2
```

```bash
# 清理集群数据和容器
$ ./cleanup.sh
```
