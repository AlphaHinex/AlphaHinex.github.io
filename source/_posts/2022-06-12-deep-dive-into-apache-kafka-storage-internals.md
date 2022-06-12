---
id: deep-dive-into-apache-kafka-storage-internals
title: "【译】深入了解 Apache Kafka 存储内部"
description: "Deep dive into Apache Kafka storage internals: segments, rolling and retention"
date: 2022.06.12 10:26
categories:
    - Kafka
tags: [Kafka, Java]
keywords: Kafka, storage, patition, segment, index, log, message, record, roll, retention
cover: /contents/deep-dive-into-apache-kafka-storage-internals/2021-12-17-index.png
---

英文原文：[Deep dive into Apache Kafka storage internals: segments, rolling and retention](https://strimzi.io/blog/2021/12/17/kafka-segment-retention/)

作者：[Paolo Patierno](https://twitter.com/ppatierno)

Apache Kafka 采用类似提交日志的方式处理消息的存储。消息一个接一个的追加在每个日志的末尾，每个日志也会被分成段。分段有助于删除较旧的消息记录及提高性能等。所以，日志是一个由段（文件）组成的消息记录的逻辑序列，每个段内存储的是一部分消息。消息代理（Broker）的配置允许您调整与日志相关的参数。您可以使用这些配置来控制段的滚动、记录的保留策略等。

> 译注：Kafka 中使用主题（topic）对消息进行分类隔离。每个 topic 下可以设置分区（partition），每个 partition 内消息是有序的，一个 topic 的不同 partition 之间，不能保证消息顺序。生产者会将消息指派给 topic 内的某一个 partition，可以基于轮询策略，也可以根据消息中的关键字进行划分，将相同关键字的消息发送给同一个 partition，以保证消息的有序性。一个主题的逻辑结构如下[图](https://kafka.apache.org/24/documentation.html#intro_topics)，图中分区内的每个标序号的小方格，即为上文中提到的 **段**。
> ![](/contents/deep-dive-into-apache-kafka-storage-internals/topic.png)

并非每个人都知道这些参数对消息代理的行为有何影响。例如，他们会决定消息记录被保存多久以便使消费者能够消费这些消息。在这篇文章中，我们将深入探讨在日志清理策略设置为删除（`delete`）时，日志分段和记录保留策略会如何影响消息代理的性能。当您了解有关其工作原理的更多信息后，您可能会想要调整您的日志配置。

> 当使用压缩（`compact`）策略而不是删除（`delete`）策略时，日志保留的处理方式会有所不同。使用键来标识消息，Kafka 压缩时会保留特定消息键的最新消息（偏移量最高的）。具有相同键的早期消息将被丢弃。您可以在 Strimzi 的文档 [removing log data with cleanup policies](https://strimzi.io/docs/operators/latest/using.html#removing_log_data_with_cleanup_policies) 中了解有关压缩的更多信息。


磁盘上的主题分区结构
=================

Apache Kafka 中，主题（topic）会被分割成多个分区，消息记录追加至每个分区的末尾。每个分区可以定义为一个工作单元，而不是存储单元，因为客户端使用它来交换记录。分区进一步拆分为段，这些段是磁盘上的实际文件。拆分为多个段确实有助于提高性能。当磁盘上的记录需要被删除或消费者开始从特定偏移量消费消息时，未分段的大文件会更慢且更容易出错。

在消息代理节点的磁盘中，可以看到每个主题的分区，都是一个包含相应段文件和其他文件的目录。以 Strimzi Canary 组件及其生产者和消费者为例，下面是目录结构的示例。

```text
├── __strimzi_canary-0
│   ├── 00000000000000000000.index
│   ├── 00000000000000000000.log
│   ├── 00000000000000000000.timeindex
│   ├── 00000000000000000109.index
│   ├── 00000000000000000109.log
│   ├── 00000000000000000109.snapshot
│   ├── 00000000000000000109.timeindex
```

> 译注：Kafka 使用文件系统进行消息的存储及缓存，相关内容可查阅官方文档 [4.2 Persistence](https://kafka.apache.org/documentation/#persistence)。文件存储路径为：[log.dirs](https://kafka.apache.org/documentation/#brokerconfigs) + `/<topic>-<partition_idx>`

该示例显示了 Strimzi Canary 组件使用的 `__strimzi_canary` 主题的 分区0 的目录结构。该目录包含以下文件：

* `.log` 文件是实际的段文件，包含特定偏移量以内的消息记录。文件名表示日志中记录的消息的起始偏移量。
* `.index` 文件是索引文件，将消息记录的逻辑偏移量（实际上是记录的 id）映射到 `.log` 文件中记录的字节偏移量。它用于访问日志中指定偏移量的记录，而无需扫描整个 `.log` 文件。
* `.timeindex` 文件是用于按日志中的时间戳访问记录的另一个索引文件。
* `.snapshot` 文件中包含生产者状态的快照，记录了用于避免消息记录重复的序列 ID。当集群选举出一个新的 Leader 节点后，首选的 Leader 节点恢复并要再次成为 Leader 节点时，就会使用它。

继续使用上面的例子，这是之前那个主题分区目录更详细的视图。

```text
drwxrwxr-x.  2 ppatiern ppatiern      200 Nov 14 16:33 .
drwxrwxr-x. 55 ppatiern ppatiern     1220 Nov 14 16:33 ..
-rw-rw-r--.  1 ppatiern ppatiern       24 Nov 14 16:33 00000000000000000000.index
-rw-rw-r--.  1 ppatiern ppatiern    16314 Nov 14 16:33 00000000000000000000.log
-rw-rw-r--.  1 ppatiern ppatiern       48 Nov 14 16:33 00000000000000000000.timeindex
-rw-rw-r--.  1 ppatiern ppatiern 10485760 Nov 14 16:33 00000000000000000109.index
-rw-rw-r--.  1 ppatiern ppatiern      450 Nov 14 16:33 00000000000000000109.log
-rw-rw-r--.  1 ppatiern ppatiern       10 Nov 14 16:33 00000000000000000109.snapshot
-rw-rw-r--.  1 ppatiern ppatiern 10485756 Nov 14 16:33 00000000000000000109.timeindex
-rw-rw-r--.  1 ppatiern ppatiern        8 Nov 14 16:24 leader-epoch-checkpoint
```

从上面的输出内容中，可以看到第一个日志段文件 `00000000000000000000.log` 中包含偏移量从 0 到 108 的消息记录。第二段 `00000000000000000109.log` 文件包含从偏移量 109 开始的消息，这个段被称为 ***活动段（active segment）***。

活动段是唯一一个允许进行读写操作的文件。它是用来追加接收到的新消息记录的段。一个分区只有一个活动段。非活动段是只读的，由消费者访问用来读取较旧的消息记录。当活动段写满后，它会被滚动（`rolled`），这意味着文件将被关闭并以只读模式重新打开。一个新的段文件将会被创建并以读写模式打开，成为新的活动段。

从示例中，您可以看到旧段在达到 16314 字节时被关闭。这是因为 Canary 的主题配置了 `segment.bytes=16384` 参数，指定了段的最大尺寸。我们将在稍后讨论此配置。150 byes 是 Canary 组件发送的每条消息的大小。因此，每个段将包含 109 条记录。109 * 150 字节 = 16350 字节，接近段的最大容量。

![](/contents/deep-dive-into-apache-kafka-storage-internals/2021-12-17-segments.png)

还可以通过使用 Apache Kafka 发行版提供的 `DumpLogSegments` 工具从日志段中转储记录。运行以下命令将显示指定段日志中的记录。

```bash
./bin/kafka-run-class.sh kafka.tools.DumpLogSegments --deep-iteration --print-data-log --files /tmp/kafka-logs-0/__strimzi_canary-0/00000000000000000000.log 
Dumping /tmp/kafka-logs-0/__strimzi_canary-0/00000000000000000000.log
Starting offset: 0
baseOffset: 0 lastOffset: 0 count: 1 baseSequence: 0 lastSequence: 0 producerId: -1 producerEpoch: -1 partitionLeaderEpoch: 0 isTransactional: false isControl: false position: 0 CreateTime: 1639132508991 size: 148 magic: 2 compresscodec: NONE crc: 2142666254 isvalid: true
| offset: 0 CreateTime: 1639132508991 keysize: -1 valuesize: 78 sequence: 0 headerKeys: [] payload: {"producerId":"strimzi-canary-client","messageId":1,"timestamp":1639132508991}
baseOffset: 1 lastOffset: 1 count: 1 baseSequence: 0 lastSequence: 0 producerId: -1 producerEpoch: -1 partitionLeaderEpoch: 0 isTransactional: false isControl: false position: 148 CreateTime: 1639132514555 size: 148 magic: 2 compresscodec: NONE crc: 1895373344 isvalid: true
| offset: 1 CreateTime: 1639132514555 keysize: -1 valuesize: 78 sequence: 0 headerKeys: [] payload: {"producerId":"strimzi-canary-client","messageId":4,"timestamp":1639132514555}
baseOffset: 2 lastOffset: 2 count: 1 baseSequence: 0 lastSequence: 0 producerId: -1 producerEpoch: -1 partitionLeaderEpoch: 0 isTransactional: false isControl: false position: 296 CreateTime: 1639132519561 size: 148 magic: 2 compresscodec: NONE crc: 1097825866 isvalid: true
..
..
..
..
| offset: 107 CreateTime: 1639133044553 keysize: -1 valuesize: 80 sequence: 0 headerKeys: [] payload: {"producerId":"strimzi-canary-client","messageId":322,"timestamp":1639133044553}
baseOffset: 108 lastOffset: 108 count: 1 baseSequence: 0 lastSequence: 0 producerId: -1 producerEpoch: -1 partitionLeaderEpoch: 0 isTransactional: false isControl: false position: 16164 CreateTime: 1639133049552 size: 150 magic: 2 compresscodec: NONE crc: 1749984078 isvalid: true
| offset: 108 CreateTime: 1639133049552 keysize: -1 valuesize: 80 sequence: 0 headerKeys: [] payload: {"producerId":"strimzi-canary-client","messageId":325,"timestamp":1639133049552}
```

从该示例中，您可以看到从偏移量 0 到 108 的记录都存储在 `00000000000000000000.log` 段文件中。


分区中的索引是如何工作的？
=====================

如前所述，`.index` 文件包含一个索引，该索引将逻辑偏移量映射到 `.log` 文件中记录的字节偏移量。您可能希望此映射可用于每条记录，但它不是以这种方式工作的。让我们考虑 Canary 组件发送的记录，其大小约为 150 字节。在下图中，您可以看到，对于日志文件中存储的 85 条记录，相应的索引只有 3 个条目。

![](/contents/deep-dive-into-apache-kafka-storage-internals/2021-12-17-index.png)

偏移量为 28 的记录位于日志文件中字节偏移量 4169 处，偏移量为 56 的记录位于字节偏移量 8364 处，依此类推。通过使用 `DumpLogSegments` 工具，可以转储 `.index` 文件内容。

```bash
bin/kafka-run-class.sh kafka.tools.DumpLogSegments --deep-iteration --print-data-log --files /tmp/kafka-logs-0/__strimzi_canary-0/00000000000000000000.index
Dumping /tmp/kafka-logs-0/__strimzi_canary-0/00000000000000000000.index
offset: 28 position: 4169
offset: 56 position: 8364
offset: 84 position: 12564
```

这些条目是如何添加进索引文件中的，是由 `log.index.interval.bytes` 参数定义的，该参数默认值为 4096 字节。这意味着，日志文件中每添加 4096 个字节的记录，就会在相应的索引文件中添加一个条目。每个条目的大小为 8 个字节，4 个字节用于存储偏移量，4 个字节存储日志段中的字节位置。在此示例中，每新增 28 条消息记录就会添加一个新的索引条目，因为 28 * 150 = 4200。

如果一个消费者想要从指定的偏移量开始读取消息，则按如下方式搜索记录：

* 根据 `.index` 文件的文件名查找索引文件，该文件遵循与相应的 `.log` 文件相同的模式。从文件名可以获得该索引文件中索引的消息记录的起始偏移量。
* 在 `.index` 文件中搜索与请求的偏移量最接近的条目。
* 使用条目对应的字节偏移量访问 `.log` 文件，并搜索消费者需要的起始偏移量。

可以调整 `log.index.interval.bytes` 参数，使得索引文件条目增多以便更快地搜索记录，反之亦然。如果将 `log.index.interval.bytes` 设置为小于默认的 4096 字节，则索引中将有更多的条目以进行更细粒度的搜索。但是，更多的条目也会导致索引文件的大小快速增长。如果将参数设置为高于默认的 4096 字节，则索引中的条目将减少，这将减慢搜索速度。这也意味着索引文件的大小会以更慢的速度增加。

Apache Kafka 还允许您根据时间戳开始使用记录。这是 `.timeindex` 进入画面的时候。`.timeindex` 文件中的每个条目都定义一个时间戳和偏移量对，该偏移量指向相应的 `.index` 文件对应条目。

在下图中，您可以看到从 `1638100314372` 时间戳开始的消息，起始的偏移量是 28，`1638100454372` 时间戳的消息，起始的偏移量为 56，依此类推。

![](/contents/deep-dive-into-apache-kafka-storage-internals/2021-12-17-timeindex.png)

时间戳索引文件中每个条目的大小为 12 个字节，时间戳为 8 个字节，偏移量为 4 个字节。它准确地反映了 Strimzi Canary 组件如何生成记录，因为它每 5 秒发送一条记录。140 秒（28 x 5）内将发送 28 条记录，这正是时间戳之间的间隔：1638100454372 - 1638100314372 = 140000 毫秒。通过使用 `DumpLogSegments` 工具，可以转储 `.timeindex` 文件内容。

```bash
bin/kafka-run-class.sh kafka.tools.DumpLogSegments --deep-iteration --print-data-log --files /tmp/kafka-logs-0/__strimzi_canary-0/00000000000000000000.timeindex 
Dumping /tmp/kafka-logs-0/__strimzi_canary-0/00000000000000000000.timeindex
timestamp: 1638100314372 offset: 28
timestamp: 1638100454372 offset: 56
timestamp: 1638100594371 offset: 84
```


我们来谈谈滚动段（rolling segments）
================================

当满足某些特定条件时，将滚动出一个新的段文件。一个条件是当段文件大小达到设定的最大值时，由配置参数 `log.segment.bytes` 指定（默认为 1 GiB）。另一个条件是基于参数 `log.roll.ms` 或 `log.roll.hours`（默认为 7 天）。在这种条件下，当段中第一条记录的生产者时间戳（或者如果没有时间戳，则以段文件创建时间）达到或超过配置的时间间隔时，将滚动段。满足第一个条件时将触发滚动新的段文件。值得注意的是，作为一个不太常见的情况，记录中的生产者时间戳可能不是有序的，因此由于重试或生产者的特定业务逻辑，可能段中的第一条记录并不是最早产生的那条记录。

另一个有用的参数是 `log.roll.jitter.ms`，它在滚动段时设置最大抖动间隔。抖动间隔时间用于避免多个段同时产生滚动时导致的磁盘高争抢。每个段会随机生成一个最大值之内的抖动间隔。

上述条件，按段文件大小或时间，是众所周知的，但不是每个人都知道还有第三个条件。

当段文件对应的索引（或时间索引）文件写满时，也会触发段文件滚动。索引和时间索引文件使用相同的最大值，由 `log.index.size.max.bytes` 参数定义，默认值为 10 MB。让我们考虑默认日志段的最大大小，即 1 GiB。我们知道，由于 `log.index.interval.bytes` 在默认情况下为 4096 字节，因此每 4096 字节的记录就会在索引中添加一个条目。这意味着对于 1 GiB 的段文件大小，1 GiB / 4096 字节 = 262144 个条目可以被添加到索引文件中。这相当于索引文件中的 2 MB（262144 * 8 个字节）。默认索引大小 10 MB 足以处理 5 GiB 的段大小。减小索引大小或增加段大小将导致在索引文件写满时滚动新段，而不是在达到段文件设定的最大值时。因此，在不增加索引大小的情况下设置大于 5 GiB 的段大小是无用的，因为当索引已满时，消息代理将滚动新段。

将段大小增加到 5 GiB 以上时，您应该同时增加索引文件大小。同样，如果您决定减小索引文件大小，则可能也需要按比例减小段大小。

时间索引文件可能也需要引起注意。因为时间索引（timeindex）文件中的每个条目都比索引中的条目大 1.5 倍（12 个字节比 8 个字节），因此它可能更早地被写满并导致滚动新段。

为了演示索引和时间索引文件大小对滚动新日志段有何影响，让我们考虑一个使用 `log.index.interval.bytes=150` 和 `log.index.size.max.bytes=300` 参数的集群，利用 Strimzi Canary 生产和消费消息，使用通常的配置 `retention.ms=600000;segment.bytes=16384`。由于 Strimzi Canary 产生消息的大小约 150 个字节，因此我们预计每两条消息记录会在索引文件中写入一个条目。索引最大值为 300 字节，故索引文件中将有大约 300 / 8 = 37 个条目，时间索引文件中大约有 300 / 12 = 25 个条目。

通过运行 Strimzi Canary 一段时间，我们得到以下输出：

```text
-rw-rw-r--.  1 ppatiern ppatiern  192 Dec 10 16:23 00000000000000000000.index
-rw-rw-r--.  1 ppatiern ppatiern 7314 Dec 10 16:23 00000000000000000000.log
-rw-rw-r--.  1 ppatiern ppatiern  288 Dec 10 16:23 00000000000000000000.timeindex
-rw-rw-r--.  1 ppatiern ppatiern  296 Dec 10 16:23 00000000000000000049.index
-rw-rw-r--.  1 ppatiern ppatiern 4500 Dec 10 16:26 00000000000000000049.log
-rw-rw-r--.  1 ppatiern ppatiern   10 Dec 10 16:23 00000000000000000049.snapshot
-rw-rw-r--.  1 ppatiern ppatiern  300 Dec 10 16:23 00000000000000000049.timeindex
```

从该示例中可以看出，当活动段仅为 7314 byes 时，就滚动了一个新段，并未达到配置的 16384 字节。同时，索引文件的大小为 192 字节，因此实际上有 192 / 8 = 24 个条目，并不是预期的 37 个。原因是因为时间索引文件首先达到了 300 字节的限制。它是 288 字节，包含 288 / 12 = 24 个条目 —— 与索引文件中的条目数相同。

您可以在消息代理级别设置这些参数，但也可以在主题级别覆盖它们。


我的记录会保留多长时间？比您预期的要长！
================================

管理记录时，一个重要的方面是它们在被删除之前保留多长时间。这是可以根据大小和保留时间进行配置的。您可以使用 `log.retention.bytes` 参数指定要保留的最大字节数。如果要设置保留期，可以使用 `log.retention.ms`、`log.retention.minutes` 或 `log.retention.hours`（默认为 7 天）参数。与控制何时滚动段的参数一样，第一个条件被满足即会触发从磁盘中删除较旧的记录。

> 这些参数也可以在消息代理级别设置，并在主题级别被覆盖。

假设您使用 `TOPIC_CONFIG` 环境变量配置 `retention.ms=600000;segment.bytes=16384`，指定 Strimzi 的 canary 主题的保留时间为 600000 毫秒（10 分钟），段大小为 16384 字节。

使用此配置，期望是每当当前活动段的大小达到 16384 字节时，就会滚动一个新段。可能并不总是这样。如果下一条记录由于超出最大段大小而无法存储在活动段中，则会提前滚动新段。Canary 记录的大小约为 150 字节，预期每个段在关闭之前可以存储大约 16384 / 150 = 109 条记录。假设将 Canary 配置为每 5 秒生成一条记录，则在 109 * 5 = 545 秒内填满一个段。换句话说，每 9 分钟会滚动一个新段。

关于记录保留，预期记录在删除之前保留 10 分钟。但这其实并不那么简单。追加记录后，我们可能仍能读取记录的最短和最长时间是多少？

段，及其中包含的记录，只有在关闭时才能被删除。这意味着，如果生产者产生记录非常缓慢，在 10 分钟内并未达到 16384 字节的最大大小，则不会删除较旧的记录。记录保留期因此会高于其本意。

即使活动段能够被快速填充，保留时间也会从段关闭前追加的最后一条记录开始计算。最新的记录将按我们希望的 10 分钟被保留，但段中的第一条记录会保留更长时间。当然，这取决于段的填充速度以及第一条记录和最后一条记录之间的时间间隔。

在我们的 Canary 示例中，段需要 9 分钟才能被写满并关闭。当最后一条记录到达时，该段中的第一条记录已经保留 9 分钟了。在等待最后一条记录到达后被保留 10 分钟时，第一条记录“应该”在 19 分钟后被删除。

无论如何，即使我们认为在最后一条记录到达保留时间后，它可能仍然存在！原因与在消息代理上定期运行的 Apache Kafka 线程有关，这个线程负责清理记录并检查哪些已关闭的段可以被删除。您可以使用 `log.retention.check.interval.ms` 参数配置此线程的运行周期（默认为 5 分钟）。根据追加最后一条记录和关闭段的时间，定期删除的检查可能会进一步导致超过预计保留的 10 分钟时间。已关闭的段可能会在下次检查时才被删除，这将导致最多近 5 分钟的延迟。

在我们的示例中，段中的第一条记录可能会被保留长达近 24 分钟！

假设在某个时刻，清理线程开始运行，并验证了一个已关闭的段可以被删除。它会为相应的文件添加 `.delete` 扩展名，但实际上并不会从文件系统中删除该段文件。消息代理上的 `log.segment.delete.delay.ms` 参数用来指定当文件被标记为“delete”时，文件会延迟多久再真正从文件系统中被删除（缺省时间为 1 分钟）。

![](/contents/deep-dive-into-apache-kafka-storage-internals/2021-12-17-total-retention-time.png)

再次回到 Canary 的例子，并假设延迟删除，我们段中的第一条记录在 25 分钟后仍然存在！它比预期的 10 分钟长得多，不是吗？

如您所见，很明显，保留机制与最初的预期并不完全匹配。实际上，记录的寿命可能远长于我们设定的 10 分钟，具体取决于消息代理的配置和内部机制。使用 `log.retention.ms` 设置的保留时长通常只代表一种下限。Kafka 保证不会删除任何存活期小于指定期限的记录，但任何较旧的记录都可能在将来的任意时刻被删除，这取决于具体的设置。

值得一提的还有它对消费者方面的影响。消费者可以从已关闭的段中获取记录，但不会从标记为删除的段中获取记录，即使它们仅是被标记为“已删除”实际上并未从文件系统中删除。即使消费者从头开始读取分区，也是如此。更长的保留期不会对消费者产生直接的影响，但会对磁盘使用量产生更大的影响。


结论
===

了解消息代理如何在磁盘上存储分区和相应的记录非常重要。配置参数可能会对数据的保留时间产生惊人的巨大影响。了解这些参数以及如何调整它们，可以让您在如何处理数据上有更强的控制力。