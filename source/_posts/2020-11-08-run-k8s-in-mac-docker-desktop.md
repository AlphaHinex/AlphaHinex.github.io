---
id: run-k8s-in-mac-docker-desktop
title: "在 Mac 的 Docker Desktop 中运行 K8s"
description: "想变成 running 并不容易"
date: 2020.11.08 10:34
categories:
    - K8s
tags: [K8s, Docker Desktop]
keywords: Docker Desktop for Mac, K8s, starting, running, pki, mirror
cover: /contents/k8s-starting/versions.png
---

[Docker Desktop for Mac](https://docs.docker.com/docker-for-mac/) 从 [Docker Community Edition 18.06.0-ce-mac70 2018-07-25](https://docs.docker.com/docker-for-mac/release-notes/#docker-community-edition-18060-ce-mac70-2018-07-25) 版本起，添加了对 Kubernetes 的支持，可以方便的在 Mac 上运行一个单节点的 K8s 集群。

在 Docker Desktop 的 `Preferences` 中的 `Kubernetes` 页面里，提供了一个 `Enable Kubernetes` 选框，点击之后即可在 Mac 上启动 K8s。

然而点击之后，就没有然后了，一直是下图这个状态：

![starting](/contents/k8s-starting/starting.jpg)

此问题的主要原因，是 K8s 运行所需的一些 `k8s.gcr.io` 下的镜像，无法直接下载得到。

## 准备镜像

### 配置镜像服务

在 `Preferences` => `Docker Engine` 里，可以配置 `registry-mirrors`，国内可用的一些镜像服务有：

* 中国科大：https://docker.mirrors.ustc.edu.cn / https://ustc-edu-cn.mirror.aliyuncs.com
* 阿里云：https://\<xxxxx>.mirror.aliyuncs.com，可使用阿里云账号在 [这里](https://cr.console.aliyun.com/cn-hangzhou/instances/mirrors) 获得
* 网易云：https://hub-mirror.c.163.com
* DaoCloud：http://f1361db2.m.daocloud.io

> 另外，中国科大还有 [GCR](https://github.com/ustclug/mirrorrequest/issues/91) 和 [Quay](https://github.com/ustclug/mirrorrequest/issues/135) 的镜像。

可添加多个镜像，如：

```json
{
  "registry-mirrors": [
    "https://xxxxx.mirror.aliyuncs.com",
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "http://f1361db2.m.daocloud.io"
  ],
  "debug": true,
  "experimental": true
}
```

之后点击 `Apply & Restart` 应用配置。

### 下载镜像

在 [阿里云容器服务的 GitHub 组织](https://github.com/AliyunContainerService) 下，有个 [k8s-for-docker-desktop](https://github.com/AliyunContainerService/k8s-for-docker-desktop) 仓库即为解决此问题而存在。解决的方式为：先从阿里云下载所需的镜像副本至本地，再将镜像 tag 修改至 `k8s.gcr.io` 下。

以如下软件版本为例：

![versions](/contents/k8s-starting/versions.png)

可使用 [当前](https://github.com/AliyunContainerService/k8s-for-docker-desktop/tree/28caeb743b4f1e7b0c70ce24469a7d735de81efc) master 分支最新的内容，直接执行 `load_images.sh` 完成镜像的下载及 tag 修改。

下载之后的镜像包括如下 8 个，与 [images.properties](https://github.com/AliyunContainerService/k8s-for-docker-desktop/blob/28caeb743b4f1e7b0c70ce24469a7d735de81efc/images.properties) 中内容一一对应：

```bash
$ docker images
REPOSITORY                                                       TAG                                              IMAGE ID            CREATED             SIZE
k8s.gcr.io/kube-proxy                                            v1.19.3                                          cdef7632a242        3 weeks ago         118MB
k8s.gcr.io/kube-apiserver                                        v1.19.3                                          a301be0cd44b        3 weeks ago         119MB
k8s.gcr.io/kube-controller-manager                               v1.19.3                                          9b60aca1d818        3 weeks ago         111MB
k8s.gcr.io/kube-scheduler                                        v1.19.3                                          aaefbfa906bd        3 weeks ago         45.7MB
k8s.gcr.io/etcd                                                  3.4.13-0                                         0369cf4303ff        2 months ago        253MB
k8s.gcr.io/coredns                                               1.7.0                                            bfe3a36ebd25        4 months ago        45.2MB
k8s.gcr.io/pause                                                 3.2                                              80d28bedfe5d        8 months ago        683kB
quay.io/kubernetes-ingress-controller/nginx-ingress-controller   0.26.1                                           29024c9c6e70        13 months ago       483MB
```

### 其他版本？

如果使用的不是上图中的版本，且 `k8s-for-docker-desktop` 仓库还没有支持该版本时，可根据 K8s 版本通过如下方式获得 `images.properties` 中对应版本信息：

安装 K8s 对应版本的 [kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/) ，之后运行：

```bash
# 替换 ${KUBERNETES_VERSION} 为所使用的 K8s 版本
$ ./kubeadm config images list --kubernetes-version=${KUBERNETES_VERSION}
```

可得到类似如下信息：

```text
k8s.gcr.io/kube-apiserver:v1.19.3
k8s.gcr.io/kube-controller-manager:v1.19.3
k8s.gcr.io/kube-scheduler:v1.19.3
k8s.gcr.io/kube-proxy:v1.19.3
k8s.gcr.io/pause:3.2
k8s.gcr.io/etcd:3.4.13-0
k8s.gcr.io/coredns:1.7.0
```

也可参照这个 [entrypoint.sh](https://github.com/maguowei/actions/blob/master/k8s-image-sync/entrypoint.sh) 中的 [内容](https://github.com/maguowei/actions/blob/master/k8s-image-sync/entrypoint.sh#L3-L10) ，或直接从 [这个](https://github.com/gotok8s/gotok8s/actions) 定期执行的 GitHub Actions 记录中找到对应版本执行时的输出信息，如 [v1.19.3 记录](https://github.com/gotok8s/gotok8s/runs/1367596287?check_suite_focus=true#step:3:15)。

根据所得到的对应版本镜像信息，修改 `images.properties` 文件中内容，再执行 `load_images.sh` 即可。

## 依旧 Starting ？

在完成镜像下载并重启 Docker Desktop 之后，K8s 依旧停留在 Starting 状态。

通过

```bash
$ pred='process matches ".*(ocker|vpnkit).*"
  || (process in {"taskgated-helper", "launchservicesd", "kernel"} && eventMessage contains[c] "docker")'
/usr/bin/log stream --style syslog --level=debug --color=always --predicate "$pred"
```

查看日志，发现不断输出如下内容：

```log
2020-11-07 01:01:48.307809+0800  localhost com.docker.driver.amd64-linux[2646]: cannot get lease for master node: an error on the server ("") has prevented the request from succeeding (get leases.coordination.k8s.io docker-desktop)
2020-11-07 01:01:48.308417+0800  localhost com.docker.backend[1833]: external: POST /events 200 "DockerDesktopGo" ""
2020-11-07 01:01:49.231052+0800  localhost com.docker.driver.amd64-linux[2646]: (libsystem_info.dylib) [com.apple.network.libinfo:getaddrinfo] nat64_v4_requires_synthesis(127.0.0.1) == false
```

按照 [这里](https://github.com/docker/for-win/issues/3769#issuecomment-486046718) 及 [这里](https://github.com/AliyunContainerService/k8s-for-docker-desktop/issues/78#issuecomment-661802062) 提到的方式，删除掉 `pki` 文件夹：

```bash
$ rm -rf ~/Library/Group\ Containers/group.com.docker/pki/
```

之后再重启并观察日志，上述问题不再出现，并且新下载了 3 个 desktop 相关的镜像：

```bash
$ docker images | grep desktop
docker/desktop-kubernetes                                        kubernetes-v1.19.3-cni-v0.8.5-critools-v1.17.0   7f85afe431d8        3 weeks ago         285MB
docker/desktop-storage-provisioner                               v1.1                                             e704287ce753        7 months ago        41.8MB
docker/desktop-vpnkit-controller                                 v1.0                                             79da37e5a3aa        8 months ago        36.6MB
```

等待一会之后，终于变成 Running 状态了！

![running](/contents/k8s-starting/running.png)

> Tips: 如果还是 Starting 状态，可以尝试将当前安装的 Docker Desktop 环境都清理掉，全新安装一个稳定版本，可能就不会有奇怪的问题了。

> 另外，在没开启 `Preferences` => `Kubernetes` 中的 `Show system containers (advanced)` 选项时，`docker ps` 是看不到 K8s 相关的容器的。
