---
id: unable-to-hibernate
title: "纳尼？休眠不能？！"
description: "宇宙不重启，我们不休息！"
date: 2020.09.20 10:26
categories:
    - Linux
tags: [Linux]
keywords: Linux, hibernate, UEFI, Secure Boot
cover: /contents/covers/hibernate.jpg
---


## 现象

CentOS 7，`systemctl hibernate` 休眠失败，按照提示使用 `journalctl -xe` 查看具体原因，得到类似如下内容的日志：

```log
Feb 09 14:18:14 pike systemd[1]: Starting Sleep.
Feb 09 14:18:14 pike systemd[1]: Reached target Sleep.
Feb 09 14:18:14 pike systemd[1]: Starting Hibernate...
Feb 09 14:18:14 pike systemd-sleep[2284]: Failed to write mode to /sys/power/disk: Operation not permitted
Feb 09 14:18:14 pike systemd[1]: systemd-hibernate.service: main process exited, code=exited, status=1/FAILURE
Feb 09 14:18:14 pike systemd[1]: Failed to start Hibernate.
Feb 09 14:18:14 pike systemd[1]: Dependency failed for Hibernate.
Feb 09 14:18:14 pike systemd[1]: Service sleep.target is not needed anymore. Stopping.
Feb 09 14:18:14 pike systemd[1]: Unit systemd-hibernate.service entered failed state.
Feb 09 14:18:14 pike systemd[1]: Stopping Sleep.
Feb 09 14:18:14 pike systemd[1]: Stopped target Sleep.
```

查看 `/sys/power/disk` 提示不可使用。

```bash
$ cat /sys/power/disk
[disabled]
```


## 解决

查找了一些资料（详见参考资料），发现是设备启用了 `Secure Boot` 导致的。

在 BIOS 设置中，进入 `Security` 或 `Boot` 等分类下，将 `Secure Boot` 关闭（`Enabled` 改为 `Disabled`）即可。


## 原因

从参考资料中了解到，`休眠`是将系统内存状态进行快照并保存到磁盘中，之后切断系统电源；在唤醒时，再将磁盘中的内存快照恢复到内存中，以恢复休眠时的状态。

而当前缺乏一种手段保证唤醒时磁盘中保存的内容跟休眠时存入的内容一致，这就产生了一定的安全隐患。

Linux 内核中包含了一种锁定（`lockdown`）模式，当内核版本支持该特性，并且检测到系统启用了 `Secure Boot` 时，会自动进入锁定模式，进而导致无法进行休眠。


## 参考资料

* [F20 Unable to hibernate, /sys/power/disk disabled](https://unix.stackexchange.com/questions/114889/f20-unable-to-hibernate-sys-power-disk-disabled)
* [secure boot是什么意思？secure boot功能详解和关闭secure boot方法](http://www.dnxtc.net/zixun/zhuangjijiaocheng/2019-08-27/4003.html)
* [18.04 hibernate with UEFI and secure boot enabled](https://askubuntu.com/questions/1106105/18-04-hibernate-with-uefi-and-secure-boot-enabled)
* [Kernel lockdown in 4.17?](https://lwn.net/Articles/750730/)
