---
id: add-docker-container-port-mapping-without-restart
title: "不重启容器，增加 docker 容器端口映射"
description: "三种临时方案，在运行时设置端口映射"
date: 2025.07.27 10:34
categories:
    - Docker
    - Linux
tags: [Docker, Linux]
keywords: Docker, Linux, port mapping, iptables, socat, Nginx
cover: /contents/covers/add-docker-container-port-mapping-without-restart.png
---

# 场景

在某些情况下，我们可能需要在不重启 Docker 容器的情况下，动态地增加端口映射。例如，我们有一个 Redis 容器，默认情况下只在容器内部监听 6379 端口，但我们希望能够临时通过宿主机的 6400 端口访问它。

通过下面方式模拟这个未映射端口的容器：

```bash
docker run -d --rm --name redis_without_port_mapping redis:6-alpine
```

获得该容器的 IP：

```bash
$ docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' redis_without_port_mapping
172.17.0.2
```

# 方案

## 一、Docker 代理容器

在这种情况下，我们可以新创建一个代理容器来实现端口映射，而不需要重启原有的容器。我们可以使用 Nginx 的 TCP 代理来实现这一点。

```bash
docker run -d --rm --name proxy_nginx -p 6400:8080 nginx:1.24.0
```

进入容器修改配置：

```bash
docker exec -ti proxy_nginx bash
```

在配置文件中追加内容：

```bash
cat >> /etc/nginx/nginx.conf << EOF


stream {
    upstream redis {
        server 172.17.0.2:6379;
    }

    server {
        listen 8080;
        proxy_pass redis;
    }
}
EOF
```

之后重启 Nginx 服务：

```bash
nginx -s reload
```

此时在宿主机即可通过 6400 端口 telnet 或 Redis 客户端访问 redis 服务：

```bash
$ telnet localhost 6400
Trying ::1...
Connected to localhost.
Escape character is '^]'.
^]
telnet> quit
Connection closed.
```

临时使用过后，可直接删除代理容器关闭临时端口映射。

## 二、iptables

手动添加 iptables 转发规则，实现 docker 容器映射端口动态调整：

```bash
# 查看 NAT 表规则
$ iptables -t nat -L -n -v
# 将宿主机的 6400 端口转发到容器的 6379 端口
$ iptables -t nat -A DOCKER -p tcp --dport 6400 -j DNAT --to-destination 172.17.0.2:6379
# 允许转发流量
$ iptables -A DOCKER -p tcp -d 172.17.0.2 --dport 6400 -j ACCEPT
```

临时使用过后，可删除规则关闭端口映射：

```bash
# 查看 NAT 表规则及编号（关键步骤）
$ iptables -t nat -L --line-numbers -n -v
# 按编号删除规则（以 DOCKER 链第 2 条为例）
$ iptables -t nat -D DOCKER 2
```

## 三、socat

[socat](http://www.dest-unreach.org/socat/) 是一个用于在两个独立数据通道之间进行双向数据传输的中继工具。基本用法是：

```bash
socat [options] <bi-address> <bi-address>
```

可在 https://repo.or.cz/socat.git 下载源码后编译安装：

```bash
tar x...; ./configure; make; make install
```

或通过包管理工具等方式安装：

```bash
$ sudo apt install socat
$ sudo yum install socat
$ brew install socat
```

按如下方式启动 socat，实现宿主机端口到容器端口的映射：

```bash
socat TCP-LISTEN:<host_port>,fork TCP:<container_ip>:<container_port>
```

```bash
socat TCP-LISTEN:6400,fork TCP:172.17.0.2:6379
```

关于 socat 的更多用法可参考：[新版瑞士军刀：socat](https://zhuanlan.zhihu.com/p/347722248)

# 参考

- [如何给运行中的容器动态增加端口映射](https://baijiahao.baidu.com/s?id=1809991430705776957&wfr=spider&for=pc)
- [How To Publish a Port of a Running Container](https://iximiuz.com/en/posts/docker-publish-port-of-running-container/)
- [Use cases and workarounds](https://docs.docker.com/desktop/features/networking/#use-cases-and-workarounds)
- [Unable to connect to the Docker Container from the host browser on MacOS](https://github.com/docker/for-mac/issues/2670)
