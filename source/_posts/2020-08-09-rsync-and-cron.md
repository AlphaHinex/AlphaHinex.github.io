---
id: rsync-and-cron
title: "通过 rsync 和 cron 实现日志文件的准实时同步"
description: "并非完美，但简单有效"
date: 2020.08.09 10:26
categories:
    - Linux
tags: [Linux]
keywords: Linux, rsync, cron, crontab, tail, append, near real time, Firm Real-Time Task, 准实时, 同步日志
cover: /contents/covers/rsync.jpg
---

需求
---

服务器中日志文件希望即时同步到另一个服务器中，并且能够 tail。


准备
---

1. 通过 rsync 进行文件的同步
1. 通过计划任务完成准实时的同步

### rsync

[rsync](https://rsync.samba.org/) 是一个 [开源](https://github.com/WayneD/rsync) 的工具，提供了快速的增量文件同步功能。包含在了 Linux 各主流发行版中。

基本用法为：`rsync [options] src dest`，支持本地及远程文件的拷贝（但不支持 src 和 dest 同时为远程地址）。

详细用法可以参考 [官方文档](https://rsync.samba.org/documentation.html) 或网上其他资料，如 [rsync - Linux下进行文件同步命令](https://cloud.tencent.com/developer/article/1114056)。

### cron

cron 是 Linux 中的计划任务工具，包括 cron 守护进程和 crontab 配置文件。且 cron 的计划表达式，基本成为了各类计划任务工具的通用标准。有一个在线网站 [crontab guru](https://crontab.guru/) 可以清晰的了解到 cron 计划表达式的含义。


方案
---

以在本地环境同步两个文件夹为例，源文件夹为 `/Users/alphahinex/Desktop/app`，目标文件夹为 `/Users/alphahinex/Desktop/sync`。

可通过如下命令完成一次两个文件夹的同步。

```bash
$ rsync -r /Users/alphahinex/Desktop/app /Users/alphahinex/Desktop/sync
```

假设在 app 路径下有一个持续输出的日志文件 `app.log`，通过执行上述命令，`app.log` 文件被同步到了目标路径下，Well Done！

不过等一下，我们 `tail -f /Users/alphahinex/Desktop/sync/app.log` 时，会发现，目标路径下的日志文件并没有持续刷新，即使我们不停的手动执行上面的 rsync 命令也不行。

在 rsync 命令后面增加 `-v` 参数，可以看到每次同步时，整个日志文件都被进行了传输。默认情况下，rsync 在发现文件发生变化时，会将目标位置的旧文件删除掉，并将源位置的新文件发送过去。

这就会导致我们的 tail 始终是一个内容不变的文件。那么想让目标路径的日志文件也能被 tail 时该怎么办呢？

### tail 目标路径日志文件，内容不变

查看 [官方文档](https://rsync.samba.org/documentation.html)，我们发现这样一组参数：

```text
--append
  This special copy mode only works to efficiently update files that are known to be growing larger where any existing content on the receiving side is also known to be the same as the content on the sender. The use of --append can be dangerous if you aren't 100% sure that all the files in the transfer are shared, growing files. You should thus use filter rules to ensure that you weed out any files that do not fit this criteria.

  Rsync updates these growing file in-place without verifying any of the existing content in the file (it only verifies the content that it is appending). Rsync skips any files that exist on the receiving side that are not shorter than the associated file on the sending side (which means that new files are trasnferred).

  This does not interfere with the updating of a file's non-content attributes (e.g. permissions, ownership, etc.) when the file does not need to be transferred, nor does it affect the updating of any directories or non-regular files.

--append-verify
  This special copy mode works like --append except that all the data in the file is included in the checksum verification (making it much less efficient but also potentially safer). This option can be dangerous if you aren't 100% sure that all the files in the transfer are shared, growing files. See the --append option for more details.

  Note: prior to rsync 3.0.0, the --append option worked like --append-verify, so if you are interacting with an older rsync (or the transfer is using a protocol prior to 30), specifying either append option will initiate an --append-verify transfer.
```

大意就是，可以通过增加 `--append` 参数来实现文件的增量传输。当需要验证所有文件内容（未传输部分）时，可以使用 `--append-verify` 参数。

对于我们的场景，`--append` 参数即可满足需求，调整后的同步命令变为了：

```bash
$ rsync -r --append /Users/alphahinex/Desktop/app /Users/alphahinex/Desktop/sync
```

此时再去 tail 目标路径日志文件，发现在执行同步命令后，更新的日志文件内容会显示到 tail 中。

由于对实时性要求不是很高，所以每秒同步一次就可以了。让计划任务每秒执行一次上述命令不就好了吗？

### cron 表达式的最小粒度是分钟 orz

理想总是很丰满。cron 表达式 `* * * * *` 是 `分钟 小时 日 月 星期几`，也就是说最快也只能每分钟执行一次。

这个时候可以采用一些变通方案，来使得 cron 支持每秒执行一次，比如写一个简单的脚本 `sync.sh`

```bash
#!/bin/bash
for((i=0;i<60;i++));
do
rsync -r --append /Users/alphahinex/Desktop/app/ /Users/alphahinex/Desktop/sync/
sleep 1
done
```

这个脚本的作用是，每次执行一次同步命令后，休眠 1 秒，执行 60 次。这样就变相实现了每秒执行一次同步指令。再通过 `crontab -e` 进行计划任务的配置，如：

```crontab
* * * * * /Users/alphahinex/Desktop/app/sync.sh
```

即实现了本次的需求。

> 注意 crontab 调整过后不会马上生效，稍等一会即可。
