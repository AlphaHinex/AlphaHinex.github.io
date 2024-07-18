---
id: gitlab-mr-merge-ref
title: "GitLab Merge Request 的 merge 引用"
description: "当在 GitLab 中创建一个 MR 时，remote 仓库中会自动创建 refs/merge-requests/$iid/head 和 refs/merge-requests/$iid/merge 两个引用"
date: 2024.07.21 10:34
categories:
    - Git
tags: [GitLab, Git]
keywords: refs/merge-requests/$iid/merge, refs/merge-requests/$iid/head, GitLab MR, GitLab Merge Request
cover: /contents/covers/gitlab-mr-merge-ref.png
---


`merge` 引用及用途
================

[10.3 Git 内部原理 - Git 引用](https://git-scm.com/book/zh/v2/Git-内部原理-Git-引用) 及 [10.5 Git 内部原理 - 引用规范](https://git-scm.com/book/zh/v2/Git-内部原理-引用规范) 中介绍了 Git 的引用（references，或简写为 refs）及其规范，可在本地 Git 仓库的 `.git/refs` 路径下查看已经 fetch 到本地的引用文件。

当我们在 GitLab 中创建一个 MergeRequest 时，remote 仓库中会自动创建 `refs/merge-requests/$iid/head` 和 `refs/merge-requests/$iid/merge` 两个引用，分别对应 MR 源分支内容，以及 **将 MR 源分支内容合并至目标分支后的内容**。

当我们对这个 `merge` 引用进行持续集成时，就可以实现未雨绸缪的效果：

**即使尚未合并 MR，持续集成检查和验证的，却相当于是将 MR 合并至目标分支之后的效果。**

这样在出现问题时，只需继续在 MR 中进行修改即可，而不是将已经合并至目标分支的内容回滚之后再重新处理。


本地获取 `merge` 引用
===================

增加 `fetch` 引用规范
-------------------

`.git/config` 配置文件中可以指定多个用于获取操作的引用规范。

添加 `merge` 引用的方式为增加 `+refs/merge-requests/*/merge:refs/remotes/origin/merge-requests/*/merge`，如：

```ini
[remote "origin"]
    url = https://gitlab.com/AlphaHinex/merge-refs-test.git
    fetch = +refs/heads/*:refs/remotes/origin/*
    fetch = +refs/merge-requests/*/merge:refs/remotes/origin/merge-requests/*/merge
```

在 GitLab 上创建 MergeRequest 之后，可使用 `fetch` 命令获取 `merge` 引用，如：

```bash
$ git fetch origin
remote: Enumerating objects: 1, done.
remote: Counting objects: 100% (1/1), done.
remote: Total 1 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0)
展开对象中: 100% (1/1), 248 字节 | 248.00 KiB/s, 完成.
来自 https://gitlab.com/AlphaHinex/merge-refs-test
 * [新引用]          refs/merge-requests/1/merge -> origin/merge-requests/1/merge
```

`show-ref` 查看引用列表
---------------------

之后可通过 `show-ref` 查看引用及对应的 commit id：

```bash
$ git show-ref
dcaeb64e20196eda19b7f71b86287566d987ea56 refs/heads/main
8f8976a512437c13784586460556dffeef53c645 refs/heads/mr
dcaeb64e20196eda19b7f71b86287566d987ea56 refs/remotes/origin/HEAD
dcaeb64e20196eda19b7f71b86287566d987ea56 refs/remotes/origin/main
f03da17f11a905fcc4766c97f05de2fa8c78ecda refs/remotes/origin/merge-requests/1/merge
8f8976a512437c13784586460556dffeef53c645 refs/remotes/origin/mr
```

也可以将 `fetch` 配置为 `+refs/merge-requests/*:refs/remotes/origin/merge-requests/*`，同时获得 MR 的 `head` 和 `merge` 分支：

```bash
$ git fetch
来自 https://gitlab.com/AlphaHinex/merge-refs-test
 * [新引用]          refs/merge-requests/1/head -> origin/merge-requests/1/head
$ git show-ref
dcaeb64e20196eda19b7f71b86287566d987ea56 refs/heads/main
8f8976a512437c13784586460556dffeef53c645 refs/heads/mr
dcaeb64e20196eda19b7f71b86287566d987ea56 refs/remotes/origin/HEAD
dcaeb64e20196eda19b7f71b86287566d987ea56 refs/remotes/origin/main
8f8976a512437c13784586460556dffeef53c645 refs/remotes/origin/merge-requests/1/head
f03da17f11a905fcc4766c97f05de2fa8c78ecda refs/remotes/origin/merge-requests/1/merge
8f8976a512437c13784586460556dffeef53c645 refs/remotes/origin/mr
```

可以看到，共有三个不同的 commit id：

1. `dcaeb64e20196eda19b7f71b86287566d987ea56`：对应本地及远程的 `main` 分支及 `HEAD` 引用
1. `8f8976a512437c13784586460556dffeef53c645`：对应本地及远程的 `mr` 分支，以及 `merge-requests/1/head` 引用
1. `f03da17f11a905fcc4766c97f05de2fa8c78ecda`：对应远程的 `merge-requests/1/merge` 引用

![](/contents/covers/gitlab-mr-merge-ref.png)

> 左侧未显示完整的即为 `merge-requests/1/merge` 引用。

从本地和 GitLab 上的 `main` 分支及 `mr` 分支提交记录里可以找到前两个 commit id，而第三个 commit id 则是 GitLab 在远程仓库的 `merge-requests/1/merge` 分支上将 `mr` 分支合并至目标分支 `main` 自动创建的 commit 对应的 id。


为 `merge` 引用创建分支
=====================

```bash
$ git branch -a
* main
  mr
  remotes/origin/HEAD -> origin/main
  remotes/origin/main
  remotes/origin/merge-requests/1/head
  remotes/origin/merge-requests/1/merge
  remotes/origin/mr
```

```bash
$ git checkout merge-requests/1/merge
分支 'merge-requests/1/merge' 设置为跟踪来自 'origin' 的远程分支 'merge-requests/1/merge'。
切换到一个新分支 'merge-requests/1/merge'
```

```bash
$ git branch -a
  main
* merge-requests/1/merge
  mr
  remotes/origin/HEAD -> origin/main
  remotes/origin/main
  remotes/origin/merge-requests/1/head
  remotes/origin/merge-requests/1/merge
  remotes/origin/mr
```

```bash
$ git status
位于分支 merge-requests/1/merge
您的分支与上游分支 'origin/merge-requests/1/merge' 一致。

无文件要提交，干净的工作区
```

此时即可直接在本地的 `merge-requests/1/merge` 分支上审查 MR 合并后的代码状态。


`merge` 引用行为验证
==================

> 以下内容在 GitLab Community Edition v16.8.1 版本，及在线版 GitLab Enterprise Edition 17.3.0-pre [453542d17ca](https://gitlab.com/gitlab-org/gitlab/-/commits/453542d17ca) 中验证。

创建 MR 之前，是否会在远程库中出现 head/merge 分支
---------------------------------------------

不会。

在 MR 分支上提交新 commit 时，merge 分支内容是否会同步变化？
-----------------------------------------------------

会。但可能稍微有个延迟。

```bash
$ git checkout mr
切换到分支 'mr'
您的分支与上游分支 'origin/mr' 一致。
```

```bash
$ touch new-file-in-mr-branch
$ git add .
$ git commit -am "New commit in mr branch"
[mr 3436570] New commit in mr branch
 1 file changed, 0 insertions(+), 0 deletions(-)
 create mode 100644 new-file-in-mr-branch
$ git push origin mr
枚举对象中: 3, 完成.
对象计数中: 100% (3/3), 完成.
使用 8 个线程进行压缩
压缩对象中: 100% (2/2), 完成.
写入对象中: 100% (2/2), 306 字节 | 306.00 KiB/s, 完成.
总共 2（差异 0），复用 0（差异 0），包复用 0
remote:
remote: View merge request for mr:
remote:   https://gitlab.com/AlphaHinex/merge-refs-test/-/merge_requests/1
remote:
To https://gitlab.com/AlphaHinex/merge-refs-test.git
   8f8976a..3436570  mr -> mr
```

拉取远程库的 `merge` 引用：

```bash
$ git fetch origin
来自 https://gitlab.com/AlphaHinex/merge-refs-test
   8f8976a..3436570  refs/merge-requests/1/head -> origin/merge-requests/1/head
```

> 如果拉取时没有 merge 引用的变化，可稍等一会之后再试：
> ```bash
> $ git fetch
> remote: Enumerating objects: 1, done.
> remote: Counting objects: 100% (1/1), done.
> remote: Total 1 (delta 0), reused 0 (delta 0), pack-reused 0 (from 0)
> 展开对象中: 100% (1/1), 248 字节 | 248.00 KiB/s, 完成.
> 来自 https://gitlab.com/AlphaHinex/merge-refs-test
>  + f03da17...b20a111 refs/merge-requests/1/merge -> origin/merge-requests/1/merge  (强制更新)
> ```

在目标分支上提交新 commit 时，merge 分支内容是否会同步变化？
----------------------------------------------------

也会，同样可能有个延迟。

```bash
$ git checkout main
```

```bash
$ touch new-file-in-main-branch
$ git add .
$ git commit -am "New commit in main branch"
[main 8a98bc0] New commit in main branch
 1 file changed, 0 insertions(+), 0 deletions(-)
 create mode 100644 new-file-in-main-branch
$ git push origin main
枚举对象中: 4, 完成.
对象计数中: 100% (4/4), 完成.
使用 8 个线程进行压缩
压缩对象中: 100% (2/2), 完成.
写入对象中: 100% (3/3), 299 字节 | 299.00 KiB/s, 完成.
总共 3（差异 0），复用 0（差异 0），包复用 0
To https://gitlab.com/AlphaHinex/merge-refs-test.git
   dcaeb64..8a98bc0  main -> main
```

```bash
$ git fetch origin
remote: Enumerating objects: 4, done.
remote: Counting objects: 100% (4/4), done.
remote: Compressing objects: 100% (2/2), done.
remote: Total 2 (delta 1), reused 0 (delta 0), pack-reused 0 (from 0)
展开对象中: 100% (2/2), 293 字节 | 146.00 KiB/s, 完成.
来自 https://gitlab.com/AlphaHinex/merge-refs-test
 + b20a111...2978ae6 refs/merge-requests/1/merge -> origin/merge-requests/1/merge  (强制更新)
```

MR 分支新 commit 与目标分支新 commit 存在冲突时，merge 分支内容是否会同步变化？
------------------------------------------------------------------------

此时 merge 分支不再同步变化，后续 MR 分支上的新提交 commit 也不会同步到 merge 分支上，需要处理冲突之后，才能恢复同步。

MR 关闭之后，是否还会同步更新 merge 分支内容？
----------------------------------------

不会了，重新开启 MR 后会继续同步更新。


参考资料
=======

1. [[Commit Status Publisher] Allow refs/merge-requests/* in gitlab support](https://youtrack.jetbrains.com/issue/TW-45099/Commit-Status-Publisher-Allow-refs-merge-requests-in-gitlab-support)
1. [TeamCity Trigger on Pull Request vs Trigger on Merge](https://stackoverflow.com/questions/38619518/teamcity-trigger-on-pull-request-vs-trigger-on-merge/49388182#49388182)
1. [6.3 GitHub - Maintaining a Project](https://git-scm.com/book/id/v2/GitHub-Maintaining-a-Project)
1. [Git refs merge vs head in pull request](https://stackoverflow.com/questions/63594658/git-refs-merge-vs-head-in-pull-request)
1. [Create merge refs for MRs (merge and squash methods)](https://gitlab.com/gitlab-org/gitlab-foss/-/issues/47110)
1. [Consider using the merge URL on PR builds](https://github.com/readthedocs/readthedocs.org/issues/6958)
1. [Difference of refs/pull-requests/<ID>/merge and refs/pull-requests/<ID>/from](https://community.atlassian.com/t5/Bitbucket-questions/Difference-of-refs-pull-requests-lt-ID-gt-merge-and-refs-pull/qaq-p/772142)
1. [Use merge request HEAD ref for detached merge request pipelines](https://gitlab.com/gitlab-org/gitlab-foss/-/merge_requests/25504)
1. [Able to push to /ref/merge-requests/*/head](https://gitlab.com/gitlab-org/gitlab/-/issues/215432)
1. [Merge requests API](https://docs.gitlab.com/ee/api/merge_requests.html)
1. [Gitlab 中文文档 - Merge requests API](https://www.bookstack.cn/read/gitlab-doc-zh/docs-337.md)
1. [Merge request pipelines](https://docs.gitlab.com/ee/ci/pipelines/merge_request_pipelines.html)
1. [Using Git refs to check out GitLab Merge Requests, from your local repo](https://www.jvt.me/posts/2019/01/19/git-ref-gitlab-merge-requests/)
