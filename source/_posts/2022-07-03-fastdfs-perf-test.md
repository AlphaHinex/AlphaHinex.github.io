---
id: fastdfs-perf-test
title: "FastDFS 性能测试"
description: "使用自带工具进行性能测试"
date: 2022.07.03 10:34
categories:
    - FastDFS
tags: [FastDFS]
keywords: FastDFS, 性能测试, tracker, storage, nginx
cover: /contents/fastdfs-perf-test/cover.jpeg
---

# FastDFS 简介

[FastDFS](https://github.com/happyfish100/fastdfs) 是一个开源的分布式文件存储系统。

> FastDFS 类似 Google FS，属于应用级文件系统，不是通用的文件系统，只能通过专有 API 访问。 —— [FastDFS架构及特点介绍](https://mp.weixin.qq.com/s/CTix6wgSE1neQgVgdeXSrA)

代码库中相关文档并不是很多，可以关注上面链接中的作者公众号（FastDFS分享与交流）或微信（fastdfs）了解更多信息。本节大部分内容也摘自作者公众号中的文章 [FastDFS架构和设计理念解读](https://mp.weixin.qq.com/s/WV0sKwE5Ct7Y6WUvqh8EOw) 及其他文章。

## 架构

> FastDFS 的架构如下图所示：
> ![](/contents/fastdfs-perf-test/cover.jpeg)

FastDFS 只有两个角色：`tracker` 和 `storage`。

> Tracker server 作为中心结点，管理集群拓扑结构，其主要作用是负载均衡和调度。

> Storage server 在其他文件系统中通常称作 Trunk Node 或 Data Node。Storage server 直接利用 OS 的文件系统存储文件。

FastDFS 在 Google Code 的 [wiki](https://code.google.com/archive/p/fastdfs/wikis/Overview.wiki) 中，有文件上传下载流程的图片链接，但链接已经失效了。在 [什么是fastdfs,原理,上传下载流程](https://www.likecs.com/show-204532453.html) 里有两张疑似副本：

文件上传流程：

![](/contents/fastdfs-perf-test/upload.png)

文件下载流程：

![](/contents/fastdfs-perf-test/download.png)

## 存储形式

> FastDFS 不会对文件进行分块存储，客户端上传的文件和 Storage server 上的文件一一对应（V3 引入的小文件合并存储除外）。

> 为了防止一个目录下的文件数过多影响访问性能，FastDFS 采用两级目录来保存文件。每一级目录最大 256 个子目录（默认配置为 256，可以酌情改小），两级目录对应的存储目录数为 256 * 256 = 65536。如果平均一个目录下保存 1k 个文件，那么存储的文件总数将超过 6kw。 —— [FastDFS的三大误解](https://mp.weixin.qq.com/s/e9bZkJhoQKatYVFvSp8aLg)

## 集群

> FastDFS 集群中的 Tracker server 也可以有多台，Tracker server 和Storage server 均不存在单点问题。Tracker server 之间采用 Leader-Follower 机制，基本是对等关系，组内的 Storage server 之间也是对等关系。

> FastDFS 采用了分组存储方式。集群由一个或多个组构成，集群存储总容量为集群中所有组的存储容量之和。一个组由一台或多台存储服务器组成，同组内的多台 Storage server 之间是类似 RAID1 的互备关系，同组存储服务器上的文件是完全一致的。文件上传、下载、删除等操作可以在组内任意一台 Storage server 上进行。类似木桶短板效应，一个组的存储容量为该组内存储服务器容量最小的那个，由此可见组内存储服务器的软硬件配置最好一致。

> 为了相互备份，一个group的storage server通常有两台即可。如果对数据可靠性要求很苛刻，一个group可以有三台甚至更多storage server。因一个group内的storage server对文件采用冗余备份的RAID1方式，文件写入性能不会随storage server的增加而增加，理论上文件读取性能随着storage server的增加而线性增加。—— [FastDFS集群部署指南](https://mp.weixin.qq.com/s/oRNpXStNhqwhxnUO8iDErQ)

> 采用分组存储方式的好处是灵活、可控性较强。比如上传文件时，可以由客户端直接指定上传到的组。一个分组的存储服务器访问压力较大时，可以在该组增加存储服务器来扩充服务能力（纵向扩容）。当系统容量不足时，可以增加组来扩充存储容量（横向扩容）。采用这样的分组存储方式，可以使用 FastDFS 对文件进行管理，使用主流的 Web server 如apache、nginx 等进行文件下载。

## FastDFS Nginx 扩展模块

按照上面文件上传下载流程所示，client 通过 tracker 可以直接获得 storage 的连接信息，client 直接连接 storage 完成文件的上传下载操作。那么为什么还需要这个 Nginx 扩展模块呢？

FastDFS 的 Nginx 扩展模块 [fastdfs-nginx-module](https://github.com/happyfish100/fastdfs-nginx-module) 和 Apache 扩展模块 [fastdfs-apache-module](https://github.com/happyfish100/fastdfs-apache-module) 的主要作用，都是为 FastDFS 中存储的文件提供一种 HTTP 下载文件的方式。

> 对于互联网应用，FastDFS 的标准使用姿势：通过 FastDFS API 进行文件上传等更新操作，storage server 上通过 FastDFS nginx 扩展模块使用 HTTP 方式下载文件。FastDFS 的文件名由 storage server 通过算法生成，生成的文件名中包含时间戳、文件大小、文件内容 CRC32 校验码、随机数等，因此 FastDFS 生成的文件名是完全离散的，客户端无法野蛮遍历或穷举。由此可见，storage server 上部署的 HTTP 服务完全可以直接暴露到公网，提供给客户端浏览器访问。—— [FastDFS安全注意事项](https://mp.weixin.qq.com/s/GI8AksoshH_h_PmrFFgxzA)

> 使用 FastDFS 扩展模块可以解决文件异步复制带来延迟导致文件访问不到的问题。如果请求文件在当前 storage 上不存在，通过文件 ID 反解出源 storage 的 ID 或 IP 地址，直接请求源 storage。请求源storage server有两种模式：代理（proxy）和HTTP重定向（redirect），在配置文件mod_fastdfs.conf中设置，配置项为 response_mode，建议配置为 proxy模式。—— [FastDFS nginx扩展模块介绍](https://mp.weixin.qq.com/s/nvAtTpPppUoAul44aX6xAA)

关于 `proxy` 和 `redirect` 两种模式的区别，在 [mod_fastdfs.conf](https://github.com/happyfish100/fastdfs-nginx-module/blob/master/src/mod_fastdfs.conf) 注释的解释如下：

```conf
# response mode when the file not exist in the local file system
## proxy: get the content from other storage server, then send to client
## redirect: redirect to the original storage server (HTTP Header is Location)
response_mode=proxy
```


# 安装

本文以 FastDFS [v5.11](https://github.com/happyfish100/fastdfs/tree/V5.11) 版本为例，可参考发布包中的 [INSTALL](https://github.com/happyfish100/fastdfs/blob/V5.11/INSTALL) 文档步骤进行编译安装，或使用 [delron/fastdfs](https://hub.docker.com/r/delron/fastdfs) Docker 镜像部署。

> 若需在 Docker 中运行其他版本的 FastDFS，可考虑参照 `delron/fastdfs` [镜像层](https://hub.docker.com/layers/delron/fastdfs/latest/images/sha256-9583cb80170c153bc12615fd077fe364a8fd5a95194b7cf9a8a32d2c11f8a49d?context=explore) 中的指令编写 Dockerfile，或者试试官方仓库从 `v5.12` 版本开始加入的 [docker 文件夹](https://github.com/happyfish100/fastdfs/tree/V5.12/docker) 中的 Dockerfile。


# 测试

完成 FastDFS 的安装部署后，可使用其自带的测试工具进行基本的功能测试及性能测试。

## 功能测试

### 准备工作

以使用 `delron/fastdfs` 镜像为例，可在容器中，查看 `fdfs_` 前缀的命令，及 FastDFS 版本：

```bash
# 拉取镜像
$ docker pull delron/fastdfs
# 启动一个容器
$ docker run --name fastdfs-perf-test -d --rm delron/fastdfs tracker
3d62dcc9ae1632262283dc45f1a743721dd445cb0ab8f616f63781cd7ac51867
# 进入容器
$ docker exec -ti fastdfs-perf-test bash
# 通过 tab 键补全
[root@3d62dcc9ae16 nginx-1.12.2]# fdfs_
fdfs_append_file      fdfs_appender_test1   fdfs_delete_file      fdfs_file_info        fdfs_storaged         fdfs_test1            fdfs_upload_appender
fdfs_appender_test    fdfs_crc32            fdfs_download_file    fdfs_monitor          fdfs_test             fdfs_trackerd         fdfs_upload_file
# 查看版本
[root@3d62dcc9ae16 nginx-1.12.2]# fdfs_test
This is FastDFS client test program v5.11

Copyright (C) 2008, Happy Fish / YuQing

FastDFS may be copied only under the terms of the GNU General
Public License V3, which may be found in the FastDFS source kit.
Please visit the FastDFS Home Page http://www.csource.org/
for more detail.

Usage: fdfs_test <config_file> <operation>
	operation: upload, download, getmeta, setmeta, delete and query_servers
```

可使用此容器作为 FastDFS 的客户端，进行相关的测试工作。需先修改 `/etc/fdfs/client.conf` 文件中的 `tracker_server` 配置，以便能够连接到目标 FastDFS 服务。

### 上传文件

将 `payload_file` 文件上传至 `client.conf` 文件中指定的 `tracker_server`：

```bash
$ fdfs_upload_file /etc/fdfs/client.conf payload_file
group1/M00/00/00/Cul4amK7_-eARegtAAAw1Kehtx89877162
```

之后按照上传后返回的文件 ID，可在 storage 节点的数据存储路径中（如 `/var/fdfs/data`），找到上传的这个文件：`/var/fdfs/data/00/00/Cul4amK7_-eARegtAAAw1Kehtx89877162` 。

### 下载文件

根据上传文件时返回的文件 ID `group1/M00/00/00/Cul4amK7_-eARegtAAAw1Kehtx89877162` 下载文件：

```bash
$ fdfs_download_file /etc/fdfs/client.conf group1/M00/00/00/Cul4amK7_-eARegtAAAw1Kehtx89877162
```

### 删除文件

```bash
$ fdfs_delete_file /etc/fdfs/client.conf group1/M00/00/00/Cul4amK7_-eARegtAAAw1Kehtx89877162
```

## 性能测试

### 准备工作

性能测试相关工具，源码在 [test](https://github.com/happyfish100/fastdfs/tree/V5.11/test) 路径中，需要单独再进行一下编译。为避免缺少相关依赖而报错，可在 FastDFS 部署环境，或上面创建的 `fastdfs-perf-test` 容器里进行编译：

```bash
# 将 FastDFS 源码包拷贝至容器内
$ docker cp /Users/alphahinex/Downloads/fastdfs-5.11.zip fastdfs-perf-test:/opt/fdfs/fastdfs
$ docker exec -ti fastdfs-perf-test bash
[root@3d62dcc9ae16 nginx-1.12.2]# cd /opt/fdfs/fastdfs/
[root@3d62dcc9ae16 fastdfs]# unzip fastdfs-5.11.zip
[root@3d62dcc9ae16 fastdfs]# cd fastdfs-5.11/test/
[root@3d62dcc9ae16 test]# make
cc -g -Wall -O -D_FILE_OFFSET_BITS=64 -DDEBUG -c -o common_func.o common_func.c  -I/usr/local/include -I/usr/include/fastdfs -I/usr/include/fastcommon
cc -g -Wall -O -D_FILE_OFFSET_BITS=64 -DDEBUG -c -o dfs_func_pc.o dfs_func_pc.c  -I/usr/local/include -I/usr/include/fastdfs -I/usr/include/fastcommon
cc -g -Wall -O -D_FILE_OFFSET_BITS=64 -DDEBUG -o gen_files gen_files.c  common_func.o dfs_func_pc.o -L/usr/local/lib -lfdfsclient -lfastcommon -I/usr/local/include -I/usr/include/fastdfs -I/usr/include/fastcommon
cc -g -Wall -O -D_FILE_OFFSET_BITS=64 -DDEBUG -o test_upload test_upload.c  common_func.o dfs_func_pc.o -L/usr/local/lib -lfdfsclient -lfastcommon -I/usr/local/include -I/usr/include/fastdfs -I/usr/include/fastcommon
cc -g -Wall -O -D_FILE_OFFSET_BITS=64 -DDEBUG -o test_download test_download.c  common_func.o dfs_func_pc.o -L/usr/local/lib -lfdfsclient -lfastcommon -I/usr/local/include -I/usr/include/fastdfs -I/usr/include/fastcommon
cc -g -Wall -O -D_FILE_OFFSET_BITS=64 -DDEBUG -o test_delete test_delete.c  common_func.o dfs_func_pc.o -L/usr/local/lib -lfdfsclient -lfastcommon -I/usr/local/include -I/usr/include/fastdfs -I/usr/include/fastcommon
cc -g -Wall -O -D_FILE_OFFSET_BITS=64 -DDEBUG -o combine_result combine_result.c  common_func.o dfs_func_pc.o -L/usr/local/lib -lfdfsclient -lfastcommon -I/usr/local/include -I/usr/include/fastdfs -I/usr/include/fastcommon
```

编译成功后，会得到 `combine_result`、`gen_files`、`test_delete`、`test_download`、`test_upload` 这几个二进制可执行文件，将其安装至 `/bin` 路径：

```bash
[root@3d62dcc9ae16 test]# make install
mkdir -p /bin
cp -f gen_files test_upload test_download test_delete combine_result /bin
```

### 上传文件

```bash
# 先通过 gen_files 生成测试用的文件
$ gen_files
done.
$ ls *M *K
100M  10M  1M  200K  50K  5K
# 测试上传，等待十个测试进程结束
$ ./test_upload.sh
proccess 5, time used: 34s
proccess 6, time used: 37s
proccess 4, time used: 37s
proccess 9, time used: 41s
proccess 7, time used: 44s
proccess 8, time used: 45s
proccess 2, time used: 49s
proccess 0, time used: 49s
proccess 1, time used: 49s
proccess 3, time used: 49s
# 进入 upload 路径
$ cd upload
# 合并各线程执行数据，显示总体测试结果
$ combine_result 10
total_count=65560, success_count=65560, success ratio: 100.00% time_used=43s, avg time used: 0ms, QPS=1524.65

file_type total_count success_count time_used(s) avg(ms) QPS success_ratio
5K 50000 50000 19 0 2631.58 100.00
50K 10000 10000 4 0 2500.00 100.00
200K 5000 5000 2 0 2500.00 100.00
1M 500 500 1 2 500.00 100.00
10M 50 50 1 35 50.00 100.00
100M 10 10 9 937 1.11 100.00

IO speed = 88325 KB
ip_addr  total_count success_count time_used(s) avg(ms) QPS success_ratio
10.233.94.67 21854 21854 4 0 5463.50 100.00
10.233.120.106 21853 21853 28 1 780.46 100.00
10.233.94.202 21853 21853 6 0 3642.17 100.00
```

> 注意：为避免产生垃圾数据，执行过上传测试之后，需配套执行删除测试。未清理之前的测试文件之前，不要重复执行上传测试！

### 下载文件

```bash
$ ./test_download.sh
proccess 4, time used: 300s
proccess 6, time used: 300s
proccess 3, time used: 300s
proccess 17, time used: 300s
proccess 13, time used: 300s
proccess 2, time used: 300s
proccess 18, time used: 300s
proccess 1, time used: 300s
proccess 7, time used: 300s
proccess 0, time used: 300s
proccess 8, time used: 300s
proccess 5, time used: 300s
proccess 15, time used: 300s
proccess 9, time used: 300s
proccess 16, time used: 300s
proccess 14, time used: 300s
proccess 10, time used: 300s
proccess 11, time used: 300s
proccess 12, time used: 300s
proccess 19, time used: 300s

$ cd download

$ combine_result 20
total_count=1390134, success_count=1390134, success ratio: 100.00% time_used=300s, avg time used: 0ms, QPS=4633.78

file_type total_count success_count time_used(s) avg(ms) QPS success_ratio
5K 1060134 1060134 179 0 5922.54 100.00
50K 211329 211329 39 0 5418.69 100.00
200K 107168 107168 24 0 4465.33 100.00
1M 10574 10574 10 1 1057.40 100.00
10M 799 799 5 6 159.80 100.00
100M 130 130 6 52 21.67 100.00

IO speed = 232074 KB
ip_addr  total_count success_count time_used(s) avg(ms) QPS success_ratio
10.233.120.106 463388 463388 170 0 2725.81 100.00
10.233.94.202 463342 463342 47 0 9858.34 100.00
10.233.94.67 463404 463404 47 0 9859.66 100.00
```

> 注意：测试下载时，会将下载请求分散到相同 group 的所有 storage 节点中，需保证 storage 节点已经完成数据同步后再进行下载，避免出现负载到的节点还没有同步到上传的文件就响应下载请求，导致文件不存在的异常。

### 删除文件

```bash
$ ./test_delete.sh
proccess 3, time used: 20s
proccess 6, time used: 20s
proccess 8, time used: 20s
proccess 7, time used: 20s
proccess 2, time used: 20s
proccess 0, time used: 20s
proccess 4, time used: 20s
proccess 5, time used: 20s
proccess 1, time used: 20s
proccess 9, time used: 20s

$ cd delete

$ combine_result 10
total_count=65560, success_count=65560, success ratio: 100.00% time_used=20s, avg time used: 0ms, QPS=3278.00

file_type total_count success_count time_used(s) avg(ms) QPS success_ratio
5K 50000 50000 12 0 4166.67 100.00
50K 10000 10000 2 0 5000.00 100.00
200K 5000 5000 1 0 5000.00 100.00
1M 500 500 0 0 0.00 100.00
10M 50 50 0 0 0.00 100.00
100M 10 10 0 0 0.00 100.00

IO speed = 189900 KB
ip_addr  total_count success_count time_used(s) avg(ms) QPS success_ratio
10.233.94.67 21854 21854 4 0 5463.50 100.00
10.233.120.106 21853 21853 6 0 3642.17 100.00
10.233.94.202 21853 21853 4 0 5463.25 100.00
```

> 注意：删除文件测试，需要在上传文件测试之后执行。删除时 **会** 根据上传脚本生成的 `upload` 路径中保存的文件 ID 进行删除，**不会** 删除原本 FastDFS 中的非测试文件。


# 参考资料

* [FastDFS压力测试](https://blog.csdn.net/xiaofei0859/article/details/52808896)
* [FastDFS-Nginx扩展模块源码分析](https://www.cnblogs.com/littleatp/p/4361318.html)