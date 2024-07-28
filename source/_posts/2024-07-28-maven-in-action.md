---
id: maven-in-action
title: "Maven 实用技巧"
description: "Maven Wrapper、Multi-module vs. Inheritance、Reactor、模块间依赖及部分构建、执行指定的测试等 Maven 实用技巧"
date: 2024.07.28 10:26
categories:
    - Java
tags: [Java, Maven]
keywords: maven, mvn, maven wrapper, mvnw, reactor, multi-module, aggregator, parent, inheritance
cover: /contents/maven-in-action/cover.jpg
---

Maven Wrapper
=============

[Maven Wrapper](https://maven.apache.org/wrapper/) 借鉴了 [Gradle Wrapper](https://docs.gradle.org/current/userguide/gradle_wrapper.html) 的思想，可以在工程源码中提交 Wrapper 的脚本和配置，之后在工程目录中使用 `mvnw` 或 `mvnw.cmd` 命令代替 `mvn` 命令，从而保证了各个开发及持续集成环境在构建时使用的 Maven 版本是一致的。

主要文件
------

Maven Wrapper 最主要的是下面三个文件，可以使用 `mvn wrapper:wrapper -Dtype=only-script`（或 `-Dtype=script`） 命令生成，也可直接从其他工程复制：

```text
├── .mvn
│   └── wrapper
│       └── maven-wrapper.properties
├── mvnw
└── mvnw.cmd
```

1. `.mvn/wrapper/maven-wrapper.properties`：指定了 Maven 版本及下载地址
2. `mvnw`：Linux/Unix 系统下的 Maven Wrapper 脚本
3. `mvnw.cmd`：Windows 系统下的 Maven Wrapper 脚本

> 除上面三个文件外，根据使用 `mvn wrapper:wrapper` 命令时指定的 `type` 参数的不同，还可能生成 `.mvn/wrapper/maven-wrapper.jar`（`mvn wrapper:wrapper`） 或 `.mvn/wrapper/MavenWrapperDownloader.java`（`mvn wrapper:wrapper -Dtype=source`） 文件，用以下载指定的 Maven 版本发布包。

指定版本
-------

要指定使用的 Maven 版本，可以通过如 `mvn wrapper:wrapper -Dmaven=3.8.1` 命令，或直接修改 `maven-wrapper.properties` 文件中的 `distributionUrl` 属性值：

```properties
distributionUrl=https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/3.8.1/apache-maven-3.8.1-bin.zip
```

> 使用带身份认证的私有 Maven 仓库时，可以通过在 URL 中添加用户名和密码的方式进行认证（`http://uname:pwd@url`），或设定 `MVNW_USERNAME` 和 `MVNW_PASSWORD` 环境变量。

存放路径
-------

通过 Maven Wrapper 下载的 Maven 版本放在 `~/.m2/wrapper` 路径下：

```text
└── .m2
    └── wrapper
        └── dists
            ├── apache-maven-3.5.4
            │   └── 23a80dd6
            │       ├── .DS_Store
            │       ├── LICENSE
            │       ├── NOTICE
            │       ├── README.txt
            │       ├── bin
            │       ├── boot
            │       ├── conf
            │       ├── lib
            │       └── mvnw.url
            ├── apache-maven-3.6.1
            │   └── 29f90916
            │       ├── LICENSE
            │       ├── NOTICE
            │       ├── README.txt
            │       ├── bin
            │       ├── boot
            │       ├── conf
            │       ├── lib
            │       └── mvnw.url
            └── apache-maven-3.9.8
                └── 8e4360d6
                    ├── LICENSE
                    ├── NOTICE
                    ├── README.txt
                    ├── bin
                    ├── boot
                    ├── conf
                    ├── lib
                    └── mvnw.url
```

使用方式
-------

在包含 Maven Wrapper 的工程中，可以直接使用 `./mvnw` 或 `./mvnw.cmd` 命令代替 `mvn` 命令，例如：

```bash
$ ./mvnw clean package
```


Multi-module vs. Inheritance
============================

在 Maven 中，多模块构建（Multi-module）和继承（Inheritance）是两个不同的概念，互相独立，可分别使用。

多模块
-----

Maven 在 pom 中通过 `<modules>` 元素表示 [多模块或聚合](https://maven.apache.org/pom.html#aggregation-or-multi-module)，如：

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
 
  <groupId>org.codehaus.mojo</groupId>
  <artifactId>my-parent</artifactId>
  <version>2.0</version>
  <packaging>pom</packaging>
 
  <modules>
    <module>my-project</module>
    <module>another-project</module>
    <module>third-project/pom-example.xml</module>
  </modules>
</project>
```

继承
----

`<parent>` 元素可将多个模块的配置抽取到一个父模块中，子模块可以继承父模块的配置，包括依赖、插件、属性等。继承关系是单向的，父模块不会知道子模块的存在：

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
 
  <parent>
    <groupId>org.codehaus.mojo</groupId>
    <artifactId>my-parent</artifactId>
    <version>2.0</version>
    <relativePath>../my-parent</relativePath>
  </parent>
 
  <artifactId>my-project</artifactId>
</project>
```

通常情况下，多模块构建和继承可以结合使用，例如将多个模块聚合在一起，同时抽取公共配置到父模块中：

[![Enterprise Multi-module vs. Inheritance](/contents/maven-in-action/pom_real_multi.png)](https://books.sonatype.com/mvnref-book/reference/pom-relationships-sect-pom-best-practice.html#fig-multi-module)

> 上图中，红线代表继承关系，蓝线代表聚合关系，可见二者是相互独立的两个体系。

子模块可以从父模块 [继承](https://maven.apache.org/pom.html#inheritance) 的属性包括：

```text
- groupId
- version
- description
- url
- inceptionYear
- organization
- licenses
- developers
- contributors
- mailingLists
- scm
- issueManagement
- ciManagement
- properties
- dependencyManagement
- dependencies
- repositories
- pluginRepositories
- build
  - plugin executions with matching ids
  - plugin configuration
  - etc.
- reporting
```

不可继承的属性包括：

```text
- artifactId
- name
- prerequisites
- profiles (but the effects of active profiles from parent POMs are)
```


Reactor
=======

[Reactor](https://maven.apache.org/guides/mini/guide-multiple-modules.html) 是 Maven 用来处理多模块项目的一个核心组件，负责收集可用模块并按照依赖关系排序，确保每个模块都能够在依赖它的其他模块被编译之前完成编译。

以 http://books.sonatype.com/mvnref-book/mvnref-examples.zip 示例代码包中 `ch-running` 文件夹下 Maven 工程为例，其中包含的模块和模块间依赖关系如下：

[![Directory Structure of Sample Multi-module Project](/contents/maven-in-action/running_aro-project-dir.png)](https://books.sonatype.com/mvnref-book/reference/_using_advanced_reactor_options.html#fig-running-aro-dir-struct)

[![Dependencies within Sample Multi-module Project](/contents/maven-in-action/running_aro-dependencies.png)](https://books.sonatype.com/mvnref-book/reference/_using_advanced_reactor_options.html#fig-running-aro-depends)

其中 `sample-parent` 模块 `pom.xml` 中定义的 `<modules>` 元素如下：

```xml
  <modules>
    <module>sample-admin-webapp</module>
    <module>sample-webapp</module>
    <module>sample-services</module>
    <module>sample-rest</module>
    <module>sample-persist</module>
    <module>sample-util</module>
    <module>sample-model</module>
    <module>sample-security</module>
    <module>sample-gui</module>
    <module>sample-admin-gui</module>
    <module>sample-client-connector</module>
  </modules>
```

Reactor 会根据模块间的依赖关系排序，最后没有其他规则需要遵守时，也会参照 `<modules>` 元素中定义的顺序排序：

```bash
$ mvn package
...
[INFO] ------------------------------------------------------------------------
[INFO] Reactor Summary:
[INFO]
[INFO] sample-parent 1.0-SNAPSHOT ......................... SUCCESS [  0.003 s]
[INFO] sample-model ....................................... SUCCESS [  0.706 s]
[INFO] sample-persist ..................................... SUCCESS [  0.016 s]
[INFO] sample-services .................................... SUCCESS [  0.014 s]
[INFO] sample-util ........................................ SUCCESS [  0.012 s]
[INFO] sample-security .................................... SUCCESS [  0.011 s]
[INFO] sample-admin-webapp ................................ SUCCESS [  0.015 s]
[INFO] sample-webapp ...................................... SUCCESS [  0.011 s]
[INFO] sample-rest ........................................ SUCCESS [  0.014 s]
[INFO] sample-client-connector ............................ SUCCESS [  0.012 s]
[INFO] sample-gui ......................................... SUCCESS [  0.012 s]
[INFO] sample-admin-gui 1.0-SNAPSHOT ...................... SUCCESS [  0.021 s]
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
...
```


模块间依赖及部分构建
=================

在多模块项目中，有时候只需要构建其中的某个模块，或者只需要构建某个模块及其依赖的模块，这时可以使用 Maven 的一些 [高级 Reactor 选项](https://books.sonatype.com/mvnref-book/reference/_using_advanced_reactor_options.html)：

- `-rf`, `--resume-from`：从指定的项目恢复构建
- `-pl`, `--projects`：构建指定的项目而不是所有项目
- `-am`, `--also-make`：如果通过 `-pl` 参数指定了项目列表，还会构建列表中项目所依赖的项目
- `-amd`, `--also-make-dependents`：如果通过 `-pl` 参数指定了项目列表，还会构建依赖于列表中项目的项目

恢复构建
-------

仍然以上面的 `sample-parent` 项目为例，如果需要从 `sample-client-connector` 模块继续构建，可以使用 `-rf` 参数：

```bash
$ mvn --resume-from sample-client-connector package
[INFO] Scanning for projects...
[INFO] ------------------------------------------------------------------------
[INFO] Reactor Build Order:
[INFO]
[INFO] sample-client-connector                                            [jar]
[INFO] sample-gui                                                         [jar]
[INFO] sample-admin-gui                                                   [jar]
...
```

如果遇到找不到其他模块报错问题（如下），可先执行 install 将模块安装到本地仓库：

```bash
$ mvn package -rf sample-client-connector
...
[WARNING] The POM for org.sonatype.mavenbook.running:sample-model:jar:1.0-SNAPSHOT is missing, no dependency information available
[WARNING] The POM for org.sonatype.mavenbook.running:sample-util:jar:1.0-SNAPSHOT is missing, no dependency information available
[INFO] ------------------------------------------------------------------------
[INFO] Reactor Summary:
[INFO]
[INFO] sample-client-connector 1.0-SNAPSHOT ............... FAILURE [  0.105 s]
[INFO] sample-gui ......................................... SKIPPED
[INFO] sample-admin-gui 1.0-SNAPSHOT ...................... SKIPPED
[INFO] ------------------------------------------------------------------------
[INFO] BUILD FAILURE
[INFO] ------------------------------------------------------------------------
[INFO] Total time: 0.218 s
[INFO] Finished at: 2024-07-27T16:24:22+08:00
[INFO] ------------------------------------------------------------------------
[ERROR] Failed to execute goal on project sample-client-connector: Could not resolve dependencies for project org.sonatype.mavenbook.running:sample-client-connector:jar:1.0-SNAPSHOT: The following artifacts could not be resolved: org.sonatype.mavenbook.running:sample-model:jar:1.0-SNAPSHOT, org.sonatype.mavenbook.running:sample-util:jar:1.0-SNAPSHOT: Failure to find org.sonatype.mavenbook.running:sample-model:jar:1.0-SNAPSHOT in http://repo.maven.apache.org/maven2 was cached in the local repository, resolution will not be reattempted until the update interval of local-nexus has elapsed or updates are forced -> [Help 1]
...
```

```bash
$ mvn install
$ mvn package -rf sample-client-connector
```

多层级模块
--------

当存在多层级模块的聚合，使用 `-rf`、`-pl` 等参数指定模块名时，需要在模块名前面加冒号。

比如在 `ch-running` 目录下：

```text
├── pom.xml
└── sample-parent
    ├── mvn
    ├── pom.xml
    ├── sample-admin-gui
    ├── sample-admin-webapp
    ├── sample-client-connector
    ├── sample-gui
    ├── sample-model
    ├── sample-persist
    ├── sample-rest
    ├── sample-security
    ├── sample-services
    ├── sample-util
    └── sample-webapp
```

```bash
$ mvn package -pl sample-util
[INFO] Scanning for projects...
[ERROR] [ERROR] Could not find the selected project in the reactor: sample-util @
[ERROR] Could not find the selected project in the reactor: sample-util -> [Help 1]
[ERROR]
[ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
[ERROR] Re-run Maven using the -X switch to enable full debug logging.
[ERROR]
[ERROR] For more information about the errors and possible solutions, please read the following articles:
[ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/MavenExecutionException
```

```bash
$ mvn package -pl :sample-util
[INFO] Scanning for projects...
[INFO]
[INFO] -------------< org.sonatype.mavenbook.running:sample-util >-------------
[INFO] Building sample-util 1.0-SNAPSHOT
[INFO] --------------------------------[ jar ]---------------------------------
...
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
...
```


执行指定的测试
============

在 Maven 项目中，可以通过 `-Dtest` 参数指定执行的测试类或测试方法，例如：

```bash
$ mvn test -Dtest=com.example.MyTestClass
$ mvn -pl :module-a -am test -Dtest=com.example.MyTestClass -DfailIfNoTests=false
```
