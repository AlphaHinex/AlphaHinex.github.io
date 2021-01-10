---
id: mac-create-bootable-usb-stick
title: "MacOS 制作 USB 启动盘"
description: "自带命令即可完成，无需安装其他软件"
date: 2021.01.10 10:26
categories:
    - Mac
tags: [Mac]
keywords: 启动盘, MacOS, dd, diskutil
cover: /contents/covers/mac-create-bootable-usb-stick.jpg
---

安装操作系统时，当前常用的方式是获取操作系统对应的 ISO 文件，并制作 U 盘启动盘，使用 U 盘引导系统进行安装。

当使用 MacOS 时，可以很方便的利用系统自带工具，完成上述工作，具体步骤如下。

## 获得操作系统镜像

推荐从官方进行下载，如：

* [Windows 10](https://www.microsoft.com/zh-cn/software-download/windows10ISO)
* [Ubuntu](https://ubuntu.com/#download)
* [CentOS](https://www.centos.org/download/)

下载到的文件名如 `Win10_20H2_v2_Chinese(Simplified)_x64.iso`、`ubuntu-20.04.1-desktop-amd64.iso`、`CentOS-7-x86_64-DVD-2003.iso` 等。

## 制作启动盘

```bash
# 使用 diskutil 查看 U 盘设备 ID
$ diskutil list
...
/dev/disk2 (external, physical):
   #:                       TYPE NAME                    SIZE       IDENTIFIER
   0:                                                   *15.5 GB    disk2
...

# 取消 U 盘挂载，否则在后续操作中可能会提示资源忙，无法进行启动盘制作
# 注意使用上面查询到的设备 ID，本例中为 /dev/disk2，一定注意不要写错
$ diskutil unmountDisk /dev/disk2
Unmount of all volumes on disk2 was successful

# 使用 dd 将操作系统镜像写入 U 盘
# if=file 代表要写入的源文件路径
# of=file 代表要写入的目标文件，此处为代表 U 盘的设备 ID，但注意，命令中使用的是 rdisk2 而不是 disk2，也可以使用 disk2，区别稍后再讲
# bs=n 代表同时设置输入输出的块大小，n 代表字节数，默认为 512，可以使用 b/k/m/g 等字母后缀代表不同的单位，如下面命令代表每个块大小为 1048576(1m) 字节
# 写入时间较长，过程中没有任何输出，最终成功结束时会输出统计信息
$ sudo dd if=/Users/alphahinex/Downloads/CentOS-7-x86_64-Minimal-2003.iso of=/dev/rdisk2 bs=1m
1035+0 records in
1035+0 records out
1085276160 bytes transferred in 415.019150 secs (2615003 bytes/sec)
```

写入完成后，会弹出 `此电脑不能读取您插入的磁盘。` 的提示，直接点 `忽略` 或 `推出` 即可，不要点 `初始化...`。

也可以使用 `diskutil` 将 U 盘弹出：

```bash
$ diskutil eject /dev/disk2
Disk /dev/disk2 ejected
```

制作好的启动盘，在 Mac 或 Windows 上都无法查看其中内容，但并不影响使用。

### /dev/rdisk

通过 `diskutil` 我们查询到的 U 盘设备路径为 `/dev/disk2`，在使用 `dd` 的时候为什么要使用 `/dev/rdisk2` 呢？

在 [RPi Easy SD Card Setup][rpi] 中，提到了在 Mac OS 中 `/dev/disk` 和 `/dev/rdisk` 的区别：

> Note: In OS X each disk may have two path references in /dev:
>
> * /dev/disk# is a buffered device, which means any data being sent undergoes extra processing.
> * /dev/rdisk# is a raw path, which is much faster, and perfectly OK when using the dd program.
>
> On a Class 4 SD card the difference was around 20 times faster using the rdisk path.

Mac 自带的 `hdiutil` 工具的使用手册中也有相关描述：

```term
$ man hdiutil
...
DEVICE SPECIAL FILES
     Since any /dev entry can be treated as a raw disk image, it is worth noting which devices can be accessed when and how.  /dev/rdisk nodes are character-special devices, but are
     "raw" in the BSD sense and force block-aligned I/O.  They are closer to the physical disk than the buffer cache.  /dev/disk nodes, on the other hand, are buffered block-special
     devices and are used primarily by the kernel's filesystem code.

     It is not possible to read from a /dev/disk node while a filesystem is mounted from it, but anyone with read access to the appropriate /dev/rdisk node can use hdiutil verbs
     such as fsid or pmap with it.  Beware that information read from a raw device while a filesystem is mounted may not be consistent because the consistent data is stored in mem-
     ory or in the filesystem's journal.

     The DiskImages framework will attempt to use authopen(1) to open any device which it can't open (due to EACCES) for reading with open(2).  Depending on session characteristics,
     this behavior can cause apparent hangs while trying to access /dev entries while logged in remotely (an authorization panel is waiting on console).

     Generally, the /dev/disk node is preferred for imaging devices (e.g.  convert or create -srcdevice operations), while /dev/rdisk is usable for the quick pmap or fsid.  In par-
     ticular, converting the blocks of a mounted journaled filesystem to a read-only image will prevent the volume in the image from mounting (the journal will be permanently
     dirty).
...
```

总结一下，就是在制作启动盘时使用 `/dev/rdisk#` 会比 `/dev/disk#` 速度更快。

使用数据验证一下：

```bash
$ sudo dd if=/Users/alphahinex/Downloads/CentOS-7-x86_64-Minimal-2003.iso of=/dev/rdisk2 bs=1m
1035+0 records in
1035+0 records out
1085276160 bytes transferred in 415.019150 secs (2615003 bytes/sec)

$ sudo dd if=/Users/alphahinex/Downloads/CentOS-7-x86_64-Minimal-2003.iso of=/dev/disk2 bs=1m
1035+0 records in
1035+0 records out
1085276160 bytes transferred in 771.201933 secs (1407253 bytes/sec)
```

虽然效果并不拔群，但也确实快了近一倍。

> `dd` 过程中，可以通过 `iostat` 命令查看磁盘状态，如 `iostat -c 1000 disk2`

## 参考资料

* [Mac 制作 Ubuntu 18.04 启动盘](https://www.jianshu.com/p/0abdd301e0d6)
* [Why is “/dev/rdisk” about 20 times faster than “/dev/disk” in Mac OS X](https://superuser.com/questions/631592/why-is-dev-rdisk-about-20-times-faster-than-dev-disk-in-mac-os-x/1346063#1346063)
* [RPi Easy SD Card Setup][rpi]

[rpi]:https://elinux.org/RPi_Easy_SD_Card_Setup
