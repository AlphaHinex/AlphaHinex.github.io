---
id: install-k8s-cluster-offline-with-kubeasz
title: "使用 kubeasz 离线安装 k8s 集群"
description: "一键部署 so easy"
date: 2020.10.04 10:26
categories:
    - Cloud
    - DevOps
    - Docker
tags: [Cloud, DevOps, Docker, K8s]
keywords: Kubernetes, K8s, Ansible, Cluster, Offline, kubeasz
cover: /contents/covers/kubeasz.png
---

[kubeasz](https://github.com/easzlab/kubeasz) 将 k8s 集群的部署难度降低到了傻瓜相机的级别。
本文以 [kubeasz v2.2.1](https://github.com/easzlab/kubeasz/tree/2.2.1) 为例，介绍一下使用 kubeasz 离线安装 k8s 集群的方式。

## 下载离线安装所需内容

在一个可联网的环境，按 [离线安装集群](https://github.com/easzlab/kubeasz/blob/master/docs/setup/offline_install.md) 文档中内容，将所需文件都下载到本地：

```bash
# 下载工具脚本 easzup，举例使用 kubeasz 版本 2.2.1
$ export release=2.2.1
$ curl -C- -fLO --retry 3 https://github.com/easzlab/kubeasz/releases/download/${release}/easzup
$ chmod +x ./easzup
# kubeasz v2.2.1 默认使用 docker 版本 `19.03.8`，k8s 版本 `1.18.3`
# 如需更换版本，可使用 ./easzup -D -d 19.03.5 -k v1.18.2
# 下载默认版本离线安装包
$ ./easzup -D
# 下载离线系统软件包
$ ./easzup -P
```

执行成功后，所有文件均已整理好放入目录 `/etc/ansible` 。

离线文件包括：

* `/etc/ansible` 包含 kubeasz 版本为 ${release} 的发布代码
* `/etc/ansible/bin` 包含 k8s/etcd/docker/cni 等二进制文件
* `/etc/ansible/down` 包含集群安装时需要的离线容器镜像
* `/etc/ansible/down/packages` 包含集群安装时需要的系统基础软件

离线文件不包括：

* 管理端 ansible 安装，但可以使用 kubeasz 容器运行 ansible 脚本
* 其他更多 kubernetes 插件镜像

为防止出现在 kubeasz 容器无法 ping 通集群中其他主机的情况，也可以考虑打包个离线安装版本的 [ansible](https://www.ansible.com/)，可参考如下路径组织离线安装包内容：

```tree
├── ansible
│   ├── PyYAML-3.10-11.el7.x86_64.rpm
│   ├── ansible-2.6.18-1.el7.ans.noarch.rpm
│   ├── install.sh
│   ├── libyaml-0.1.4-11.el7_0.x86_64.rpm
│   ├── python-babel-0.9.6-8.el7.noarch.rpm
│   ├── python-backports-1.0-8.el7.x86_64.rpm
│   ├── python-backports-ssl_match_hostname-3.5.0.1-1.el7.noarch.rpm
│   ├── python-cffi-1.6.0-5.el7.x86_64.rpm
│   ├── python-enum34-1.0.4-1.el7.noarch.rpm
│   ├── python-httplib2-0.9.2-1.el7.noarch.rpm
│   ├── python-idna-2.4-1.el7.noarch.rpm
│   ├── python-ipaddress-1.0.16-2.el7.noarch.rpm
│   ├── python-jinja2-2.7.2-4.el7.noarch.rpm
│   ├── python-markupsafe-0.11-10.el7.x86_64.rpm
│   ├── python-netaddr-0.7.5-9.el7.noarch.rpm
│   ├── python-paramiko-2.1.1-9.el7.noarch.rpm
│   ├── python-ply-3.4-11.el7.noarch.rpm
│   ├── python-pycparser-2.14-1.el7.noarch.rpm
│   ├── python-setuptools-0.9.8-7.el7.noarch.rpm
│   ├── python-six-1.9.0-2.el7.noarch.rpm
│   ├── python2-cryptography-1.7.2-2.el7.x86_64.rpm
│   ├── python2-jmespath-0.9.0-3.el7.noarch.rpm
│   ├── python2-pyasn1-0.1.9-7.el7.noarch.rpm
│   └── sshpass-1.06-2.el7.x86_64.rpm
├── easzup
└── k8s-1.18.3-offline.tar
```

* `ansible/install.sh` 中内容为 `ls *.rpm |xargs -n1 rpm -ivh --nodeps`，可安装该路径下所有 rpm 文件
* `easzup` 为基于 kubeasz 2.2.1 版本内容，将安装调整为离线安装的版本，可参照 [fork 仓库](https://github.com/AlphaHinex/kubeasz) offline 分支内容
* `k8s-1.18.3-offline.tar` 为 `/etc/ansible` 内容打包

以上内容打包进 `kubeasz-2.2.1-offline.tar`，作为本次安装使用的离线包。

可从百度网盘获得此离线安装包：

链接: https://pan.baidu.com/s/1xtL9EYldFrpUrANB9tBlpQ 提取码: `xx2r`

## 部署环境准备

本文使用 [VirtualBox](https://www.virtualbox.org/) 创建虚拟机，系统使用 [CentOS 7 x86_64](http://isoredirect.centos.org/centos/7/isos/x86_64/) `Minimal` 版本，1核1G 配置，网络连接方式选用 `桥接网卡`。

完成第一个虚拟机的安装后，启动并进入系统，开启网络服务：

```bash
# 修改配置文件
$ vi /etc/sysconfig/network-scripts/ifcfg-enp0s3
```

找到选项 ONBOOT，默认为 `no`，将其设置为 `yes`，之后使用 `reboot` 重启。

重启后可通过 `ip addr` 命令查看 IP 地址。

完成上述配置后，可将此虚拟机作为模板，快速复制出部署集群环境所需的虚拟机。

## 设置 hostname

为方便起见，可先为每台虚拟机设置 hostname：

```bash
# 设置 hostname 为 k8s-m1
$ hostnamectl set-hostname k8s-m1
```

## 集群规划及安装

假设准备了四个主机：

- 192.168.1.2
- 192.168.1.3
- 192.168.1.4
- 192.168.1.5

选取一个主机作为安装节点，解压初始化：

```bash
$ tar zxvf kubeasz-2.2.1-offline.tar && cd kubeasz-2.2.1-offline
$ ./easzup -S
```

> 以上命令执行完毕后，离线安装包及解压出来的路径均可以清理掉，因为所有内容已经被复制到 `/etc/ansible` 路径下了，之后使用的也是 `/etc/ansible` 路径下内容。

安装节点执行以下命令，依次分发安装节点公钥至 k8s 集群节点（***含安装节点***，**部署时需换为实际IP**） 根据提示输入 `yes` 与节点 root 口令：

```bash
$ ssh-copy-id root@192.168.1.2
$ ssh-copy-id root@192.168.1.3
$ ssh-copy-id root@192.168.1.4
$ ssh-copy-id root@192.168.1.5
```

> 注意：ssh-copy-id 操作 *必须* 也包含安装节点本身！

### AIO (All in One)

单节点集群模式将主节点安装在安装节点上，可先使用此模式快速开始，之后再通过增加节点的方式扩展集群。

在确保在安装节点执行过 `./easzup -S` 及 `ssh-copy-id` 后，可使用下面命令安装单节点集群

```bash
$ docker exec -it kubeasz easzctl start-aio
```

### Cluster

预先对集群进行了规划时，可按下述方式直接部署好 k8s 集群。

先复制并调整多节点配置文件：

```bash
$ cp /etc/ansible/example/hosts.multi-node /etc/ansible/hosts
```

调整配置文件内容，`etcd` 一般为奇数（建议三个，存储 k8s 节点信息及元数据）

```text
[etcd]
192.168.1.2 NODE_NAME=etcd1
192.168.1.3 NODE_NAME=etcd2
192.168.1.4 NODE_NAME=etcd3

# master node(s)
[kube-master]
192.168.1.2

# work node(s)
[kube-node]
192.168.1.3
192.168.1.4
192.168.1.5

# [optional] ntp server for the cluster
[chrony]
192.168.1.2
```

分发及安装各节点（在安装节点执行）

```bash
$ ansible-playbook /etc/ansible/90.setup.yml
```

等待安装完成。。。

> 注意：以上所有操作均在安装节点执行即可。

如果一切顺利，上述命令均可正常执行。之后可在集群各节点查看集群状态：

```bash
$ kubectl get node
```

> 注意：非安装节点使用 `kubectl` 等命令若提示不存在，重新 ssh 登录一下即可。

### [管理 MASTER 节点](https://github.com/easzlab/kubeasz/blob/master/docs/op/op-master.md)

#### 增加 master 节点

首先配置 ssh 免密码登录新增节点，然后执行 (假设待增加节点为 192.168.1.11)：

```bash
# dir: /etc/ansible/tools
$ easzctl add-master 192.168.1.11
```

之后可使用 `kubectl get node` 进行验证

#### 删除 master 节点

```bash
# dir: /etc/ansible/tools
$ easzctl del-master 192.168.1.11 # 假设待删除节点 192.168.1.11
```

### [管理 NODE 节点](https://github.com/easzlab/kubeasz/blob/master/docs/op/op-node.md)

#### 增加 node 节点

首先配置 ssh 免密码登录新增节点，然后执行 (假设待增加节点为 192.168.1.11)：

```bash
# dir: /etc/ansible/tools
$ easzctl add-node 192.168.1.11
```

#### 删除 node 节点

```bash
# dir: /etc/ansible/tools
$ easzctl del-node 192.168.1.11 # 假设待删除节点 192.168.1.11
```

### [管理 ETCD 节点](https://github.com/easzlab/kubeasz/blob/master/docs/op/op-etcd.md)


## 可能遇到的问题

### master 节点重启后状态始终为 NotReady

查看 `journalctl -f -u kubelet` 提示 /etc/cni/net.d 没初始化，到路径下查看，发现内容为空，其他 Ready 的 work node 中，该路径下有 `10-flannel.conflist` 文件，且文件内容相同。
将此文件内容复制到 master 节点相同路径下，稍等一会后再使用 `kubectl get node` 查看节点状态就都 Ready 了。

### 启动 kube-apiserver 服务报错

安装过程中遇到报错

```error
fatal: [192.168.174.72]: FAILED! => {"changed": true, "cmd": "systemctl daemon-reload && systemctl restart kube-apiserver && systemctl restart kube-controller-manager && systemctl restart kube-scheduler", "delta": "0:00:00.221579", "end": "2020-09-28 15:21:21.710485", "msg": "non-zero return code", "rc": 1, "start": "2020-09-28 15:21:21.488906", "stderr": "Job for kube-apiserver.service failed because the control process exited with error code. See \"systemctl status kube-apiserver.service\" and \"journalctl -xe\" for details.", "stderr_lines": ["Job for kube-apiserver.service failed because the control process exited with error code. See \"systemctl status kube-apiserver.service\" and \"journalctl -xe\" for details."], "stdout": "", "stdout_lines": []}
```

按提示通过 `systemctl status kube-apiserver.service` 看到服务启动报错时执行的命令，将命令在终端中直接执行，有具体的报错信息：

```error
Error: failed to create listener: failed to listen on 127.0.0.1:8080: listen tcp 127.0.0.1:8080: bind: address already in use
```

因为 `kube-apiserver` 默认启用 http 服务，且端口为 `8080`。可修改服务配置的命令（需修改 ansible 里的 .j2 模板 `/etc/ansible/roles/kube-master/templates/kube-apiserver.service.j2`），在 `ExeccStart` 中增加 --insecure-port 参数，指定其他端口或直接禁用（=0），如：

```j2
[Unit]
Description=Kubernetes API Server
Documentation=https://github.com/GoogleCloudPlatform/kubernetes
After=network.target

[Service]
ExecStart={{ bin_dir }}/kube-apiserver \
  --advertise-address={{ inventory_hostname }} \
  --allow-privileged=true \
  --anonymous-auth=false \
  --authorization-mode=Node,RBAC \
{% if BASIC_AUTH_ENABLE == "yes" %}
  --basic-auth-file={{ ca_dir }}/basic-auth.csv \
{% endif %}
  --bind-address={{ inventory_hostname }} \
  --insecure-port=0 \
  --client-ca-file={{ ca_dir }}/ca.pem \
  --endpoint-reconciler-type=lease \
  --etcd-cafile={{ ca_dir }}/ca.pem \
  --etcd-certfile={{ ca_dir }}/kubernetes.pem \
  --etcd-keyfile={{ ca_dir }}/kubernetes-key.pem \
  --etcd-servers={{ ETCD_ENDPOINTS }} \
  --kubelet-certificate-authority={{ ca_dir }}/ca.pem \
  --kubelet-client-certificate={{ ca_dir }}/admin.pem \
  --kubelet-client-key={{ ca_dir }}/admin-key.pem \
  --kubelet-https=true \
  --service-account-key-file={{ ca_dir }}/ca.pem \
  --service-cluster-ip-range={{ SERVICE_CIDR }} \
  --service-node-port-range={{ NODE_PORT_RANGE }} \
  --tls-cert-file={{ ca_dir }}/kubernetes.pem \
  --tls-private-key-file={{ ca_dir }}/kubernetes-key.pem \
  --requestheader-client-ca-file={{ ca_dir }}/ca.pem \
  --requestheader-allowed-names= \
  --requestheader-extra-headers-prefix=X-Remote-Extra- \
  --requestheader-group-headers=X-Remote-Group \
  --requestheader-username-headers=X-Remote-User \
  --proxy-client-cert-file={{ ca_dir }}/aggregator-proxy.pem \
  --proxy-client-key-file={{ ca_dir }}/aggregator-proxy-key.pem \
  --enable-aggregator-routing=true \
  --v=2
Restart=always
RestartSec=5
Type=notify
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
```

之后重新执行报错步骤即可。


## 相关资料

* [手把手从零搭建与运营生产级的 Kubernetes 集群与 KubeSphere](https://www.kubernetes.org.cn/7315.html)
* [白话 flannel 和 calico 网络原理](https://yuerblog.cc/2019/02/25/flannel-and-calico/)
* [Kubernetes 的三种外部访问方式：NodePort、LoadBalancer 和 Ingress](http://www.dockone.io/article/4884)
