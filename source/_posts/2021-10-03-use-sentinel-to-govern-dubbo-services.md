---
id: use-sentinel-to-govern-dubbo-services
title: "使用 Sentinel 进行 Dubbo 服务治理"
description: "实时监控、熔断及限流"
date: 2021.10.03 10:34
categories:
    - Cloud
tags: [Microservices, Governance]
keywords: Sentinel, Dubbo, Governance, 服务治理, 熔断, 限流
cover: /contents/use-sentinel-to-govern-dubbo-services/cover.jpeg
---

服务治理
=======

服务治理是一个比较宏观的概念，包括的内容也比较多，就像 [《当我们在说微服务治理的时候究竟在说什么》](https://www.jianshu.com/p/dd818114ab4b) 里所说，可以用治理城市交通的方式，来类比服务的治理，例如：

* 前方道路拥堵时，即使绿灯，交警也会让原地等待，直至缓解后才能通行，即为 **熔断**
* 路面出现裂缝，临时铺盖铁板，即为 **降级**
* 道路施工或查酒驾，车道变少，即为 **限流**
* 人行道、非机动车道、机动车道等，均为 **路由**
* 限号、限行，即为 **访问限制**
* 导航躲避拥堵路段，即为 **负载均衡**

采用各种治理手段的目的，都是为了能够在相同的基础设施条件下，尽可能的多的支撑各种流量场景，提升系统整体的容错性、健壮性和可用性。


Dubbo 服务如何进行服务治理
=======================

[Dubbo](https://dubbo.apache.org/zh/) 默认便提供了 [集群容错](http://alibaba.github.io/dubbo-doc-static/Fault+Tolerance-zh.htm)、[负载均衡](http://alibaba.github.io/dubbo-doc-static/Load+Balance-zh.htm)、[路由规则](http://alibaba.github.io/dubbo-doc-static/Router+Rule-zh.htm)、[服务降级](http://alibaba.github.io/dubbo-doc-static/Service+Degradation-zh.htm) 等基本的服务治理手段，结合新版本（0.3.0）的 [Dubbo Admin](https://github.com/apache/dubbo-admin)，可以方便的进行访问限制、路由规则、负载均衡策略等动态调整。

此外，Dubbo 还提供了 [本地存根](http://alibaba.github.io/dubbo-doc-static/Stub+Proxy-zh.htm) 和 [本地伪装](http://alibaba.github.io/dubbo-doc-static/Mock+Proxy-zh.htm) 的方式进行侵入式（需要修改 xml 文件及增加代码）的服务降级。

然而对于熔断和限流，则需要借助其他工具来实现，如 Sentinel。


Sentinel 对 Dubbo 服务进行的治理
=============================

Sentinel
--------

![Sentinel](/contents/use-sentinel-to-govern-dubbo-services/sentinel.png)

`Sentinel` 意为`哨兵`，[Sentinel](https://github.com/alibaba/Sentinel) 也旨在成为微服务的哨兵。

![features](/contents/use-sentinel-to-govern-dubbo-services/sentinel-features-overview-en.png)

从上面特性列表可以看出，Sentinel 分为四个主要部分：

1. 绿色区域为 Sentinel 的核心，囊括了其服务治理的主要手段
1. 蓝色区域为针对不同开源框架/库的适配，方便接入 Sentinel 进行治理
1. 黄色区域为 Sentinel 的 GUI，可通过浏览器进行监控和配置
1. 紫色区域为可对接的配置中心，保存 Sentinel 相关规则配置

本文主要涉及必备的 Sentinel Core、Dubbo 服务的适配器 Sentinel Apache Dubbo Adapter，和 Sentinel Dashboard。

### Sentinel Apache Dubbo Adapter

[Sentinel Apache Dubbo Adapter](https://github.com/apache/dubbo-sentinel-support) 的作用，是使 Dubbo 的服务接口和方法（包括调用端和服务端）成为 Sentinel 中的资源，在配置了规则后就可以自动享受到 Sentinel 的防护能力。

引入此适配器的方式分为 **侵入式** 和 **非侵入式**。

侵入式 —— 可参照 [dubbo-sentinel-support](https://github.com/apache/dubbo-sentinel-support) 仓库中的说明，直接引入依赖（Sentinel Core 会被一同引入）：

```xml
<dependency>
    <groupId>com.alibaba.csp</groupId>
    <artifactId>sentinel-apache-dubbo-adapter</artifactId>
    <version>x.y.z</version>
</dependency>
```

非侵入式 —— [通过 Java Agent 接入](https://help.aliyun.com/document_detail/102506.html)：

1. 获得 [最新版本 Java Agent](https://ahasoss-cn-hangzhou.oss-cn-hangzhou.aliyuncs.com/agent/prod/latest/ahas-java-agent.jar)，可参考 [Java Agent 版本说明](https://help.aliyun.com/document_detail/160563.htm) 及 [支持组件列表](https://help.aliyun.com/document_detail/128800.htm)
1. 添加 JVM 启动参数，如：

    ```bash
    //将<AppName>替换为自定义的应用名称，/opt/aliyunahas/agent/ahas-java-agent.jar是ahas-java-agent.jar的下载路径，请替换为实际路径。
    -Dproject.name=<AppName>
    -Dahas.namespace=default
    -javaagent:/opt/aliyunahas/agent/ahas-java-agent.jar
    ```

> 非常遗憾，此种方式仅在阿里云环境使用 [应用高可用服务AHAS](https://help.aliyun.com/document_detail/90320.html) 时有效。不过别急，下面会给出一个替代方案。

同样，具体治理规则的定义也有侵入式和非侵入式两种方式：

* 侵入式：可参考 [Configure Rules](https://github.com/alibaba/Sentinel/wiki/How-to-Use#configure-rules)
* 非侵入式：需使用 Sentinel Dashboard

### Sentinel Dashboard

[Sentinel Dashboard](https://github.com/alibaba/Sentinel/wiki/%E6%8E%A7%E5%88%B6%E5%8F%B0) 是一个轻量级的开源控制台，提供机器发现以及健康情况管理、监控（单机和集群），规则管理和推送的功能。

从 [官方发布页面](https://github.com/alibaba/Sentinel/releases) 或通过 [源码](https://github.com/alibaba/Sentinel/tree/master/sentinel-dashboard) 构建获得可执行 jar 包，`java -jar sentinel-dashboard.jar` 启动后，通过 http://localhost:8080 访问 Dashboard 界面，默认用户及密码均为 `sentinel`，可在 `application.properties` 配置文件中进行修改。

要在 Dashboard 中进行规则的动态配置，还需要在 Dubbo 服务中进行接入，接入方式可参照 [Dubbo 服务接入 Dashboard 文档](https://github.com/alibaba/Sentinel/tree/master/sentinel-demo/sentinel-demo-dubbo#sentinel-dashboard)。


实战演示
=======

接下来以一个实际的场景展示一下 Sentinel 对 Dubbo 服务的治理。

假设有两个 Dubbo 服务：服务消费者 `dub-consumer` 和服务提供者 `dub-provider`，使用 Sentinel 当前最新版本 1.8.2 进行治理，Sentinel Dashboard 进行监控及规则配置。

Sentinel Dashboard
------------------

下载 [Sentinel Dashboard v1.8.2](https://github.com/alibaba/Sentinel/releases/download/1.8.2/sentinel-dashboard-1.8.2.jar)，并运行：

```bash
$ java -jar sentinel-dashboard-1.8.2.jar --server.servlet.context-path=/demo/dashboard --auth.username=alpha --auth.password=hinex
```

服务已启动在 http://localhost:8080/demo/dashboard ，可通过 `alpha` / `hinex` 登录。

服务提供者非侵入式接入
------------------

上文提到的非侵入式 Java Agent 仅在阿里云环境有效，在开源环境时，无法将服务数据上报到 Sentinel Dashboard。可参照 [如何给 Spring Boot 外挂 classpath？](https://alphahinex.github.io/2021/03/14/spring-boot-launcher/) 中内容，采取外挂 Sentinel 相关依赖的方式，变相实现非侵入式接入，具体步骤如下：

### 第一步：准备好 Sentinel 相关依赖

治理 Dubbo 服务，所需依赖如下：

```text
sentinel-transport-simple-http-1.8.2.jar
sentinel-apache-dubbo-adapter-1.8.2.jar
sentinel-core-1.8.2.jar
sentinel-datasource-extension-1.8.2.jar
sentinel-transport-common-1.8.2.jar
```

> 注意，为尽可能减少问题，尽量保证 Sentinel 相关依赖版本需与 Dashboard 版本一致。

可将所有依赖放置在一个路径下（如 `./sentinel-1.8.2`），方便下面进行外挂。

### 第二步：修改启动命令

按照 [如何给 Spring Boot 外挂 classpath？](https://alphahinex.github.io/2021/03/14/spring-boot-launcher/) 调整启动命令。在本例中，有几个特殊的地方：

1. 需要指定 Sentinel 相关参数：`-Djava.net.preferIPv4Stack=true -Dcsp.sentinel.dashboard.server=localhost:8080 -Dproject.name=dub-provider`，启动项配置说明可见 [这里](https://github.com/alibaba/Sentinel/wiki/%E5%90%AF%E5%8A%A8%E9%85%8D%E7%BD%AE%E9%A1%B9)
1. 因为 Dashboard 使用了 context path，还需要额外增加一个 [参数](https://github.com/alibaba/Sentinel/blob/1.8.2/sentinel-transport/sentinel-transport-common/src/main/java/com/alibaba/csp/sentinel/transport/config/TransportConfig.java#L39)：`-Dcsp.sentinel.heartbeat.api.path=/demo/dashboard/registry/machine`，其中 `/registry/machine` 为固定值，`/demo/dashboard` 为 Dashboard 配置的 context path
1. 如果同时使用了外挂的配置文件，可通过 `-Dloader.path` 参数指定多个路径（如一个 jar 包的路径，一个配置文件所在路径），通过逗号间隔

本例中各文件路径结构为：

```text
├── dashboard
│   ├── sentinel-dashboard-1.8.2.jar
│   └── start.sh
├── dub-provider
│   ├── config
│   │   └── application.yml
│   ├── dub-provider.jar
│   └── run.sh
└── sentinel-1.8.2
    ├── sentinel-apache-dubbo-adapter-1.8.2.jar
    ├── sentinel-core-1.8.2.jar
    ├── sentinel-datasource-extension-1.8.2.jar
    ├── sentinel-transport-common-1.8.2.jar
    └── sentinel-transport-simple-http-1.8.2.jar
```

完整的启动命令为：

```run.sh
java -Djava.net.preferIPv4Stack=true -Dcsp.sentinel.dashboard.server=localhost:8080 -Dcsp.sentinel.heartbeat.api.path=/demo/dashboard/registry/machine -Dproject.name=dub-provider -cp dub-provider.jar -Dloader.path=../sentinel-1.8.2,./config org.springframework.boot.loader.PropertiesLauncher
```

服务消费者侵入式接入
-----------------

将上面非侵入式方案外挂的 jar 包，打包进服务消费者应用里，即可实现侵入式接入。当然，Sentinel 相关的 [启动配置项](https://github.com/alibaba/Sentinel/wiki/%E5%90%AF%E5%8A%A8%E9%85%8D%E7%BD%AE%E9%A1%B9) 还是要传的，要么是通过启动参数传，要么是通过配置文件设定。

在演示环境中，因为服务提供者和消费者都在一台机器上，所以需要额外指定一下 `csp.sentinel.api.port` 参数，避免两个服务冲突。

消费者路径下的文件包括：

```text
├── application.yml
├── dub-consumer-sentinel.jar
└── start.sh
```

完整的启动命令为：

```start.sh
java -Djava.net.preferIPv4Stack=true -Dcsp.sentinel.api.port=8482 -Dcsp.sentinel.heartbeat.api.path=/demo/dashboard/registry/machine -Dcsp.sentinel.dashboard.server=localhost:8080 -Dproject.name=dub-consumer -jar dub-consumer-sentinel.jar 
```

效果验证
-------

Dubbo 服务均接入 Sentinel Dashboard 后，即可通过 Dashboard 进行服务治理。

注意，默认情况下，需要真正产生 Dubbo 调用后（并且稍有延后），才会在 Dashboard 上观测到数据，如：

![dashboard](/contents/use-sentinel-to-govern-dubbo-services/dashboard.png)

> 如果控制台没有显示我的应用或者没有监控展示，可参考 [此 FAQ](https://github.com/alibaba/Sentinel/wiki/FAQ#q-sentinel-%E6%8E%A7%E5%88%B6%E5%8F%B0%E6%B2%A1%E6%9C%89%E6%98%BE%E7%A4%BA%E6%88%91%E7%9A%84%E5%BA%94%E7%94%A8%E6%88%96%E8%80%85%E6%B2%A1%E6%9C%89%E7%9B%91%E6%8E%A7%E5%B1%95%E7%A4%BA%E5%A6%82%E4%BD%95%E6%8E%92%E6%9F%A5) 进行排查。

可以通过 [Dubbo Admin](https://github.com/apache/dubbo-admin) 进行 Dubbo 服务的调用：

![Dubbo Admin](/contents/use-sentinel-to-govern-dubbo-services/dubbo-admin.png)

为了产生连续的调用，将服务消费者的接口暴露为 HTTP 服务，通过 [Apache Bench](http://httpd.apache.org/docs/2.4/programs/ab.html)（`ab`） 进行调用，如：

```bash
$ ab -t 1200 -c 100 'http://127.0.0.1:8080/dub/consumer/web/resources'
```

> 注意：使用 `ab` 调用本地服务时，不能使用 `localhost`，[需使用 `127.0.0.1`](https://www.bram.us/2020/02/20/fixing-ab-apachebench-error-apr_socket_connect-invalid-argument-22/)，否则会遇到 `apr_socket_connect(): Invalid argument (22)` 报错

![origin](/contents/use-sentinel-to-govern-dubbo-services/origin.png)

产生了流量，我们就可以开始治理了。

比如设定一个流控规则，限定 QPS 为 50：

![rule](/contents/use-sentinel-to-govern-dubbo-services/rule.png)

看看添加规则后的 QPS 曲线吧：

![after](/contents/use-sentinel-to-govern-dubbo-services/after.png)