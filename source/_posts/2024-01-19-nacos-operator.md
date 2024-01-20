---
id: nacos-operator
title: "正确管理kubernetes有状态应用之nacos"
description: "本文旨在分享 kubernetes 环境下如何管理 nacos，阅读本文需要一定 kubernetes 基础。"
date: 2024.01.19 10:34
categories:
    - K8s
tags: [K8s, Golang, Nacos]
keywords: Kubernetes, k8s, operator, nacos, helm, CR, CRD
cover: /contents/nacos-operator/api.png
---

# 介绍


本文旨在分享 `kubernetes` 环境下如何管理 `nacos`，阅读本文需要一定 `kubernetes` 基础。

nacos介绍
---------

`nacos` 是阿里开源的一款注册中心、配置中心软件。更多信息移步：https://nacos.io/zh-cn/docs/what-is-nacos.html

有状态应用管理方式
----------------

`Kubernetes` 有状态应用管理方式，通常有三种：手动、`helm`、`operator`

推荐的优先级：手动 < `helm` < `operator`

![priority](/contents/nacos-operator/priority.png)

`kubernetes` 发展初期，用户通常使用 `helm` 管理有状态应用（例如zk集群），管理方式则是以预置 `webhook` 函数形式，当 `helm` 执行 `update` 命令时，触发对应钩子函数进而执行相关动作（扩容/更换镜像）。

随着后续 `operator` 的引入，有状态应用的管理更加便捷。由于 `operator` 引入有状态 `CRD` 及对应的控制器，从而扩展了 `Kubernetes` 的 `API`，管理有状态应用变得像管理 `Kubernetes` 原生资源对象（Deployment、StatefulSet）一样简单。

```bash
$ kubectl get nacos
NAME    REPLICAS   READY     TYPE         DBTYPE   VERSION   CREATETIME
nacos   1          Running   standalone            2.0.4     2023-09-18T02:31:23Z
```

operator介绍
------------

上面我们提到了，现阶段 `kubernetes` 推荐用户使用 `operator` 管理集群内的有状态应用。那接下来，我们来了解下 `kubernetes` 的 `operator` 究竟是什么。

维护应用程序基础结构需要许多重复性的人为操作，而这些重复性操作通常没有太大的意义。计算机是执行精确任务的首选方法，可以验证对象的状态，从而使基础设施需求能够被编码。`operator` 提供了一种方法来封装应用程序所需的活动、检查和语句管理。

在 `Kubernetes` 中，`operator` 通过扩展 `API` 的功能来提供智能的动态管理功能。这些 `operator` 组件允许通用流程的自动化以及响应式应用程序不断适应其环境。这反过来促进应用更快速的开发，减少故障点，更低的平均恢复时间，并增加了工程自治权。

`Kubernetes` 和其他容器协调器的成功，一直归功于他们对容器的主要功能的关注。尽管部分企业开启了云原生路线，但与更具体的用例(微服务、无状态应用程序)合作更有意义。`operator` 模式可以解决状态管理问题。通过利用 `Kubernetes` 内置的功能，如自愈、协调和扩展应用程序特定的复杂性; 可以将任何应用程序的生命周期、操作自动化，并将其转化为功能强大的产品。

`operator` 与 `Kubernetes` 不应是绑定的，管理完全自动化的应用程序的思想可以导出到其他平台。

当然，你也可以将 `operator` 理解为基于 `Kubernetes` 的扩展控制器，管理 `Kubernetes` `API` 扩展资源类型（CR）生命周期。

![cr](/contents/nacos-operator/cr.png)

CR&CRD介绍
----------

`CR` 全称是 `Custom Resource`，即自定义资源（ConfigMap、Secret等为kubernetes内置资源类型）。
`CRD`全称是`Custom Resource Definition`，`CRD`本身是一种 `Kubernetes` 内置的资源类型，即自定义资源的定义，用于描述用户定义的资源（CR）是什么样子。`CRD` 的相关概念：
1. 从 `Kubernetes` 的用户角度来看，所有东西都叫资源 `Resource`，就是 `Yaml` 里的字段 **`Kind`** 的内容，例如 `Service`、`Deployment`等。
2. 除了常见内置资源之外，`Kubernetes` 允许用户自定义资源 `Custom Resource`，而 CRD 表示自定义资源的定义。

![cr&crd](/contents/nacos-operator/cr-crd.png)

# Nacos operator选型

`operator` 可以自己开发，或者选择已有开源项目，当然优先选取官方的 `operator`，而 `nacos` 为使用者提供了 `operator`，我们直接拿来用就可以了。

https://github.com/nacos-group/nacos-k8s/blob/master/operator/README.md

# Nacos operator chart改造

为方便在内网环境使用，我们需要对官方的 `operator` 进行一定的改造。

