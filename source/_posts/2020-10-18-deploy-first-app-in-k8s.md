---
id: deploy-first-app-in-k8s
title: "在 k8s 集群中部署第一个应用"
description: "完事开头难"
date: 2020.10.18 10:26
categories:
    - Cloud
    - DevOps
    - K8s
tags: [Cloud, DevOps, Docker, K8s]
keywords: Kubernetes, K8s, Deploy, Deployment, Service, Kuboard
cover: /contents/covers/deploy-first-app-in-k8s.jpeg
---

在 [使用 kubeasz 离线安装 k8s 集群](https://alphahinex.github.io/2020/10/04/install-k8s-cluster-offline-with-kubeasz/) 中，我们完成了 k8s 集群的搭建，接下来，可以开始在集群中部署第一个应用了。

## 目标

在集群中启动一个最简单的 nginx 服务，并能够通过 http 进行访问。

## 预热

回忆 docker 环境下，要实现这个目标，需要做的事情很简单，一行命令即可：

```bash
$ docker run --name some-nginx -d -p 8080:80 nginx
```

之后便可访问 http://localhost:8080 看到 nginx 的欢迎页面。

也可以使用 docker-compose 配置文件来实现此目标：

```yml
some-nginx:
  image: nginx
  ports:
    - "8080:80"
```

## 准备

Kubernetes 官方提供了一个 [Kompose](https://kompose.io/) 工具，可以方便的将 Docker Compose 的配置文件转换成 k8s 所需的形式。让我们来看看官网上的例子：

>It’s as simple as 1-2-3
1. [Use an example docker-compose.yaml file](https://raw.githubusercontent.com/kubernetes/kompose/master/examples/docker-compose-v3.yaml) or your own
2. Run kompose up
3. Check your Kubernetes cluster for your newly deployed containers!

```bash
$ wget https://raw.githubusercontent.com/kubernetes/kompose/master/examples/docker-compose-v3.yaml -O docker-compose.yaml

$ kompose up
We are going to create Kubernetes Deployments, Services and PersistentVolumeClaims for your Dockerized application.
If you need different kind of resources, use the 'kompose convert' and 'kubectl create -f' commands instead.

INFO Successfully created Service: redis          
INFO Successfully created Service: web            
INFO Successfully created Deployment: redis       
INFO Successfully created Deployment: web         

Your application has been deployed to Kubernetes. You can run 'kubectl get deployment,svc,pods,pvc' for details.

$ kubectl get po
NAME                            READY     STATUS              RESTARTS   AGE
frontend-591253677-5t038        1/1       Running             0          10s
redis-master-2410703502-9hshf   1/1       Running             0          10s
redis-slave-4049176185-hr1lr    1/1       Running             0          10s
```

什嘛？这就结束啦？这也太快了啪？

我们还是慢慢来，自己掌握一下节奏吧。

看到 `kompose up` 下面的提示内容，我们可以通过 `kompose convert` 命令将 Docker Compose 的文件转换为 k8s 格式的内容：

```bash
$ kompose convert -f docker-compose.yml
```

转换后得到两个 yaml 文件：some-nginx-deployment.yaml 和 some-nginx-service.yaml 。

## 部署

kompose 将 docker-compose.yml 转换生成了两个 yaml 文件，一个 [Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) 和一个 [Service](https://kubernetes.io/docs/concepts/services-networking/service/)。

`Deployment` 包含了创建一个容器所必须的信息，如镜像、端口、资源需求、副本数等。k8s 会依据 Deployment 中的 template 定义创建必需数量的容器。

`Service` 用来将 k8s 集群中的服务暴露出来，供外部进行访问。类似在 docker 环境中映射端口至宿主机的操作。k8s 提供了四种 [ServiceTypes](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) 来发布服务，但实际在非云提供商大部分的 k8s 环境中，只能选择 [NodePort](https://kubernetes.io/docs/concepts/services-networking/service/#nodeport) 类型。指定了 `nodePort` 端口后，k8s 集群中每个节点都会将此端口代理至该 Service，不论这个 Serivce 部署在哪个节点上。Service 通过 `selector` 与 Deployment 进行关联。

查看 kompose 生成的文件内容，发现里面会包含一些 annotations 信息，以及并没有设定 ServiceType。所以在 kompose 的主页上有这样一段描述：

> Transformation of the Docker Compose format to Kubernetes resources manifest may not be exact, but it helps tremendously when first deploying an application on Kubernetes.

可以基于 Docker Compose 文件通过转换工具自动生成基础版本，再基于基础版本进行调整，获得最终使用的版本，可参考如下配置文件 `nginx.yml`：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  labels:
    app: nginx
spec:
  selector:
    matchLabels:
      app: nginx
  replicas: 1
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.17.9
        resources:
          requests:
            cpu: 100m
            memory: 100Mi
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: nginx
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

将该配置文件应用至集群中：

```bash
$ kubectl apply -f nginx.yml
```

之后，即可通过集群中任意节点的 ip，加配置文件中 `nodePort` 指定的端口（30080），访问集群中的 nginx 服务。

配置文件参考手册可见 [这里](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.18/)。

## 清理

可对配置文件执行 delete 操作清理其中包括的资源，如：

```bash
$ kubectl delete -f nginx.yml
```

## 可视化界面

使用 k8s 提供的命令行工具，可完成对集群的各项操作。同时也可借助可视化界面，更简便的操作集群，比如： [Kuboard](https://kuboard.cn/) 。

[Kuboard 在线演示](http://demo.kuboard.cn/dashboard?k8sToken=eyJhbGciOiJSUzI1NiIsImtpZCI6InZ6SzVqZFNJOXZFMmxQSkhXamNBcFY4RU9FR0RvSUR5bzJIY0NwVG1zODQifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJrdWJvYXJkLXZpZXdlci10b2tlbi0yOW40cyIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJrdWJvYXJkLXZpZXdlciIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6IjQzMWMwNmYyLTNiNTAtNGEyMy1hYjM1LTkyNDQwNTQ2NzFkZCIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDprdWJlLXN5c3RlbTprdWJvYXJkLXZpZXdlciJ9.kgwTa6t00gNC0vgr6HOvCqkDghPcW-jVDg-_K6WLy97ppb9jvaqVz-AxXzF7mJqXnNetbJw-8-x_L3ogSsDlTKmRucao96VA2tPKxel8pM04J8MU0ZmYgWhTJelibbxmQK3jwGM4x32bckOOvmtumcXdsBRN0z1SZ1iu4H0VoaswhfoFS4ZJKoe61xyqoDhQx4RLCVJh_-Uctd5RCcPLWFEk-BHqC8vUTy8QcRst6RIIozQdTqsv7Xs6bH6dHrHFS--eVVTH2orQdm8znuUFhlqFOOjmCIMzIlaUQC_SO9URIGYOs0jrk27N9KC0HvQ5dLgFmwyNJ0Gu7cYi23NP1A)

Kuboard 提供了 [Docker 镜像](https://hub.docker.com/r/eipwork/kuboard)，可使用官方提供的 [kuboard.yaml](https://kuboard.cn/install/install-dashboard-offline.html#%E5%87%86%E5%A4%87kuboard-yaml%E6%96%87%E4%BB%B6) 方便的将其部署到 k8s 集群中，进行使用。
