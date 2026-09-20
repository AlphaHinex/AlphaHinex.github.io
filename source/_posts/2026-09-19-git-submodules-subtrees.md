---
id: git-submodules-subtrees
title: "【译】使用子模块和子树管理 Git 项目"
description: "子模块和子树帮助你在多个仓库中管理子项目"
date: 2026.09.19 10:34
categories:
    - Git
tags: [Git]
keywords: Git, submodule, subtree, .gitmodules, .gittrees, git-subtree, git-submodule
cover: /contents/git-submodules-subtrees/browser_web_internet_website.png
---

- 原文地址：https://opensource.com/article/20/5/git-submodules-subtrees
- 原文作者：[Manaswini Das](https://opensource.com/users/manaswinidas)

---

![](https://alphahinex.github.io/contents/git-submodules-subtrees/browser_web_internet_website.png)

如果你从事开源开发，你可能使用过 Git 来管理源代码。你可能会遇到包含大量依赖和/或子项目的项目。你如何管理它们？

对于开源组织来说，为社区和产品实现单一来源的文档和依赖管理可能很棘手。文档和项目常常变得碎片化和冗余，这使它们难以维护。

## 需求

假设你想将一个项目作为子项目放在一个仓库中。传统方法只是将该项目复制到父仓库中。但是，如果你想在许多父仓库中使用同一个子项目呢？将子项目复制到每个父仓库中，并且每次更新时都必须在所有父仓库中进行更改，这是不可行的。这会在父仓库中产生冗余和不一致，并使子项目的更新和维护变得困难。

## Git 子模块和子树

如果你可以用一条命令将一个项目放入另一个项目呢？如果你可以将该项目作为子项目添加到任意数量的项目中，并随时推送更改呢？Git 为此提供了解决方案：Git 子模块和 Git 子树。这些工具旨在更模块化的层面上支持代码共享开发工作流，致力于弥合 Git 仓库的源代码管理（SCM）与其内部的子仓库之间的差距。

![长在桑树上的樱桃树](https://alphahinex.github.io/contents/git-submodules-subtrees/640px-bialbero_di_casorzo.jpg)

这是本文将要详细介绍的概念的一个真实场景。如果你已经熟悉树，这个模型将看起来像这样：

![带有子树的树](https://alphahinex.github.io/contents/git-submodules-subtrees/subtree_0.png)

## 什么是 Git 子模块？

Git 在其默认包中提供了子模块，使 Git 仓库能够嵌套在其他仓库中。确切地说，Git 子模块指向子仓库上的一个特定提交。以下是我的 [Docs-test](https://github.com/manaswinidas/Docs-test/) GitHub 仓库中 Git 子模块的样子：

![Git 子模块快照](https://alphahinex.github.io/contents/git-submodules-subtrees/git-submodules_github.png)

**folder@commitId** 格式表明该仓库是一个子模块，你可以直接点击该文件夹进入子仓库。名为 **.gitmodules** 的配置文件包含所有子模块仓库的详细信息。我的仓库的 **.gitmodules** 文件如下所示：

![.gitmodules 文件快照](https://alphahinex.github.io/contents/git-submodules-subtrees/gitmodules.png)

你可以使用以下命令在你的仓库中使用 Git 子模块。

### 克隆仓库并加载子模块

要克隆包含子模块的仓库：

```bash
$ git clone --recursive <URL to Git repo>
```

如果你已经克隆了一个仓库并想加载其子模块：

```bash
$ git submodule update --init
```

如果有嵌套的子模块：

```bash
$ git submodule update --init --recursive
```

### 下载子模块

按顺序下载子模块可能是一项繁琐的任务，因此 **clone** 和 **submodule update** 将支持 **--jobs** 或 **-j** 参数。

例如，要一次下载八个子模块，请使用：

```bash
$ git submodule update --init --recursive -j 8
$ git clone --recursive --jobs 8 <URL to Git repo>
```

### 拉取子模块

在运行或构建父仓库之前，你必须确保子依赖项是最新的。

要拉取子模块中的所有更改：

```bash
$ git submodule update --remote
```

### 创建包含子模块的仓库

要将子仓库添加到父仓库：

```bash
$ git submodule add <URL to Git repo>
```

要初始化一个现有的 Git 子模块：

```bash
$ git submodule init
```

### 更新子模块提交

如上所述，子模块是一个指向子仓库中特定提交的链接。如果你想更新子模块的提交，不用担心。你不需要明确指定最新的提交。你可以直接使用通用的子模块更新命令：

```bash
$ git submodule update
```

像平常一样添加并提交，以创建父仓库并将其推送到 GitHub。

### 从父仓库中删除子模块

仅仅手动删除子项目文件夹并不会从父仓库中移除子项目。要删除名为 **childmodule** 的子模块，请使用：

```bash
$ git rm -f childmodule
```

尽管 Git 子模块可能看起来易于使用，但对于初学者来说，找到使用它们的方法可能很困难。

## 什么是 Git 子树？

Git 子树在 Git 1.7.11 中引入，允许你将任意仓库的副本作为另一个仓库的子目录插入。它是 Git 项目注入和管理项目依赖的几种方式之一。它以常规提交的形式存储外部依赖。Git 子树提供了干净的集成点，因此更容易回滚。

如果你使用 [GitHub 提供的子树教程](https://help.github.com/en/github/using-git/about-git-subtree-merges) 来使用子树，当你添加子树时，你不会在本地看到 **.gittrees** 配置文件。这使得识别子树变得困难，因为子树看起来像普通文件夹，但它们是子仓库的副本。带有 **.gittrees** 配置文件的 Git 子树版本在默认的 Git 包中不可用，因此要获取带有 **.gittrees** 配置文件的 git-subtree，你必须从 Git 源代码仓库的 [/contrib/subtree 文件夹](https://github.com/git/git/tree/master/contrib/subtree)中下载 git-subtree。

你可以像克隆任何其他普通仓库一样克隆任何包含子树的仓库，但可能需要更长时间，因为子仓库的完整副本驻留在父仓库中。

你可以使用以下命令在你的仓库中使用 Git 子树。

### 向父仓库添加子树

要向父仓库添加新的子树，你首先需要 **remote add** 它，然后运行 **subtree add** 命令，如下所示：

```bash
$ git remote add remote-name <URL to Git repo>
$ git subtree add --prefix=folder/ remote-name subtree-branchname
```

这会将整个子项目的提交历史合并到父仓库中。

### 向子树推送更改和从子树拉取更改

```bash
$ git subtree push --prefix=folder/ remote-name subtree-branchname
```

或

```bash
$ git subtree pull --prefix=folder/ remote-name subtree-branchname
```

## 你应该使用哪个？

每个工具都有优点和缺点。以下是一些可以帮助你决定哪种最适合你的用例的特性。

- Git 子模块的仓库尺寸更小，因为它们只是指向子项目中特定提交的链接，而 Git 子树则容纳了整个子项目及其历史记录。
- Git 子模块需要在（检出环境的）服务器中可访问，但子树是去中心化的。
- Git 子模块主要用于基于组件的开发，而 Git 子树用于基于系统的开发。

Git 子树并不是 Git 子模块的直接替代品。有一些注意事项指导着它们各自的使用场景。如果你有一个自己拥有的外部仓库，并且可能会将代码推送回去，请使用 Git 子模块，因为它更容易推送。如果你有不太可能推送到的第三方代码，请使用 Git 子树，因为它更容易拉取。

尝试一下 Git 子树和子模块，并在评论中告诉我效果如何。
