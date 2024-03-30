---
id: git-commit-tree-browser
title: "Git Commit Tree Browser"
description: "安利一个小工具：Git 仓库 Commit 文件树查看器。"
date: 2024.03.31 10:34
categories:
    - Git
tags: [Git, Shell]
keywords: git, bash, tree, commit, browser, repo, terminal
cover: /contents/git-commit-tree-browser/cover.png
---

原文地址：https://wyiyi.github.io/amber/2024/04/01/git-commit-tree/

## 痛点

在`Git`项目中，代码的频繁迭代会使得追踪项目文件结构变化的过程异常艰难，尤其是历史 `commit` 中存在、当前最新版本中已经不存在的文件/文件夹。

为了解决这个问题，`Git Commit Tree Browser` 提供了一个高效的解决方案。

## 简介

[Git Commit Tree Browser](https://github.com/AlphaHinex/git-commit-tree-browser) 是基于`Bash`的脚本工具，通过为每个 `commit` 生成文件目录树，并配备交互式的浏览界面，可视化展示 `Git` 仓库各个 `commit` 状态下的文件树结构。

## 效果

![demo](/contents/git-commit-tree-browser/demo.gif)

## 功能特点

* 为指定 `Git` 仓库中每个 `commit` 生成文件目录树文件
* 提供终端交互界面，通过左右箭头键切换查看不同 `commit` 的文件目录树状态；按回车后激活跳转到指定 `commit` 模式，输入 `commit` ID（加文件扩展名 `.txt`）完成跳转

## 使用方法

### 前置条件

1. 工具使用 Bash 脚本实现，需可执行 Bash 脚本的终端环境（`Windows` 操作系统可在 `Git Bash` 中使用）
1. 工具依赖 `tree` 命令生成文件树结构，如终端中无法使用需提前安装（`Windows` 用户可以在 `Git Bash` 中安装 [Tree for Windows](https://gnuwin32.sourceforge.net/packages/tree.htm)）

### 执行 prepare.sh 脚本

执行 `prepare.sh` 脚本，传入 `Git` 仓库的路径作为参数：

```bash
$ git clone https://github.com/AlphaHinex/git-commit-tree-browser
$ cd git-commit-tree-browser
$ ./prepare.sh /path/to/your/git/repo
```

脚本将遍历指定 Git 仓库的所有 `commit`，并为每个 `commit` 在当前路径生成文件目录树文本文件 `<commit_id>.txt`。

> 当前生成目录树使用的命令是 [tree -N -d -L 3](https://github.com/AlphaHinex/git-commit-tree-browser/blob/main/prepare.sh#L18)，即只显示文件夹，最多显示三级路径。可根据实际需要进行调整。

### 执行 browser.sh 脚本

执行 `browser.sh` 脚本，开始按 `commit` 从老到新的顺序进行文件目录树浏览：

```bash
$ ./browser.sh
```

终端中将显示第一个`commit`的文件目录树，如：

```bash
File: 20df792.txt
.
|-- bronze
|   |-- gradle
|   |   `-- wrapper
|   `-- src
|       |-- main
|       `-- test
`-- git-commit-tree-browser

7 directories
20df792
Press left/right arrow to navigate, or Enter to jump to a file:
```

可以使用以下方式导航：

* 使用左右箭头键在不同的 `commit` 之间切换
* 按 `Enter` 键，然后输入 `<commit_id>.txt` 文件名，直接跳转到特定的`commit`

**小工具会继续丰富功能，请期待~~~**