---
id: huawei-kunpeng-redis-docker-image
title: "华为鲲鹏下可用的 Redis docker 镜像"
description: "自己动手丰衣足食"
date: 2020.09.06 10:26
categories:
    - Docker
tags: [Docker, Redis, Arm]
keywords: Docker, Redis, Arm64, 华为, kunpeng, 鲲鹏
cover: /contents/redis-arm-image/cover.png
---

在华为鲲鹏服务器下，使用 Docker 时，因鲲鹏服务器使用的芯片为 ARM 架构，镜像也需要使用 ARM 版本的。

从 x86 架构拉取的镜像直接导出导入到鲲鹏服务器上是不可以直接使用的。

可以通过 `docker inspect IMAGE_NAME` 查看镜像的架构类型。

在鲲鹏服务器上重新拉取镜像，会自动下载 ARM 架构的镜像，前提是需要有提供 ARM 架构的版本，如：

![Redis Official Image](/contents/redis-arm-image/redis-image.png)

但在鲲鹏服务器上，使用官方提供的 ARM64 版本的 Redis 镜像，启动时会报如下异常：

```bash
<jemalloc>: Unsupported system page size
```

从 Docker Hub 上试了一些有提供 ARM 版本的 Redis 镜像，基本都是相同的问题。唯一一个好用的镜像好像只有 Redis 4.x 的版本。

查找了一些资料，在华为云论坛上也有提到类似的问题：

* [在鲲鹏上通过docker上部署redis5.0.9时报错](https://bbs.huaweicloud.com/forum/thread-64268-1-1.html)
* [Centos下启动redis官方容器报错处理办法](https://bbs.huaweicloud.com/forum/thread-47123-1-1.html)

解决办法是需要在目标服务器上自行构建一个镜像。

为了给懒人提供一个方便，这里先提供一个已经构建好的，鲲鹏服务器上可用的 Redis 5.0.9 版本的镜像文件：https://gitee.com/AlphaHinex/trunk/blob/master/docker-library/redis/5.0/redis-kunpeng-5.0.9.tar.gz

如需自行构建，可参考如下构建步骤。

## 获取官方镜像的 Dockerfile

如：https://github.com/docker-library/redis/tree/master/5.0

## 根据实际情况进行调整

比如更换国内更快的 apt-get 数据源

```dockerfile
RUN sed -i s@/deb.debian.org/@/mirrors.163.com/@g /etc/apt/sources.list
RUN apt-get clean
```

> 阿里云的 debian 镜像中 arm 相关的包不全，可使用 163 的镜像

如果在代理网络环境下，可以添加代理相关配置，以及网络不稳定时可提前下载好所需资源，`COPY` 到镜像中，如：

```diff
10a14,17
>         echo "Acquire::http::Proxy \"http://user:pwd@proxy.com:8080\";" >/etc/apt/apt.conf; \
>         echo "Acquire::https::Proxy \"http://user:pwd@proxy.com:8080\";" >>/etc/apt/apt.conf; \
>         export http_proxy=http://user:pwd@proxy.com:8080; \
>         export https_proxy=http://user:pwd@proxy.com:8080; \
14,17c21,26
< 	dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')"; \
< 	wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch"; \
< 	wget -O /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch.asc"; \
< 	export GNUPGHOME="$(mktemp -d)"; \
---
> 	dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')"
>
> COPY gosu-arm64 /usr/local/bin/gosu
> COPY gosu-arm64.asc /usr/local/bin/gosu.asc
>
> RUN export GNUPGHOME="$(mktemp -d)"; \
35a45,48
>         echo "Acquire::http::Proxy \"http://user:pwd@proxy.com:8080\";" >/etc/apt/apt.conf; \
>         echo "Acquire::https::Proxy \"http://user:pwd@proxy.com:8080\";" >>/etc/apt/apt.conf; \
>         export http_proxy=http://user:pwd@proxy.com:8080; \
>         export https_proxy=http://user:pwd@proxy.com:8080; \
47c60
< 	wget -O redis.tar.gz "$REDIS_DOWNLOAD_URL"; \
---
> 	wget -O redis.tar.gz "$REDIS_DOWNLOAD_URL" --no-check-certificate; \
```

调整后完整的 Dockerfile 文件可见：https://gitee.com/AlphaHinex/trunk/blob/master/docker-library/redis/5.0/Dockerfile

## 执行构建

在 Dockerfile 所在路径执行 `docker build -t redis-kunpeng:5.0.9 .`，即可构建出新的镜像。

> 导出镜像为离线文件时，可使用 `docker save > redis-kunpeng-5.0.9.tar redis-kunpeng:5.0.9`

> 将离线镜像文件导入，可使用 `docker load < redis-kunpeng-5.0.9.tar`
