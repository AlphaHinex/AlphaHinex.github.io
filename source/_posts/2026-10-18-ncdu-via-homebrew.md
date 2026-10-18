---
id: ncdu-via-homebrew
title: "用 ncdu 分析及清理 Mac 磁盘空间那些事"
description: "ncdu 分析磁盘空间；清理 Docker 和 Chrome 占用的大量空间；Homebrew 安装历史版本 ncdu"
date: 2026.10.18 10:34
categories:
    - Mac
tags: [Mac, Homebrew, ncdu]
keywords: ncdu, Mac, disk usage, disk cleanup, Homebrew, brew extract, tap, bottle, formula, zig, llvm, ncdu 1.x, brew pin, firmlink
cover: /contents/covers/ncdu-via-homebrew.png
---

[NCurses Disk Usage(Ncdu)](https://dev.yorhel.nl/ncdu) 是 [Yorhel](https://dev.yorhel.nl/) 开源的基于文本 UI 库 [NCurses](https://invisible-island.net/ncurses/announce.html) 实现的磁盘用量分析工具，支持在 Linux、Mac 平台上运行。[v1](https://dev.yorhel.nl/ncdu/changes) 版本基于 C 语言实现，[v2](https://dev.yorhel.nl/ncdu/changes2) 版本基于 [Zig 语言](https://ziglang.org/) 实现。源码可见：

- https://code.blicky.net/yorhel/ncdu
- https://g.blicky.net/ncdu.git

Ncdu 使用简单。如果你在 Mac 上通过 Homebrew 安装 Ncdu 时遇到了问题，可以跳到下面 `安装` 章节查看是否是类似原因。

## 使用

Ncdu 以交互式界面展示目录和文件的大小，支持排序、浏览、删除等操作。安装完成后，直接扫描根目录即可看到整个磁盘的空间分布：

```bash
ncdu /
```

在 macOS 上扫描根目录时，如果使用的是 [1.x 版本](https://dev.yorhel.nl/ncdu/man/1_22)，需要加上 `--exclude-firmlinks` 参数，**避免 mac 下数据重复计算**。[firmlink 是 macOS Catalina 之后引入的机制](https://developer.apple.com/forums/thread/117470)，同一个目录可能通过多个路径访问到，不加参数会导致占用被重复统计：

```bash
ncdu / --exclude-firmlinks
```

> [2.x 版本](https://dev.yorhel.nl/ncdu/man/2_0) 没有也不需要使用这个参数了，可以直接 `ncdu /` 。

进入 ncdu 界面后，目录会按占用空间从大到小排列，使用方向键逐层进入，找到占用异常的大目录后，可以直接按 `d` 删除选中的文件或目录，也可以按 `s` 按文件大小排序、按 `t` 按修改时间排序，快速定位占用磁盘空间最多的文件。

![](https://alphahinex.github.io/contents/covers/ncdu-via-homebrew.png)

以我的实际情况为例，占用空间最多的是 `/System/Volumes/Data/Users/alphahinex/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw` 和 `/System/Volumes/Data/Users/alphahinex/Library/Application Support/Google/Chrome/Default/Service Worker/CacheStorage` 分别为 Docker Desktop 占用的磁盘文件，以及 Chrome 缓存数据，可以通过 `docker system prune -a --volumes` 清理所有停止的容器、未使用的镜像、卷和构建缓存，以及在 Chrome 中访问 `chrome://settings/content/all` 选择数据进行清理。

## 安装

在 macOS 上安装 Ncdu 最常用的安装方式就是 [Homebrew](https://formulae.brew.sh/formula/ncdu)：

```bash
brew install ncdu
```

> 安装 Homebrew 如果遇到问题可以参考：[【2026实测】Homebrew安装+配置国内源+使用一篇搞定（多种安装方式）](https://developer.aliyun.com/article/1745255#1) 。

### 安装时间超长

理想情况下，这个命令成功执行后就可以使用 `ncdu` 命令了，然而不出意外的话出意外了：安装命令执行时间明显超预期。

中断后打开日志重新执行：

```
brew install -y --verbose --debug ncdu
```

发现出现大量类似下面的日志：

```log
[1778/8125] cd /private/tmp/s-m40oG1E8/llvmA20-20261013-72265-cr0n9m/llvm-project-20.1.8.src/llvm/build && /private/tmp/s-m40oG1E8/llvmA20-20261013-72265-cr0n9m/llvm-project-20.1.8.src/llvm/build/bin/llvm-tblgen -gen-asm-writer -I /private/tmp/s-m40oG1E8/llvmA20-20261013-72265-cr0n9m/llvm-project-20.1.8.src/llvm/lib/Target/VE -I/private/tmp/s-m40oG1E8/llvmA20-20261013-72265-cr0n9m/llvm-project-20.1.8.src/llvm/build/include -I/private/tmp/s-m40oG1E8/llvmA20-20261013-72265-cr0n9m/llvm-project-20.1.8.src/llvm/include -I /private/tmp/s-m40oG1E8/llvmA20-20261013-72265-cr0n9m/llvm-project-20.1.8.src/llvm/lib/Target /private/tmp/s-m40oG1E8/llvmA20-20261013-72265-cr0n9m/llvm-project-20.1.8.src/llvm/lib/Target/VE/VE.td --write-if-changed -o lib/Target/VE/VEGenAsmWriter.inc -d lib/Target/VE/VEGenAsmWriter.inc.d
```

注意开头部分的 `[1778/8125]`，表示等待了很长时间，才完成 8125 步中的 1778 步。

Homebrew Formula 中的 `bottle do ... end` 代码块，用来声明 **哪些平台可以直接下载现成的二进制** 。以 [ncdu 2.9.2 的 formula](https://github.com/Homebrew/homebrew-core/blob/33f30f4b6ce0386f7c84d5ca0079dccd231d8a93/Formula/n/ncdu.rb#L14-L22) 为例：

```rb
  bottle do
    sha256 cellar: :any,                 arm64_golden_gate: "138b29744585e45a993e785bda2c8ec6133044227821878a1dd0d6fbc17321cb"
    sha256 cellar: :any,                 arm64_tahoe:       "9a08dd709b18d87d90b016b8685d56f2de8d537e437ab44cf4ed92203df7a245"
    sha256 cellar: :any,                 arm64_sequoia:     "d56b0ffa80c15fa5758a8b7b59525687a1a04ce043d540936b6db917c7c14c30"
    sha256 cellar: :any,                 arm64_sonoma:      "b86c878b672bb5a7d8644e9908c4ed1ca3fd942095becec43ceff480340d2a2b"
    sha256 cellar: :any,                 sonoma:            "768ace20bc54c22b86ddce63d51bd8488cb04816e28e330286a2685047d5484e"
    sha256 cellar: :any_skip_relocation, arm64_linux:       "2a2d143126f866ae7a7f0aeecc2d12282bde98542e1ece1203d821a8d499343b"
    sha256 cellar: :any_skip_relocation, x86_64_linux:      "762c13f508d0699c363f0a3a0741a19cbd14d1ef8a86fdd1d70aeaaf2f7bd851"
  end
```

逐行解读一下 `bottle do` 块中的关键信息：

- **`sha256`** ：每个 bottle 文件的校验值，用于验证下载完整性。
- **`cellar: :any`** ：表示这个 bottle 与 Homebrew 的 Cellar 路径有关，安装时可能需要重定位，通常用于 macOS 上的包。
- **`cellar: :any_skip_relocation`** ：表示可以跳过重定位步骤，通常用于不依赖 Cellar 绝对路径的包（如 Linux 上的静态二进制）。
- **平台标签** ：
  - `arm64_golden_gate`、`arm64_tahoe`、`arm64_sequoia`、`arm64_sonoma`：Apple Silicon（M 系列）Mac 上的不同 macOS 版本。
  - `sonoma`（无 `arm64_` 前缀）：Intel Mac 上的 macOS Sonoma（14.x）。
  - `arm64_linux`、`x86_64_linux`：Linux 平台，分别对应 ARM64 和 x86_64 架构。

macOS 操作系统名称和版本对应关系可见：https://support.apple.com/zh-cn/109033#latest 。

运行下面的命令确认自己的系统信息：

```bash
brew config
```

输出中重点关注 `macOS:` 后面的版本号和 `CPU:` 中信息。

如果你的 Mac 是 Intel 芯片且系统版本低于 macOS Sonoma（14），或者虽然是 Apple Silicon 但系统较老，没有匹配的 bottle，通过 `brew install` 安装 ncdu 2.9.2 版本时，就会回退到从源码编译。

而 ncdu 2.x 是用 **Zig** 编写的，Zig 工具链又依赖 **LLVM** (编译时间超长)，于是 `brew install ncdu` 变成了"先编译 Zig/LLVM，再编译 ncdu"，这就是那一大串 `llvm-tblgen` 构建日志的来源。

Homebrew 官方文档 [Why do you compile everything?](https://docs.brew.sh/FAQ#why-do-you-compile-everything) 也对不能使用预编译包的情况进行了说明，可以在 https://github.com/Homebrew/homebrew-core/packages 查找所有的预编译包（[Bottles](https://docs.brew.sh/Bottles)）。

### 解决方案：安装有对应系统预编译包的版本

以在 macOS 12.7 上安装 x86 版本 ncdu 为例，在 https://github.com/Homebrew/homebrew-core/pkgs/container/core%2Fncdu/271572867?tag=2.5 找到有 Ncdu 2.5 版的预编译包，随后通过最新版本的 [ncdu.rb](https://github.com/Homebrew/homebrew-core/blob/main/Formula/n/ncdu.rb) 文件提交历史，找到 [2.5 版本的 ncdu.rb](https://github.com/Homebrew/homebrew-core/blob/c01aeaac6a1d1bacd301f945a8e67cc6abeda1f3/Formula/n/ncdu.rb)，将内容保存到本地 `ncdu.rb` 文件中。

[Homebrew 4.6.4](https://github.com/Homebrew/brew/releases/tag/4.6.4) 版本起不再支持直接安装本地 formula 文件，除非设置 [HOMEBREW_DEVELOPER=1](https://github.com/Homebrew/brew/pull/20414) ：

```bash
HOMEBREW_DEVELOPER=true brew install --formulae ncdu.rb
```

成功安装 Ncdu 2.5 版本。更多关于安装旧版本 Hombrew 包的信息可见：[How To Install Older Versions of Homebrew Packages](https://dev.to/nelsonfigueroa/how-to-install-older-versions-of-homebrew-packages-2bn8#1) 。

🔒 **安装后锁定版本**：安装旧版后，建议用 `brew pin` 将其锁定，防止后续 `brew upgrade` 时被自动升级。

```bash
brew pin ncdu
```

需要解除锁定时，使用 `brew unpin ncdu`。

## 附1：Homebrew 基本概念

Homebrew 中的专有词汇很多，[Homebrew terminology](https://docs.brew.sh/Formula-Cookbook#homebrew-terminology) 列出了术语表，下面介绍其中的几组基础概念。

### 🍺 Formula（配方）

**Formula 是 Homebrew 的"安装说明书"** ，是一个用 Ruby 写的脚本文件（`.rb`）。它定义了：

- 软件的名称、版本、下载地址（通常是源码 tarball）
- 依赖哪些其他库或工具
- 用什么命令编译（`./configure`、`make`、`zig build` 等）
- 安装后哪些文件放到哪里
- 如何做测试（`brew test`）

比如 `ncdu 2.9.2` 的 formula 片段，里面写了 `depends_on "zig@0.15"`，所以 Homebrew 才会去安装 Zig 和 LLVM（zig 的依赖）：

```ruby
class Ncdu < Formula
  desc "NCurses Disk Usage"
  homepage "https://dev.yorhel.nl/ncdu"
  url "https://dev.yorhel.nl/download/ncdu-2.9.2.tar.gz"
  sha256 "e91135281cb66569f2ca4c0bac277246991e7e52524c0ca8cba3de5c8e81cec9"
  license "MIT"
  head "https://g.blicky.net/ncdu.git", branch: "zig"

  ...

  depends_on "pkgconf" => :build
  depends_on "zig@0.15" => :build
  # Without this, `ncdu` is unusable when `TERM=tmux-256color`.
  depends_on "ncurses"
  depends_on "zstd"

  ...

  def install
    args = []
    args << "-Dpie=true" if OS.mac?

    ...

    system "zig", "build", *args, *std_zig_args
    man1.install "ncdu.1"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/ncdu -v")
    system bin/"ncdu", "-o", "test"
    output = JSON.parse((testpath/"test").read)
    assert_equal "ncdu", output[2]["progname"]
    assert_equal version.to_s, output[2]["progver"]
    assert_equal Pathname.pwd.size, output[3][0]["asize"]
  end
end
```

### 🖥️ Cask（桶）

**Cask 是 Formula 的"图形界面/二进制版"扩展** ，专门用来安装 macOS 上的 **预编译应用、二进制文件、字体、插件** 等，通常不涉及从源码编译。

Google Chrome、Visual Studio Code、Docker Desktop 这些，都可以通过 cask 安装。Cask 的文件也是 Ruby 脚本，但描述的是"下载这个 `.dmg`，把 `.app` 拖到 `/Applications`"，如：

```bash
$ brew info google-chrome
==> google-chrome (Google Chrome): 155.0.8059.85 (auto_updates)
Web browser
https://www.google.com/chrome/
Not installed
From: https://github.com/Homebrew/homebrew-cask/blob/HEAD/Casks/g/google-chrome.rb
==> Requirements
Required: macOS >= 13 ✘
==> Artifacts
Google Chrome.app (App)
==> Analytics
install: 20,839 (30 days), 81,117 (90 days), 434,759 (365 days)
```

> 简单区分：**Formula 是命令行工具/库，Cask 是图形应用/预编译二进制。**

### 📦 Tap（水龙头/第三方仓库）

**Tap 是一个额外的软件源**，可以理解为一个 Git 仓库，里面存放着 Formula 和 Cask。Homebrew 默认只从官方的 `homebrew/core` 和 `homebrew/cask` 获取软件。

当你需要：

- 某个软件官方仓库没有
- 某个历史版本
- 使用别人维护的专用工具

就可以 `tap` 一个第三方仓库。

```bash
brew tap                          # 列出已 tap 的仓库
brew tap homebrew/core --force    # 强制下载官方核心仓库
brew tap-new local/ncdu-history   # 创建你自己的本地 tap
```

### 🍾 Bottle（瓶子/预编译包）

**Bottle 是 Homebrew 预先编译好的二进制包**，用来避免用户从源码编译。如果有 bottle，`brew install` 会直接下载编译好的二进制，几秒钟装完；如果没有，则按 Formula 中描述通过源码进行编译。

```bash
brew install --force-bottle ncdu   # 强制使用预编译包（如果有）
```

### 🏠 Cellar / Keg（酒窖 / 酒桶）

- **Cellar**：Homebrew 安装软件的**总目录**。Intel Mac 是 `/usr/local/Cellar`，Apple Silicon 是 `/opt/homebrew/Cellar`。
- **Keg**：Cellar 里**某个软件某个版本的具体目录**。比如 `/usr/local/Cellar/ncdu/1.16`。

Homebrew 会把不同版本并排放在 Cellar 里，然后通过软链接（symlink）把当前使用的版本链接到 `/usr/local/bin` 等路径，这就是为什么可以同时保留多个版本。

```bash
brew --cellar                  # 查看 Cellar 路径
```

### 🔗 它们之间的关系

1. **Tap** 是仓库，里面存放着 **Formula** 和 **Cask**。
2. **Formula** 描述如何从源码构建命令行软件；**Cask** 描述如何安装图形应用/预编译包。
3. **Bottle** 是 Formula 对应的预编译二进制，用来加速安装。
4. 安装后的文件放在 **Cellar** 里，每个版本是一个 **Keg**。

## 附2：通过 Tap 安装软件的历史版本

以安装 Ncdu 1.x 版本为例。结合 Homebrew 的 tap 机制，可以用 `brew extract` 从官方仓库的历史中提取旧版 formula 到自己的本地 tap 中安装。

[Homebrew 官方文档 Extracting a historical formula into your tap](https://docs.brew.sh/How-to-Create-and-Maintain-a-Tap#extracting-a-historical-formula-into-your-tap) 提供了从历史版本中提取 formula 的方法，步骤如下。

**1. 创建一个本地 tap：**

```bash
brew tap-new local/ncdu-history
```

**2. 强制克隆官方核心仓库：**

`brew extract` 需要从 `homebrew/core` 的 Git 历史中提取旧版 formula，但新版 Homebrew 默认不完整克隆 `homebrew/core`，所以要先强制下载：

```bash
brew tap homebrew/core --force
```

**3. 从历史中提取 ncdu 1.16 的 formula 到本地 tap：**

```bash
$ brew extract --version=1.16 ncdu local/ncdu-history
==> Searching repository history
==> Writing formula for ncdu at 1.16 from revision 2f9e830 to:
/usr/local/Homebrew/Library/Taps/local/homebrew-ncdu-history/Formula/ncdu@1.16.rb
```

**4. 安装：**

```bash
brew install local/ncdu-history/ncdu@1.16
```

**5.（可选）解除官方核心仓库的完整克隆：**

```bash
brew untap homebrew/core
```