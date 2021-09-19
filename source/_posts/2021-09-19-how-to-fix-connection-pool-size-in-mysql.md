---
id: how-to-fix-connection-pool-size-in-mysql
title: "连接池如何固定住 MySQL 的连接数"
description: "最大化 Ingress 价值"
date: 2021.09.19 10:34
categories:
    - Database
tags: [Database, Connection Pools]
keywords: fixed size, connection pool, HikariCP, druid, MySQL, wait_timeout, KeepAlive
cover: /contents/how-to-fix-connection-pool-size-in-mysql/cover.png
---

连接池
=====

为什么要用连接池
-------------

相比于 SQL 执行的时间（不考虑慢 SQL），创建数据库连接的操作可谓相当昂贵，频繁的打开和关闭数据库连接，会导致系统性能非常低下。连接池可以缓存已经创建的连接，在需要连接时，从连接池中获取一个空闲连接，在使用过后将连接归还连接池。

关于连接池的大小应该如何设置，可以参考 [关于数据库连接池，你可能做错了](https://alphahinex.github.io/2021/09/12/about-connection-pool-sizing/)。

使用连接池时期望的行为
------------------

* **配置固定数目连接池后，数据库中连接数目能保持不变**
* **数据库重启后，连接池能帮助应用自动重新创建好连接**


MySQL
=====

wait_timeout
------------

MySQL 的 [wait_timeout](https://dev.mysql.com/doc/refman/5.7/en/server-system-variables.html#sysvar_wait_timeout) 变量用来控制 MySQL 主动关闭空闲连接的时间，单位秒，默认 8 小时。

为了实验方便，将此值改为 35 秒，可通过启动参数或配置文件进行指定，或使用此 [docker-compose.yml](https://github.com/AlphaHinex/connection-pool-with-mysql/blob/master/mysql/docker-compose.yml) 文件启动 MySQL。

```bash
$ docker-compose up -d mysql
```

此时创建的数据库连接，在空闲超过 35 秒时会被 MySQL 主动关闭：

![wait_timeout](/contents/how-to-fix-connection-pool-size-in-mysql/wait-timeout.png)


在这种情况下，当前主流的 Java 连接池如何保证连接池数量固定
===========================================

HikariCP
--------

使用 HikariCP 的默认配置，如在 [HikariCP Demo](https://github.com/AlphaHinex/connection-pool-with-mysql/tree/master/pools/hikari) 中执行 `./gradlew bootRun`，观察连接数变化情况：

![HikariCP default configuration](/contents/how-to-fix-connection-pool-size-in-mysql/hikari-default.png)

可以看到，虽然 HikariCP [默认的配置](https://github.com/brettwooldridge/HikariCP#frequently-used) 是 `minimumIdle` = `maximumPoolSize` = `10`，但在超过 `wait_timeout` 设置的时间后，数据库连接被关闭了，并且连接池没有再将 `minimumIdle` 数目的连接建立起来。

这时数据库如果发生了重启，连接池也同样不会主动建立连接。

> 在 MySQL Connector/J 中，有一个 [autoReconnect](https://dev.mysql.com/doc/connector-j/8.0/en/connector-j-connp-props-high-availability-and-clustering.html) 属性，可以加到 jdbc 连接串上，但这个属性并不会改变上述的情况，并且官方也并不建议启用这个属性。

**结论1：HikariCP 在默认配置下，两个期望行为均不能保证。**

HikariCP 提供了一个 `keepaliveTime` 参数，来主动尝试保持连接可用：

> ⏳keepaliveTime
>
> This property controls how frequently HikariCP will attempt to keep a connection alive, in order to prevent it from being timed out by the database or network infrastructure. This value must be less than the maxLifetime value. A "keepalive" will only occur on an idle connection. When the time arrives for a "keepalive" against a given connection, that connection will be removed from the pool, "pinged", and then returned to the pool. The 'ping' is one of either: invocation of the JDBC4 isValid() method, or execution of the connectionTestQuery. Typically, the duration out-of-the-pool should be measured in single digit milliseconds or even sub-millisecond, and therefore should have little or no noticible performance impact. The minimum allowed value is 30000ms (30 seconds), but a value in the range of minutes is most desirable. Default: 0 (disabled)

让我们加上这个参数：

```diff
$ diff src/main/resources/application.properties src/main/resources/application-keepalive.properties
4c4,6
< spring.datasource.driverClassName=com.mysql.cj.jdbc.Driver
\ No newline at end of file
---
> spring.datasource.driverClassName=com.mysql.cj.jdbc.Driver
>
> spring.datasource.hikari.keepalive-time=30000
\ No newline at end of file
```

启动应用：

```bash
$ ./gradlew bootRun -Pprofile=keepalive
```

再观察一下效果：

![HikariCP keepalive](/contents/how-to-fix-connection-pool-size-in-mysql/hikari-keepalive.png)

MySQL 重启之后：

![HikariCP after restart](/contents/how-to-fix-connection-pool-size-in-mysql/hikari-after-restart.png)

**结论2：HikariCP 在启用 `keepaliveTime` 配置后，两个期望行为均能完美保证。**

> 注意：根据 HikariCP 文档描述，`keepaliveTime` 默认不启用，允许设置的最小值是 30 秒，但建议设置到分钟级别，另外还需综合考虑数据库超时、重启或网络问题导致的连接中断，也不宜设置到小时级别。

Druid
-----

类似的，我们可以通过 [Druid Demo](https://github.com/AlphaHinex/connection-pool-with-mysql/tree/master/pools/druid) 来观察 Druid 连接池的行为。

先以默认配置启动应用：

```bash
$ ./gradlew bootRun
```

在默认配置中，同样使用了固定尺寸（`initial-size` = `max-active` = `min-idle` = `10`）的连接池：

![Druid default configuration](/contents/how-to-fix-connection-pool-size-in-mysql/druid-default.png)

重启 MySQL 同样不会主动创建连接。

**结论1：Druid 在默认配置下，两个期望行为均不能保证。**

在 Druid 的 [DruidDataSource配置属性列表](https://github.com/alibaba/druid/wiki/DruidDataSource%E9%85%8D%E7%BD%AE%E5%B1%9E%E6%80%A7%E5%88%97%E8%A1%A8) 中，我们同样找到了 `keepAlive` 属性，默认也是未开启的：

|配置|缺省值|说明|
|:--|:----|:--|
|keepAlive|false（1.0.28）|连接池中的minIdle数量以内的连接，空闲时间超过minEvictableIdleTimeMillis，则会执行keepAlive操作。|

然而按照文档中描述的与 `keepAlive` 属性相关的值进行设置：

```properties
spring.datasource.druid.min-idle=10
spring.datasource.druid.keep-alive=true
spring.datasource.druid.min-evictableIdle-time-millis=30000
```

依然无法保持数据库中固定的连接数。

在 Druid 的最新发布版 [1.2.6](https://github.com/alibaba/druid/releases/tag/1.2.6) 中，提到：

> 修复连接池在MySQL服务器主动连接断开时keepAlive机制失效的问题 #4227

不过按照上述配置依然无效。

经过反复测试，keepalive 机制的生效，除将 `keepAlive` 设置为 `true` 外，还需添加一个文档中并未描述的隐藏属性 `keepAliveBetweenTimeMillis`（最小值为 `30000`）。另外为了匹配 `wait_timeout`，将 `timeBetweenEvictionRunsMillis` 的值从默认一分钟调小：

```properties
spring.datasource.druid.keep-alive=true
spring.datasource.druid.keep-alive-between-time-millis=30000
spring.datasource.druid.time-between-eviction-runs-millis=15000
```

观察此配置下连接数情况：

```bash
$ ./gradlew bootRun -Pprofile=keepalive
```

![Druid keepalive](/contents/how-to-fix-connection-pool-size-in-mysql/druid-keepalive.png)

相比 HikariCP，keepAlive 相关属性的定义略显混乱，理解和配置起来难度也更大。

虽然能维持住连接了，但对比 HikariCP 的直线，Druid 的连接数显得有些波动。当遇到 MySQL 重启时，波动更为明显：

![Druid after restart](/contents/how-to-fix-connection-pool-size-in-mysql/druid-after-restart.png)

**结论2：Druid 在启用 keepAlive 相关配置后，能够主动维持连接数，但在遇到 MySQL 重启等中断情况时，连接数的保持不是很稳定，需要根据实际环境的配置进行具体调整，才能达到理想的状态。**