---
id: how-to-integrate-seata-at-mode-with-spring-cloud
title: "How to integrate SEATA AT mode with Spring Cloud"
description: "本文基于一个 Spring Cloud 业务实例，说明如何集成 SEATA AT 模式，进行分布式事务控制"
date: 2020.01.23
categories:
    - Java
    - Microservice
    - Distributed Transaction
tags: [SEATA, Spring Cloud, Nacos, OpenFeign, Docker, Gradle]
keywords: Distributed Transaction, SEATA, AT Mode, Spring Cloud, Spring Cloud Alibaba
cover: /contents/distributed-transaction/seata-at.png
---

本文基于一个 Spring Cloud 业务实例，说明如何集成 SEATA AT 模式，进行分布式事务控制。


背景介绍
-------

### SEATA 是什么？

Seata: Simple Extensible Autonomous Transaction Architecture

> Seata 是一款开源的分布式事务解决方案，致力于提供高性能和简单易用的分布式事务服务。Seata 将为用户提供了 AT、TCC、SAGA 和 XA 事务模式，为用户打造一站式的分布式解决方案。 —— 引用自 SEATA [官方文档](https://seata.io/zh-cn/docs/overview/what-is-seata.html)

### AT 模式是什么？

[TXC分布式事务简介](https://blog.csdn.net/m0_38110132/article/details/77043580) 中提到，AT 模式意为 Automatic Taobao Transaction Constructor，但在 SEATA 的官方文档中，并没有关于 AT 名称具体的解释。个人认为 AT 模式可以归类为柔性事务中的二阶段提交方式实现，一阶段先将本地事务进行提交，二阶段如果需要回滚，会根据一阶段生成的 undo log 自动进行回滚，所以可以认为 AT 模式是自动完成回滚的二阶段提交分布式事务处理模型，这也应该是 AT 模式名称的由来。

### 为什么要使用 SEATA AT 模式？

由上述内容可以看到，AT 模式的优缺点非常明显：
* 优点：侵入性小，可以用较小代价获得基本的分布式事务控制
* 缺点：一阶段会直接提交，不保证读隔离性

> 如果应用在特定场景下，必需要求全局的 **读已提交** ，目前 Seata 的方式是通过 SELECT FOR UPDATE 语句的代理。

为了付出二成努力获得八成效果，AT 模式的优点具有很强吸引力。


基础环境
-------

假设当前有这样一个基础微服务环境：

* 基于 [Spring Cloud](https://spring.io/projects/spring-cloud) 构建，使用 [Nacos](https://nacos.io) 作为注册中心，利用 [OpenFeign](https://github.com/OpenFeign/feign) 进行服务间 RESTFul API 的调用。

包含以下服务：

1. 库存服务（storage）
1. 用户账户服务（account）
1. 订单服务（order）
1. 业务服务（business）

业务服务作为直接被调用的接口，组织关联其他三个服务。下订单时，服务的调用顺序如下：

```
1. 减库存（storage）
2. 创建订单
2.1. 扣减用户账户（account）
2.2. 生成订单（order）
```

### 实例

[这里](https://github.com/AlphaHinex/seata-at-demo/tree/master) 构建了一个包含上述环境的可运行实例，可导入 IDEA 中或使用提供的 docker-compose 查看效果。

> 注意：该实例运行需要用到发布到 GitHub Packages Registry 的 jar 包，可参考 [GitHub Packages in Action](https://alphahinex.github.io/2020/01/17/github-packages-in-action/) 进行配置。

可以在发送第二个 POST 请求得到异常之后查看数据库的数据变化情况，也可以通过集成测试来验证在没有分布式事务控制的情况下，发生异常时三个服务的数据状态出现了不一致。


集成 SEATA AT 模式
-----------------

集成所需所有改动可见 https://github.com/AlphaHinex/seata-at-demo/compare/master...seata-at

### 添加 SEATA 依赖

```gradle
implementation 'com.alibaba.cloud:spring-cloud-starter-alibaba-seata:2.1.1.RELEASE'
implementation 'io.seata:seata-all:1.0.0'
implementation 'io.seata:seata-spring-boot-starter:1.0.0'
```

#### 为什么需要三个 SEATA 的依赖？每个依赖的作用是什么？

1. spring-cloud-starter-alibaba-seata

    对 Feign Client 和全局事务 XID 进行了自动配置。

    需要注意的是 Spring Cloud Alibaba 的毕业版本的 GroupId 是 `com.alibaba.cloud`。`spring-cloud-starter-alibaba-seata` 这个依赖中只依赖了 `spring-cloud-alibaba-seata`，所以在项目中添加 `spring-cloud-starter-alibaba-seata` 和 `spring-cloud-alibaba-seata` 是一样的。

1. seata-all

    `spring-cloud-starter-alibaba-seata` 装配的 SEATA 版本为 0.9.0，若需使用其他版本，需额外进行依赖。本例中使用的 SEATA 版本为 1.0.0，故需单独配置 `io.seata:seata-all:1.0.0` 依赖。

1. seata-spring-boot-starter

  包括自动代理数据源，及支持 yml 配置。

  此处需注意，虽说引入此 jar 包后可以通过 yml 的方式对 registry.conf 及 file.conf 中内容进行配置，但目前仍存在一些问题导致无法全部替代 conf 配置文件。例如：

  用 yml 配置与 registry.conf 相同的内容，会报 `no available service 'null' found, please make sure registry config correct`

  服务启动后，持续报如下警告：`io.seata.config.FileConfiguration        : Could not found property service.disableGlobalTransaction, try to use default value instead.`

  类似问题在 https://github.com/seata/seata/issues/2114 中也有讨论。目前的解决方案为：还是通过 registry.conf 和 file.conf 来存放 yml 中配置无效的内容，

  另外，在同时引入 `spring-cloud-starter-alibaba-seata` 及 `seata-spring-boot-starter` 依赖时，需要排除掉 `spring-cloud-alibaba-seata` 里的 `GlobalTransactionAutoConfiguration`，否则会报错，详见 https://github.com/seata/seata/issues/2076 。

### 在各服务数据库中增加 undo_log 表

建表语句可从 SEATA 发布版中获得，如 https://github.com/seata/seata/blob/v1.0.0/script/client/at/db/mysql.sql 。

示例中为简化过程，所有服务共用一个数据库，并通过 mysql 启动初始化过程，在库中创建了 undo_log 表。

### 各服务中配置 SEATA 服务端地址

因引入了 `seata-spring-boot-starter`，可使用 yml 进行配置，如：

```yml
seata:
  service:
    grouplist: seata-server:8091
```

### 添加全局事务注解

终于把准备工作都完成了，使用 SEATA AT 模式最核心的一步：在 controller 或者 service 上，标记 `@GlobalTransactional` 注解。That's all。

没错，这就结束了。


验证
---

可通过集成测试对分布式事务的效果进行验证。如 [seata-at-demo](https://github.com/AlphaHinex/seata-at-demo) 中 README 所示，使用 seata-at 分支代码，在所有服务均正常启动完毕之后，可通过提供的 curl 或编写好的集成测试对效果进行验证。

集成测试结果通过，即表示分布式事务生效，在调用过程中出现异常时，之前执行过的服务对数据进行的变更会自动回滚。

使用 curl 进行验证时，需自己检查数据库中数据变化情况。
