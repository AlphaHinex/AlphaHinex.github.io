---
id: give-mac-rm-a-chance
title: "给 Mac 上一个保险"
description: "给 rm 一个后悔的机会"
date: 2024.05.26 10:26
categories:
    - Mac
tags: [Mac]
keywords: macOS, Mac, rm, trash, brew
cover: /contents/covers/give-mac-rm-a-chance.png
---

如果你体会过在 Mac 上手残 `rm -f` 了一个重要的文件的痛苦，可以试试 [trash](http://hasseg.org/trash/)。

TL;DR
=====

安装 `trash` 命令：

```bash
brew install trash
```

然后将下面的命令添加到 `~/.bashrc` 或 `~/.zshrc` 文件中：

```bash
alias rm='/usr/local/bin/trash -F'
```

这样，以后使用 `rm` 命令删除文件时，文件会被移动到回收站（并且可以在回收站使用“放回原处”功能），而不是直接删除。


trash
=====

[trash](https://github.com/ali-rantakari/trash) 是一个 MIT 协议的开源命令行工具，可将文件或文件夹移至回收站。

并且会静默接受所有 `rm` 命令的参数，可以直接替换 `rm` 命令，相当于给 `rm` 命令加了一个保险。

安装
----

通过 [Homebrew](https://brew.sh/) 安装：

```bash
brew install trash
```

或源码安装：

```bash
$ git clone https://github.com/ali-rantakari/trash.git
$ cd trash
$ make
$ cp trash /usr/local/bin/
$ make docs
$ cp trash.1 /usr/local/share/man/man1/
```

支持放回原处
----------

`trash` 命令与 `-F` 参数共同使用时，通过 `trash` 移动至回收站的文件，可以在回收站中使用“放回原处”功能。

> 未添加 `-F` 参数时，只会将文件移动至回收站，并不能将文件恢复至原处。

其他功能
-------

`trash` 命令还支持以下功能：

- `-l`：列出回收站中内容（同时使用 `-v` 参数时，显示额外信息）
- `-e`：清空回收站（需确认）
- `-y`：无需确认，**立即永久清空回收站**


相关链接
=======

- [Trash files from the OS X command line](http://hasseg.org/blog/post/406/trash-files-from-the-os-x-command-line/)：`trash` 工具的作者博客，介绍了 `trash` 的由来。
- [https://github.com/LaiJingli/rmtrash](https://github.com/LaiJingli/rmtrash)：`rmtrash` 是一个类似的脚本工具，支持 Linux 和 Mac 环境。并未直接使用 Mac 中的回收站，而是在用户目录下创建了一个 `.rmtrash` 隐藏文件夹，将 `rm` 命令替换成使用此脚本后，删除的文件会被移动到 `.rmtrash` 文件夹中。