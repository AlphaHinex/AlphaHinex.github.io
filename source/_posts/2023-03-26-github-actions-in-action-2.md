---
id: github-actions-in-action-2
title: "GitHub Actions 再战"
description: "持续集成环境常用功能的 GitHub Actions 实现"
date: 2023.03.26 10:26
categories:
    - DevOps
tags: [GitHub, CI]
keywords: GitHub, GitHub Actions, workflow, CI, automation, softprops/action-gh-release, codeball.ai
cover: /contents/covers/github-actions-in-action.png
---

接续 [GitHub Actions 实战](https://alphahinex.github.io/2020/03/27/github-actions-in-action/) ，继续介绍一些持续集成环境常用功能的实现方式：

## CD

构建命令中，可能有切换路径的需要。

每次使用 [jobs.<job_id>.steps[*].run](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idstepsrun) 的 `run` 关键字时，会在 runner 环境中使用一个新的进程和 shell。所以当需要切换路径时，可以通过如下三种方式：

1. 单行命令：
    ```yml
    - name: Install Dependencies
    - run: cd themes/obsidian && npm install
    - run: npm install hexo-cli -g
    ```
1. [多行命令](https://code-maven.com/slides/github-ci/change-directory-in-github-actions)：
    ```yml
    - name: Experiment
      run: |
        pwd             # /home/runner/work/try/try
        mkdir hello
        cd hello
        pwd             # /home/runner/work/try/try/hello
    ```
1. `working-directory` 关键字：
    ```yml
    - name: Clean temp directory
      run: rm -rf *
      working-directory: ./temp
    ```

> 注意上面 yaml 中声明多行字符串的 `|` 语法，更多内容可见 https://yaml-multiline.info/ 。

## push to origin

构建时如果需要使用 git 命令，如进行 commit 并 push，可在 [actions/checkout](https://github.com/actions/checkout) 中直接使用。

如 [使用内置的 token 推送 commit](https://github.com/actions/checkout#push-a-commit-using-the-built-in-token)：

```yml
on: push
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: |
          date > generated.txt
          git config user.name github-actions
          git config user.email github-actions@github.com
          git add .
          git commit -m "generated"
          git push
```

如果需要向其他仓库推送，可参照 [下例](https://github.com/AlphaHinex/AlphaHinex.github.io/blob/develop/.github/workflows/deploy.yml)，使用 [${{ secrets.GITHUB_TOKEN }}]() 或 [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) 推送：

```yml
- uses: actions/checkout@v3
  run: |
    cd ./public
    git init
    git config user.name "Alpha Hinex"
    git config user.email "AlphaHinex@gmail.com"
    git add .
    git commit -m "Update docs"
    git push --force "https://AlphaHinex:${{ secrets.GITHUB_TOKEN }}@github.com/AlphaHinex/AlphaHinex.github.io" master:master
```

## 自动创建 GitHub Release

当向 GitHub 推送一个 tag 之后，可以根据 tag 创建 Release，并在 Release 中填写发布说明以及上传此版本对应的制品，如：https://github.com/AlphaHinex/go-toolkit/releases

![release](/contents/github-actions-in-action-2/release.png)

这些都可以通过 [softprops/action-gh-release](https://github.com/softprops/action-gh-release) 来自动完成。

### 创建 Release

```yml
name: Main

on:
  push:
    tags:
      - "v*.*.*"

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      - name: Release
        uses: softprops/action-gh-release@v1
```

### 上传制品

使用 `with.files` 向 release 中上传制品，支持单行、多行语法，以及通配符，如：

```yml
name: Main

on: push

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      - name: Build
        run: echo ${{ github.sha }} > Release.txt
      - name: Test
        run: cat Release.txt
      - name: Release
        uses: softprops/action-gh-release@v1
        if: startsWith(github.ref, 'refs/tags/')
        with:
          files: |
            Release.txt
            LICENSE
            build/*
```

### 自动生成 release notes

GitHub 提供了 [自动生成 Release Notes](https://docs.github.com/en/repositories/releasing-projects-on-github/automatically-generated-release-notes) 的能力，在 actions 中可以利用：

```yml
- name: Release
  uses: softprops/action-gh-release@v1
  with:
    generate_release_notes: true
```

在 `step.with` 中可使用的完整参数列表可见：https://github.com/softprops/action-gh-release#inputs

## AI Code Review

[sturdy-dev/codeball-action@v2](https://github.com/sturdy-dev/codeball-action) 可以使用 [Codeball](https://codeball.ai/) 对 Pull Request 进行 AI 代码审查，并给出评审结果，如：https://github.com/AlphaHinex/go-toolkit/pull/3

![review](/contents/github-actions-in-action-2/review.png)

评审通过可以评论 `LGTM`（Look Good To Me）或给 PR 打 label；评审不通过时，可以打 label 或让检查 job 失败，虽然有给改进建议的参数，但目前并不能给出具体的有效评审意见。

```yml
name: Codeball

on:
  pull_request: {}
  pull_request_review_comment:
    types: [created, edited]

jobs:
  codeball_job:
    runs-on: ubuntu-latest
    name: Codeball
    steps:
      # Run Codeball on all new Pull Requests and Review Comments! 🚀
      # For customizations and more documentation, see https://github.com/sturdy-dev/codeball-action
      # For all configuration options see https://github.com/sturdy-dev/codeball-action/blob/v2/action.yml
      - name: Codeball
        uses: sturdy-dev/codeball-action@v2
        with:
          approvePullRequests: "true"
          labelPullRequestsWhenApproved: "false"
          labelPullRequestsWhenReviewNeeded: "true"
          failJobsWhenReviewNeeded: "true"
          codeSuggestionsFromComments: "true"
```

完成参数可见 https://github.com/sturdy-dev/codeball-action/blob/v2/action.yml