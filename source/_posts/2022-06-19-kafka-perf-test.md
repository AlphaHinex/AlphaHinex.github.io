---
id: kafka-perf-test
title: "Kafka 性能测试"
description: "使用自带脚本进行性能测试"
date: 2022.06.19 10:34
categories:
    - Kafka
tags: [Kafka, Java]
keywords: Kafka, Producer, Consumer, Performance, Test
cover: /contents/covers/kafka-perf-test.jpeg
---

## Kafka 自带脚本简介

在 [Apache Kafka](https://kafka.apache.org/) 安装目录的 `bin` 路径下，包括启停服务在内的很多脚本。这些脚本能够帮助我们完成对 Kafka 的各类操作，其中就有对生产者和消费者进行性能测试的工具。

脚本分为两个版本：Linux 下执行的 Shell 脚本，以及 Windows 下执行的 bat 脚本。

以 Shell 脚本为例，可以查看脚本内容，除了停止 ZooKeeper 和 Kafka 服务的脚本外，其余脚本均会在最后调用 `kafka-run-class.sh` 并根据使用脚本的不同，传入不同的类进行处理。

本文主要涉及下面五个脚本：

1. `kafka-topics.sh` —— 操作主题
1. `kafka-console-producer.sh` —— 控制台生产者
1. `kafka-console-consumer.sh` —— 控制台消费者
1. `kafka-producer-perf-test.sh` —— 生产者性能测试
1. `kafka-consumer-perf-test.sh` —— 消费者性能测试

可以先随便执行一个脚本查看一下是否能够正常执行脚本，如：

```bash
$ ./kafka-topics.sh --version
2.4.1 (Commit:c57222ae8cd7866b)
```

> 如果在执行脚本时，遇到端口占用等问题无法正常执行，可以查看 `kafka-run-class.sh` 脚本查找原因。例如 JMX 端口被占用时，可通过环境变量重新指定端口后再执行脚本：`JMX_PORT=6666 ./kafka-topics.sh --version`。

## 创建主题

可参照如下命令，创建一个名为 `hinex-topic` 的主题，分区数为 `6`，副本数为 `2`：

```bash
$ ./kafka-topics.sh --create --bootstrap-server localhost:9092 --topic hinex-topic --partitions 6 --replication-factor 2
```

命令执行成功后，可以在消息代理的日志路径（`<log.dirs>/<topic>-<partition_idx>`）中，看到分区的存储目录。本例中第一个分区在第三个消息代理节点上的存储路径为 `/kafka/kafka-logs-kafka-sh-2/hinex-topic-0`。关于 Kafka 的记录存储结构，可阅读 [【译】深入了解 Apache Kafka 存储内部](https://alphahinex.github.io/2022/06/12/deep-dive-into-apache-kafka-storage-internals/) 了解更多。


## 控制台生产者及消费者

可通过脚本，在控制台中生产及消费消息，验证消息队列基本功能。

在一个终端窗口中启动生产者：

```bash
$ ./kafka-console-producer.sh --broker-list localhost:9092 --topic hinex-topic
```

在另一个终端窗口中启动消费者：

```bash
$ ./kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic hinex-topic
```

此时在生产者中输入消息内容并回车，消费者终端窗口中可以接收到消息。

功能正常，接下来可以开始进行性能测试了。


## 生产者性能测试

由于测试用的主题中并没有什么消息记录，所以先进行生产者性能测试产生消息，再进行消费者性能测试。

可参照如下方式，使用 `kafka-producer-perf-test.sh` 脚本，约每秒钟产生 10 条消息，每条消息 1024 字节，共产生 200 条消息：

```bash
$ ./kafka-producer-perf-test.sh --producer-props bootstrap.servers=localhost:9092 --topic hinex-topic --throughput 10 --record-size 1024 --num-records 200
52 records sent, 10.4 records/sec (0.01 MB/sec), 14.9 ms avg latency, 428.0 ms max latency.
50 records sent, 10.0 records/sec (0.01 MB/sec), 2.2 ms avg latency, 3.0 ms max latency.
50 records sent, 10.0 records/sec (0.01 MB/sec), 1.9 ms avg latency, 3.0 ms max latency.
200 records sent, 10.005003 records/sec (0.01 MB/sec), 5.40 ms avg latency, 428.00 ms max latency, 2 ms 50th, 14 ms 95th, 26 ms 99th, 428ms 99.9th.
```

从执行结果中，可以看到消息发送的进度、每秒发送的消息数及数据量、平均延迟及最大延迟等统计信息。

如果想测试一下消息队列的吞吐量，可以将 `--throughput` 参数设为 `-1`：

```bash
$ ./kafka-producer-perf-test.sh --producer-props bootstrap.servers=localhost:9092 --topic hinex-topic --throughput -1 --record-size 1024 --num-records 1000000
685215 records sent, 137043.0 records/sec (133.83 MB/sec), 189.0 ms avg latency, 665.0 ms max latency.
1000000 records sent, 133333.333333 records/sec (130.21 MB/sec), 206.16 ms avg latency, 679.00 ms max latency, 134 ms 50th, 629 ms 95th, 668 ms 99th, 677 ms 99.9th.
```


## 消费者性能测试

消费者性能测试可使用 `kafka-consumer-perf-test.sh` 脚本，如：

```bash
$ ./kafka-consumer-perf-test.sh --broker-list localhost:9092 --topic hinex-topic --messages 1000000
start.time, end.time, data.consumed.in.MB, MB.sec, data.consumed.in.nMsg, nMsg.sec, rebalance.time.ms, fetch.time.ms, fetch.MB.sec, fetch.nMsg.sec
2022-06-16 06:58:43:565, 2022-06-16 06:58:46:464, 976.7813, 336.9373, 1000224, 345023.8013, 1655362724003, -1655362721104, -0.0000, -0.0006
```

可通过 `kafka-consumer-perf-test.sh --help` 获得参数详细说明。


## 清理测试数据

测试结束后，可将测试主题删除：

```bash
$ ./kafka-topics.sh --delete --bootstrap-server localhost:9092 --topic hinex-topic
```

> 注意，执行删除操作后，分区目录不会被立即删除，而是会添加 `delete` 后缀，需等待清理线程确实将目录从磁盘删除后，才能再次创建同名主题。


## 实测数据

对照 [Benchmarking Apache Kafka: 2 Million Writes Per Second (On Three Cheap Machines)](https://engineering.linkedin.com/kafka/benchmarking-apache-kafka-2-million-writes-second-three-cheap-machines) 中场景，使用自带脚本进行一组实测。

每组测试使用 5 千万条记录，每条记录大小为 100 字节。

### 仅生产者

各场景结果汇总如下：

|场景|引文|实测|
|:---|:---|:---|
|单个生产者，6 分区无副本| 821,557 records/sec (78.3 MB/sec)| 1,000,000 records/sec (95.37 MB/sec)|
|单个生产者，6 分区 3 异步副本| 786,980 records/sec (75.1 MB/sec)| 615,558 records/sec (58.70 MB/sec)|
|单个生产者，6 分区 3 同步副本| 421,823 records/sec (40.2 MB/sec)| 335,629 records/sec (32.01 MB/sec)|
|三个生产者，6 分区无副本| 2,024,032 records/sec (193.0 MB/sec)| 2,646,892 records/sec (252.42 MB/sec)|

各场景运行过程记录如下。

#### 场景一：单个生产者，6 分区无副本

```bash
$ ./kafka-topics.sh --create --bootstrap-server localhost:9092 --topic topic-6-1 --partitions 6

$ ./kafka-producer-perf-test.sh --producer-props bootstrap.servers=localhost:9092 --topic topic-6-1 --throughput -1 --record-size 100 --num-records 50000000
50000000 records sent, 1000000.000000 records/sec (95.37 MB/sec), 24.25 ms avg latency, 1206.00 ms max latency, 3 ms 50th, 112 ms 95th, 498 ms 99th, 1094 ms 99.9th.
```

#### 场景二：单个生产者，6 分区 3 异步副本

```bash
$ ./kafka-topics.sh --create --bootstrap-server localhost:9092 --topic topic-6-3 --partitions 6 --replication-factor 3

$ ./kafka-producer-perf-test.sh --producer-props bootstrap.servers=localhost:9092 acks=1 --topic topic-6-3 --throughput -1 --record-size 100 --num-records 50000000
50000000 records sent, 615558.865894 records/sec (58.70 MB/sec), 375.32 ms avg latency, 2870.00 ms max latency, 84 ms 50th, 1253 ms 95th,2091 ms 99th, 2806 ms 99.9th.
```

#### 场景三：单个生产者，6 分区 3 同步副本

```bash
$ ./kafka-producer-perf-test.sh --producer-props bootstrap.servers=localhost:9092 acks=all --topic topic-6-3 --throughput -1 --record-size 100 --num-records 50000000
50000000 records sent, 335629.035939 records/sec (32.01 MB/sec), 873.85 ms avg latency, 4041.00 ms max latency, 791 ms 50th, 2017 ms 95th, 3058 ms 99th, 3872 ms 99.9th.
```

#### 场景四：三个生产者，6 分区无副本

三个终端同时执行如下命令（两个生产 1700 万数据，一个生产 1600 万数据）：

```bash
$ /opt/kafka/bin/kafka-producer-perf-test.sh --producer-props bootstrap.servers=kafka-sh.app-ns:9092 --topic topic-6-1 --throughput -1 --record-size 100 --num-records 17000000
```

```bash
# 终端一结果：
17000000 records sent, 880829.015544 records/sec (84.00 MB/sec), 30.52 ms avg latency, 368.00 ms max latency, 4 ms 50th, 232 ms 95th, 323 ms 99th, 350 ms 99.9th.

# 终端二结果：
17000000 records sent, 906956.892872 records/sec (86.49 MB/sec), 31.32 ms avg latency, 568.00 ms max latency, 5 ms 50th, 167 ms 95th, 381 ms 99th, 455 ms 99.9th.

# 终端三结果：
16000000 records sent, 859106.529210 records/sec (81.93 MB/sec), 21.48 ms avg latency, 438.00 ms max latency, 4 ms 50th, 105 ms 95th, 239 ms 99th, 373 ms 99.9th.
```

### 仅消费者

各场景使用 6 分区 3 副本的主题，结果汇总如下：

|场景|引文|实测|
|:---|:---|:---|
|单个消费者| 940,521 records/sec (89.7 MB/sec)| 2,527,424 records/sec (241.03 MB/sec)|
|三个消费者| 2,615,968 records/sec (249.5 MB/sec)| 6,403,110 records/sec (610.65 MB/sec)|

各场景运行过程记录如下。

#### 场景一：单个消费者

```bash
$ /opt/kafka/bin/kafka-consumer-perf-test.sh --broker-list kafka-sh.app-ns:9092 --topic topic-6-3 --messages 50000000
start.time, end.time, data.consumed.in.MB, MB.sec, data.consumed.in.nMsg, nMsg.sec, rebalance.time.ms, fetch.time.ms, fetch.MB.sec, fetch.nMsg.sec
2022-06-16 07:46:52:812, 2022-06-16 07:47:12:595, 4768.3754, 241.0340, 50000040, 2527424.5564, 1655372813244, -1655372793461, -0.0000, -0.0302
```

#### 场景二：三个消费者

三个终端同时执行如下命令（两个消费 1700 万数据，一个消费 1600 万数据）：

```bash
$ /opt/kafka/bin/kafka-consumer-perf-test.sh --broker-list kafka-sh.app-ns:9092 --topic topic-6-3 --messages 17000000
```

```bash
# 终端一结果：
start.time, end.time, data.consumed.in.MB, MB.sec, data.consumed.in.nMsg, nMsg.sec, rebalance.time.ms, fetch.time.ms, fetch.MB.sec, fetch.nMsg.sec
2022-06-16 07:47:50:540, 2022-06-16 07:47:58:508, 1621.2508, 203.4702, 17000047, 2133540.0351, 1655430470988, -1655430463020, -0.0000, -0.0103

# 终端二结果：
start.time, end.time, data.consumed.in.MB, MB.sec, data.consumed.in.nMsg, nMsg.sec, rebalance.time.ms, fetch.time.ms, fetch.MB.sec, fetch.nMsg.sec
2022-06-16 07:47:50:474, 2022-06-16 07:47:58:614, 1621.2880, 199.1754, 17000437, 2088505.7740, 1655430470849, -1655430462709, -0.0000, -0.0103

# 终端三结果：
start.time, end.time, data.consumed.in.MB, MB.sec, data.consumed.in.nMsg, nMsg.sec, rebalance.time.ms, fetch.time.ms, fetch.MB.sec, fetch.nMsg.sec
2022-06-16 07:47:50:567, 2022-06-16 07:47:57:903, 1525.9067, 208.0025, 16000291, 2181064.7492, 1655430470939, -1655430463603, -0.0000, -0.0097
```

### 生产同时消费

使用一个新的 6 分区 3 副本的主题，生产脚本和消费脚本同时执行。

引文：795,064 records/sec (75.8 MB/sec)
实测：738,836 records/sec (70.46 MB/sec)

生产者终端：

```bash
$ /opt/kafka/bin/kafka-topics.sh --create --bootstrap-server kafka-sh.app-ns:9092 --topic newer-6-3 --partitions 6 --replication-factor 3

$ /opt/kafka/bin/kafka-producer-perf-test.sh --producer-props bootstrap.servers=kafka-sh.app-ns:9092 --topic newer-6-3 --throughput -1 --record-size 100 --num-records 50000000
50000000 records sent, 738836.185241 records/sec (70.46 MB/sec), 148.42 ms avg latency, 2406.00 ms max latency, 18 ms 50th, 840 ms 95th, 1596 ms 99th, 2278 ms 99.9th.
```

消费者终端：

```bash
$ /opt/kafka/bin/kafka-consumer-perf-test.sh --broker-list kafka-sh.app-ns:9092 --topic newer-6-3 --messages 50000000
start.time, end.time, data.consumed.in.MB, MB.sec, data.consumed.in.nMsg, nMsg.sec, rebalance.time.ms, fetch.time.ms, fetch.MB.sec, fetch.nMsg.sec
2022-06-16 07:58:37:525, 2022-06-16 07:59:44:772, 4768.3716, 70.9083, 50000000, 743527.5923, 1655373517960, -1655373450713, -0.0000, -0.0302
```