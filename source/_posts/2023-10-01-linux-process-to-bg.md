---
id: linux-process-to-bg
title: "Linux 中前台进程转后台，并重定向输出"
description: "前台执行至中途，又不想半途而废的补救措施"
date: 2023.10.01 10:34
categories:
    - Linux
tags: [Linux]
keywords: Linux, process, pid, jobs, bg, disown, gdb
cover: /contents/covers/linux-process-to-bg.jpeg
---

有时候我们直接在终端中执行了命令，等待很长时间后发现还需要很久才能执行完，又不想一直开着终端等待结果，可以按照下面的方式，将前台进程转至后台，并重定向输出内容至文件，以便随时连接回来查看执行状态。


## 示例程序

假设我们需要执行很久的任务是下面这段脚本：每隔五秒打印一段内容至控制台。

```bash
$ cat > test.sh << EOF
> while true; do
>     echo "Press Ctrl+C to stop."
>     sleep 5
> done
> EOF
$ chmod +x test.sh
$ ./test.sh
Press Ctrl+C to stop.
Press Ctrl+C to stop.
...
```


## 前台任务转后台任务

先按 `Ctrl+z` 中断当前任务：

```bash
...
Press Ctrl+C to stop.
^Z
[1]+  已停止               ./test.sh
```

查看当前 shell 会话中所有正在运行或被停止（suspended）的后台作业的列表：

```bash
$ jobs
[1]+  已停止               ./test.sh
```

使用 `bg %n` 将指定的停止的后台作业切换到后台运行。`%n` 是作业编号，例如 `bg %1` 将作业编号为 `1` 的作业切换到后台运行。

```bash
$ bg %1
[1]+ ./test.sh &
$ Press Ctrl+C to stop.
Press Ctrl+C to stop.
Press Ctrl+C to stop.
```

这时会看到进程输出的内容又回到了控制台，但并不影响控制台进行其他操作，`Ctrl+C` 也不会停止掉这个进程。关掉终端窗口会终止此进程，若想实现类似 `nohup [command] &` 的效果，此时需要使用 `disown %n` 将后台运行的这个进程与当前 shell 分离：

```bash
$ disown %1
```

先查找一下这个进程的 pid，如 `24863`，关闭终端再重新打开窗口后，可查看相关进程情况：

```bash
$ $ ps -ef | grep 24863
ec2-user 24863     1  0 14:05 ?        00:00:00 -bash
ec2-user 26696 24863  0 14:53 ?        00:00:00 sleep 5
ec2-user 26698 26320  0 14:53 pts/0    00:00:00 grep --color=auto 24863
```

虽然进程依然在运行，但新打开的终端中已经无法看到进程输出的内容了。


## 重定向日志

在 Linux 中，如果一个进程已经在运行，并且您想要将其标准输出重定向到一个文件或设备，可以使用以下步骤。

首先查看一下进程的文件描述符（继续以 pid 是 `24863` 为例）：

```bash
$ ll /proc/24863/fd
总用量 0
lrwx------ 1 ec2-user ec2-user 64 9月  30 14:10 0 -> /dev/pts/2 (deleted)
l-wx------ 1 ec2-user ec2-user 64 9月  30 14:10 1 -> /dev/pts/2 (deleted)
lrwx------ 1 ec2-user ec2-user 64 9月  30 14:10 2 -> /dev/pts/2 (deleted)
lr-x------ 1 ec2-user ec2-user 64 9月  30 14:10 254 -> /home/ec2-user/temp/test/test.sh
lrwx------ 1 ec2-user ec2-user 64 9月  30 14:10 255 -> /dev/pts/2 (deleted)
```

可以看到当前标准输出 `1` 对应的 `/dev/pts/2` 已被删掉。

使用 `gdb` 命令附加到该进程。`gdb` 是一个用于调试程序的工具，也可以用于向运行中的进程发送信号。在 `gdb` 命令提示符下，执行以下命令来重定向进程的标准输出：

```bash
$ gdb -p 24863
...
(gdb) p creat("/home/ec2-user/temp/test/test.log", 0644)
$1 = 3
(gdb) p dup2(3,1)
$2 = 1
(gdb) p close(3)
$3 = 0
(gdb) q
A debugging session is active.

	Inferior 1 [process 24863] will be detached.

Quit anyway? (y or n) y
```

再次查看文件描述符：

```bash
$ ll /proc/24863/fd
总用量 0
lrwx------ 1 ec2-user ec2-user 64 9月  30 14:10 0 -> /dev/pts/2 (deleted)
l-wx------ 1 ec2-user ec2-user 64 9月  30 14:10 1 -> /home/ec2-user/temp/test/test.log
lrwx------ 1 ec2-user ec2-user 64 9月  30 14:10 2 -> /dev/pts/2 (deleted)
lr-x------ 1 ec2-user ec2-user 64 9月  30 14:10 254 -> /home/ec2-user/temp/test/test.sh
lrwx------ 1 ec2-user ec2-user 64 9月  30 14:10 255 -> /dev/pts/2 (deleted)
```

现在，进程的标准输出将被重定向到指定的文件中。

> 请注意：此方法对某些进程可能无效，因为有些进程会在启动时检查其输出是否已被重定向。此外，由于 gdb 是一个用于调试的工具，执行此操作可能会对进程的运行产生一些影响。
> 
> 请谨慎使用，并确保对正在运行的进程的操作没有负面影响。


## 参考资料

* [linux让前台正在执行的命令转入后台并nohup的方法](https://blog.51cto.com/lonelyprogram/1355265)
* [进程输出重定向](https://yunisaworld.github.io/2018/04/27/%E8%BF%9B%E7%A8%8B%E8%BE%93%E5%87%BA%E9%87%8D%E5%AE%9A%E5%90%91/)