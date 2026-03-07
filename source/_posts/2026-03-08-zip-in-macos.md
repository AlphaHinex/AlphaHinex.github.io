---
id: zip-in-macos
title: "macOS 自带 zip 压缩中文文件名乱码问题"
description: "分析 macOS 内置 zip 工具压缩中文文件名出现乱码的原因，并提供解决方案"
date: 2026.03.08 10:26
categories:
    - Mac
tags: [Mac, Linux, zip]
keywords: zip, macOS, Linux, 中文乱码, UNICODE_SUPPORT, Info-ZIP
cover: /contents/covers/zip-in-macos.png
---

# TL;DR

macOS 自带的 zip 命令因缺少 `UNICODE_SUPPORT` 编译选项，无法正确处理 UTF-8 编码的中文文件名。解决方案是通过 `brew install zip` 安装支持 Unicode 的 zip 版本。

# 重现

在 macOS 上创建一个包含中文文件名的测试目录进行复现：

```bash
# 创建测试目录和文件
$ mkdir -p test/文档
$ touch test/文档/需求说明.txt
$ touch test/文档/用户手册.pdf

# 使用 macOS 内置 zip 压缩
$ zip -r test.zip test/
  adding: test/ (stored 0%)
  adding: test/文档/ (stored 0%)
  adding: test/文档/用户手册.pdf (stored 0%)
  adding: test/文档/需求说明.txt (stored 0%)
```

得到的 test.zip 文件在 Mac 上解压没问题，但到 Windows 环境解压，中文文件名会乱码：

```cmd
c:\Users\Administrator\Desktop\test>tree /F
文件夹 PATH 列表
卷序列号为 504B-1F01
C:.
└─鏂囨。
        鐢ㄦ埛鎵嬪唽.pdf
        闇€姹傝鏄_txt
```

# 原因分析

对比 Linux 环境，发现如下情况：

| 压缩系统 | 解压系统 | 中文文件名乱码 |
|:-------|:--------|:-------------|
| macOS  | Windows | 是 |
| macOS  | Linux   | 否 |
| Linux  | Windows | 否 |
| Linux  | macOS   | 否 |

进一步对比 macOS 和 Linux 中 zip 版本：

```bash
# macOS zip version
$ zip -v
Copyright (c) 1990-2008 Info-ZIP - Type 'zip "-L"' for software license.
This is Zip 3.0 (July 5th 2008), by Info-ZIP.
Currently maintained by E. Gordon.  Please send bug reports to
the authors using the web page at www.info-zip.org; see README for details.

Latest sources and executables are at ftp://ftp.info-zip.org/pub/infozip,
as of above date; see http://www.info-zip.org/ for other sites.

Compiled with gcc Apple LLVM 13.1.6 (clang-1316.0.21.3) [+internal-os, ptrauth-isa=deployment-target-based] for Unix (Mac OS X) on Aug 17 2023.

Zip special compilation options:
    USE_EF_UT_TIME       (store Universal Time)
    SYMLINK_SUPPORT      (symbolic links supported)
    LARGE_FILE_SUPPORT   (can read and write large files on file system)
    ZIP64_SUPPORT        (use Zip64 to store large files in archives)
    STORE_UNIX_UIDs_GIDs (store UID/GID sizes/values using new extra field)
    UIDGID_16BIT         (old Unix 16-bit UID/GID extra field also used)
    [encryption, version 2.91 of 05 Jan 2007] (modified for Zip 3)

Encryption notice:
    The encryption code of this program is not copyrighted and is
    put in the public domain.  It was originally written in Europe
    and, to the best of our knowledge, can be freely distributed
    in both source and object forms from any country, including
    the USA under License Exception TSU of the U.S. Export
    Administration Regulations (section 740.13(e)) of 6 June 2002.

Zip environment options:
             ZIP:  [none]
          ZIPOPT:  [none]
```