## 1. 下载官方项目

https://github.com/nacos-group/nacos-k8s/archive/refs/heads/master.zip

## 2. 修改 `operator` 镜像 `tag`

如果您的 `kubernetes` 环境可以联网，则不需要使用私有镜像库。

下载完项目后，我们上传至 `Linux` 服务器（需安装 `helm`），编辑 `operator/chart/nacos-operator/values.yaml` 修改以下内容:

```yaml
# 更改前
image:
  repository: nacos/nacos-operator
  pullPolicy: Always
  # Overrides the image tag whose default is the chart appVersion.
  tag: "latest"
  
 # 更改后
image:
  repository: harbor.cloud.io/nacos/nacos-operator
  pullPolicy: Always
  # Overrides the image tag whose default is the chart appVersion.
  tag: "latest"
```

即引用私有镜像库中的镜像，注：`harbor.cloud.io` 为脱敏后的域名。

## 3. 修改默认配额（可选）

编辑`operator/chart/nacos-operator/values.yaml`修改以下内容:

```yaml
# 更改前
resources:
  # We usually recommend not to specify default resources and to leave this as a conscious
  # choice for the user. This also increases chances charts run on environments with little
  # resources, such as Minikube. If you do want to specify resources, uncomment the following
  # lines, adjust them as necessary, and remove the curly braces after 'resources:'.
  limits:
    cpu: 100m
    memory: 128Mi
  requests:
    cpu: 100m
    memory: 128Mi
# 更改后
resources:
  # We usually recommend not to specify default resources and to leave this as a conscious
  # choice for the user. This also increases chances charts run on environments with little
  # resources, such as Minikube. If you do want to specify resources, uncomment the following
  # lines, adjust them as necessary, and remove the curly braces after 'resources:'.
  limits:
    cpu: 1
    memory: 2048Mi
  requests:
    cpu: 500m
    memory: 1024Mi
```

## 4. 对chart进行打包，方便后续使用及分发

```bash
$ helm package operator/chart/nacos-operator
Successfully packaged chart and saved it to: /root/nacos-k8s-master/nacos-operator-0.1.0.tgz
```

由此我们获取了`chart`文件：`nacos-operator-0.1.0.tgz`

## 5. 下载相关镜像，导入私有镜像库内

```text
# 镜像列表
nacos/nacos-operator
nacos/nacos-server:v2.0.4
```

# Nacos operator使用方式

首先我们将修改好的 `nacos-operator` 发布至集群内

```bash
$ kubectl create ns nacos
$ helm install nacos-operator -n nacos ./nacos-operator-0.1.0.tgz
```

查看 `nacos-operator` 发布情况

```bash
$ kubectl get pod -n nacos -w
NAME                              READY   STATUS    RESTARTS   AGE
nacos-operator-5865c799f5-pdc4n   1/1     Running   0          36s
```

运行成功！我们接下来创建几个样例，熟悉使用方式

单点
---

创建一个单节点实例，选择 `v2.0.4` 版本进行发布，数据库选择内嵌类型，并挂载 `10Gi` 的卷。

```bash
$ cat > nacos.yaml <<EOF
apiVersion: nacos.io/v1alpha1
kind: Nacos
metadata:
  name: nacos-single
spec:
  type: standalone
  image: harbor.cloud.io/nacos/nacos-server:v2.0.4
  replicas: 1
  database:
    type: embedded
  # Start the data volume, otherwise the data will be lost after restart
  volume:
    enabled: true
    requests:
      storage: 10Gi
EOF

# Install demo standalone mode
$ kubectl apply -f nacos.yaml -n nacos
```

观察 `nacos` 实例状态

```bash
$ kubectl get nacos -n nacos -w
NAME           REPLICAS   READY      TYPE         DBTYPE     VERSION   CREATETIME
nacos-single   1          Creating   standalone   embedded             2023-09-26T06:30:19Z
```

创建完毕后，会自动生成 `svc`、`pvc`、`pod` 等实例

```bash
$ kubectl get svc -n nacos nacos-single
NAME           TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)                      AGE
nacos-single   ClusterIP   10.233.4.18   <none>        8848/TCP,7848/TCP,9848/TCP   2m39s

$ kubectl get pvc -n nacos
NAME                STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS           AGE
db-nacos-single-0   Bound    pvc-3f391db7-738e-4597-853a-a69a0219d6a5   10Gi       RWO            default   3m10s

$ kubectl get pod -n nacos nacos-single-0
NAME             READY   STATUS    RESTARTS   AGE
nacos-single-0   1/1     Running   0          3m53s
```

当然数据库类型也可以选择外部 `mysql`，但单点 `nacos` 一般用于开发、测试环境，没有必要单独创建一个 `mysql` 实例，内嵌数据库比较简单。

