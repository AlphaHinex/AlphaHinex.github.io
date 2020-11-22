---
id: k8s-config-map
title: "K8s ConfigMap"
description: "分离配置与镜像，提高可移植性"
date: 2020.11.22 10:34
categories:
    - K8s
tags: [K8s, DevOps]
keywords: K8s, ConfigMap, subPath
cover: /contents/covers/k8s-config-map.png
---

[在 k8s 集群中部署第一个应用](https://alphahinex.github.io/2020/10/18/deploy-first-app-in-k8s/) 中，完成了一个基本的 NGINX 服务的部署，但在真实环境中使用 NGINX 时，一般都需要定制其配置文件，使满足实际代理需求。K8s 提供了一个 [ConfigMap](https://kubernetes.io/docs/concepts/configuration/configmap/) 的概念，允许将配置文件与镜像文件分离，以使容器化的应用程序具有可移植性。

## 什么是 ConfigMap

可以按字面方式，将 ConfigMap，理解为一个 Config 的 Map：

* Map 的 Key 为配置标识，可以是文件名等
* Map 的 Value 为配置内容，可以是字符串、文本内容等

一个 ConfigMap 中可以包含多个 Key / Value 对。

## 怎么创建 ConfigMap

可以使用 `kubectl create configmap` 命令基于 目录、文件 或字符串来创建 ConfigMap，也可以直接编写 yaml 文件进行定义：

```yaml
# nginx-config.yml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
data:
  nginx_conf: |
    user  nginx;
    worker_processes  2;

    error_log  /var/log/nginx/error.log warn;
    pid        /var/run/nginx.pid;

    events {
        worker_connections  1024;
    }

    http {
        include       /etc/nginx/mime.types;
        default_type  application/octet-stream;

        log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                          '$status $body_bytes_sent "$http_referer" '
                          '"$http_user_agent" "$http_x_forwarded_for"';

        access_log  /var/log/nginx/access.log  main;

        sendfile        on;
        #tcp_nopush     on;

        keepalive_timeout  65;

        #gzip  on;

        include /etc/nginx/conf.d/*.conf;
    }
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: confd-config
data:
  file_server.conf: |
    server {
        listen       2020;
        server_name  file_server;
        location / {
            autoindex on;
            root /usr/share/nginx;
            charset utf-8;
        }
    }
  another.conf: |
    server {
        listen       8000;
        server_name  another;
        location / {
            root /usr/share/nginx/html;
        }
    }
```

之后可使用 `kubectl apply -f nginx-config.yml` 完成 ConfigMap 的创建。

## 怎么使用 ConfigMap

ConfigMap 有多种定义形式，也有多种使用形式，详细情况可以查阅 [官方文档](https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/)。本文仍以 NGINX 配置文件为例，说明一下 ConfigMap 中定义的配置文件的使用方式。

上面的 `nginx-config.yml` 定义了两个 ConfigMap，目标是放到 NGINX 容器中的如下两个位置：

* nginx-config => /etc/nginx/nginx.conf
* confd-config => /etc/nginx/conf.d

可以将 ConfigMap 添加到 Volume 中，再进行挂载以使用，如：

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
        volumeMounts:
        - name: nginx-config-vol
          mountPath: /etc/nginx/nginx.conf # 也可挂载到文件
          subPath: nginx.conf # 挂载到文件时，需设置子路径
        - name: confd-vol # 与 volumes 中的 name 对应
          mountPath: /etc/nginx/conf.d # 配置文件要挂载的路径
      volumes:
      - name: nginx-config-vol # 对应 ConfigMap 的 name
        configMap:
          name: nginx-config
          items:
          - key: nginx_conf
            path: nginx.conf
      - name: confd-vol
        configMap:
          name: confd-config
          # 此时会将此 ConfigMap 中的所有配置以文件形式挂载
          # 如果只需挂载一个文件（如 file_server.conf），可以按如下方式指定：
          # items:
          # - key: file_server.conf
          #   path: file_server.conf
```

有两个地方需要说明一下：

### 使用 mountPath 挂载路径时

比如上例中的 `mountPath: /etc/nginx/conf.d`，此时可指定挂载 ConfigMap 中的某个配置到该路径下的具体文件，也可将整个 ConfigMap 中的所有配置以多个文件的形式挂载到指定路径下。

不论哪种方式，都会将容器中原路径下所有先前的文件清除，需注意。

### 使用 mountPath 挂载文件时

若想将配置文件挂载至容器中某个具体文件处，不影响该文件所在路径的其他文件，可按上例中的 `nginx.conf` 文件方式：

```yaml
mountPath: /etc/nginx/nginx.conf # 也可挂载到文件
subPath: nginx.conf # 挂载到文件时，需设置子路径
```

即 `mountPath` 直接指定到具体文件，并通过 `subPath` 表明文件名。

## 挂载的 ConfigMap 自动更新

更新已经在数据卷中使用的 ConfigMap 时，已映射的配置内容最终也会被自动更新。`kubelet` 在每次定期同步时都会检查已挂载的 ConfigMap 是否是最新的。但是，它使用其本地的基于 TTL 的缓存来获取 ConfigMap 的当前值。因此，从更新 ConfigMap 到将新值映射到 Pod 的总延迟，可能与 kubelet 同步周期 + ConfigMap 在 kuelet 中缓存的 TTL 一样长。

另外，使用 ConfigMap 作为 `subPath` 的数据卷将不会收到 ConfigMap 更新。

以上面配置为例，当更新 ConfigMap 中 NGINX 配置文件内容并 apply 到集群之后，可以稍等一会，然后进入到容器中观察配置文件，`nginx.conf` 文件的内容不会随 ConfigMap 文件更新同步，但 `/etc/nginx/conf.d` 路径下内容，会按更新周期，自动同步 `confd-config` 中的所有变更，包括配置文件内容，以及配置文件个数。

## 完整的 K8s 配置

本文中完整的 K8s 配置如下：

```yaml
# nginx-test.yml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
data:
  nginx_conf: |
    user  nginx;
    worker_processes  2;

    error_log  /var/log/nginx/error.log warn;
    pid        /var/run/nginx.pid;

    events {
        worker_connections  1024;
    }

    http {
        include       /etc/nginx/mime.types;
        default_type  application/octet-stream;

        log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                          '$status $body_bytes_sent "$http_referer" '
                          '"$http_user_agent" "$http_x_forwarded_for"';

        access_log  /var/log/nginx/access.log  main;

        sendfile        on;
        #tcp_nopush     on;

        keepalive_timeout  65;

        #gzip  on;

        include /etc/nginx/conf.d/*.conf;
    }
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: confd-config
data:
  file_server.conf: |
    server {
        listen       2020;
        server_name  file_server;
        location / {
            autoindex on;
            root /usr/share/nginx;
            charset utf-8;
        }
    }
  another.conf: |
    server {
        listen       8000;
        server_name  another;
        location / {
            root /usr/share/nginx/html;
        }
    }
---
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
        volumeMounts:
        - name: nginx-config-vol
          mountPath: /etc/nginx/nginx.conf # 也可挂载到文件
          subPath: nginx.conf # 挂载到文件时，需设置子路径
        - name: confd-vol # 与 volumes 中的 name 对应
          mountPath: /etc/nginx/conf.d # 配置文件要挂载的路径
      volumes:
      - name: nginx-config-vol # 对应 ConfigMap 的 name
        configMap:
          name: nginx-config
          items:
          - key: nginx_conf
            path: nginx.conf
      - name: confd-vol
        configMap:
          name: confd-config
          # 此时会将此 ConfigMap 中的所有配置以文件形式挂载
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
  - name: file
    port: 2020
    nodePort: 30081
  - name: fb
    port: 8000
    nodePort: 30082
  selector:
    app: nginx
```

`kubectl apply -f nginx-test.yml` 完成部署之后，可通过集群的 `30081` 端口访问容器内 `2020` 端口的服务，并可以修改 ConfigMap 中内容，进入到容器中观察 NGINX 对应配置文件的变化。
