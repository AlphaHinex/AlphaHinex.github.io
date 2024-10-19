---
id: spring-cloud-release-train-and-version-compatibility
title: "Spring Cloud 的 Release Train 和版本兼容性"
description: "本文介绍了 Spring Cloud 发布列车的命名方式，并整理了各子项目版本兼容性"
date: 2024.10.20 10:34
categories:
    - Spring
tags: [Spring, Spring Cloud]
keywords: release train, version compatibility, Spring Cloud
cover: /contents/covers/spring-cloud-release-train-and-version-compatibility.png
---

# Spring Cloud 发布列车（Release Train）命名规范

https://github.com/spring-cloud/spring-cloud-release/wiki/Release-Train-Naming-Convention

## 介绍

Spring Cloud 是一个包含多个独立项目的总项目，这些项目原则上有不同的发布节奏。为了管理这个组合项目，会发布一个 BOM（材料清单），其中包含对各个独立项目的依赖版本集合。

## 历史命名

从历史上看，发布列车有名称而不是版本，以避免与子项目混淆。这些名称是按字母顺序排列的（因此可以按时间顺序排序），使用的是伦敦地铁站的名称（“Angel”是第一个版本，“Brixton”是第二个，等等）。当各个项目的版本积累到一定程度，或者其中一个项目有关键错误需要更新版本以提供给所有人时，发布列车将推出以“.SRX”结尾的“服务版本”（service releases），其中“X”是一个数字。

命名的发布列车有：

* Angel
* Brixton
* Camden
* Dalston
* Edgware
* Finchley
* Greenwich
* Hoxton

Hoxton 是（历史命名法的）最后一个发布列车。有关其支持时间表，请参见 [Supported-Versions](https://github.com/spring-cloud/spring-cloud-release/wiki/Supported-Versions)。

## Calver 发布列车

从 2020 年开始，[Spring 团队](https://spring.io/blog/2020/04/30/updates-to-spring-versions)转向[日历版本](https://calver.org/)（简称 calver）风格的发布列车版本。对于 Spring Cloud，这始于 [2020.0.0-M1](https://spring.io/blog/2020/04/17/spring-cloud-2020-0-0-m1-released)。

Spring Cloud 将遵循 `YYYY.MINOR.MICRO` [scheme](https://calver.org/#scheme)，其中 `MINOR` 是每年从零开始递增的数字。`MICRO` 段对应于先前使用的后缀：`.0` 类似于 `.RELEASE`，`.2` 类似于 `.SR2`。预发布后缀也将从使用 `.` 更改为 `-` 作为分隔符，例如，`2020.0.0-M1` 和 `2020.0.0-RC2`。还将停止使用 `BUILD-` 作为快照的前缀 -- 例如 `2020.0.0-SNAPSHOT`。

Spring Cloud 还将继续使用伦敦地铁站的名称作为代码名称，但这些名称将不再用于发布到 maven 仓库的版本。

Calver 发布列车

* 2020.0 (codename `Ilford`)
* 2021.0 (codename `Jubilee`)
* 2022.0 (codename `Kilburn`)
* 2023.0 (codename `Leyton`)
* 2024.0 (codename `Moorgate`)

# 版本兼容性

https://github.com/AlphaHinex/spring-cloud-release/blob/develop/Version%20Compatibility.md

![](/contents/covers/spring-cloud-release-train-and-version-compatibility.png)
