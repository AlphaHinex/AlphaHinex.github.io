---
id: github-packages-in-action
title:  "GitHub Packages in Action"
description: "本文以 Maven 类型为例，说明了如何利用 GitHub Packages 进行 jar 包的发布"
date:   2020.01.17 11:14:34
categories: Java
tags: [GitHub, Gradle, Maven, Java]
keywords: gpr, GitHub Packages, GitHub Packages Registry
cover: https://github.blog/wp-content/uploads/2019/05/facebook-1200x630.png?fit=1203%2C633
---

[GitHub Packages](https://help.github.com/en/github/managing-packages-with-github-packages) 可以用来当做 Release 版本 jar 包的 Maven 仓库。

与 Maven 中央库比，没有繁琐的申请流程，可以快速的将 jar 包发布出去供他人使用。

与 Nexus 私服相比，无需架设公网访问环境。

**缺点** 是只支持 Release 版本的发布和下载，Snapshot 版本虽然可以发布上去，但无法被其他项目依赖。目前尚不支持自行删除已上传的 jar 包，需联系 GitHub 协助处理。

本文以实例说明，在 Gradle 中如何利用 GPR（GitHub Packages Registry）进行发布版 jar 包的上传、下载及删除。


上传
---

参考 [官方文档](https://help.github.com/en/github/managing-packages-with-github-packages/configuring-gradle-for-use-with-github-packages)，需完成如下步骤。

### 在 GitHub 创建 Personal access token

GPR 相当于一个需要权限才可访问的 Maven 仓库。故必须使用 GitHub 账号进行相应操作。虽按文档描述可直接利用 GitHub 账号密码（实际若直接用密码，会收到提示，无法正常使用），但更推荐的是通过 token 的方式，限定 token 的权限范围，利用不同 token 完成不同操作。

可在 https://github.com/settings/tokens 创建个人的 token，GRP 相关权限可见 [About tokens](https://help.github.com/en/github/managing-packages-with-github-packages/about-github-packages#about-tokens)。

建议创建如下两个 token：

* 只读 token（包含 `read:packages`）：可用来从 GPR 下载自己 **及他人** 发布的 jar 包
* 管理 token（包含 `read:packages`, `write:packages`, `delete:packages`, `repo`）：可发布、删除 packages

### 在 `build.gradle` 中添加配置

借助 Gradle 的 `maven-publish` 插件，将 GPR 配置为 Maven 仓库，通过 `publish` task 即可完成上传。

以使用 Gradle Groovy 的单包仓库为例，可在 `build.gradle` 中添加如下内容（注意替换 `username` 和 `password`）：

```gradle
plugins {
    id("maven-publish")
}

publishing {
    repositories {
        maven {
            name = "GitHubPackages"
            url = uri("https://maven.pkg.github.com/OWNER/REPOSITORY")
            credentials {
                username = project.findProperty("gpr.user") ?: System.getenv("USERNAME")
                password = project.findProperty("gpr.key") ?: System.getenv("PASSWORD")
            }
        }
    }
    publications {
        gpr(MavenPublication) {
            from(components.java)
        }
    }
}
```

> 更多示例可参考 [官方文档](https://help.github.com/en/github/managing-packages-with-github-packages/configuring-gradle-for-use-with-github-packages) 或 [spring-roll](https://github.com/AlphaHinex/spring-roll) 项目的 [实例](https://github.com/AlphaHinex/spring-roll/blob/master/build.gradle)。

此处需补充一下，发布 jar 包时若需要包含源码，需在编译阶段生成好源码 jar 包。

Gradle 6.0.1 Java 插件对此提供了支持，可直接在 `build.gradle` 中添加如下内容

```gradle
java {
    withSourcesJar()
}
```

> 若是 6.x 之前的版本，可自定义 task 完成源码 jar 包的打包，但是否能正常上传 GPR 未验证。

### 发布

```bash
$ ./gradlew publish
```

发布成功后，可在仓库的 [packages](https://github.com/AlphaHinex/spring-roll/packages) 选项卡或 [Profile](https://github.com/AlphaHinex?tab=packages) 中查看，也可使用类似 https://maven.pkg.github.com/alphahinex/spring-roll/io/github/spring-roll/roll-base/0.0.1.RELEASE/roll-base-0.0.1.RELEASE.pom 的地址（需提供 GPR 的访问权限）确认。

> 开发时若需要将 SNAPSHOT 版本发布到本地 Maven 库，可使用 `./gradlew publishToMavenLocal`，并在项目 `build.gradle` 文件的 `repositories` 块中增加 `mavenLocal()`。


下载
---

需下载他人发布到 GPR 中的 jar 包时，配置方式与配置 Nexus 私服的方式类似，例如：

```gradle
repositories {
  mavenCentral()
  mavenLocal()
  maven {
    url "https://maven.pkg.github.com/alphahinex/spring-roll"
    credentials {
      username = 'GITHUB_USERNAME'
      password = 'TOKEN_WITH_READ:PACKAGES_SCOPE'
    }
  }
}
```

之后在 `dependencies` 中添加依赖，如 `implementation 'io.github.spring-roll:roll-base:0.0.1.RELEASE'`，若一切顺利即可下载到 roll-base v0.0.1.RELEASE 的 jar 包和源码。


删除
---

虽然有 `delete:packages` 权限，但目前 GitHub 仅允许用户对上传到 GPR 的私有仓库的 jar 包进行删除。

若需要删除公开仓库的 jar 包，需通过 [支持](https://support.github.com/contact) 与 GitHub 联系，并提供需要删除的包的链接。

删除私有库的 jar 包需使用 GitHub 在 GraphQL 中提供的删除方法（未验证）。

删除前需获得要删除的包的 `packageVersionId`（界面不可见），可通过查询接口进行查询，如：

```bash
$ curl -X POST \
-H "Authorization: bearer TOKEN" \
-H "Accept: application/vnd.github.packages-preview+json" \
-d '{"query": "query { user(login: \"AlphaHinex\") { registryPackagesForQuery(packageType: MAVEN, first: 100) { edges { node { name id version(version: \"0.1.0.RELEASE\") { id version }} } } }}"}' https://api.github.com/graphql
```

得到类似下方的信息：

```json
{
  "data": {
    "user": {
      "registryPackagesForQuery": {
        "edges": [
          {
            "node": {
              "name": "io.github.spring-roll.roll-base",
              "id": "MDc6UGFja2FnZTkyOTgy",
              "version": {
                "id": "MDE0OlBhY2thZ2VWZXJzaW9uNTI3MTcx",
                "version": "0.1.0-SNAPSHOT"
              }
            }
          },
          {
            "node": {
              "name": "io.github.spring-roll.roll-dev-configs",
              "id": "MDc6UGFja2FnZTkyOTg0",
              "version": {
                "id": "MDE0OlBhY2thZ2VWZXJzaW9uNTI3MTcy",
                "version": "0.1.0-SNAPSHOT"
              }
            }
          },
          {
            "node": {
              "name": "io.github.spring-roll.roll-dl",
              "id": "MDc6UGFja2FnZTkyOTg1",
              "version": {
                "id": "MDE0OlBhY2thZ2VWZXJzaW9uNTI3MTcz",
                "version": "0.1.0-SNAPSHOT"
              }
            }
          },
          {
            "node": {
              "name": "io.github.spring-roll.roll-test",
              "id": "MDc6UGFja2FnZTkyOTg2",
              "version": {
                "id": "MDE0OlBhY2thZ2VWZXJzaW9uNTI3MTc0",
                "version": "0.1.0-SNAPSHOT"
              }
            }
          },
          {
            "node": {
              "name": "io.github.spring-roll.roll-utils",
              "id": "MDc6UGFja2FnZTkyOTg3",
              "version": {
                "id": "MDE0OlBhY2thZ2VWZXJzaW9uNTI3MTc3",
                "version": "0.1.0-SNAPSHOT"
              }
            }
          },
          {
            "node": {
              "name": "io.github.spring-roll.roll-web",
              "id": "MDc6UGFja2FnZTkyOTg4",
              "version": {
                "id": "MDE0OlBhY2thZ2VWZXJzaW9uNTI3MTc5",
                "version": "0.1.0-SNAPSHOT"
              }
            }
          }
        ]
      }
    }
  }
}
```

获得到要删除的 jar 包的 `packageVersionId` 后，依旧通过 GraphQL 接口删除：

```bash
$ curl -X POST \
-H "Accept: application/vnd.github.package-deletes-preview+json" \
-H "Authorization: bearer TOKEN" \
-d '{"query":"mutation { deletePackageVersion(input:{packageVersionId:\"MDc6UGFja2FnZTkyOTgy\"}) { success }}"}' \
https://api.github.com/graphql
```


实例
---

* jar 包发布可参考项目 [spring-roll](https://github.com/AlphaHinex/spring-roll)
* 使用 jar 包可参考项目 [seata-at-demo](https://github.com/AlphaHinex/seata-at-demo)


参考资料
-------

1. [GraphQL 实战：GitHub V4 API 使用](https://www.jianshu.com/p/af7ac20f2c64)
