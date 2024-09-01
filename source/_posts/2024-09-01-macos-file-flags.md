---
id: macos-file-flags
title: "【译】如何使用文件标志修改 macOS 中的文件行为"
description: "macOS 中可以使用文件标志（flags）来限制文件被修改的方式。可以使用 `chflags` 来更改标志，`ls` 来查看标志"
date: 2024.09.01 10:34
categories:
    - Mac
tags: [Mac, Linux]
keywords: flags, macOS, file, chflags, ls, hidden, nodump, sappnd, schg, uappnd, uchg, hidden, opaque, immutable, append, chattr, lsattr, arch
cover: /contents/macos-file-flags/flags.webp
---

![flags](/contents/macos-file-flags/flags.webp)

- 原文地址：https://www.maketecheasier.com/use-file-flags-modify-file-behavior-macos/
- 原文作者：[Alexander Fox](https://www.maketecheasier.com/author/alexfox/)

在 macOS 中，可以使用文件标志（flags）来限制文件被修改的方式。它们与文件权限不同，并且与 `chown` 和 `chmod` 等命令并行运行。您将使用 `chflags` 来更改标志，以及使用 `ls` 来查看标志。Unix 运行一个类似的系统，但是选项更多，称为“属性”，而不是标志。


# 在 macOS 上查看已设置的标志

在终端中，您可以使用 `ls` 命令来查看任何已设置的标志。

```bash
$ ls -lO 
drwx------@ 88  alexander staff hidden 2992 Jan 25 14:01 Library
```

如果文件或文件夹没有设置标志，则会显示一个短横线。

```bash
$ ls -lO ~/Library/Caches
drwx------+ 234 alexander staff   -    7956 Jan 25 13:03 Caches
```

已设置的标志可以使用它们的相反形式来删除，就如下面描述的那样。


# 在 macOS 上设置和清除标志

![set flag](/contents/macos-file-flags/set-flag.webp)

文件标志通常以问题形式出现。因为它们会设置额外的权限，且很容易被忽略。您是否发现自己有一个无法删除的文件，无论您的用户权限有多高？您可能需要清除一个或两个标志。

可以在 macOS 上设置的标志如下所示。这是可用选项的完整列表，以及它们的功能说明。大多数标志只能由文件的所有者或超级用户设置；`sappnd` 和 `schg` 只能由超级用户设置，因为它们是系统级标志。只有隐藏标志可以在不升级权限的情况下设置。


## 在 macOS 上设置标志

在 macOS 上设置标志时，请使用以下命令。递归标志 `-R` 可用于目录级操作：

```bash
$ sudo chflags -R [标志] /usr/bin/local
$ sudo chflags [标志] /usr/bin/local/mnt.sh
$ chflags -R hidden ~/Desktop
```

将设置适当的标志。例如，以下命令将设置 nodump 标志：

```bash
sudo chflags nodump /usr/bin/local/tty.sh
```

每个 chflags 命令只能设置或删除一个标志。

- **opaque** 将文件夹设置为在通过[联合挂载](https://en.wikipedia.org/wiki/Union_mount)查看时呈现为不透明的方式，这是一种同时查看多个目录的老式方法。
- **nodump** 防止在使用 `dump` 命令备份系统时转储文件或文件夹。
- **sappnd, sappend** 设置系统追加标志，允许向文件添加内容，但不允许修改或删除。要删除此标志，需要进入单用户模式。
- **schg, schange, simmutable** 设置系统不可变标志，阻止任何权限级别的用户对文件进行更改。要删除此标志，需要进入单用户模式。
- **uappnd, uappend** 设置用户追加标志。文件所有者可以设置此标志，并且可以在不升级权限的情况下取消设置。由于它锁定文件，在较低的安全级别下使用 `sappnd` 或 `schg`，它被更频繁地使用。
- **uchg, uchange, uimmutable** 设置用户不可变标志，它与系统不可变标志的关系，跟 `uappnd` 标志与 `sappnd` 的关系相同。
- **hidden** 设置隐藏标志。这将在 Finder GUI 和 ls 命令中隐藏该项。

> 译注：除上述选项外，还有 **arch, archived** 用于设置存档标志（仅超级用户）。完整选项列表可见 `man chflags`。


## 在 macOS 上清除标志

要清除给定的标志，请设置其相反标志。在大多数情况下，这意味着在命令前加上“no”。对于 nodump，使用 dump 标志来清除，如下所示：

```bash
sudo chflags dump /usr/bin/local/oty.sh
```

更多标准选项可以使用“no”前缀进行反转，如下所示：

```bash
sudo chflags nosappnd /usr/bin/local/oty.sh
```

与 chmod 一样，递归标志也可用：

```bash
chflags -R nohidden ~/Desktop
```

清除标志后，您将可以按预期更改文件的所有权和权限。


# 在 Unix 上使用属性

![attributes](/contents/macos-file-flags/attributes.webp)

Unix 在后台运行类似的系统，但是使用不同的命令处理。在最流行的 Linux 平台上，您将使用 `chattr` 和 `lsattr` 来更改和查看“属性”，这也是文件标志在大多数其他 Unix 系统中的体现。

可以使用 `lsattr` 查看属性：

```bash
lsattr /path/to/file.txt
```

更改属性依赖于一组首字母缩写，并在 [chattr man 页面](https://linux.die.net/man/1/chattr) 中列出：

> “The letters ‘acdeijstuADST’ select the new attributes for the files: append only (a), compressed (c), no dump (d), extent format (e), immutable (i), data journalling (j), secure deletion (s), no tail-merging (t), undeletable (u), no atime updates (A), synchronous directory updates (D), synchronous updates (S), and top of directory hierarchy (T).”

> “字母 ‘acdeijstuADST’ 选择文件的新属性：追加（a），压缩（c），不转储（d），扩展格式（e），不可变（i），数据日志（j），安全删除（s），不合并尾部（t），不可删除（u），不更新访问时间（A），同步目录更新（D），同步更新（S）和目录层次结构顶部（T）。”

命令如下所示：

```bash
chattr +s /file/name.txt
```

这将为指定路径设置安全删除属性。


# 总结

在限制谁可以更改文件时，标志非常有用。通过锁定文件，您可以在文件系统级别防止篡改或意外编辑。除非升级为 root 或文件所有者，否则无法更改这些权限，因此它们具有适度的安全性。
