---
id: upload-jars
title: "批量上传 Jar 包至 Maven 仓库"
description: "通过 pom 文件或 GAV 三级路径解析坐标"
date: 2023.02.05 10:34
categories:
    - Go
tags: [Go, Golang]
keywords: Golang, Linux, cli, Maven, Jar, pom, Java, Maven, Nexus
cover: /contents/upload-jars/cover.png
---

如果你有一些只有 Jar 包没有 pom 文件的类库需要上传至 Maven 仓库（如 Nexus），
或 Jar 和 pom 都有，但需要通过离线方式从一个 Maven 仓库迁移至另一个 Maven 仓库，可以试试下面这个命令行工具。

Upload Jars：https://github.com/AlphaHinex/go-toolkit/tree/main/upload-jars

简介
---

批量上传 Jar 包至 Maven 仓库的命令行工具。
如果存在与 Jar 包同名的 pom 文件，也会一并上传。

Jar 包及 pom 文件可都放置在同一路径内，并将此路径通过 `-i` 参数传入。

若仅有 Jar 包没有 pom 文件，需将 Jar 包按照要上传至的位置，放置在三级路径内：`GruopId/ArtifactId/Version`

示例
----

例如将 Jar 包及 pom 文件按如下路径放置：

```text
├── activiti-spring-5.15.jar
├── activiti-spring-5.15.pom
├── c3p0
│   └── c3p0
│       └── 0.9
│           └── c3p0-0.9-SNAPSHOT.jar
├── c3p0-0.9.1.2.jar
├── upload-jars
```

在相同路径执行 `./upload-jars -s snapshoturl -r release-url` 后，相当于执行了如下 Maven 命令：

```bash
$ mvn deploy:deploy-file \
-DgroupId=c3p0 -DartifactId=c3p0 -Dversion=0.9 \
-Dpackaging=jar -Dfile=./c3p0/c3p0/0.9/c3p0-0.9-SNAPSHOT.jar -Durl=snapshot-url
$ mvn deploy:deploy-file \
-DgroupId=org.activiti -DartifactId=activiti-spring -Dversion=5.15 \
-Dpackaging=jar -Durl=release-url \
-DpomFile=./activiti-spring-5.15.pom -Dfile=./activiti-spring-5.15.jar
```

> 因上例中的 `c3p0-0.9.1.2.jar` 无同名 pom 文件，无法确定其 GAV 信息，无法被上传。

用法
----

`upload-jars [-i 查找 Jar 包的根路径] [-c 配置文件] [-s snapshot 仓库 url] [-r release 仓库 url]`

默认从命令执行路径查找要上传的 Jar 包。
批量上传的 Jar 包及同名 pom 文件（如果存在）可按如下两种方式放置在查找 Jar 包的根路径中：
1. 直接将 pom 文件和 Jar 包放置在根路径中（此种方式不支持仅有 Jar 包没有 pom 文件的情况，因为需要从 pom 文件中获取 GAV 信息）
2. 按 GAV（group、artifact、version）创建三级路径，将 Jar 包及 pom 文件（如果存在）放在 version 路径内，如：
```text
├── com.alibaba
│   └── druid
│       └── 2.5.8
│           └── test.jar
├── org.codehaus.groovy
│   ├── groovy-console
│   │   ├── 2.5.8
│   │   │   ├── test-snapshot.jar
│   │   │   ├── test-snapshot.pom
│   │   │   ├── test.jar
│   │   │   └── test.pom
│   │   └── 2.5.9
│   │       └── test.jar
│   └── groovy-shell
│       ├── 2.5.8
│       │   ├── test-snapshot.jar
│       │   ├── test-snapshot.pom
│       │   ├── test.jar
│       │   └── test.pom
│       └── 2.5.9
│           └── test.jar
```

Maven 仓库地址需通过命令行参数或配置文件指定，命令行参数会覆盖配置文件中对应地址。
仓库地址需指定两个，一个 snapshot 仓库，一个 release 仓库。
工具根据 Jar 包文件名中是否包含 snapshot（不区分大小写）关键字进行区分，
若包含，上传至 snapshot 仓库；不包含则上传至 release 仓库。
Maven 仓库上传需要身份认证时，需将认证信息包含进仓库地址中，格式如下：
```
http://username:pwd@host:port/path/to/repository
```
其中用户名、密码如包含特殊字符，需进行 URL 转义。

配置文件格式示例：

```properties
snapshot=http://username:pwd@host:port/path/to/snapshot-repository
release=http://username:pwd@host:port/path/to/release-repository
```

下载地址
-------

可在 [GitHub 仓库](https://github.com/AlphaHinex/go-toolkit/tree/main/upload-jars) 通过源码编译最新版本，或下载预编译版本：

1. [upload-jars Windows AMD64 版本](/contents/upload-jars/upload-jars_win_amd64.exe)
1. [upload-jars Linux AMD64 版本](/contents/upload-jars/upload-jars_linux_amd64)