集群
---

接下来，我们创建一个3节点实例的 `nacos` 集群，选择 `v2.0.4` 版本进行发布，数据库选择外部数据库，并配置相关配额及环境变量。数据库表需要提前创建：[nacos表结构sql](https://raw.githubusercontent.com/alibaba/nacos/develop/distribution/conf/mysql-schema.sql)

```bash
$ cat > nacos-cluster.yaml <<EOF
apiVersion: nacos.io/v1alpha1
kind: Nacos
metadata:
  name: nacos-cluster
spec:
  type: cluster
  image: harbor.cloud.io/nacos/nacos-server:v2.0.4
  replicas: 3
  database:
    type: mysql
    mysqlHost: mysql.nacos
    mysqlDb: nacos
    mysqlUser: ******
    mysqlPort: "3306"
    mysqlPassword: "******"
  resources:
    limits:
      cpu: "1"
      memory: 4Gi
    requests:
      cpu: 500m
      memory: 2Gi
EOF
```

查看创建状态

```bash
$ kubectl get nacos.nacos.io -n nacos
NAME            REPLICAS   READY      TYPE         DBTYPE     VERSION   CREATETIME
nacos-cluster   3          Creating   cluster      mysql                2023-09-26T08:02:03Z
nacos-single    1          Running    standalone   embedded   2.0.4     2023-09-26T06:30:19Z

$ kubectl get pod -n nacos -l app=nacos-cluster
NAME              READY   STATUS    RESTARTS   AGE
nacos-cluster-0   1/1     Running   0          35s
nacos-cluster-1   1/1     Running   0          35s
nacos-cluster-2   1/1     Running   0          35s
```

通过 `pod` 名称我们可以发现，`nacos operator` 底层基于 `StatefulSet` 管理 `nacos` 实例

```bash
$ kubectl describe pod nacos-cluster-0 -n nacos |grep Controlled
Controlled By:  StatefulSet/nacos-cluster
```

通过观察 `Service` 可知，`nacos operator` 创建集群类型 `nacos` 时会创建两种类型 `Service`，分别用于 `Web` 控制台（nacos-cluster-client）与程序侧配置（nacos-cluster-headless）

```bash
$ kubectl get svc -n nacos -l app=nacos-cluster
NAME                     TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)                      AGE
nacos-cluster-client     ClusterIP   10.233.48.176   <none>        8848/TCP                     3m54s
nacos-cluster-headless   ClusterIP   None            <none>        8848/TCP,7848/TCP,9848/TCP   3m54s
```

开启 `NodePort` 访问控制台，观察集群状态

![nacos](/contents/nacos-operator/nacos.png)

# 进阶：封装nacos管理接口

通过 `nacos operator` 我们可以方便的管理`nacos`实例，但仅限于后台操作（kubectl）。如果我们能将对`nacos`的操作封装成一个服务，可以很方便的对外提供服务。

架构设计
-------

调用者通过 `REST HTTP` 接口访问 `nacos` 管理服务实现对集群内 `nacos` 服务的运维管理。

接口类型可分为四类：
- 创建：创建 `nacos` 实例，入参类型：配额、`nacos` 部署类型、`nacos` 数据存储类型等
- 删除：删除 `nacos` 实例，入参类型：`nacos`名称、命名空间
- 修改：修改 `nacos` 实例，入参类型：配额
- 查询：查询 `nacos` 实例及运行状态、查询当前可创建`nacos`版本

![crud](/contents/nacos-operator/crud.png)

接口设计样例
----------

篇幅有限，以下仅展示部分接口设计。

![api](/contents/nacos-operator/api.png)

实现解析
-------

本质就是对 `Kubernetes` 的 `CRD` 对象操作，操作时使用 `DynamicK8sClientSet` 对象。

- 查询核心代码

```go
var gvr = schema.GroupVersionResource{
   Group:    "nacos.io",
   Version:  "v1alpha1",
   Resource: "nacos",
}
func getNacosItem(name, namespace string) (Nacos, error) {
   resp, err := client.DynamicK8sClientSet.
   Resource(gvr).
   Namespace(namespace).
   Get(context.Background(), name, v1.GetOptions{})
   if err != nil {
      return FindItem{}, err
   }
   data, _ := resp.MarshalJSON()
   nacos := &v1alpha1.Nacos{}
   json.Unmarshal(data, nacos)

   return nacos
}
```

- 删除核心代码

```go
func deleteNacosItem(name, namespace string) error {
   return client.
   DynamicK8sClientSet.
   Resource(gvr).
   Namespace(namespace).
   Delete(context.Background(), name, v1.DeleteOptions{})
}
```

其他接口类似，只是出入参不同而已。