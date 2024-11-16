---
id: maven-repositories-and-mirrors
title: "Maven 配置中的仓库和镜像"
description: "下载依赖不迷路"
date: 2024.11.17 10:34
categories:
    - Java
tags: [Java, Maven]
keywords: repository, profile, mirror, settings.xml, pom, nexus, central
cover: /contents/covers/maven-repositories-and-mirrors.png
---

# 一些概念

## 仓库（Repository）

Maven 中，仓库（Repository）是指存放 `pom` 和 `jar` 等文件的地方，分为本地仓库和远程仓库。

### 本地仓库（Local Repository）

本地仓库是 Maven 在本地文件系统中的一个目录，用于存储 Maven 项目的构建输出、依赖库、插件等。默认情况下，本地仓库位于用户目录下的 `.m2` 目录。可以在 [settings.xml](https://maven.apache.org/settings.html) 配置文件中通过 `<localRepository>` 元素修改本地仓库的默认路径。

### 远程仓库（Remote Repository）

不在本地的仓库，都是远程仓库，一般通过网络访问。远程仓库大致分为以下几类：

- **中央仓库（Central Repository）**：指由 `Sonatype` 公司维护的 Maven 官方仓库，地址 https://repo.maven.apache.org/maven2 。
- **插件仓库（Plugin Repository）**：仓库包含两种主要类型的工件（artifact）。第一种是作为其他工件依赖项使用的工件。这些工件是中央仓库中大多数工件。另一种类型的工件是插件。Maven 插件本身是一种特殊类型的工件。因此，插件仓库可能会与其他仓库分开。
- **镜像仓库（Mirror Repository）**：镜像仓库是一个代理服务器，用于加速 Maven 项目的依赖库、插件等的下载。镜像仓库会缓存被代理仓库中的内容，可以镜像中央仓库，也可以镜像其他类型的仓库。
- **私有仓库（Private Repository）**：私有仓库一般是指非 Maven 官方维护的 Maven 仓库，工件的发布流程较中央仓库更加自由。最佳实践是通过 [Repository Manager](https://maven.apache.org/repository-management.html) 来搭建一个私有仓库，如常见的 [Sonatype Nexus OSS](https://www.sonatype.com/products/repository-oss-download)。

# Maven 中的相关配置

## 仓库（Repository）

仓库会按如下 [顺序](https://maven.apache.org/guides/mini/guide-multiple-repositories.html) 查询配置文件，直到找到有效结果：

1. 有效的 `settings`：
    1. 全局 `settings.xml`（`${maven.home}/conf/settings.xml`）
    1. 用户 `settings.xml`（`${user.home}/.m2/settings.xml`）
2. 有效的本地 POM：
    1. 本地 `pom.xml`
    1. 父 POM，递归查找
    1. [Super POM](https://maven.apache.org/ref/3.9.9/maven-model-builder/super-pom.html)
3. 依赖路径中工件的有效的 POM

## Profile

在 `settings.xml` 的配置中，[仓库](https://maven.apache.org/settings.html#repositories) 需要配置到 [profiles](https://maven.apache.org/settings.html#profiles) 下。多个激活的 profile 中配置的仓库，[按照 profile 定义的顺序 **倒序** 查询](https://maven.apache.org/guides/introduction/introduction-to-profiles.html#Profile_Order)，不按照激活 profile 的顺序。例如在 `settings.xml` 中有如下配置：

```xml
<settings>
  ...
    <profiles>
        <profile>
            <id>no3</id>
            <repositories>
                <repository>
                    <id>repo3</id>
                    <url>https://repo3.com/maven2</url>
                </repository>
                <repository>
                    <id>repo4</id>
                    <url>https://repo4.com/maven2</url>
                </repository>
            </repositories>
        </profile>
        <profile>
            <id>no2</id>
            <repositories>
                <repository>
                    <id>repo2</id>
                    <url>https://repo2.com/repository/public</url>
                </repository>
            </repositories>
        </profile>
        <profile>
            <id>no1</id>
            <repositories>
                <repository>
                    <id>repo1</id>
                    <url>https://repo1.org/maven2</url>
                </repository>
            </repositories>
        </profile>
    </profiles>

    <activeProfiles>
        <activeProfile>no2</activeProfile>
        <activeProfile>no3</activeProfile>
        <activeProfile>no1</activeProfile>
    </activeProfiles>
    ...
</settings>
```

会优先使用在 `repo_no1` profile 中定义下载依赖使用的仓库顺序会是 `repo1`, `repo2`, `repo3`, `repo4`。

可以使用 `mvn help:effective-settings` 和 `mvn help:effective-pom -Dverbose` 来查看包含配置文件的有效设置和本地构建 POM，以便轻松查看它们的仓库顺序。

## 镜像（Mirror）

**在从仓库下载工件之前，会先应用镜像配置。**

比如在 `Super POM` 中定义的 `central` 仓库，在网络受限环境可以使用 `Nexus` 搭建一个中央仓库的代理服务，然后通过镜像配置将需要从中央仓库地址下载的工件替换为使用 `Nexus` 的地址加速下载。

可以在 `settings.xml` 配置文件的 [mirrors](https://maven.apache.org/settings.html#mirrors) 标签内配置镜像仓库，通过 `mirrorOf` 和仓库 `id` 进行关联，如：

```xml
<settings>
  ...
  <mirrors>
    <mirror>
      <id>internal-repository</id>
      <name>Maven Repository Manager running on repo.mycompany.com</name>
      <url>http://repo.mycompany.com/proxy</url>
      <mirrorOf>*,!repo1</mirrorOf>
    </mirror>
    <mirror>
      <id>foo-repository</id>
      <name>Foo</name>
      <url>http://repo.mycompany.com/foo</url>
      <mirrorOf>repo1</mirrorOf>
    </mirror>
  </mirrors>
  ...
</settings>
```

> 上面配置为所有非 `repo1` 的仓库配置了一个镜像地址，为 `repo1` 仓库配置了另一个镜像地址。更多用法可参阅 [Using Mirrors for Repositories](https://maven.apache.org/guides/mini/guide-mirror-settings.html)。
