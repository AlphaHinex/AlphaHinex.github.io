---
id: openeuler
title: "openEuler 社区人才认证考试"
description: "包含学习资料及随堂测下载"
date: 2023.03.05 10:34
categories:
    - Linux
tags: [Linux]
keywords: openEuler, Linux
cover: /contents/openEuler/cover.jpeg
---

原文地址：https://wyiyi.github.io/amber/2023/03/01/openEuler/

学习资料及随堂测磨题帮导入数据下载地址：https://github.com/AlphaHinex/AlphaHinex.github.io/tree/develop/source/contents/openEuler

# openEuler 社区人才认证考试

## 01 系统安装概述
1. 通常在少量安装时，采用U盘、光盘或者虚拟光驱的方式安装；在批量安装时，采用 PXE 引导的方式安装。
2. 针对不同的架构，openEuler 提供的启动模式也不同。X86 架构包含 Legacy 和 UEFI 模式，而 ARM 架构目前只包含 UEFI 模式
3. 在安装引导界面，按 “e” 进入已选选项的参数编辑界面，按 “c” 进入命令行模式。
4. 查看系统信息命令: `cat /etc/os-release`
5. https://docs.openeuler.org/zh/docs/22.03_LTS/docs/Installation/installation.html


## 02 物理存储及逻辑卷管理
### 磁盘存储挂载与使用
1. 扩展分区与逻辑分区是为了突破分区表中只能保存4个分区的限制而出现的，扩展分区不能直接使用，需要在扩展分区内划分一个或多个逻辑分区后才能使用。
2. 前4个分区(主分区或扩展分区)用数字1到4，逻辑分区从5开始，例如：`/dev/hda3`，是第一个 IDE 磁盘上第三个主分区或扩展分区；`/dev/sdb6` 是第二个 SCSI 硬盘上的第二个逻辑分区
3. **磁盘分区方案 - MBR**
    - Master Boot Record（主启动记录）
    - 它位于硬盘开始部分的一个特殊扇区，扇区内部包含已安装系统的启动加载器和硬盘内逻辑分割区的信息。在启动操作系统时，会从扇区内使用一段代码来启动系统。
    - 使用MBR磁盘分区表格的硬盘在计算机启动时，会先启动主板的 BIOS ，随后 BIOS 加载 MBR ，再从 MBR 启动操作系统
    - MBR 的局限性主要体现在三个方面:
        - MBR 只适用于最大容量 2T 的硬盘， 如果是更大容量的硬盘使用 MBR ，那么多出来部分则无法识别;
        - MBR只支持最大4个主分区，如果 要创建更多分区，就必须将一种一个主分区作为“扩展分区”，并在 其中创建逻辑分区。
        - 分区和引导数据都存储在同一个地方，如果这个数据被覆盖或损坏，用户将无法启动计算机
4. fdisk 是传统的 Linux 硬盘分区工具，也是 Linux 系统中最常用的一种硬盘分区工具之一，但不支持大于 2TB 的分区。
5. **磁盘分区方案 - GPT**
    - GPT 意为 GUID 分区表，驱动器上的每个分区都有一个全局唯一的标识符(globally unique identifier，GUID)，对于运行统一可扩展固件接口(UEFI) 固件的系统,GPT是在 物理硬盘上布置分区表的标准。
    - 没有主分区和逻辑分区之分，每个硬盘最多可以有 128 个分区，GPT 为逻辑块地址分配 64位 ，因此最大支持 18EB 的分区大小。
6. parted 是另一款在 linux 下常用的分区软件，可支持创建 2T 以上磁盘分区

### 逻辑卷管理
1. LVM-逻辑卷管理是 Linux 环境中对磁盘分区进行管理的一种机制，是建立在硬盘和分区之上、文件系统之 下的一个逻辑层，可提高磁盘分区管理的灵活性。
    - 物理单元（PE）：Physical Extends
    - 逻辑单元（LE）：Logical Extents
    - 物理卷（PV）：Physical Volume
    - 卷组（VG）：Volume Group
    - 逻辑卷（LV）：Logical Volume
2. 逻辑卷(lv)是将几个磁盘分区或者块设备(pv，pv可以位于不同的磁盘分区里，pv大小可以不一)组织起来形 成一个大的扩展分区(vg卷组，一个vg至少要包含一个pv)，该扩展分区不能直接用，需要将其划分成逻辑 卷(lv)才能使用，lv可以格式化成不同的文件系统，挂载后直接使用。

