---
id: github-actions-in-action
title: "GitHub Actions 实战"
description: "持续集成环境常用功能的 GitHub Actions 实现"
date: 2020.03.27 19:26
categories:
    - DevOps
tags: [GitHub, CI]
keywords: GitHub, GitHub Actions, workflow, CI, automation
cover: /contents/covers/github-actions-in-action.png
---

## GitHub Actions 是什么？

与 [Jenkins](https://jenkins.io/)、[TeamCity](https://www.jetbrains.com/teamcity/)、[Travis CI](https://travis-ci.org/) 类似，[GitHub Actions](https://help.github.com/en/actions) 是 GitHub 提供的一个持续集成平台。

## 与三方持续集成平台的对比

||GitHub Actions|Jenkins|TeamCity|Travis CI|
|:--|:--|:--|:--|:--|
|代码仓库平台无关性|×|√|√|√|
|构建配置即源码|√|×|×|√|
|无需单独部署|√|×|×|√|
|自动回调 GitHub 构建状态接口|√|×|×|√|
|无需配置敏感信息|√|×|×|×|

* 代码仓库平台无关性：GitHub Actions 绑定 GitHub，若代码仓库迁移至其他持续集成平台，无法直接复用在 GitHub Actions 中定义的 workflow。
* 构建配置即源码：GitHub Actions 及 Travis CI 均使用 yaml 配置文件描述构建过程，便于复制且可与源码共同进行版本控制。
* 无需单独部署：GitHub Actions 及 Travis CI 为 SaaS 开箱即用，提交配置文件后即可看到效果。
* 自动回调 GitHub 构建状态接口：GitHub Actions 及 Travis CI 的构建状态无需插件及额外配置，会自动调用 GitHub 的 API 接口，完成状态显示。
* 无需配置敏感信息：在需要持续集成平台进行代码提交时（如自动合并代码），需要有代码仓库的相应权限。三方平台均需配置 GitHub 的 token，GitHub Actions 内置参数进行支持。

## 怎么使用？

在 GitHub 代码仓库根路径，创建 `.github/workflows` 路径，在路径内即可放置 `.yml` 或 `.yaml` 文件，在文件中定义各个具体的 workflow 内容，语法可见 [Workflow syntax for GitHub Actions](https://help.github.com/en/actions/automating-your-workflow-with-github-actions/workflow-syntax-for-github-actions)。

## 常用功能实现方式

### 各分支及 PR 触发检查

即当发生 `push` 或 `pull_request` 事件时，会触发 workflow 的执行，如：

```yaml
# Trigger the workflow on push or pull request
on: [push, pull_request]
```

实例可见：https://github.com/AlphaHinex/seata-at-demo/blob/seata-at/.github/workflows/check.yml#L4-L9

相关文档：

* [Events that trigger workflows](https://help.github.com/en/actions/reference/events-that-trigger-workflows)
* [on.<push|pull_request>.<branches|tags>](https://help.github.com/en/actions/reference/workflow-syntax-for-github-actions#onpushpull_requestbranchestags)

### 分支自动合并

例如有这样一个需求：`master` 分支的任何变更，希望自动合并到 `develop` 分支上。可借助 [Nightly Merge Action](https://github.com/marketplace/actions/nightly-merge) 来实现，如：

`on`:
```yaml
on:
  push:
    branches:
      - master
```

`steps`:
```yaml
steps:
- name: Auto Merge
  uses: robotology/gh-action-nightly-merge@v1.2.0
  with:
    stable_branch: 'master'
    development_branch: 'develop'
```

实例可见：https://github.com/AlphaHinex/seata-at-demo/blob/seata-at/.github/workflows/auto-merge.yml

> 如希望合并操作在检查操作通过之后再执行，可将 master 分支的 push workflow 单独做，step1 check，step2 merge。

### 每日定时执行

有时可能需要以计划任务方式执行构建，如每晚执行集成测试或打包等。可使用 [schedule](https://help.github.com/en/actions/reference/events-that-trigger-workflows#scheduled-events-schedule) 事件进行触发，如：

```yaml
on:
  schedule:
    # * is a special character in YAML so you have to quote this string
    - cron:  '*/15 * * * *'
```

### Release 自动发布

在代码达到一个稳定版本需要进行释放时，可能需要将成果物发布到中央仓库中（如 Maven、npm registry、GitHub Packages Registry 等）以供他人使用。

在 GitHub 中，当设置了 tag 后，即可在仓库的 releases 页面看到一个发布（如 https://github.com/AlphaHinex/spring-roll/releases ），并且可以为这个发布编写版本发布说明（如：https://github.com/spring-projects/spring-framework/releases/tag/v5.2.4.RELEASE）。

GitHub Actions 中分别有两种事件对应上述两种情况：

[on.<push|pull_request>.<branches|tags>](https://help.github.com/en/actions/reference/workflow-syntax-for-github-actions#onpushpull_requestbranchestags)

```yaml
on:
  push:
    # Sequence of patterns matched against refs/tags
    tags:        
      - v1             # Push events to v1 tag
      - v1.*           # Push events to v1.0, v1.1, and v1.9 tags
```

[release event](https://help.github.com/en/actions/reference/events-that-trigger-workflows#release-event-release)

```yaml
on:
  release:
    types: [published]
```

实例可见：https://github.com/AlphaHinex/spring-roll/pull/25/files

### Badge

可按照 [官方文档](https://help.github.com/en/actions/configuring-and-managing-workflows/configuring-a-workflow#adding-a-workflow-status-badge-to-your-repository) 中内容，按格式获得 badge 链接，也可以在创建好 actions 之后，直接在页面获得所需的 badge url，如：https://github.com/AlphaHinex/seata-at-demo/actions?query=workflow%3ACheck

实例如下：

`https://github.com/AlphaHinex/seata-at-demo/workflows/Check/badge.svg`

[![Check](https://github.com/AlphaHinex/seata-at-demo/workflows/Check/badge.svg)](https://github.com/AlphaHinex/seata-at-demo/actions?query=workflow%3ACheck)

## 已知问题

### 3306 端口无法使用

GitHub Actions 运行在 GitHub-hosted runner 上，在这些环境中会预装一些软件，详细信息可见 [Software installed on GitHub-hosted runners](https://help.github.com/en/actions/reference/software-installed-on-github-hosted-runners)。

所以在希望自建一些服务（不使用预装的）时，可能需要调整端口。如 MySQL 的默认端口 `3306`，在使用 [MySQL 相关的 actions](https://github.com/marketplace?type=actions&query=mysql) 或通过 Docker Compose 构建 MySQL 容器时，需要调整默认端口。

### wait-for-it 无效

在 [微服务的自动化集成测试实战](https://alphahinex.github.io/2020/02/05/microservices-integration-test-in-action/#%E6%8C%81%E7%BB%AD%E9%9B%86%E6%88%90%E7%8E%AF%E5%A2%83%E9%85%8D%E7%BD%AE) 一文中遇到了此问题：在 GitHub Actions 环境下 [wait-for-it](https://github.com/vishnubob/wait-for-it) 脚本虽然能正常执行但没有起到实际作用。此处没有找到太好的解决办法，通过增加一个等待的 action，在执行 `docker-compose up` 后强行等待一段时间，等服务都启动完成后再去执行集成测试。具体例子可见 [check.yml#L43-L46](https://github.com/AlphaHinex/seata-at-demo/blob/seata-at/.github/workflows/check.yml#L43-L46)。
