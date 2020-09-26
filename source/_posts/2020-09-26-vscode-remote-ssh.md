---
id: vscode-remote-ssh
title: "VS Code Remote - SSH 插件"
description: "vi 是不错，但切换路径很烦"
date: 2020.09.26 10:34
categories:
    - IDE
tags: [VS Code]
keywords: IDE, VS Code, Visual Studio Code, Plugin, Remote - SSH, Visual Studio Code Remote Development, Remote - Containers, Remote - WSL
cover: /contents/vscode/cover.png
---

在需要到服务器上编辑文件的时候，如果遇到有较多文件分散在不同目录时，使用终端工具其实挺繁琐的。

在 VS Code 中，有一个插件 [Remote - SSH](https://github.com/Microsoft/vscode-remote-release)，可以配置好 SSH 连接后，打开远程主机上的任意路径，之后就像使用 VS Code 操作本地文件夹一样。

官方对此插件的简介为：

> Open any folder on a remote machine using SSH and take advantage of VS Code's full feature set.

但实际使用时，有些场景跟操作本地文件还是有点区别的，比如全文检索时，通过 Remote - SSH 插件只能搜索已经打开过的文件。

不过总体来说还是很方便的。

![ssh readme](/contents/vscode/ssh-readme.gif)

在 Visual Studio Code Remote Development 中，除 Remote - SSH 之外，还提供了 Remote - Containers 和 Remote - WSL，分别用来使用 VS Code 直接操作 docker 容器或 WSL (Windows Subsystem for Linux) 中的文件夹。


## 遇上 Arm64 时

当远程主机是 Arm64 架构时，也可以使用此插件，不过需要在 [VS Code - Insiders](https://code.visualstudio.com/insiders/) 中使用。

Insiders 版本相当于 VS Code 的内部预览版，能够更早的体验到一些新特性，更多信息可看此 [博客](https://code.visualstudio.com/blogs/2016/05/23/evolution-of-insiders) 内容。