![](https://wyiyi.github.io/amber/contents/openEuler/02-1.png)

![](https://wyiyi.github.io/amber/contents/openEuler/02-2.png)

``` bash
# 将/dev/sdb、/dev/sdc创建为物理卷
$ pvcreate /dev/sdb /dev/sdc
# 显示物理卷/dev/sdb的基本信息
$ pvdisplay /dev/sdb
# 禁止分配/dev/sdb物理卷上的PE
$ pvchange -x n /dev/sdb
# 删除物理卷/dev/sdb
$ pvremove /dev/sdb
```
``` bash
# 创建卷组 vg1，并且将物理卷/dev/sdb和/dev/sdc添加到卷组中 
$ vgcreate vg1 /dev/sdb /dev/sdc 
# 显示卷组vg1的基本信息 
$ vgdisplay vg1 
# 将卷组vg1状态修改为活动。如果修改为非活动，则是-a n 
$ vgchange –a y vg1 
# 向卷组vg1中添加物理卷/dev/sdb 
$ vgextend vg1 /dev/sdb 
# 从卷组vg1中移除物理卷/dev/sdb2 
$ vgreduce vg1 /dev/sdb2 
# 删除卷组vg1 
$ vgremove vg1 
```
``` bash
# 在卷组vg1中创建10G大小的逻辑卷 
$ lvcreate -L 10G vg1 
# 在卷组vg1中创建200M的逻辑卷，并命名为lv1 
$ lvcreate -L 200M -n lv1 vg1 
# 显示逻辑卷lv1的基本信息 
$ lvdisplay /dev/vg1/lv1 
# 为逻辑卷/dev/vg1/lv1增加200M空间 
$ lvresize -L +200 /dev/vg1/lv1 
# 为逻辑卷/dev/vg1/lv1减少200M空间
$ lvresize -L -200 /dev/vg1/lv1 
# 为逻辑卷/dev/vg1/lv1增加100M空间 
$ lvextend -L +100M /dev/vg1/lv1 
# 将逻辑卷/dev/vg1/lv1的空间减少100M 
$ lvreduce -L -100M /dev/vg1/lv1 
# 删除逻辑卷/dev/vg1/lv1 
$ lvremove /dev/vg1/lv1 
# 
``` 


## 03 系统服务的配置和管理
### 系统服务基本概念
1. 所有的可用systemd unit类型，可在如下表所示的路径下查看

| 路径                        | 描述                         |
|---------------------------|----------------------------     |
| /usr/lib/systemd/system/  | 随安装的RPM产生的systemd units。   |
| /run/systemd/system/      | 在运行时创建systemd units。       |
| /etc/systemd/system/      | 由系统管理员创建和管理的systemd units。 |

2. systemd 提供按需启动能力
3. systemd 采用 cgroup 特性跟踪和管理进程的生命周期
4. 启动挂载点和自动挂载的管理
5. 实现事务性依赖关系管理
6. 与 SysV 初始化脚本兼容
7. 能够对系统进行快照和恢复

### 管理系统服务
1. systemd 提供 systemctl 命令来运行、关闭、重启、显示、启用/禁用系统服务。 `systemctl` 命令与 `sysvinit` 命令的功能类似。当前版本中依然兼容 service 和 chkconfig 命令， 但建议用 `systemctl` 进行系统服务管理。
```bash
# 显示当前正在运行的服务 
$ systemctl list-units --type service 
# 显示所有的服务(包括未运行的服务)，需要添加-all参数 
$ systemctl list-units --type service --all 
# 显示某个服务的状态 
$ systemctl status name.service 
# 鉴别某个服务是否运行 
$ systemctl is-active name.service 
# 判断某个服务是否被启用 
$ systemctl is-enabled name.service 
# 运行 httpd 服务，请在root权限下执行如下命令 
$ systemctl start httpd.service 
# 关闭蓝牙服务，请在root权限下执行如下命令 
$ systemctl stop bluetooth.service 
# 重启蓝牙服务,请在root权限下执行如下命令 
$ systemctl restart bluetooth.service 
# 在开机时启用某个服务，请在root权限下执行如下命令 
$ systemctl enable name.service 
# 在开机时禁用某个服务，请在root权限下执行如下命令 
$ systemctl disable name.service 
```
2. systemd 用目标(target) 替代了运行级别的概念，提供了更大的灵活性
```bash
# 查看当前系统默认的启动目标，命令如下: 
$ systemctl get-default 
# 查看当前系统所有的启动目标，命令如下: 
$ systemctl list-units --type=target 
# 改变系统默认的目标，在root权限下执行如下命令: 
$ systemctl set-default name.target 
# 改变当前系统的目标，在root权限下执行如下命令: 
$ systemctl isolate name.target 
```
3. 改变当前系统为救援模式，在 root 权限下执行如下命令:  `systemctl rescue`，这条命令和 `systemctl isolate rescue.target` 类似。
4. 改变当前系统为紧急模式，在 root 权限下执行如下命令: `systemctl emergency`，这条命令和 `systemctl isolate emergency.target` 类似。
5. 用户需要重启系统，才能从救援模式或者紧急模式进入正常模式
6. systemd 通过 `systemctl` 命令可以对系统进行关机、重启、休眠等一系列操作。当前仍兼容部分 Linux 常用管 理命令，对应关系如下表。建议用户使用 systemctl 命令进行操作。

| Linux常用管理命令      | systemctl命令        | 描述   |
|--------------------|------|----------------------  |
| halt  | systemctl halt     | 关闭系统 |
| poweroff    | systemctl poweroff | 关闭电源      |
| reboot   |  systemctl reboot     | 重启  |

7. 使用 systemctl 关闭或重启系统会给当前所有的登录用户发送一条提示消息。如果不想让 systemd 发送该消息，您可以添加 “--no-wall” 参数

```bash
# 使系统待机，在root权限下执行如下命令: 
$ systemctl suspend 
# 使系统休眠，在root权限下执行如下命令: 
$ systemctl hibernate 
# 使系统待机且处于休眠状态，在root权限下执行如下命令: 
$ systemctl hybrid-sleep 
```

### 任务管理
1. cron 系统调度进程。可以使用它在每天的非高峰负荷时间段运行作业，或在一周或一月中的不同时段运行。
2. at 命令。使用它在一个特定的时间运行一些特殊的作业，或在晚一些的非负荷高峰时间段或高峰负荷时间段运行。
3. & 使用它在后台运行一个占用时间不长的进程。
4. nohup 使用它在后台运行一个命令，即使在用户退出时也不受影响。
```bash
# 查看当前shell的后台的任务 
$ jobs
[1]- Running ping 9.xx.xx.195 > /dev/null & 
[2]+ Running sleep 100 & 
# "+"号代表最近一个放入后台的工作，也是工作恢复时默认恢复的工作。
# "-"号代表倒数第二个放入后台的工作，而第三个以后的工作就没有"+-"标志了。
```
5. 将正在运行的任务放入后台暂停，使用ctrl+z
6. `fg %job ID`: 将任务放入前台执行
7. `bg %job ID`: 将任务放入后台执行
8. 如果 fg 和 bg 后不加 job ID，表示对当前任务进行操作
9. 如果你正在运行一个进程，而且你觉得在退出帐户时该进程还不会结束，那么可以使用 nohup 命令
10. 如果使用 nohup 命令提交作业，那么在缺省情况下该作业的所有输出都被重定向到一个名 为 nohup.out 的文件中，除非另外指定了输出文件: `nohup command > myout.file 2>&1`


## 04 操作系统网络管理和防火墙
1. 通过 nmcli 配置网络
```bash
# 显示NetworkManager状态: 
$ nmcli general status 
# 显示所有连接状态:
$ nmcli connection show 
# 只显示当前活动连接，如下所示添加 -a, --active: 
$ nmcli connection show --active 
# 显示由NetworkManager识别到设备及其状态: 
$ nmcli device status 
# 使用nmcli工具启动和停止网络接口，在root权限下执行如下命令: 
$ nmcli connection up id em1 
$ nmcli device disconnect em1 
# 使用如下命令，NetworkManager将连接到对应网络设备，尝试找到合适的连接配置，并激活配置。 
$ nmcli device connect "$IFNAME" 
# 使用如下命令，NetworkManager将断开设备连接，并防止设备自动激活。 
$ nmcli device disconnect "$IFNAME" 
# 创建名为net-test的动态连接配置文件，在root权限下使用以下命令: 
$ nmcli connection add type ethernet con-name net-test ifname enp3s0
# 创建名为 net-static的静态连接配置文件，在root权限下使用以下命令:
$ nmcli con add type ethernet con-name net-static ifname enp3s0 ip4 192.168.0.10/24 gw4 192.168.0.254 
# 设定两个 IPv4 DNS 服务器地址，在root权限下使用以下命令: 
$ nmcli con mod net-static ipv4.dns "*.*.*.* *.*.*.*" 
# 使用nmcli命令为网络连接配置静态路由，使用命令如下:
$ nmcli connection modify enp3s0 +ipv4.routes "192.168.122.0/24 10.10.10.1" 
# 使用编辑器配置静态路由，使用如下命令:
$ nmcli con edit type ethernet con-name enp3s0 
```
2. 通过 ifcfg 文件配置的网络配置不会立即生效，需要在 root 权限下执行 **systemctl reload NetworkManager** 命令以重启网络服务后才生效
3. Ifcfg 配置文件在 `/etc/sysconfig/network-scripts/` 目录中
4. 使用 ip 命令配置的网络配置可以立即生效但系统重启后配置会丢失
```bash
# 在root权限下，配置设置IP地址，使用示例如下: 
$ ip address add 192.168.0.10/24 dev enp3s0 
# 查看配置结果，在root权限使用如下命令: 
$ ip addr show dev enp3s0 
```
5. ip 命令支持为同一接口分配多个地址，可在root权限下重复多次使用 ip 命令实现分配多个地址
6. 如果需要静态路由，可使用 ip route add 命令在路由表中添加，使用 ip route del 命令删除
7. **HOSTNAME 有三种类型：**
    - static: 静态主机名，可由用户自行设置，并保存在 /etc/hostname 文件中。
    - transient: 动态主机名，由内核维护，初始是 static 主机名，默认值为 “localhost”。可由 DHCP 或 mDNS 在运行时更改。
    - pretty: 灵活主机名，允许使用自由形式(包括特殊/空白字符)进行设置。静态/动态主机名遵从域名的通用限制。

```bash
# 查看当前的主机名，使用如下命令: 
$ hostnamectl status 
# 在root权限下，设定系统中的所有主机名，使用如下命令: 
$ hostnamectl set-hostname name 
# 当设定pretty主机名时，如果主机名中包含空格或单引号，需要使用引号。命令示例如下: 
$ hostnamectl set-hostname "Stephen's notebook" --pretty 
# 要清除特定主机名，并将其还原为默认形式，在root权限下，使用如下命令: 
$ hostnamectl set-hostname "" [option...] 
# 远程更改主机名，在远程系统中运行hostnamectl命令时，要使用-H，--host 选项，在root权限下使用如下命令: 
$ hostnamectl set-hostname -H [username]@hostname new_hostname 
```

```bash
# 激活开机启动防火墙服务: 
$ systemctl enable firewalld
# 启动和查看防火墙状态 
$ systemctl start firewalld
$ systemctl status firewalld
# 也可以通过防火墙命令来查看是否运行:
$ firewall-cmd --state
# 防火墙默认区域为public，查看默认区域方法如下: 
$ firewall-cmd --get-default-zone 
# 查看每个区域绑定的接口:
$ firewall-cmd --get-active-zones 
# 修改接口绑定的区域，例如将ens3从public修改为external: 
$ firewall-cmd --zone=external --change-interface=ens3 
# 如果只接入一个防火墙区域，可以直接修改默认区域: 
$ firewall-cmd --set-default-zone=external 
```


## 05 操作系统进程管理
1. 进程(Process) 是计算机中已运行程序的实体，是程序的一个具体实现。当程序被系统调用 到内存以后，系统会给程序分配一定的资源(内存，设备等等)然后进行一系列的复杂操作， 使程序变成进程以供系统调用。
   进程除包含程序的静态代码(text)，还包含堆(heap)、栈 (stack)、数据(data)段，堆用来在进程正在运行时分配所需的内存，栈用来保存临时数 据(如函数参数、返回地址、局部变量)，数据段用来保存已初始化的变量。
2. Linux 上进程有五种状态：
    - **运行(TASK_RUNNING):** 正在运行或在运行队列中等待。
    - **中断(TASK_INTERRUPTIBLE):** 休眠中， 受阻， 在等待某个条件的形成或接受到信号。
    - **不可中断(TASK_UNINTERRUPTIBLE):** 收到信号不唤醒和不可运行， 进程必须等待直到有中断发生。
    - **僵死(TASK_ZOMBIE):** 进程已终止， 但进程描述符存在， 直到父进程调用 wait4() 系统调用后释放。
    - **停止(TASK_STOPED):** 进程收到 SIGSTOP， SIGSTP， SIGTIN， SIGTOU信号后停止运行运行。
3. 进程状态变化

![](https://wyiyi.github.io/amber/contents/openEuler/05-1.png)

```bash
# 查看进程优先级
$ ps -l
 F S UID PID PPID C PRI NI ADDR SZ WCHAN TTY TIME CMD
 0 S 0 2465648 2465645 0 80 0 - 1905 - pts/2 00:00:00 bash 
 4 R 0 2472951 2465648 0 80 0 - 2249 - pts/2 00:00:00 ps 
```

4. **PRI，即进程的优先级，表示程序被CPU执行的先后顺序，值越小进程的优先级别越高。**
5. **NI，即 nice 值 ，表示进程可被执行的优先级的修正数值，可理解为“谦让度”。**
6. **进程的 nice 值不是进程的优先级，但是可以通过调整 nice 值可以影响进程的优先值。**
![](https://wyiyi.github.io/amber/contents/openEuler/05-2.png)
![](https://wyiyi.github.io/amber/contents/openEuler/05-3.png)
7. **对执行的命令 输出结果可以通过在 crontab 定时任务中都会在未尾带增加 >/dev/null 2>&1，来避免以上问题。**
![](https://wyiyi.github.io/amber/contents/openEuler/05-4.png)


## 06 文件和文件系统
### Linux 文件系统
1. 机械硬盘
    - 扇区是硬盘上存储的最小物理单位
    - 簇是此文件系统中 的最小存储单位
    - 柱面是系统分区的最小单位

![](https://wyiyi.github.io/amber/contents/openEuler/06-1.png)

2. Linux 的文件类型
    - 普通文件（-）
    - 目录文件（d, directory file）
    - 符号链接（l, symbolic link）
    - 块设备文件（b, block）和字符设备文件（c, char）：系统中的所有设备要么是块设备文件，要么是字符设备文件，无一例外。
    - FIFO（p, pipe）
    - 套接字（s, socket）
3. 文件系统的种类众多，而操作系统希望对用户提供一个统一的接口，于是在用户层与文件系统层引入 了中间层，这个中间层就称为虚拟文件系统(Virtual File System，VFS)。
4. VFS 定义了一组所有文件系统都支持的数据结构和标准接口，这样程序员不需要了解文件系统的工作 原理，只需要了解 VFS 提供的统一接口即可。

![](https://wyiyi.github.io/amber/contents/openEuler/06-2.png)

5. 在 Linux 系统中， 一个文件可以分成几个数据块存储在分区内。为了搜集各数据块，我们需要该文件对应的inode。每个文件对 应一个 inode。这个 inode 中包含多个指针，指向属于该文件各个数据块。当操作系统需要读取文件时，只 需要找到对应 inode，收集分散的数据块，就可以收获我们的文件了。
6. inode既可以表示普通文件，也可以表示目录，那么肯定 要有一种方法来区分它到底是普通文件还是目录。这个就 是通过inode中的数据块来区分的。
7. 普通文件的inode的数据块是指向普通文件自己的数据的
8. 目录的inode的数据块是指向位于该目录下的目录项的

```bash
# 获取inode中的信息:stat 文件名 
$ stat zabbix
# 查看每个硬盘分区的inode总数和已经使用的数量 
$ df -i
# 查看文件名对应的inode号码: ls –i 文件名 
$ ls -i zabbix/
```

### 管理 Linux 文件系统

```bash
# 查看文件系统的磁盘空间占用情况 
$ df -h
# 查询文件或目录的磁盘使用空间
$ du * -sh
# 可在root权限下通过mkfs命令创建文件系统 
$ mkfs -t ext4 /dev/vg1/lv1 
# 查看，文件系统类型 
$ df -T
# 显示系统打开的文件 
$ lsof /home
# 挂载文件系统 
$ mount /dev/vg1/lv1 /mnt/data 
# 查询逻辑卷的UUID 
$ blkid /dev/vg1/lv1 
# 
```

1. fsck命令检查文件系统并尝试修复错误
2. tune2fs命令允许系统管理员调整“ext2/ext3”文件系统中的可该参数
3. 手动挂载的文件系统仅在当时有效，一旦操作系统重启则会不存在

### Linux 文件和目录管理
1. 标准文件:stdin, stdout, stderr 对应的文件描述符为0,1,2
2. 输出重定向: > (覆盖导入)， >>(从文件末尾导入)
3. 输入重定向: <


## 07 用户和群组
### 管理用户和组
1. 每个用户都会分配一个特有的id号-uid。
2. 用户在登录系统时是通过UID来区分用户，而不是通过用户名来区分
3. 超级用户 也称为root用户，它的 **UID为0**
4. 普通用户:也称为一般用户， 它的 **UID 为1000-60000 之间**
5. 虚拟用户:也称为系统 用户，它的 **UID为1-999** 之间，虚拟用户最大的特点是不提供密码登录系统，它们的存在主要是为了方便系统的管理
6. 查看UID命令: id [option] [user_name]
7. 与用户账号信息有关的文件如下:
    * /etc/passwd:用户账号信息文件。
    * /etc/shadow:用户账号信息加密文件。
    * /etc/group:组信息文件。
    * /etc/default/useradd:定义默认设置文件。
    * /etc/login.defs:系统广义设置文件。
    * /etc/skel:默认的初始配置文件目录。
    * /etc/gshadow:组信息加密文件
8. **useradd** 命令可用来创建用户账号，并保存在/etc/passwd文件中。
9. **usermod** 可用来修改用户账号的各类信息。
10. **userdel** 用于删除指定的用户以及与该用户相关的文件。
11. **passwd** 用来修改用户的密码。
12. 在添加账户时，默认情况下会同时建立一个与用户同名且UID和GID相同的组; GID与UID都会将0赋予给超级用户或者具有超级用户的用户组(也就是root用户组); 系统会预留一些较前的GID给虚拟用户(也称为系统用户)。
13. **groupadd** 可用来创建一个新的用户组，并将新用户组信息添加到系统文件中。
14. **groupmod** 可用来更改群组识别码或者名称。
15. **groupdel** 可用来删除用户组，但若是用户组中包含一些用户，需先删除掉用户后再 删除用户组
16. **gpasswd** 可以用来添加或删除用户到组中。
17. /etc/passwd文件每一行由七个字段的数据组成，且字段之间用“:”隔开

![](https://wyiyi.github.io/amber/contents/openEuler/07-1.png)

18. /etc/shadow文件只有超级用户(root用户)具有读权限，其他用户均没有权限，从而保证了用户密码的安全性。

![](https://wyiyi.github.io/amber/contents/openEuler/07-2.png)

### 文件权限管理
1. 在Linux中，每个文件或目录都有一组共有9个基础权限位，每三位字符分为一组， 它们分别是所属用户权限位，用户组权限位，其他用户权限位。

![](https://wyiyi.github.io/amber/contents/openEuler/07-3.png)
![](https://wyiyi.github.io/amber/contents/openEuler/07-4.png)

2. chmod命令:修改文件权限。 使用权限:文件所有者。
3. chown命令:修改文件属主属组(只允许管理员)。
4. chgrp命令:修改文件属组。 使用权限:管理员(root用户)。
5. umask命令:遮罩码。 通过umask命令可以指定在建立文件时进行权限掩码的预设; 使用权限:管理员和普通用户。

### 其他权限管理
- 在切换用户身份时，常常用到的命令有三种:
    * su:此命令在切换用户时，仅切换root用户身份，但shell环境仍为普通用户;
    * su –:此命令在切换用户时，用户身份和shell环境都会切换为root用户;
    * sudo:此命令可以允许普通用户执行管理员账户才能执行的命令。


## 08 操作系统日志管理
1. 常用系统日志
    - dmesg：记录系统在开机时内核检测过程所产生的信息
    - /var/log/wtmp or /var/log/faillog：记录正确(wtmp)与错误(faillog)登陆系统者的账户信息, last命令就是读取wtmp文件来获取的
    - /var/log/btmp：记录错误登陆日志,这个文件是二进制的,不能使用cat命令查看,而要使用lastb命令查看.
    - /var/run/utmp：记录当前一登陆用户的信息,同样不能使用cat命令查看,而要使用w,who,users命令来查询.
    - /var/log/lastlog：记录了系统上面所有账户最近一次登陆系统时的相关信息,lastlog命令就是读取这个文件里的记录来显示的.
    - /var/log/secure：只要涉及到需要用户名和密码的操作,那么当登陆系统时(不论正确错误),都会记录到这里.
    - /var/log/messages：系统发生的错误信息,或者重要信息都会被记录在这里
    - /var/log/malilog or /var/log/mail/*：记录着邮件的往来信息,默认是postfix邮件服务器的一些信息.
2. rsyslog的全称是rocket-fast system for log
    * 当前主流linux操作系统均使用rsyslog服务管理(对应旧版本的syslog服务)系统日志，它可以用于:
    * rsyslog守护进程配置为服务器运行，接收来自各种来源的输入
    * 转换过滤格式化输出
3. rsyslog守护进程配置为客户端运行，将结果输出到不同的目的地（本地或者远端日志服务器）
4. rsyslog 特点：
    * 多线程。输入多线程、输出多线程等
    * 可以通过多种协议进行传输。UDP、TCP、RELP、SSL、TLS
    * 支持加密协议。ssl、tls、relp
    * 强大的过滤器，实现过滤日志信息中任何部分内容
    * 自定义输出格式
    * 可将日志写入到数据库
5. Facility(产生日志的设施，从功能和程序上对日志收集进行分类)在rsyslog中指定了产生日志消息的子系 统 ，severity代表日志的严重级别：

| Numerical code | Severity                 |    
|--------------------------|----------------------|
| 0              | Emergency: 会导致系统不可用的严重信息 |
| 1              | Alert: 必须马上处理的警告信息       |
| 2              | Critical: 比较严重的信息        |
| 3              | Error: 错误信息              |
| 4              | Warning: 警告信息       |
| 5              | Notice: 不影响正常功能，需要注意的信息        |
| 6              | Info: 一般信息             |
| 7              | Debug: 程序或系统调试信息 |

6. rsyslog 特性：
    * **属性替代**：常用的属性有：msg（消息体）、hostname、pri（消息等级和类别）、time（时间 相关），属性以$开头的是从本地系统获得的变量、不带$是从消息中获得的变量。语法格式：%propname:fromChar:toChar:options:fieldname%
    * **模板** template：模板的功能是定义输出格式，或者定义omfile模块的动态路径、动态文件。语法格式：$template t_msg, “%msg\n%”
    * **过滤规则**：rsyslog可以使用syslog标准的过滤规则，新增了扩展规则。过滤规则与模板组合使用：$template tmp_message, “%msg\n%” ；更复杂的过滤规则（做rainerscript的脚本语言）：startwith、contains、%（取余）等。
7. rsyslog的消息流从输入模块->预处理模块->主消息队列->过滤模块->动作队列->输出模块。
8. 输入模块主要有imjournal、imuxsock、imudp、imtcp等；
9. 过滤模块主要有jsonparse、normalize等；
10. 输出模块主要有omfile、omfwd（默认会配置，发送到UDP及TCP端口）等。
11. 日志经过rsyslog处理的过程中会经过两个队列，一个是主消息队列(main message queue)，另 一个是动作队列(action queue)。使用队列的作用，一是加速，二是可靠。
12. rsyslog 服务主要组成：
    - 主程序: /usr/sbin/rsyslogd
    - 主配置文件:/etc/rsyslog.conf
    - 服务脚本: /usr/lib/systemd/system/rsyslog.service
13. linux中一般使用logrotate服务把旧文件删除或压缩备份，并创建新的日志文件，达到日志转储的目的


## 09 常见故障定界定位

```bash
# 查看系统版本信息
$ uname -a
$ cat /etc/os-release
# 查看系统硬件信息, 详细信息使用lspci -s xx:yy.z(busnumber) -vvv查询 
$ lspci 
# 查看CPU信息
$ lscpu
# 查看网卡控制器型号 
$ lspci | grep -i eth 
# 显示网卡当前速率和链接状态 
$ ethtool enp125s0f0
# 显示网卡驱动和FW信息 
$ ethtool -i enp125s0f0
# 显示每块网卡收发包状态 
$ sar -n DEV 1
```

1. **messages 日志**：messages日志位于/var/log路径下，其中messages是记录当前系统日志的文件， 其他形如messages-YYYYMMDD的文件是历史日志信息。一般通过系统**异常的时间点**或者**关键字**在messages日志中查找相关信息进行分析。
2. **dmesg 日志**：dmesg日志只记录本次启动之后的信息，但较messages更详细。内核或应用软件bug发生的情况下大多有如下形式的calltrace(栈回溯信息)记录，可用于问题定位
3. **kdump 日志**：触发panic的情况下，在/var/crash目录下会生成以**问题发生时间点命名**的文件夹，其下有**vmcore文件**(即kdump) 以及vmcore-dmesg.txt文件。vmcore-dmesg文件包含calltrace信息，可用于基本的问题定界。


## 10 SSH 管理及安全
1. SSH配置文件目录存放于/etc/ssh，SSH服务端主要的配置文件有sshd_config
2. /usr/bin/ssh是SSH远程登录客户端
3. /usr/bin/scp是远程文件拷贝程序，用于非交互模式文件拷贝
4. /usr/bin/sftp是远程安全文件传输程序，常用于交互模式文件传输


## 11 shell 脚本
1. 默认的 Shell 可以在 /bin/sh 查看，在/etc/passwd 中修改

```bash
# 查看系统支持的shell: 
$ cat /etc/shells 
# 查看当前登陆用户默认shell 
$ echo $SHELL 
# 查看当前的shell 
$ echo $0
```

2. Shell 脚本只是静态的代码，若要输出结果，还需要解释器的参与。一般在脚本的第一行，指定执行此脚本的解释器。如果不指定解释器，脚本也能在默认的解释器中正常运行，但出于规范和安全的考虑，建议 指定如下:

```bash
#!/bin/bash 
#!/bin/csh
```

3. 有时候一些脚本执行时间较长，命令行界面会被占用，因此可以采取后台运行脚本:  `./my_script.sh &`。这种方法在退出 Shell 后，脚本进程会随之终止，为了保证脚本一直运行，可以采用:  nohup `./my_script.sh &` 脚本的的标准输出和标准错误会重定向到 nohup.out 文件里
4. Linux 的每个进程启动时，会打开三个文本流的端口:标准输入、标准输出、标准错误。这三个端口对应着一个程序的输入、输出和异常的抛出
5. 输入重定向格式: `command < inputfile` 将右边的文件作为标准输入，然后传入左边的命令。例: `wc -l < /dev/null`
6. 内联输入重定向格式: `command << maker`。输入重定向需要文件，而内联输入重定向可以使用即时输入的文本作为标准输入，传入左边的命令。右边的字符“maker”作为标志，表示标准输入的开始和结束，自身不包含在标准输入里。

```bash
[root@openEuler ~]# less << EOF 
> item 1
> item 2
> item 3 
> EOF
item 1
item 2
item 3
(END) 
```

7. 管道实际上是进程间通信(IPC)的一种方式
8. Shell 中的变量是无类型的
9. 在 Linux Shell 中，变量主要有两大类: 环境变量、用户定义变量
10. 每种类型的变量依据作用域不同，又分为全局变量和局部变量。全局变量作用在整个 Shell 会话及其子 Shell、局部变量作用在定义它们的进程及其子进程内
11. 使用 printenv 查看全局变量；使用 set 查看某个特定进程中的所有变量，包括局部变量、全局变量以及用户定义变量
12. 在 .bash_profile 或 .bashrc 中添加 export 语句，永久修改变量
13. Shell 运算符 **：求幂
14. If then else 语句格式：

```bash
if [ 条件 ] 
then 命令 
elif [ 条件 ] 
then 命令 
else 命令 
fi 
```
```bash
if [ 条件 ]; then 
    命令 
elif [ 条件 ]; then 
    命令 
else 命令 
fi 
```

15. Bash Shell 会先执行 if 后面的语句，如果其退出状态码为 0，则会继续执行 then 部分的命 令，否则会执行脚本中的下一个命令
16. case 语法：

```bash
# case命令会将指定的变量与不同模式进行比较，如果变量和模式是匹配的，那么shell会执行该模式下的命令
case variable in
 # 可以通过竖线操作符(|)在一行中分隔出多个模式模式
 pattern1 | pattern2) commands1;;
 # ;;表示模式下命令结束
 pattern3) commands2;;
 # *星号会捕获所有与已知模式不匹配的值
 *) default commands;; 
# esac作为case语句结束符 
esac
```

17. for 语法

```bash
# Shell 风格
for var in list 
do 
    commands
done 
# 例: 
for i in {1..10}
do 
    printf "$i\n"
done 
# C 语言风格
for ((var assignment ; condition ; iteration process))
do 
    commands
done 
# 例: 
for (( i = 1; i < 10 ; i++))
do 
    echo “Hello”
done 
```

18. while命令判断测试命令返回， 只有测试命令返回的值为0，循环体中命令才会执行，否则while循环退出。
19. until命令和while命令工作的方式完全相反。until命令测试命令返回非0， bash shell才会执行循环中的命令。一旦测试命令返回0，循环就结束了。
20. 脚本上激活调试模式,请向脚本第一行中的命令解释器中添加 -x 选项，如 #!/bin/bash -x
21. 每个命令返回一个退出状态，也通常称为返回状态或退出代码
22. echo $? 显示上一个命令的退出码


## 12 操作系统启动管理
1. Linux 下查看系统引导方式：查看linux下是否有 “/sys/firmware/efi”目录，如果不存在，则说明启动方式是 Legacy ( BIOS )；如果存在，则说明启动方式是UEFI

![](https://wyiyi.github.io/amber/contents/openEuler/12-1.png)

3. MBR 是不属于任何一个操作系统， 可以通过dd命令进行 MBR的读取、写入、删除等操作。

# 随堂测试
## 01 系统安装概述
1. openEuler的网络方式安装依赖PXE和Kickstart() **B** <br>
   A、对 <br>
   B、错 <br>

2. 选择自动化安装时，在“Start boot option”界面按下()按键可选择从网络 pxe启动，开始自动化安装? **A** <br>
   A、 F2 <br>
   B、 F4 <br>
   C、 F5 <br>
   D、 F8 <br>

3. 在安装引导界面，按()键可进入已选选项的参数编辑界面，按()键可进入命令行模式?  **C**  **A** <br>
   A、c <br>
   B、d <br>
   C、e <br>
   D、f <br>

4. openEuler的发布件包括哪些?() **ABCDE** <br>
   A、ISO发布包 <br>
   B、虚拟机镜像 <br>
   C、容器镜像 <br>
   D、嵌入式镜像 <br>
   E、Repo源 <br>

## 02 物理存储及逻辑卷管理
1. 磁盘分区有以下哪几种类型? (多选题) **ABC** <br>
   A. 主分区 <br>
   B. 扩展分区 <br>
   C. 逻辑分区 <br>
   D. 物理分区 <br>

2. mount /dev/sda5 /test 将/dev/sda5挂载test目录中，重启后不失效。(判断题) **B** <br>
   A. 对 <br>
   B. 错 <br>

3. 将分区/dev/hdb6格式化的命令是哪个? (单选题) **A** <br>
   A. mkfs -t ext4 /dev/hdb6 <br>
   B. format -t ext4 /dev/hdb6 <br>
   C. format /dev/hdb6 <br>
   D. makefile -t ext4 /dev/hdb6 <br>

4. 逻辑卷缩减有风险，所以要卸载并强行检测文件系统。(判断题) **B**  <br>
   A. 对 <br>
   B. 错 <br>

## 03 系统服务的配置和管理
1. 所有的可用systemd unit类型有以下哪些路径?(多选题) **ABD**  <br>
   A. /usr/lib/systemd/system/  <br>
   B. /run/systemd/system/  <br>
   C. /opt/systemd/system/  <br>
   D. /etc/systemd/system/  <br>

2. systemd不兼容/etc/fstab文件。(判断题) **B**  <br>
   A. 对  <br>
   B. 错  <br>

3. 设置httpd服务开机时启动用下列哪个命令?（单选题） **A**  <br>
   A. systemctl enable httpd.service  <br>
   B. systemctl enabled httpd.service  <br>
   C. systemctl start httpd.service  <br>
   D. systemctl disenable httpd.service  <br>

4. 执行systemctl status gdm.service可以查看Main PID  **A**  <br>
   A. 对 <br>
   B. 错 <br>

5. 什么命令可查看当前shell的后台的任务? (单选题) **C** <br>
   A. cat <br>
   B. vim <br>
   C. jobs <br>
   D. bg <br>

6. at 命令可以只指定时间，也可以时间和日期一起指定。(判断题) **A** <br>
   A. 对 <br>
   B. 错 <br>

## 04 操作系统网络管理和防火墙
1. nmcli 配置网络通常包括以下几个步骤(多选题)  **BC** <br>
   A. 连接网络设备 <br>
   B. 设置IP <br>
   C. 激活IP <br>
   D. 重启网络 <br>

2. nmcli配置网络IP地址后需要激活才能生效。(判断题)  **A** <br>
   A. 对 <br>
   B. 错 <br>

3. 通过ifcfg文件配置的网络时，以下参数必须配置(多选题)  **BCD**<br>
   A. TYPE<br>
   B. PREFIX/NETMASK<br>
   C. IPADDR<br>
   D. DEVICE<br>

4. ifcfg配置文件保存在以下哪个目录。(单选题)  **D** <br>
   A. /etc <br>
   B. /etc/network <br>
   C. /etc/sysconfig/network <br>
   D. /etc/sysconfig/network-scripts/ <br>

5. 以下关于IP命令功能的说法，错误的是(单选题)  **C** <br>
   A. 配置IP地址 <br>
   B. 配置路由 <br>
   C. 配置主机名 <br>
   D. 查看网络 <br>

6. 使用IP命令配置网络，重启操作系统后依然生效。(判断题)  **B** <br>
   A. 对 <br>
   B. 错 <br>

7. HOSTNAME包括以下几种类型 (多选题)  **ABD** <br>
   A. static <br>
   B. transient <br>
   C. dynamic <br>
   D. pretty <br>

8. hostnamectl修改主机名后直接生效。(判断题)  **A** <br>
   A. 对 <br>
   B. 错 <br>

9. 系统中防火墙的默认区域是(多选题) **B** <br>
   A. drop <br>
   B. Public <br>
   C. external <br>
   D. internal <br>

10. 防火墙区域中public比external更受信任。(判断题)  **B** <br>
    A. 对 <br>
    B. 错 <br>

## 05 操作系统进程管理
1. 以下进程状态正确的是(多选题)  **ABCD** <br>
   A. TASK_RUNNING <br>
   B. TASK_INTERRUPTIBLE <br>
   C. TASK_UNINTERRUPTIBLE <br>
   D. TASK_STOPED <br>

2. kill命令可以结束所有进程。 (判断题)  **A** <br>
   A. 对 <br>
   B. 错 <br>

3. 下列哪个命令可以动态查看主机进程信息?(单选题)  **B** <br>
   A. ps <br>
   B. top <br>
   C. free <br>
   D. lscpu <br>

4. 以下哪个符号用于创建后台执行进程(单选题)  **B** <br>
   A. @ <br>
   B. & <br>
   C. | <br>
   D. $ <br>

5. 后台进程可以使用Ctrl+C快捷键终止。(判断题)  **B** <br>
   A. 对 <br>
   B. 错 <br>

6. 以下进程状态正确的是对于进程优先级说明正确的是。(多选题)  **AD** <br>
   A. 实时进程优先级是:0-99 <br>
   B.实时进程优先级是: 100-139 <br>
   C. 非实时进程优先级是:0-99 <br>
   D.非实时进程优先级是: 100-139 <br>

7. 进程优先级PRI值越大说明优先级越低。 (判断题)  **A** <br>
   A. 对 <br>
   B. 错 <br>

8. 定时任务参数时间设置支持以下哪些时间间隔设置。(多选题)  **ABCD** <br>
   A. minute <br>                                  
   B. hour <br>
   C. day <br>
   D. month <br>

9. 对于cron定时任务一般会接结尾加上“>/dev/null 2>&1”。 (判断题)  **A** <br>
   A. 对 <br>
   B. 错 <br>

## 06 文件和文件系统
1. 下列关于 inode 的描述正确的是? (多选题)  **ACD** <br>
   A. 在 Linux 中，文件系统中管理的每个对象(文件或目录)表示为一个 inode <br>
   B. 1个 inode 中包含1个指针 <br>
   C. 普通文件的inode的数据块指向普通文件自己的数据 <br>
   D. 目录的inode的数据块指向位于该目录下的目录项 <br>

2. Linux 使用 mkfs 命令来创建文件系统。(判断题)  **A** <br>
   A. 对 <br>
   B. 错 <br>

3. 下面那个命令显示inode信息而非块使用量? (单选题)  **A** <br>
   A. df -i <br>
   B. df -h <br>
   C. du -a <br>
   D. du -h <br>

4. lsof即可显示系统打开的文件。(判断题)  **A** <br>
   A. 对 <br>
   B. 错 <br>

5. 下面那个命令可以跨主机复制文件? （单选题）  **C** <br>
   A. cp <br>
   B. mv <br>
   C. scp <br>
   D. copy <br>

6. 输出重定向可以在文件末尾增量导入。（判断题）  **A** <br>
   A. 对 <br>
   B. 错 <br>

## 07 用户和群组
1. 用户和用户组的关系,哪些是正确的? （多选题） **ABCD** <br>
   A. 一对一 <br>
   B. 一对多 <br>
   C. 多对一 <br>
   D. 多对多 <br>

2. 以下哪一个命令可以创建新用户组?（单选题）  **A** <br>
   A. groupadd <br>
   B. groupmod <br>
   C. groupdel <br>
   D. ls group <br>

3. 使用chmod命令修改test1文件权限：chmod 777 test1，修改后用户对文件权限是? （单选题）  **D** <br>
   A. 可读 <br>
   B. 可写 <br>
   C. 可操作 <br>
   D. 可读可写可操作 <br>

4. 关于chgrp命令 的说法，哪个是正确的。（单选题）  **B** <br>
   A. 控制文件被何人调用 <br>
   B. 可以对文件或目录的所属群组进行更改 <br>
   C. 将特定文件的所有者更改为指定用户或组 <br>
   D. 可以指定在建立文件时进行权限掩码的预设 <br>

5. 在openEuler中，默认情况下，以下哪个UID隶属于普通用户? （单选题） **D** <br>
   A. 0 <br>
   B. 300 <br>
   C. 900 <br>
   D. 1200 <br>

6. 以下哪一个命令可以用来查看用户和组相关联文件中的信息？（单选题）  **A** <br>
   A. cat <br>
   B. chmod <br>
   C. clear <br>
   D. chage <br>

## 08 操作系统日志管理
1. dmesg命令可以查看系统开机过程中产生的信息? （判断题）  **A** <br>
   A. 对 <br>
   B. 错 <br>

2. openEuler操作系统中，常用于日志转储的服务是？ （单选题） **B** <br>
   A. rsyslog <br>
   B. logrotate <br>
   C. audit <br>
   D. cron <br>

3. rsyslog服务器接收客户端日志的配置，通常port设置成？（单选题） **D** <br>
   A. 22 <br>
   B. 67 <br>
   C. 123 <br>
   D. 514 <br>

4. rsyslog服务器接收客户端日志的配置，可以支持（）协议。（多选题）  **AB** <br>
   A. TCP <br>
   B. UDP <br>
   C. ICMP <br>
   D. SMT <br>

## 09 常见故障定界定位
1. 查看网卡发包速率使用哪个命令? （单选题）  **B** <br>
   A. ethtool <br>
   B. sar <br>
   C. lspci <br>
   D. ethtool -i <br>

2. message日志比dmesg日志更详细，calltrace栈回溯信息存在于message日志中。（判断题）  **B** <br>
   A. 对 <br>
   B. 错 <br>

3. 系统重启后需要收集哪些日志? （多选题） **ABCD** <br>
   A. message日志 <br>
   B. kdump <br>
   C. dmesg <br>
   D. 串口日志 <br>

4. CPU比较高的时候，top和以下哪种命令配合使用来定位故障？（单选题） **C** <br>
   A. sar <br>
   B. ps aux <br>
   C. iotop <br>
   D. free <br>

## 10 SSH管理及安全
1. 下面哪个套件不是搭建SSH服务必须的：（单选题）  **B** <br>
   A、openssh; <br>
   B、openssh-askpass; <br>
   C、openssh-server； <br>
   D、openssh-clients <br>

2. 下面哪个工具不是SSH客户端工具：（单选题）  **C** <br>
   A、ssh； <br>
   B、scp； <br>
   C、rsync； <br>
   D、sftp <br>

3. 下面哪个不是SSH客户端配置：（单选题）  **A** <br>
   A、/etc/ssh/sshd_config <br>
   B、/etc/ssh/ssh_config; <br>
   C、~/.ssh/config <br>
   D、/etc/ssh/ssh_config.d/05-redhat.con <br>

## 11 shell脚本
1. Shell的功能包含：（多选题） **ABC** <br>
   A.用户界面，提供用户与内核交互接口 <br>
   B.命令解释器 <br>
   C.提供编译环境 <br>
   D.提供各种管理工具，应用程序 <br>

2. 当前主流的Linux系统默认都是bash（判断题） **A** <br>
   A. 对 <br>
   B. 错 <br>

3. i= 5 <br>
   echo $[--i] <br>
   输出的结果是什么：（单选题） **B** <br>
   A. 3 <br>
   B. 4 <br>
   C. 5 <br>
   D. 6 <br>

4. 在 Linux Shell 中，变量主要分为全局变量和局部变量： （判断题）  **A** <br>
   A. 对 <br>
   B. 错 <br>

5. 将程序的输出追加到文件中使用以下哪种符号 ：（单选题）  **D** <br>
   A. < <br>
   B. << <br>
   C. > <br>
   D. >> <br>

6. Linux 的每个进程启动时，会打开哪三个文本流的端口 （多选题） **BCD** <br>
   A. 标准字符 <br>
   B. 标准输入 <br>
   C. 标准错误 <br>
   D. 标准输出 <br>

7. 使用以下哪个命令时，只有测试命令返回的值为0，循环体中命令才会执行，否则循环退出。 （单选题）  **A** <br>
   A. While <br>
   B. until <br>
   C. for <br>
   D. break <br>

8. Bash Shell 会先执行 if 后面的语句，如果其退出状态码为非 0，则会继续执行 then 部分的命： （判断题）  **B** <br>
   A. 对 <br>
   B. 错 <br>

9. 以下哪些属于编写Shell时的良好风格。 （多选题）  **ABCDE** <br>
   A. 将长命令分解为多行更小的代码块 <br>
   B. 将多个语句的开头和结尾排好 <br>
   C. 对包含多行语句的行进行缩进 <br>
   D. 使用行间距分隔命令块以阐明一个代码段何时结束以及另一个代码段何时开始 <br>
   E. 在整个脚本中通篇使用一致的格式 <br>

10. 在脚本的第一行的命令解释器添加+x选项可以打开脚本调试模式： （判断题）  **A** <br>
    A. 对 <br>
    B. 错  <br>

## 12 操作系统启动管理
1. 在openEuler中查看系统引导方式？ **ABC** <br>  
   A. 查看linux下是否有 “/sys/firmware/efi”目录 <br>
   B. 如果不存在，则说明启动方式是Legacy ( BIOS ) <br>
   C. 如果存在，则说明启动方式是UEFI <br>

2. 如何设置系统从救援模式启动？（多选题）  **AD** <br>
   A. systemctl isolate rescue.target <br>
   B. systemctl isolate emergency.target <br>
   C. systemctl emergency <br>
   D. systemctl rescue <br>

3. 系统的rsyslog服务是否随开机自启动。（判断题）  **A** <br>
   A. 对 <br>
   B. 错 <br>