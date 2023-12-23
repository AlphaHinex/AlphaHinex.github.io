---
id: maven-offline-build
title: "离线环境下 Maven 编译打包"
description: "本文给出了在离线环境下使用 Maven 编译打包的方案。"
date: 2023.12.24 10:26
categories:
    - Java
tags: [Java, Maven]
keywords: Maven, mvn, settings.xml, offline, localRepository, _remote.repositories
cover: /contents/covers/maven-offline-build.png
---

背景
===

某些离线场景下我们可能无法连接 Maven 中央库或其他内网私服，又想通过 Maven 对源码进行编译打包。

本文给出了在离线环境下使用 Maven 编译打包的方案。


前置条件
=======

假设目标环境已经安装好了 JDK 和 Maven，并且将要编译的源码工程 `demo-project` 放置在了 `/maven-offline/build` 路径下。 


解决方案
=======

准备编译所需依赖
-------------

先在联网环境成功执行一次编译，保证使用的 Maven 本地缓存仓库（默认路径 `~/.m2/repository`）中包含了编译所需的依赖。

将本地缓存仓库目录 `repository` 发送至离线环境 `/maven-offline/build` 路径下：

```text
├── demo-project
└── repository
```

### 清理所有 `_remote.repositories` 文件

**`repository` 目录中可能包含了很多 `_remote.repositories` 文件，需先将这些文件进行清理，否则还是会去中央库查找依赖。**

- Windows：

```cmd
for /r %i in (_remote.repositories) do del %i
```

- Linux：

```bash
find ./repository -name "_remote.repositories" -exec rm {} \;
```

Maven 离线编译配置
----------------

在 `/maven-offline/build/` 下新建 `settings.xml`，内容如下：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 http://maven.apache.org/xsd/settings-1.0.0.xsd">
    
    <localRepository>/maven-offline/build/repository</localRepository>
    <offline>true</offline>
    
</settings>
```

配置文件中只需设定两个 [Simple Values](https://maven.apache.org/settings.html#simple-values)：
1. `localRepository`：指定清理过 `_remote.repositories` 文件的路径
1. `offline`：使用离线模式

指定配置文件执行编译
-----------------

以在 `/maven-offline/build/` 路径下执行命令为例：

```text
├── demo-project
├── repository
└── settings.xml
```

```bash
mvn -s settings.xml -f demo-project/pom.xml clean package
```

参考资料
=======

- [maven离线环境配置（纯内网）](https://blog.csdn.net/Remember_Z/article/details/119523295)