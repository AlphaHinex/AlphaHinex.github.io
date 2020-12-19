---
id: teamcity-kotlin-dsl
title: "TeamCity Kotlin DSL"
description: "Configuration as code"
date: 2020.12.20 10:34
categories:
    - DevOps
tags: [CI, DSL]
keywords: TeamCity, Kotlin, DSL, CI, portable
cover: /contents/teamcity-kotlin-dsl/cover.jpg
---

将持续集成环境的配置代码化（Configuration as code）有很多好处：
1. 可借助版本控制系统（VCS）对配置进行管理
1. 很容易对配置变更进行审查（review）
1. 提高配置的可移植性
1. 不同的分支可以执行不同的构建，甚至是未合并的请求分支以及历史构建

目前常见的持续集成服务都提供（甚至仅有）代码化配置方式，如：
1. [Travis CI](https://travis-ci.org/) 的 `.travis.yml`
1. [GitHub Actions](https://github.com/features/actions) 的放在代码仓库 `.github/workflows` 路径下的 [workflow yml 文件](https://docs.github.com/en/free-pro-team@latest/actions/reference/workflow-syntax-for-github-actions)
1. [GitLab CI/CD](https://docs.gitlab.com/ee/ci/README.html) 的 `.gitlab-ci.yml`
1. [Jenkins](https://www.jenkins.io/) 的 [Jenkinsfile](https://www.jenkins.io/doc/book/pipeline/jenkinsfile/)
1. [TeamCity](https://www.jetbrains.com/teamcity/) 的 [Kotlin DSL 及 XML 格式配置](https://www.jetbrains.com/help/teamcity/storing-project-settings-in-version-control.html)

TeamCity 从 10.0 版本起，[引入了通过 Kotlin DSL 的方式定义构建配置](https://confluence.jetbrains.com/display/TCD10/What%27s+New+in+TeamCity+10.0#What'sNewinTeamCity10.0-DSLforTeamCityProjectConfiguration)，并且在 [2018.x](https://confluence.jetbrains.com/display/TCD18/What%27s+New+in+TeamCity+2018.1#What'sNewinTeamCity2018.1-PortableKotlinDSLformat) 版本进行了较大改进。

之前也多次尝试过使用 Kotlin DSL，但体验上总是差一点未能下定决心切换。在 Everything as Code 的强大执念下，使用当前最新的 [TeamCity 2020.2](https://www.jetbrains.com/help/teamcity/2020.2/what-s-new-in-teamcity.html) 版本再次踏上了体验之旅。

## 将已有配置转换为 Kotlin DSL

为帮助已有项目切换至 DSL，TeamCity 针对 build configuration 提供了 `View DSL` 按钮，即时查看当前配置对应的 kotlin 代码。

启用 DSL 作为构建配置时，需要在 project 的编辑界面的 `Versioned Settings` 中进行手动启用。

![Versioned Settings](/contents/teamcity-kotlin-dsl/versioned-settings.png)

Settings format 有 xml 和 Kotlin 两种类型。点击 `Apply` 按钮完成切换。

**注意：在启用 `Versioned Settings` 后，TeamCity 会创建 `.teamcity` 目录，以及对应配置文件，并立刻 commit/push 到对应的代码仓库中！**

生成的配置文件，即 [portable DSL scripts](https://www.jetbrains.com/help/teamcity/2020.2/kotlin-dsl.html#KotlinDSL-portableDSL)，主要有如下两个：

* `settings.kts` – 主 DSL 脚本，包含整个 project 的配置
* `pom.xml` – 使 `.teamcity` 文件夹可以按 Maven Project 形式被 IDE 打开，以便获得自动补全、编译以及编写单元测试等能力。**此文件对 TeamCity Server 来讲是非必须的，仅用来帮助进行 DSL 开发**。

> 通常情况下，`.teamcity` 中应该仅包括上面两个文件。但若项目中配置了一些附加内容（如使用自定义的 Maven `settings.xml`），在自动提交的文件中也会有所体现，以便可以进行整个 project 的移植。

另外，为方便在 DSL 较复杂的场景进行配置拆分，可以保持 `settings.kts` 这个 Kotlin Script 文件作为主入口，将部分配置拆分到 Kotlin（.kt）文件中，再被 kts 文件引用。

在启用了 DSL，且未使用 Context Parameters 时，是允许通过 UI 及 DSL 两种方式对配置进行调整的。

如果 DSL 在由 TeamCity 生成并提交后未做过任何手动调整，通过 Web 界面做出的修改将直接更新代码库中的 DSL。

但如果手动修改过 DSL ，之后再通过 UI 做出的任何配置变更，都将以 [patch](https://www.jetbrains.com/help/teamcity/kotlin-dsl.html#Editing+Project+Settings+via+Web+UI) 的形式被提交到代码库中，此时需要手动将 patch 中的内容合并到 `settings.kts` 或 `.kt` 文件中，并将 `patches` 路径清理掉。

## Use settings from VCS

在 `Versioned Settings` 的 [Configuration](https://www.jetbrains.com/help/teamcity/2020.2/storing-project-settings-in-version-control.html#Defining+Settings+to+Apply+to+Builds) 中，建议选择 `use settings from VCS`，这样做的好处是不同的分支可以执行不同的构建，甚至是未合并的请求分支以及历史构建，因为构建执行时会使用对应版本的代码库中的 DSL。

## 在 DSL 中使用密文

在 Kotlin DSL 中，有两种方式处理密文：

1. Context Parameters
1. Tokens

![Context Parameters](/contents/teamcity-kotlin-dsl/context-parameters.png)

> 注意：在 project 配置页的 Parameters 中配置的三类参数，都会以明文形式体现到 DSL 中！

![Parameters](/contents/teamcity-kotlin-dsl/parameters.png)

### Context Parameters

使用 Context Parameters 可以避免 DSL 出现密码等敏感信息，因为 DSL 是要提交到代码库的。

在 DSL 中引用 Context Parameters 时，可使用 `DslContext.getParameter("key")` 的方式。

在 TeamCity Server 中能看到设置的 Context Parameters 的 Name 和 Value 内容，并且可修改及删除。

当使用了 Context Parameters 后，通过 UI 编辑 DSL 的功能自动被禁用。

### Tokens

在 TeamCity 中可为敏感信息生成一个 Token，会得到一个类似 `credentialsJSON:254e505a-697d-4962-9ba3-c90a3dab6c6e` 的 Token 字符串。使用时可参照 [Working with secure values in DSL](https://www.jetbrains.com/help/teamcity/2020.2/kotlin-dsl.html#Working+with+secure+values+in+DSL) 中描述，将 Token 字符串直接填入 DSL 中需要密文的位置。

**注意：仅填写时能看到明文，一旦生成 token 就只能引用，不能查看明文或进行修改，也不能删除，即使未被引用。**

## 可移植性

使用 DSL 的优势之一就是使配置可以被同一个 CI Server 的不同 project 或在不同 Server 中使用，即可移植性。

按照 [官方文档](https://www.jetbrains.com/help/teamcity/2020.2/kotlin-dsl.html#Sharing+Kotlin+DSL+Scripts) 的说法，如果代码仓库中包含合法 DSL，可以很容易的使用 [Create Project From URL](https://www.jetbrains.com/help/teamcity/2020.2/creating-and-editing-projects.html) 方式，基于 DSL 新建一个 project。

![Import DSL](/contents/teamcity-kotlin-dsl/import-scan-kts.png)

但实际使用中发现，如果代码仓库的 master 分支中不包含 DSL，即使默认分支（比如 develop）中有 DSL，在使用上述方式创建 project 的时候，也不能自动检测到配置。

在这种情况下，可以先创建 project，之后在 VCS Root 中指定包含 DSL 的分支作为 Default branch，再到 `Versioned Settings` 中启用 DSL，点击 Apply 后，即可检测到原有配置。

![Detect DSL](/contents/teamcity-kotlin-dsl/detect-kts.png)

## 使用 IDE 编辑 DSL

不同于 [YAML](https://yaml.org/) 格式的配置文件，TeamCity 的 DSL 基于 [Kotlin](https://kotlinlang.org/)，复用代码、动态创建配置、自动补全及代码导航等，真真正正的 Configuration as Code。

如何在 IDE 里做到这些呢？借助自动生成的 `pom.xml`，你可以将 `.teamcity` 路径，作为一个独立的 Maven 工程，引入到 IDE 中。

注意因为一些依赖是由 TeamCity Server 提供的（如：http://localhost:8111/app/dsl-plugins-repository），导入 IDE 的时候需要能够连接到持续集成服务。

### 简化相同内容配置

DRY（https://en.wikipedia.org/wiki/Don%27t_repeat_yourself） 在编程时是一个重要的原则，编写 Kotlin DSL 时，我们可以借助编程思想来解决这个问题。

比如在每一个构建（buildType）中，我们都希望加入一个 feature（*Build Files Cleaner*，AKA *Swabra*），违反 DRY 原则的做法是在每个 buildType 中都增加如下内容：

```kotlin dsl
features {
   swabra {
   }
}
```

可以定义一个 function，将需要添加这个 feature 的 buildType 包起来，实现简化配置的目的：

```kotlin dsl
fun cleanFiles(buildType: BuildType): BuildType {
   buildType.features {
       swabra {}
   }
   return buildType
}
```

在使用时：

```kotlin dsl
buildType(cleanFiles(Build))
buildType(cleanFiles(AnotherBuild))
buildType(cleanFiles(OneMoreBuild))
```

## [TeamCity Configuration as Code Roadmap](https://www.jetbrains.com/teamcity/roadmap/#configuration-as-code)

目前官网上放出的关于配置代码化的路线图有如下三个方面：

### Viewing project configuration as DSL - Developing

> The View DSL button provides a great way to learn how to describe your build configuration in Kotlin code. Right now it is available only for build configurations, which is not very helpful if you want to write configurations for complete projects or if you are looking for the right piece of code to configure one particular thing. We are going to add similar buttons to other sections of TeamCity, so you can always find the correct way to configure your VCS roots, clean-up settings, or entire projects – as Kotlin code.

当前最新的 2020.2 版本仅能使用 `View DSL` 按钮查看 build configuration 的代码，未来将增加可通过 `View DSL` 按钮查看整个 project 的 kotlin 代码。这将进一步的提升配置的可移植性。

### Omitting imports in DSL code - Designing

> We want the Kotlin DSL to be as brief and expressive as possible. To make it easier for you to describe your build configurations in Kotlin, we will allow you to omit the imports section in the beginning of the settings.kts file. This means that settings.kts can start directly with the project {...} section and will not require you to explicitly specify imports that are required to compile the script.

允许省略 DSL 头部的 import。比较期待的改进。

### Disabling UI editing - Developing

> TeamCity lets you set up CI/CD pipelines in a variety of ways based on your preferred workflow. Your projects can be configured through the DSL, through the UI, or through a mix of both. However, mixing manual edits with DSL changes may lead to a lot of confusion and versioning problems. To ensure that your configurations stay predictable and easy to manage, we will add a new option that will allow administrators to prohibit editing project configurations through the UI if they are set up using the Kotlin DSL.

目前在未使用 [Kotlin DSL Context Parameter](https://blog.jetbrains.com/teamcity/2020/09/creating-teamcity-project-templates-with-kotlin-dsl-context-parameters/) 时，是允许使用 UI 及 DSL 混用的方式进行构建配置的调整的。未来将允许管理员对启用了 DSL 配置的项目禁用 UI 配置。

## 总体感受

虽然使用 Kotlin DSL 会带来一些学习成本，并且在使用密文的时候（尤其是 Token）可能需要做一些尝试，但与其所带来的好处相比，还是可以承受的。

如果你想尝试 TeamCity Kotlin DSL，现在是个不错的时机。

## 参考资料

* [TeamCity Versioned Settings with Kotlin](https://rodm.github.io/blog/2017/03/teamcity-versioned-settings.html)
* [Configuration as Code, Part 1: Getting Started with Kotlin DSL](https://blog.jetbrains.com/teamcity/2019/03/configuration-as-code-part-1-getting-started-with-kotlin-dsl/)
* [Configuration as Code, Part 2: Working with Kotlin Scripts](https://blog.jetbrains.com/teamcity/2019/03/configuration-as-code-part-2-working-with-kotlin-scripts/)
* [Configuration as Code, Part 3: Creating Build Configurations Dynamically](https://blog.jetbrains.com/teamcity/2019/04/configuration-as-code-part-3-creating-build-configurations-dynamically/)
* [Configuration as Code, Part 4: Extending the TeamCity DSL
](https://blog.jetbrains.com/teamcity/2019/04/configuration-as-code-part-4-extending-the-teamcity-dsl/)
* [Configuration as Code, Part 5: Using DSL extensions as a library](https://blog.jetbrains.com/teamcity/2019/04/configuration-as-code-part-5-using-dsl-extensions-as-a-library/)
* [Configuration as Code, Part 6: Testing Configuration Scripts](https://blog.jetbrains.com/teamcity/2019/05/configuration-as-code-part-6-testing-configuration-scripts/)