```bash
# Linux zip version
$ zip -v
Copyright (c) 1990-2008 Info-ZIP - Type 'zip "-L"' for software license.
This is Zip 3.0 (July 5th 2008), by Info-ZIP.
Currently maintained by E. Gordon.  Please send bug reports to
the authors using the web page at www.info-zip.org; see README for details.

Latest sources and executables are at ftp://ftp.info-zip.org/pub/infozip,
as of above date; see http://www.info-zip.org/ for other sites.

Compiled with gcc 4.8.5 20150623 (Red Hat 4.8.5-11) for Unix (Linux ELF) on Nov  5 2016.

Zip special compilation options:
    USE_EF_UT_TIME       (store Universal Time)
    BZIP2_SUPPORT        (bzip2 library version 1.0.6, 6-Sept-2010)
        bzip2 code and library copyright (c) Julian R Seward
        (See the bzip2 license for terms of use)
    SYMLINK_SUPPORT      (symbolic links supported)
    LARGE_FILE_SUPPORT   (can read and write large files on file system)
    ZIP64_SUPPORT        (use Zip64 to store large files in archives)
    UNICODE_SUPPORT      (store and read UTF-8 Unicode paths)
    STORE_UNIX_UIDs_GIDs (store UID/GID sizes/values using new extra field)
    UIDGID_NOT_16BIT     (old Unix 16-bit UID/GID extra field not used)
    [encryption, version 2.91 of 05 Jan 2007] (modified for Zip 3)

Encryption notice:
    The encryption code of this program is not copyrighted and is
    put in the public domain.  It was originally written in Europe
    and, to the best of our knowledge, can be freely distributed
    in both source and object forms from any country, including
    the USA under License Exception TSU of the U.S. Export
    Administration Regulations (section 740.13(e)) of 6 June 2002.

Zip environment options:
             ZIP:  [none]
          ZIPOPT:  [none]
```

发现二者在编译选项上有所差别，macOS 中缺少 `UNICODE_SUPPORT      (store and read UTF-8 Unicode paths)`，此项正是造成差异的关键。

# 解决方案

使用 HomeBrew 重新安装 [zip](https://formulae.brew.sh/formula/zip)，替代自带 zip。

```bash
$ brew install zip
...
==> Fetching downloads for: zip
==> Downloading https://ghcr.io/v2/homebrew/core/zip/manifests/3.0-2
Already downloaded: /Users/alphahinex/Library/Caches/Homebrew/downloads/794b38c4c17afd41abe76b9b8dc73cabd3543bdb3816b4acca62ff0132aa1225--zip-3.0-2.bottle_manifest.json
==> Fetching zip
==> Downloading https://ghcr.io/v2/homebrew/core/zip/blobs/sha256:cf5690223dfcc1683280d1692d3f41339981d9b4eacf68f3dedf9cd2cbc68ec1
################################################################################################################################################## 100.0%
==> Pouring zip--3.0.monterey.bottle.2.tar.gz
==> Caveats
zip is keg-only, which means it was not symlinked into /usr/local,
because macOS already provides this software and installing another version in
parallel can cause all kinds of trouble.

If you need to have zip first in your PATH, run:
  echo 'export PATH="/usr/local/opt/zip/bin:$PATH"' >> ~/.zshrc
==> Summary
🍺  /usr/local/Cellar/zip/3.0: 15 files, 867.6KB
==> Running `brew cleanup zip`...
...
```

安装后查看版本：

```bash
$ /usr/local/opt/zip/bin/zip -v
Copyright (c) 1990-2008 Info-ZIP - Type 'zip "-L"' for software license.
This is Zip 3.0 (July 5th 2008), by Info-ZIP.
Currently maintained by E. Gordon.  Please send bug reports to
the authors using the web page at www.info-zip.org; see README for details.

Latest sources and executables are at ftp://ftp.info-zip.org/pub/infozip,
as of above date; see http://www.info-zip.org/ for other sites.

Compiled with gcc Apple LLVM 13.0.0 (clang-1300.0.29.3) for Unix (Mac OS X).

Zip special compilation options:
    USE_EF_UT_TIME       (store Universal Time)
    BZIP2_SUPPORT        (bzip2 library version 1.0.8, 13-Jul-2019)
        bzip2 code and library copyright (c) Julian R Seward
        (See the bzip2 license for terms of use)
    SYMLINK_SUPPORT      (symbolic links supported)
    LARGE_FILE_SUPPORT   (can read and write large files on file system)
    ZIP64_SUPPORT        (use Zip64 to store large files in archives)
    UNICODE_SUPPORT      (store and read UTF-8 Unicode paths)
    STORE_UNIX_UIDs_GIDs (store UID/GID sizes/values using new extra field)
    UIDGID_NOT_16BIT     (old Unix 16-bit UID/GID extra field not used)
    [encryption, version 2.91 of 05 Jan 2007] (modified for Zip 3)

Encryption notice:
    The encryption code of this program is not copyrighted and is
    put in the public domain.  It was originally written in Europe
    and, to the best of our knowledge, can be freely distributed
    in both source and object forms from any country, including
    the USA under License Exception TSU of the U.S. Export
    Administration Regulations (section 740.13(e)) of 6 June 2002.

Zip environment options:
             ZIP:  [none]
          ZIPOPT:  [none]
```

确认已支持 Unicode，用此版本在 macOS 压缩中文文件名的文件，到 Windows 环境解压，不会出现乱码。

# 参考资料

- https://formulae.brew.sh/formula/zip
- https://infozip.sourceforge.net/
- https://infozip.sourceforge.net/Zip.html
