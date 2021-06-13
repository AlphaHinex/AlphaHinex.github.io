---
id: kong-in-action
title: "Kong 实战"
description: "快速上手小贴士"
date: 2021.06.13 10:26
categories:
    - Cloud Native
tags: [Microservices, Api Gateway]
keywords: Kong, Api Gateway, Konga, service, route, upstream, plugin
cover: /contents/kong-in-action/cover.png
---

## Kong

### 简介

[Kong Gateway](https://konghq.com/kong/) 是一个 API 网关，有开源（OSS）和企业版（Enterprise）两个版本。

Kong 构建在 Nginx 之上，更明确点说，Kong 是一个运行在 Nginx 中的 Lua 应用，从其 [github](https://github.com/Kong/kong) 仓库的语言中也可以看出来。

### 基本概念

除了与 Nginx 类似的一些概念（如 Load Balancing，Upstream）外，要使用 Kong，还需了解一些基本概念。

![overview](/contents/kong-in-action/overview.png)

|概念|描述|
|:--|:--|
|Service|Service 对象代表上游的 API 接口或服务|
|Route|Route 定义了当请求到达网关后，如何以及是否将请求发送给对应的 Service。一个 Service 可以对应多个 Route|
|Admin API|Kong Gateway 提供的 RESTful API 服务，可用来对 Kong 进行配置及管理|
|Plugins|插件系统，可为网关增加各种附加能力，如访问控制、缓存、限流、日志等|

> Kong 1.1 版本起支持了 [无需数据库](https://docs.konghq.com/gateway-oss/2.4.x/db-less-and-declarative-config/) 的运行方式，虽然能最小依赖快速启动服务，但无法动态添加 Service、Route 等实体，只能通过声明式的配置一次性定义所有配置。

Kong 服务部署完成后，默认情况下会监听如下端口：

* `:8000` 接受 HTTP 请求并转发至上游服务
* `:8443` 接受 HTTPS 请求并转发至上游服务
* `:8001` Admin API HTTP 服务端口
* `:8444` Admin API HTTPS 服务端口

### 配置

为 Kong 添加配置时，需通过其 Admin API 进行操作，如 [Configuring a Service](https://docs.konghq.com/gateway-oss/2.4.x/getting-started/configuring-a-service/) 中所示。

OSS 版 Kong 并未提供官方 GUI，可使用非官方开源 GUI —— [Konga](https://github.com/pantsel/konga)


## Konga

Konga 是一个前端 Web 应用，可连接数据库存储 Konga 自身的数据，也可不依赖数据库使用本地磁盘进行存储。

下面使用 Konga 配置一个 Route，将接收到的请求转发给 Service。

### 创建 Connection

Konga 启动时无需关联 Kong，服务启动后，可以配置多个 Kong Admin API 的 Connection。只能激活一个连接，但可随时进行切换。

首先创建一个 Connection：

![connections](/contents/kong-in-action/connections.png)

### 配置 Upstream

为避免在每个 Service 配置上游服务器地址，也为了支持多个上游服务器进行负载均衡，可以为要代理的服务先配置一个 Upstream（仅 name 必填）：

![upstream](/contents/kong-in-action/upstream.png)

然后在 Details 的 Targets 中添加上游服务的 host 和 port：

![targets](/contents/kong-in-action/targets.png)

### 添加 Service

![service](/contents/kong-in-action/service.png)

添加 Service 时，主要指定要代理的服务 url，包括协议（http、https）、host、port 和 path，可通过 url 统一指定，也可分别填写各项内容。

### 配置 Route

Route 不能单独添加，需要在 Service 中进行配置：

![route](/contents/kong-in-action/route.png)

Route 里主要配置的是 `Paths` 属性，一个 Route 可以配置多个路径，这个路径代表访问 Kong Gateway 对应路径时，会匹配到此 Route 并进一步将请求转发给 Service。

一个 Service 可以配置多个 Route。

### 访问测试

完成上述配置后，即可访问 Kong Gateway 的 http://kong:8000/gateway/path ，请求会转发至 http://upstream1:8080/foo/bar。

### 使用插件

Konga 中可以配置 Kong 的 Plugin，Plugin 可以在全局开启，也可以仅对某个 Service 开启。

以 File Log 插件为例，可以使用此插件将请求和响应相关的日志，记录到文件中。

![plugin](/contents/kong-in-action/plugin.png)

> 注意：File Log 插件中的 path 为日志文件全路径，不是日志文件所在路径。