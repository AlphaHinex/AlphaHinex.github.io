---
id: flyway-in-action
title: "Flyway 实战"
description: "Everything as code"
date: 2021.08.08 10:26
categories:
    - Java
tags: [Spring Boot, Database]
keywords: Database migration, Flyway, Liquibase, Spring Boot, Gradle 
cover: /contents/flyway-in-action/cover.png
---

[Using Liquibase with Gradle in Spring Project](https://alphahinex.github.io/2018/05/15/liquibase-with-gradle/) 中，介绍了数据库版本控制工具 Liquibase，并且总结到

> 面向 SQL，选择 Flyway
> 
> 不面向 SQL，选择 Liquibase

如果你还在单独分发数据库变动脚本，甚至简单粗暴的将开发库直接导出并导入生产环境，建议一起来了解一下 Flyway 的用法。


## Flyway 中的常用概念

Flyway 中的概念可查阅 [官方文档](https://flywaydb.org/documentation/concepts/migrations)，这里挑选一些重要的进行简单介绍。

### Schema History Table

Flyway 对数据库进行版本控制的方式，是在指定数据库中创建一张表，即 Schema History Table（默认为 `flyway_schema_history`），记录由 Flyway 所执行的 sql 脚本状态。

### Migration

在 Flyway 中，所有对数据库的变动，均称为 migration，migration 可以是 SQL 文件，也可以是 Java 类。

默认的查找 migration 的路径为 `classpath:db/migration`，对应 SQL 文件可放置在 `src/main/resources/db/migration` 下，Java 类可放置在 `src/main/java/db/migration` 下。

Migration 可以是仅执行一次的（versioned），也可是重复执行的（repeatable）。

### Versioned Migration

Versioned migration 包括版本号、描述和校验值（checksum，自动计算），命名方式如下：

![Versioned Migration](/contents/flyway-in-action/versioned.png)

其中版本号必须全局（一个 Schema History Table 里）唯一，且默认情况下（可通过参数调整）版本号只能增加，不能在已经执行了高版本的 migration 之后再执行低版本的 migration。

版本号可以是数字加 `.` 的形式，例如下列都是合法的版本号：

```text
1
001
5.2
1.2.3.4.5.6.7.8.9
205.68
20130115113556
2013.1.15.11.35.56
2013.01.15.11.35.56
```

`checksum` 用来检查 migration 在执行过后是否发生了变化，如果发生了变化，会导致这个版本以及后续版本的 migration 无法执行。

### Undo Migration

Versioned migration 中，还有一种特殊的类型 undo migration，可为对应版本的常规 versioned migration 进行回退操作，命名方式如下：

![Undo Migration](/contents/flyway-in-action/undo.png)

> 此功能为收费功能，在社区版 Flyway 中无法使用。

### Repeatable Migration

Repeatable migration 包括描述和校验值，没有版本号信息，会在每次校验值（migration 内容变化会导致校验值变化）发生变化时重复执行，命名方式如下：

![Repeatable Migration](/contents/flyway-in-action/repeatable.png)

Repeatable migration 会在所有的 versioned migration 都执行过后再进行执行，Repeatable migration 内部按照其文件名中描述（description）部分的顺序执行。

在 repeatable migration 中需保证其中内容可重复执行，比如在 DDL 中使用 `CREATE OR REPLACE`。

### Baseline

当数据中已经存在内容时，再引入 Flyway，可通过 Baseline 设定一条基线。

![Baseline](/contents/flyway-in-action/baseline.png)

如果想将基线之前的数据库中表结构和数据纳入 Flyway 一同管理，可以将基线前的状态导出成数据库脚本，通过 versioned migration 添加至 flyway 中，并设定 baselin version，Flyway 会忽略基线版本号（包括）之前版本的所有 migration。

如果不想管理基线之前的数据库状态（比如多模块或应用操作同一数据库，互相之间不受影响），可以只告诉 Flyway 执行 migration 的时候是存在基线的，这样就不会报出数据库非空的异常。


## 如何在一个 Spring Boot 项目中引入 Flyway

在 Spring Boot 项目中，引入 Flyway 非常简单，因为在 Spring Boot 的 [spring-boot-autoconfigure](https://github.com/spring-projects/spring-boot/tree/v2.5.3/spring-boot-project/spring-boot-autoconfigure/src/main/java/org/springframework/boot/autoconfigure/flyway) 中包含了 Flyway 的自动配置，只要添加 flyway 的依赖即可。

### 演示工程

以在 [spring initializr](https://start.spring.io/) 中新建一个演示工程为例，添加 `Spring Web`、`Spring Data JPA` 和 `MySQL Driver` 依赖：

![spring initializr](/contents/flyway-in-action/spring-initializr.png)

设定数据库连接相关参数 `spring.datasource.url`、`spring.datasource.username` 和 `spring.datasource.password`，即可完成演示工程的准备。

### 引入 Flyway

#### 添加依赖

Gradle 可以通过 `implementation 'org.flywaydb:flyway-core'` 添加 Flyway 依赖。

Maven 可加入：

```xml
<dependency>
    <groupId>org.flywaydb</groupId>
    <artifactId>flyway-core</artifactId>
</dependency>
```

版本号推荐使用 Spring Boot 依赖管理中定义好的版本（即无需额外指定）。

添加 Flyway 依赖后，无需其他配置，Flyway 的功能是自动启用的，如果想停用 Flyway，需设置 `spring.flyway.enabled=false`。

#### 添加 sql 脚本

引入 Flyway 之后，再启动应用时，会在默认路径 `classpath:db/migration` 查找 sql 脚本，如果没找到会报错，影响应用启动。

可在 `src/main/resources/db/migration` 路径下创建 sql 文件，如 `src/main/resources/db/migration/V20210808__test.sql`，使应用可正常启动。

启动成功后，可在所指定的数据库中的 `flyway_schema_history` 表中查看初始化脚本执行状态。

可通过 `spring.flyway.table=another_table` 修改默认表名。

> 修改默认表名，可实现多个模块分别通过 Flyway 进行数据库版本控制，并连接到相同数据库的效果。

#### 非空数据库处理

当在一个已有项目中引入 Flyway 时，数据库中可能已经存在了一些表和初始化数据，此时按照上述方式引入 Flyway 时会提示如下异常：

```text
org.springframework.beans.factory.BeanCreationException: Error creating bean with name 'flywayInitializer' defined in class path resource [org/springframework/boot/autoconfigure/flyway/FlywayAutoConfiguration$FlywayConfiguration.class]: Invocation of init method failed; nested exception is org.flywaydb.core.api.FlywayException: Found non-empty schema(s) `demo` but no schema history table. Use baseline() or set baselineOnMigrate to true to initialize the schema history table.
```

此时需要设定 `spring.flyway.baseline-on-migrate=true` 参数，告诉 Flyway 在执行 sql 脚本之前，数据库是非空状态。

如果想指定 baseline version，可通过设定 `spring.flyway.baseline-version=20210809` 参数，以忽略 `20210809` 版本以及之前的所有 migration。


## 其他问题

### 执行方式

Flyway 的 migration 会在 Spring Boot 应用启动时自动执行，如果不想通过启动应用的方式执行，官方提供了命令行、API、以及 Maven 和 Gradle 插件的方式，但总的来说都会麻烦一些，因为需要将已经在 Spring Boot 中配置的参数，再到其他执行方式所各自要求的位置重新配置一遍，实用性一般。

### 生产环境数据安全性

Flyway 的 Clean 命令，会将 Flyway 所连接的数据库中的所有内容全部清理掉，不论其中的表或数据是否是通过 Flyway 添加进去的。

在生产环境中使用 Flyway 确实也存在一定的风险，但这个风险不是 Flyway 本身造成的，有权连接生产库的人的任何一个误操作，都会导致生产环境数据的丢失，建议不要因噎废食。

Flyway 对此也提供了一定的防范措施，可通过禁用 Clean 命令来防止此问题发生，比如通过 Spring Boot 的 `spring.flyway.clean-disabled=true` 参数，或通过 Gradle 插件的配置：

```build.gradle
flyway {
	...
	cleanDisabled = true
    ...
}
```

每种执行 Flyway 命令的方式均可设置此参数，建议在所有环境都禁用 Clean 命令。

### SQL 报错

通过 Spring Boot 自动执行 migration 时要注意，一旦 migration 执行失败，应用启动会终止。出现 migration 执行失败时，需要将 Schema History Table 表中的失败记录处理掉，才能再次执行 migration，否则应用会一直无法启动。

### out-of-order

多人开发时，可能会出现 A 写了 V1 脚本，B 写了 V2 脚本，B 的代码先合并进去了，V2 脚本先执行了，此时 A 的 V1 脚本受版本号只能增加的要求不能再执行。

这种情况可以通过将 `spring.flyway.out-of-order` 设置为 `true` 来暂时取消这个限制，不过还是强烈建议 A 将 V1 脚本版本号改为 V3。