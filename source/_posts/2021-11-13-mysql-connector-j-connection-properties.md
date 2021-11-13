---
id: mysql-connector-j-reference-configuration-properties
title: "是时候升级 MySQL Connector/J 到 8.0 了"
description: "MySQL JDBC url 可用参数概览"
date: 2021.11.14 10:26
categories:
    - Database
tags: [MySQL]
keywords: Connector/J, MySQL, jdbcUrl, JDBC, properties
cover: /contents/mysql-connector-j-reference-configuration-properties/cover.png
---

使用 JDBC 连接 MySQL 时，你是否也对 JDBC URL 连接串中的参数感到很神秘？

例如：

```text
jdbc:mysql://localhost:3306/hinex?useSSL=false&serverTimezone=UTC
```

连接串的通用格式为：

```text
protocol//[hosts][/database][?properties]
```

那么可用的 `properties` 都有哪些？默认值和可用的值都有什么，又都是什么含义呢？

这就要从 `Connector/J` 说起了。


Connector/J
-----------

[Connector/J][cj] 是 Java 连接 MySQL 的连接器，或称驱动。
与 MySQL 现在有两个活跃版本（`5.7.x` 和 `8.0.x`）一样，`Connector/J` 目前也有两个主要版本：`5.1` 和 `8.0`。
但并不是只能用 `5.1` 版本的驱动连 `5.7.x` 版本的 MySQL，或 `8.0` 版本的驱动连接 `8.0.x` 版本的 MySQL，让我们先来看一下两个版本驱动的 [对比][versions]：

![versions](/contents/mysql-connector-j-reference-configuration-properties/versions.png)

可以看到，官方强烈推荐使用或升级到 `8.0` 的版本，并且 `5.1` 系列版本已到达生命周期的尾声，一年多没有更新过了（最新版本 `5.1.49` 是 [2020年4月][tag] 发布的）。


[What's New in Connector/J 8.0][new]
------------------------------------

几个主要的改进：

1. 需要 Java 8 或以上版本
1. 支持 JDBC 4.2 规范
1. 连接串中的 properties 有新增、更名及移除
1. 主要代码进行了重构及修整，以提供更好的性能
1. 包结构发生了整体调整（`com.mysql.cj.jdbc`）
1. 异常更新，以匹配 JDBC 标准


Properties
----------

下面选择部分实用的属性进行说明。

### 普通属性

|Name|Default Value|Since|Description|
|:---|:------------|:----|:----------|
|connectionAttributes|-|5.1.25|用户定义的 `key:value` 对，可多个，逗号间隔，保存在 `P_S.SESSION_CONNECT_ATTRS` 里|
|createDatabaseIfNotExist|false|3.1.9|连接串中的数据库不存在时，报错（`false`）还是自动创建（`true`）|

### 用户自定义拦截器

|Name|Default Value|Since|Description|
|:---|:------------|:----|:----------|
|connectionLifecycleInterceptors|-|5.1.4|可监控或相应连接创建、销毁、提交、回滚等操作|
|queryInterceptors|-|8.0.7|提供查询执行前后的拦截能力|
|exceptionInterceptors|-|5.1.8|拦截异常并提供注入用户行为的能力|

### 网络调整

|Name|Default Value|Since|Description|
|:---|:------------|:----|:----------|
|connectTimeout/socketTimeout|0|3.0.1|客户端连接超时时间|
|useCompression|false|3.0.17|与服务端通信时是否启用压缩|

### Statement 相关

|Name|Default Value|Since|Description|
|:---|:------------|:----|:----------|
|allowMultiQueries|false|3.1.1|是否启用在一个 statement 里执行多个查询；可能会返回多个 `ResultSet`；不会影响批量 statemnt|
|defaultFetchSize|0|3.1.9|驱动会使用这个默认值在所有新创建的 `Statement` 时调用 `setFetchSize(n)`|

### Result Set 相关

|Name|Default Value|Since|Description|
|:---|:------------|:----|:----------|
|maxRows|-1|all versions|执行 statements 返回的最大行数|
|padCharsWithSpace|false|5.0.6|是否为 `CHAR` 类型的列填充空格至其定义的长度|

### 日期时间处理

|Name|Default Value|Since|Description|
|:---|:------------|:----|:----------|
|connectionTimeZone|-|3.0.2|指明服务端在处理日期时间转换时所使用的时区，即 8.0 之前版本的 `serverTimeZone` 参数，后者目前也可使用，但后续会被弃用|
|zeroDateTimeBehavior|EXCEPTION|3.1.4|定义当 MySQL 返回全是 0 的日期时间值时的行为：`EXCEPTION`、`ROUND` 或 `CONVERT_TO_NULL`|

### 性能调整

|Name|Default Value|Since|Description|
|:---|:------------|:----|:----------|
|rewriteBatchedStatements|false|3.1.13|是否重写批量插入或使用批量查询来减少发送的语句数量|
|useCursorFetch|false|5.0.0|与 `Statement.setFetchSize()` 一同，告诉服务端使用游标方式进行数据的读取|


Reference
---------

完整的 Properties 参考文档可见：

* [8.0][ref8]
* [5.1][ref5]

**强烈建议修改每个参数的默认值之前，仔细阅读官方文档中对此参数的描述！**

参考资料
-------

https://www.slideshare.net/FilipeSilva170/mysql-connectorj-feature-review-and-how-to-upgrade-from-connectorj-51


[cj]:https://dev.mysql.com/doc/index-connectors.html
[versions]:https://dev.mysql.com/doc/connector-j/5.1/en/connector-j-versions.html
[tag]:https://github.com/mysql/mysql-connector-j/releases/tag/5.1.49
[new]:https://dev.mysql.com/doc/connector-j/8.0/en/connector-j-whats-new.html
[ref8]:https://dev.mysql.com/doc/connector-j/8.0/en/connector-j-reference-configuration-properties.html
[ref5]:https://dev.mysql.com/doc/connector-j/5.1/en/connector-j-reference-configuration-properties.html