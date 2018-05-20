---
layout: post
title:  "Using Liquibase with Gradle in Spring Project"
description: "Spring 项目通过 Gradle 插件使用 Liquibase 的简易说明"
headline: "Hex"
date:   2018.05.15 15:40:47
categories: Java
tags: [Liquibase, Spring, Gradle]
comments: true
---


Liquibase 是什么
---------------

引用 [Liquibase 官网](http://www.liquibase.org/index.html) 的一张图片：

![Source Control for Your Database](http://www.liquibase.org/custom_images/home_tagline.png)

类似的工具还有 [Flyway](https://flywaydb.org/)。


为什么选择 Liquibase
------------------

[Flyway 官网](https://flywaydb.org/) 上有一个同类工具特性的对比，详见 `Feature Comparison` 部分或下图：

![Feature Comparison](/archives/liquibase-with-gradle/Feature-Comparison.png)

看图的话，Flyway 完胜，不过 **等等！看完下面内容再做决定**：

* [Liquibase vs Flyway which one to use?](https://stackoverflow.com/questions/37385823/liquibase-vs-flyway-which-one-to-use)
* [Tool-based Database Refactoring: Flyway vs. Liquibase](https://reflectoring.io/database-refactoring-flyway-vs-liquibase/)
* [Java世界最棒的DB Migration Tool](http://ju.outofmemory.cn/entry/85903)

一句话总结一下：

```
面向 SQL，选择 Flyway
不面向 SQL，选择 Liquibase
```

How to use?
-----------

Liquibase 的使用方式可参考官方提供的 [Quick Start](http://www.liquibase.org/quickstart.html) 文档，这里主要讲一下 **Liquibase 和 Spring 集成使用的方式**。

### 版本

先统一一下本文中使用的各类组件的版本：

* [liquibase v3.6.1](https://github.com/liquibase/liquibase/tree/liquibase-parent-3.6.1)
* [liquibase-gradle-plugin v1.2.4](https://github.com/liquibase/liquibase-gradle-plugin/tree/acf7a693563471f83fd26b9e15365ab98011d804)
* [Gradle v4.6](https://github.com/gradle/gradle/tree/v4.6.0)
* [H2 v1.3.176](https://github.com/h2database/h2database/tree/version-1.3/version-1.3.176/h2)

### 入口 bean

```
<bean id="liquibase" class="liquibase.integration.spring.SpringLiquibase" lazy-init="false">
    <property name="dataSource" ref="dataSource"/>
    <property name="changeLog" value="classpath*:liquibase/changelog.xml"/>
    <property name="contexts" value="${database.liquibase.profile}"/>
</bean>
```

需要注意几点：

1. 数据库的变更最好在应用启动时进行，所以需要给入口 bean 配置上 `lazy-init="false"`
1. Spring 提供的 [profiles](http://propersoft-cn.github.io/pep-refs/projects/spring-framework/4.3.0/index.html#beans-definition-profiles) 机制可以对应到 Liquibase 的 [Contexts](http://www.liquibase.org/documentation/contexts.html) 上，以便在不同的 profile 执行不同的数据库操作
1. 大型项目一般都会分模块，模块最终可能会以 jar 包方式被引用。入口 changelog.xml 可能也是存在于 jar 包中的。故 `changeLog` 属性的 `value` 配置为 `classpath*:liquibase/changelog.xml`。**想法很不错，但这里会遇到一个问题：`CORE-3139`**

#### CORE-3139

[CORE-3139](https://liquibase.jira.com/browse/CORE-3139) 是 Liquibase 无法从 JAR 包中读取资源文件的一个 bug。这个 bug 已有 [PR #725](https://github.com/liquibase/liquibase/pull/725) 进行了处理，CORE-3139 中也标记这个问题已在 Liquibase `v3.5.4` 版本中修复，但事实证明在 [Liquibase v3.6.1](https://github.com/liquibase/liquibase/tree/liquibase-parent-3.6.1) 版本中仍然存在，且之前修复这个问题的代码也基本都被覆盖掉了 orz。

这个问题只会影响到从 JAR 包中读取资源文件的情况（比如 changelog.xml 在 JAR 包中），资源直接存在于文件系统时并不受此问题影响。

为了避免这个问题再反复出现，新提交了一个 [PR #767](https://github.com/liquibase/liquibase/pull/767) 对问题进行了修正，并补充了单元测试。如需将 changelog 打入 JAR 包中，可使用合并了此 PR 的版本的 Liquibase。

### Change Log 的组织

项目模块化后，Change Log 也需要分布到各个模块中，与官方 [最佳实践](http://www.liquibase.org/bestpractices.html) 给出的结构不同，项目中的结构可能更类似下面的情况：

```
├── a
│   └── src
│       └── main
│           └── resources
│               └── liquibase
│                   └── changelog.xml
├── b
│   └── src
│       └── main
│           └── resources
│               └── liquibase
│                   └── changelogs
│                       ├── changelog-ddl-b.xml
│                       └── changelog-dml-b.xml
└── c
    └── src
        └── main
            └── resources
                └── liquibase
                    └── changelogs
                        └── changelog-dml-c.xml
```

除 `a` 模块作为 changelog 入口模块外，`b`、`c` 模块可能都是被以 JAR 包方式选择性引入的，即 `a` 模块的 changelog.xml 不应该感知到 `b`、`c` 模块内的 `changelog-*.xml`；同时当引入 `b`、`c` 模块时又能将模块下的 `changelog-*.xml` 都正常加载到。

实现这个需求需借助 Liquibase 提供的 [includeAll](http://www.liquibase.org/documentation/includeall.html)，同时要注意下其中的 `Warnings`：

```
If you do choose to use the includeAll tag, make sure you have a naming strategy in place that will insure that you will never have conflicts or need to rename files to change to force a reordering.
```

可参考如下方式组织 changelogs：

* 入口 changelog 为 `liquibase/changelog.xml`
* 为避免入口 changelog include 到自己，各模块的 changelog 存放路径要与入口 changelog 路径有区别，如放在 `liquibase/changelogs/` 路径下
* 将 DDL 和 DML 分开放置，且按 `changelog-[ddl/dml]-{module}.xml` 方式命名，因为 Liquibase 是将所有 changelog 文件按字典序方式执行，这样可以保证 DDL 会优先 DML 执行，且不会因路径相同导致 changelog 文件被覆盖

> 注：即使在不同 JAR 包下，相对路径相同的 changelog 文件也会被覆盖

> 如需从 JAR 包中读取 changelog，你可能需要 [PR #767](https://github.com/liquibase/liquibase/pull/767)。

#### 入口 Change Log

```
<?xml version="1.0" encoding="UTF-8"?>

<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
         http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-3.6.xsd">
    <includeAll path="classpath*:liquibase/changelogs/" context="dev, production"/>
</databaseChangeLog>
```

#### Change Log Template

```
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<databaseChangeLog xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                   xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
                                       http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-3.6.xsd">
    <changeSet author="alphahinex" id="20180515-1">
      ...
    </changeSet>
</databaseChangeLog>
```

### 利用 Gradle 执行 Liquibase 命令

如果不是从项目起始时就使用了 Liquibase，或者不想手写 Change Set，可以通过 Liquibase 提供的 [命令](http://www.liquibase.org/documentation/command_line.html) 来生成 Change Log 或 DDL 的变更（数据的变更暂不支持生成）。如果是使用 Gradle 的项目，可以利用 [Liquibase 的 Gradle 插件](https://github.com/liquibase/liquibase-gradle-plugin/tree/acf7a693563471f83fd26b9e15365ab98011d804) 来执行命令，更加便捷。

> Liquibase 项目本身的活跃度目前并不高，插件的活跃度及文档的准确性更是问题重重，这也是本文存在的意义之一。

#### Gradle 配置

以 [H2 数据库](http://h2database.com/html/main.html) 为例，为执行 Liquibase 引入数据库驱动：

```
buildscript {
    dependencies {
        classpath 'com.h2database:h2:1.3.176'
    }
}
```

引入插件：

```
plugins {
    id 'org.liquibase.gradle' version '1.2.4'
}
```

定义 activities 用以生成不同的 Change Log：

```
ext {
    // 数据库地址
    liquibaseUrl = 'jdbc:h2:~/data/h2/pep_dev;AUTO_SERVER=TRUE;DB_CLOSE_ON_EXIT=FALSE;MVCC=TRUE'
    // 旧版数据库地址，比较差异用
    liquibaseOldUrl = 'jdbc:h2:~/data/h2-diff/pep_dev;AUTO_SERVER=TRUE;DB_CLOSE_ON_EXIT=FALSE;MVCC=TRUE'
    liquibaseUsername = 'sa'
    liquibasePassword = ''
}

liquibase {
    activities {
        // 生成全库结构 Change Log
        genDev {
            changeLogFile 'db/dev.xml'
            url           liquibaseUrl
            username      liquibaseUsername
            password      liquibasePassword
        }
        // 生成全库数据 Change Log
        genDevData {
            changeLogFile     'db/dev-data.xml'
            url               liquibaseUrl
            username          liquibaseUsername
            password          liquibasePassword
            diffTypes         'data'
        }
        // 对比生成数据库结构变更 Change Log
        diffDev {
            changeLogFile     'db/dev-diff.xml'
            url               liquibaseOldUrl
            username          liquibaseUsername
            password          liquibasePassword
            referenceUrl      liquibaseUrl
            referenceUsername liquibaseUsername
            referencePassword liquibasePassword
        }
    }
    // 若不设定 runList，所有 activities 都会被执行
    // -PrunList=abc 并不好用，所以要执行指定的 activities 时，可直接修改此处值
    // 多个值可用逗号间隔，如 'genDev,genDevData'
    runList = 'genDevData'
}
```

### 生成 Change Log

#### 全库 Change Log，包括结构和数据

1. `runList` 设定为 `genDev,genDevData`
1. `./gradlew generateChangelog`
1. 在 `./db/dev.xml` 可找到全库结构的 Change Log
1. 在 `./db/dev-data.xml` 可找到全库数据的 Change Log。

> 注意：执行命令前需保证这两个文件不存在，否则会报错。

> 生成的 Change Log 中的内容最好进行检查和一定的调整，以免自动生成的名称没有直观的含义，或产生冲突等问题。

#### 结构变更 Change Log

1. 欲进行数据库结构变更时，先将变更前的库备份，例如从 `~/data/h2/pep_dev` 备份至 `~/data/h2-diff/pep_dev`
1. `runList` 设定为 `diffDev`
1. `./gradlew diffChangeLog`
1. 结构变更 Change Log 将生成至 `./db/dev-diff.xml`。

#### 新增数据

1. 在数据库中执行 insert 语句
1. 修改 build.gradle 中配置的 liquibase.runList，将其值改为 'genDevData'
1. `./gradlew generateChangelog`
1. 从 `db/dev-data.xml` 中找到新增数据的 changeSet，并放至相应模块的 change log 文件中

#### 变更数据

Liquibase [目前并不支持数据变更的生成](http://forum.liquibase.org/topic/data-diff-diffchangelog)，可参照官方文档手写 Change Set，语法基本类似 SQL，可参照：

* [Update](http://www.liquibase.org/documentation/changes/update.html)
* [Delete](http://www.liquibase.org/documentation/changes/delete.html)


参考资料
-------

1. [Liquibase](https://github.com/liquibase/liquibase)
1. [Liquibase Documentation](http://www.liquibase.org/documentation/index.html)
1. [liquibase-gradle-plugin](https://github.com/liquibase/liquibase-gradle-plugin)
1. [Why not use HBM2DDL?](https://github.com/liquibase/liquibase-hibernate/wiki#why-not-use-hbm2ddl)
1. [Generating Change Logs](http://www.liquibase.org/documentation/generating_changelogs.html)
1. [Adding Liquibase on an Existing project](http://www.liquibase.org/documentation/existing_project.html)
1. [liquibase-hibernate](https://github.com/liquibase/liquibase-hibernate)
1. [Database “Diff”](http://www.liquibase.org/documentation/diff.html)
1. [Spring Integration](http://www.liquibase.org/documentation/spring.html)
1. [Trimming ChangeLog Files](http://www.liquibase.org/documentation/trimming_changelogs.html)
1. [comparing databases and generating sql script using liquibase](https://stackoverflow.com/questions/8397488/comparing-databases-and-generating-sql-script-using-liquibase)
1. [Bundled Liquibase Changes](http://www.liquibase.org/documentation/changes/index.html)
