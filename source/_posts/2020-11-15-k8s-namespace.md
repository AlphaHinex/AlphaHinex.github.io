---
id: k8s-namespace
title: "K8s 命名空间"
description: "资源隔离，简单有效"
date: 2020.11.15 10:26
categories:
    - K8s
tags: [K8s, DevOps]
keywords: K8s, namespace
cover: /contents/covers/k8s-namespace.jpg
---

Kubernetes 支持在一个物理集群上划分多个虚拟集群，这些虚拟集群即 [命名空间](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/)。

## 约束

* 在同一个命名空间中，资源名称须保持唯一。但在不同命名空间中，可以存在相同名称的资源。
* 每一个资源只能隶属于一个命名空间。
* 但命名空间本身不能属于另一个命名空间。

可以通过如下命令查看哪些资源在或不在命名空间中：

```bash
# In a namespace
$ kubectl api-resources --namespaced=true

# Not in a namespace
$ kubectl api-resources --namespaced=false
```

## 创建命名空间

可参照如下配置文件创建命名空间（注意修改其中的 `alpha` 为想创建的命名空间名称）：

```yaml
# namespace-alpha.yml
apiVersion: v1
kind: Namespace
metadata:
  name: alpha
```

之后使用 `kubectl apply -f namespace-alpha.yml` 进行创建。

K8s 初始状态下包含了四个命名空间：

* `default`：默认命名空间。资源未指定命名空间时，均创建在此命名空间下
* `kube-system`：K8s 系统创建的对象在此命名空间下
* `kube-public`：这个命名空间对所有用户可见（包括未授权用户），通常作为保留资源为集群所使用
* `kube-node-lease`：此命名空间用于与各个节点相关的租期（Lease）对象；此对象的设计使得集群规模很大时节点心跳检测性能得到提升

> 注意：创建命名空间时，应避免使用 `kube-` 作为前缀。

## 查看命名空间

```bash
$ kubectl get namespace
NAME              STATUS   AGE
default           Active   1d
kube-node-lease   Active   1d
kube-public       Active   1d
kube-system       Active   1d
```

## 指定命名空间

在 Deployment 等配置文件中，可在 `metadata` 里指定所属的 `namespace`，如：

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx
  namespace: alpha
  labels:
    app: nginx
spec:
  type: NodePort
  ports:
  - name: nginx
    port: 80
    nodePort: 30080
  selector:
    app: nginx
```

## 查询命名空间中资源

在设定了 namespace 后，进行查询等操作时，均需指定命名空间，如：

```bash
$ kubectl get pods -n alpha
$ kubectl get pods --namespace=alpha
```

## 设定命名空间偏好

可在当前上下文中，设定命名空间偏好，使后续的 `kubectl` 命令不再需要特殊指定命名空间：

```bash
$ kubectl config set-context --current --namespace=alpha
# Validate it
kubectl config view --minify | grep namespace:
```

## 跨命名空间服务访问

默认情况下，使用服务名可以直接访问相同命名空间内的服务。如果需要访问其他命名空间里的服务，可使用 `服务名.命名空间` 的形式，如 `nginx.alpha` 。
