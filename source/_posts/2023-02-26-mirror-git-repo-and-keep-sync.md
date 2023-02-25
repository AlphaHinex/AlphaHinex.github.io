---
id: mirror-git-repo-and-keep-sync
title: "镜像 Git 仓库，并保持同步"
description: "How to mirror a git repo and keep sync"
date: 2023.02.26 10:26
categories:
    - Git
tags: [Git]
keywords: git, mirror, prune, bare
cover: /contents/covers/mirror-git-repo-and-keep-sync.png
---

有 A、B 两个 git 仓库，想实现类似主从数据库的效果：
- A 库作为主库提交 Commit 记录
- B 库作为备份库，同步 A 库内容，并在不影响 A 库的情况下提供读取、分析等操作

假设
- A 库地址为 http://git/repo/source.git
- B 库地址为：http://another/git/sourcemirror.git

# TL;DR

全量镜像，执行一次：

```bash
rm -rf source.git
git clone --mirror http://git/repo/source.git
cd source.git
git remote add target http://another/git/sourcemirror.git
git push --mirror target 
```

增量同步，定时执行：

```bash
git --git-dir=/path/to/source.git fetch --prune
git --git-dir=/path/to/source.git push --mirror target
```

# 实现原理

实现原理如下图：

![mirror-then-sync](/contents/covers/mirror-git-repo-and-keep-sync.png)

大致分为三个步骤：
1. 全量同步
1. 增量更新
1. 同步变化

其中 2/3 步可以放在一起定时执行，起到保持同步的作用，并避免了每次同步全量更新，提高同步效率。

## Step 1 克隆镜像仓库

在进行仓库的全量镜像时，我们不仅希望同步某些特定分支的提交记录，而是想完整的镜像源仓库的所有分支、tag 等信息。

这时，通常用来更新、提交代码的 clone、pull、push 操作就不太适合了。

Git 中有一个裸仓库（bare Git reposiotry）的概念，`git-clone` 的 Manual 中对此有如下描述：

```manual
--bare
    Make a bare Git repository. That is, instead of creating
    <directory> and placing the administrative files in
    <directory>/.git, make the <directory> itself the $GIT_DIR. This
    obviously implies the --no-checkout because there is nowhere to
    check out the working tree. Also the branch heads at the remote are
    copied directly to corresponding local branch heads, without
    mapping them to refs/remotes/origin/. When this option is used,
    neither remote-tracking branches nor the related configuration
    variables are created.
```

即在添加了 `--bare` 参数进行 `git clone` 时，我们得到的不再是一个包含了所有已提交文件最新版本的工作空间，而是原本存在于工作空间 `.git` 路径下的内容本身。

### git clone

举个例子，在 `git clone --mirror http://git/repo/source.git` 之后，我们得到的是一个名为 `source` 的文件夹，路径下包括如下内容：

```bash
➜  source git:(master) tree -a -L 2
.
├── .git
│   ├── COMMIT_EDITMSG
│   ├── HEAD
│   ├── ORIG_HEAD
│   ├── config
│   ├── description
│   ├── hooks
│   ├── index
│   ├── info
│   ├── logs
│   ├── objects
│   ├── packed-refs
│   └── refs
├── README.md
├── Test.css
├── Test.groovy
├── Test.java
├── Test.js
├── Test.less
├── Test.scss
├── Test.vue
├── test.properties
└── test.yaml

6 directories, 17 files
```

### git clone --bare

`git clone --bare http://git/repo/source.git` 之后，我们得到的是一个名为 `source.git` 的文件夹，路径下包括如下内容：

```bash
➜  source.git git:(master) tree -L 1
.
├── FETCH_HEAD
├── HEAD
├── config
├── description
├── hooks
├── info
├── objects
├── packed-refs
└── refs

4 directories, 5 files
```

可以看到，克隆相同的仓库，裸仓库中不包含我们提交的文件，只包含 Git 自己生成的文件。

### `--mirror` vs `--bare`

与 `--bare` 参数类似，`git-clone` 还提供了另一个参数 —— `--mirror`：

```manual
--mirror
    Set up a mirror of the source repository. This implies --bare.
    Compared to --bare, --mirror not only maps local branches of the
    source to local branches of the target, it maps all refs (including
    remote-tracking branches, notes etc.) and sets up a refspec
    configuration such that all these refs are overwritten by a git
    remote update in the target repository.
```

使用了 `--mirror` 参数，相当于同时指定了 `--bare`，也会得到类似上面 `$GIT_DIR` 的目录结构。

与 `--bare` 不同的是，通过 `--mirror` 参数克隆出来的裸仓库，是可以后续增量更新的。

**所以如果只希望进行一次性的仓库迁移，使用哪个参数都可以；如果希望持续更新，需要使用 `--mirror`。**

## Step 2 同步源仓库并进行修剪

### 同步

裸仓库的更新，与普通 git 仓库的更新也有区别。

通常我们使用 git pull 拉取最新代码，而 pull 操作相当于先执行了 fetch 操作，再接着执行 merge。

裸仓库中因为没有工作目录，没有办法执行 merge 操作，所以可以单独使用 fetch 进行更新，或使用 `--mirror` 参数文档中提到的 `git remote udpate` 命令更新。

### 修剪

同步时我们不仅希望同步增加的内容，也希望同步源仓库中减少的内容（如分支、tag等），这时需要为更新命令增加 `--prune` 参数，以修剪已不存在的内容。

```manual
-p, --prune
    Before fetching, remove any remote-tracking references that no
    longer exist on the remote. Tags are not subject to pruning if they
    are fetched only because of the default tag auto-following or due
    to a --tags option. However, if tags are fetched due to an explicit
    refspec (either on the command line or in the remote configuration,
    for example if the remote was cloned with the --mirror option),
    then they are also subject to pruning. Supplying --prune-tags is a
    shorthand for providing the tag refspec.

    See the PRUNING section below for more details.
```

### `--git-dir`

同步操作会定时执行，为方便计划任务执行脚本，可在命令中指定 `--git-dir` 参数，设定 git 仓库路径，方便脚本在任意位置执行。

```manual
--git-dir=<path>
    Set the path to the repository. This can also be controlled by
    setting the GIT_DIR environment variable. It can be an absolute
    path or relative path to current working directory.
```

### 小结

同步并修剪，可使用下面任一方式执行：

```bash
$ git --git-dir=/path/to/source.git fetch --prune
```

或

```bash
$ git --git-dir=/path/to/source.git remote update origin --prune
```

## Step 3 推送变更

克隆镜像仓库，或更新变更之后，可以通过 push 命令将内容推送至 B 仓库。在镜像仓库内执行 push 时，相当于默认指定了 `--mirror` 参数：

```manual
--mirror
    Instead of naming each ref to push, specifies that all refs under
    refs/ (which includes but is not limited to refs/heads/,
    refs/remotes/, and refs/tags/) be mirrored to the remote
    repository. Newly created local refs will be pushed to the remote
    end, locally updated refs will be force updated on the remote end,
    and deleted refs will be removed from the remote end. This is the
    default if the configuration option remote.<remote>.mirror is set.
```

故推送变更可使用

```bash
$ git --git-dir=/path/to/source.git push target
```

或

```bash
$ git --git-dir=/path/to/source.git push --mirror target
```

> 注意：指定了 `--mirror` 参数的推送相当于强制推送，即使目标仓库中原本存在一些与源库不一致的内容，也会将两个仓库的内容同步为一致的。 如果有分支被保护不允许强制提交，推送可能会失败。需要临时允许强制提交，待完成同步后，再禁止强制提交即可。