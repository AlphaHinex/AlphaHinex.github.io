---
id: dubbo-telnet
title: "使用 Telnet 调用 Dubbo 服务"
description: "自带工具，快速验证"
date: 2020.10.25 10:34
categories:
    - Cloud
    - DevOps
    - Java
tags: [Microservices, RPC]
keywords: ZooKeeper, Dubbo, Telnet, Fastjson
cover: /contents/covers/dubbo-telnet.png
---

当使用 [Dubbo](https://github.com/apache/dubbo) 作为 RPC 框架时，有时会希望验证 provider 提供的服务是否好用，比起开发一个 consumer，可以使用自带工具来进行更快速的验证。

本文以使用 [ZooKeeper v3.6.1](https://github.com/apache/zookeeper/tree/release-3.6.1) 为注册中心，[dubbo-samples-zookeeper](https://github.com/apache/dubbo-samples/tree/master/java/dubbo-samples-zookeeper) 示例代码为例，介绍一下自 dubbo v2.0.5 版本开始支持的 telnet 命令用法。

## 环境准备

### 启动注册中心

先在本地 `2181` 端口启动一个 ZooKeeper 服务，可使用示例中提供的 [docker-compose.yml](https://github.com/apache/dubbo-samples/blob/master/java/dubbo-samples-zookeeper/src/main/resources/docker/docker-compose.yml) 或如下内容：

```yaml
version: '3.3'
services:
  zookeeper:
    image: "zookeeper:3.6.1"
    ports:
      - "2181:2181"
```

在 docker-compose.yml 文件所在路径执行 `docker-compose up -d` 完成服务启动，并可通过 `docker ps` 查看服务状态：

```bash
$ docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                                                  NAMES
651bded02416        zookeeper:3.6.1     "/docker-entrypoint.…"   36 minutes ago      Up 36 minutes       2888/tcp, 3888/tcp, 0.0.0.0:2181->2181/tcp, 8080/tcp   compose-docker_zookeeper_1
```

### 启动 Dubbo Provider 服务

将 `dubbo-samples-zookeeper` 路径下内容导入 IDE，并运行 `ProviderBootstrap.java`，在 Console 中看到 `dubbo service started` 意味着服务完成启动。


## 通过注册中心找到 provider 信息

假定我们并不清楚服务发布在了哪，可以先通过注册中心，查找到所要调用的服务相关信息。

在 ZooKeeper 的运行路径中，包含了一个客户端可以查询 ZK 中信息。以前面环境为例，先进入到注册中心的容器中：

```bash
$ docker exec -ti compose-docker_zookeeper_1 bash
```

在容器内 `/apache-zookeeper-3.6.1-bin/bin` 路径下运行客户端脚本：

```bash
$ ./zkCli.sh
```

进入客户端后通过 `ls` 命令查询服务信息：

```bash
[zk: localhost:2181(CONNECTED) 0] ls /dubbo/org.apache.dubbo.samples.api.GreetingService/providers
[dubbo%3A%2F%2F127.0.0.1%3A20880%2Forg.apache.dubbo.samples.api.GreetingService%3Fanyhost%3Dtrue%26application%3Dzookeeper-demo-provider%26deprecated%3Dfalse%26dubbo%3D2.0.2%26dynamic%3Dtrue%26generic%3Dfalse%26group%3Dabc%26interface%3Dorg.apache.dubbo.samples.api.GreetingService%26methods%3DsayHello%26pid%3D10929%26release%3D2.7.7%26revision%3D1.0.0%26side%3Dprovider%26timestamp%3D1603525931278%26version%3D1.0.0]
```

查询结果进行 URI decode 之后得到如下内容：

```text
dubbo://127.0.0.1:20880/org.apache.dubbo.samples.api.GreetingService?anyhost=true&application=zookeeper-demo-provider&deprecated=false&dubbo=2.0.2&dynamic=true&generic=false&group=abc&interface=org.apache.dubbo.samples.api.GreetingService&methods=sayHello&pid=10929&release=2.7.7&revision=1.0.0&side=provider&timestamp=1603525931278&version=1.0.0
```

可以看到 dubbo 的服务运行在注册中心相同主机的 `20880` 端口。

## 调用服务

因本例中所有服务均在本地启动，可以 telnet 进 dubbo 服务中：

```bash
$ telnet localhost 20880
Trying ::1...
Connected to localhost.
Escape character is '^]'.

dubbo> help
Please input "help [command]" show detail.
 status [-l]                      - Show status.
 shutdown [-t <milliseconds>]     - Shutdown Dubbo Application.
 pwd                              - Print working default service.
 trace [service] [method] [times] - Trace the service.
 exit                             - Exit the telnet.
 help [command]                   - Show help.
 invoke [service.]method(args)    - Invoke the service method.
 count [service] [method] [times] - Count the service.
 clear [lines]                    - Clear screen.
 ls [-l] [service]                - List services and methods.
 log level                        - Change log level or show log
 select [index]                   - Select the index of the method you want to invoke.
 ps [-l] [port]                   - Print server ports and connections.
 cd [service]                     - Change default service.
```

查看提供的服务：

```bash
dubbo>ls
PROVIDER:
org.apache.dubbo.samples.api.GreetingService:1.0.0
```

查看服务中方法信息：

```bash
dubbo>ls org.apache.dubbo.samples.api.GreetingService -l
org.apache.dubbo.samples.api.GreetingService:1.0.0 (as provider):
	java.lang.String sayHello(java.lang.String)
```

调用方法：

```bash
dubbo>invoke org.apache.dubbo.samples.api.GreetingService.sayHello('hinex')
```

此时可能会遇到一个异常信息：

```text
Invalid json argument, cause: com/alibaba/fastjson/JSON
```

如果执行示例代码中的 `ConsumerBootstrap` 会发现 consumer 能正常的消费提供者的服务，并没有上述异常。此问题仅在通过 telnet 调用服务的时候出现。

可在 [pom.xml](https://github.com/apache/dubbo-samples/blob/master/java/dubbo-samples-zookeeper/pom.xml) 中添加 [fastjson](https://github.com/alibaba/fastjson) 的依赖来解决此问题：

```xml
<dependency>
    <groupId>com.alibaba</groupId>
    <artifactId>fastjson</artifactId>
    <version>1.2.73</version>
</dependency>
```

重启 `ProviderBootstrap` 服务，并再次通过 telnet 进行调用，可得到正常的调用结果：

```bash
dubbo>invoke org.apache.dubbo.samples.api.GreetingService.sayHello('hinex')
Use default service org.apache.dubbo.samples.api.GreetingService.
result: "hello, hinex"
elapsed: 1 ms.
```

## 参考资料

* [Telnet 命令参考手册](http://dubbo.apache.org/zh-cn/docs/user/references/telnet.html)
