---
id: k8s-enable-service-links
title: "【转】Kubernetes 服务自动注入变量引发的血案"
description: "环境变量覆盖配置文件中设置导致的异常"
date: 2025.07.06 10:34
categories:
    - K8s
    - Spring
tags: [K8s, Kubernetes, Spring Boot]
keywords: enableServiceLinks, Relaxed Binding, environment variables, externalized configuration
cover: /contents/covers/k8s-enable-service-links.png
---

- 原文地址：https://www.jianshu.com/p/3cfdb680b14e
- 原文作者：[微凉哇](https://www.jianshu.com/u/d682f8cbe064)
- 相关阅读：
1. [enableServiceLinks](https://notes.kodekloud.com/docs/Kubernetes-Troubleshooting-for-Application-Developers/Troubleshooting-Scenarios/enableServiceLinks)
1. [Relaxed-Binding-2.0#environment-variables](https://github.com/spring-projects/spring-boot/wiki/Relaxed-Binding-2.0#environment-variables)
1. [Externalized Configuration](https://docs.spring.io/spring-boot/reference/features/external-config.html)

### 背景介绍

笔者最近基于kubernetes部署一套系统时，发现了一个有趣的现象：配置文件内的部分变量读取错误，报错日志如下

```log
2025-06-13T17:08:54.591570855+08:00 Caused by: org.springframework.beans.TypeMismatchException: Failed to convert value of type 'java.lang.String' to required type 'int'; nested exception is java.lang.NumberFormatException: For input string: "tcp://10.233.17.38:9200"
```

配置片段如下：

```yaml
es:
  clusterName: es-cluster
  connectTimeout: 5000
  connectionRequestTimeout: 5000
  enableAuth: false
  host: es.demo
  maxConnectNum: 100
  maxConnectPerRoute: 100
  password: elastic
  port: 9200
```

明明`port`配置的`9200`，为什么取的却是`tcp://10.233.17.38:9200`？

笔者开始了漫漫的探索真相之路。

ps: `es`与`java`应用部署在同一命名空间下，且均配置了`service`

### 猜想阶段

1. 猜想配置文件未读取到

由于部署的是spring boot应用，猜想可能配置的优先级问题（毕竟spring boot可以通过多个参数配置）

论证：首先排除这种情况，因为配置文件内的其他配置项（如数据库连接项）是可以正确读取到的。

猜想失败

2. 猜想配置文件格式问题，导致的配置项未正确读取到

论证：笔者将配置内容脱敏后，使用yaml校验工具校验，发现无误。

猜想失败

3. 猜测代码内取值错误

论证：笔者将部署包反编译后，查看配置项取值，发现无误。

猜想失败

### 求索阶段

由于部署时间紧，没有太多的时间去研究这个问题。笔者干脆通过命令行参数的形式（--es.port=9200）传入配置项，使其生效，问题解决。

系统部署交付完成后，这个问题一直困扰着笔者，想了解为什么会存在这种问题？于是笔者借助deepseek分析可能原因。deepseek给出了以下几种可能：
1. 配置值包含非数字字符 -> 修正配置为纯数字端口
2. 字段类型与配置类型不匹配
3. 使用类型安全绑定（@ConfigurationProperties）
4. 配置值被意外覆盖 -> 检查配置优先级（环境变量>配置文件）
5. 缺少 setter 方法	为配置类的每个字段添加 setter

其中第4种情况引起了笔者的注意，笔者了解到环境变量是能覆盖配置文件内的配置项的。

笔者于是进入该应用pod查看环境变量：

```bash
$ env|grep ES_PORT  
KUBERNETES_PORT_443_TCP=tcp://10.233.0.1:443
ES_PORT_9200_TCP_ADDR=10.233.17.38
ES_PORT=tcp://10.233.17.38:9200
KUBERNETES_PORT_443_TCP_PROTO=tcp
ES_PORT_9200_TCP_PROTO=tcp
KUBERNETES_PORT_443_TCP_ADDR=10.233.0.1
KUBERNETES_PORT=tcp://10.233.0.1:443
KUBERNETES_PORT_443_TCP_PORT=443
ES_PORT_9200_TCP_PORT=9200
ES_PORT_9200_TCP=tcp://10.233.17.38:9200
```

似乎我们接近了真相！

此时，笔者又有了新的疑惑：这些环境变量是谁注入进来的？

于是再次请教deepseek，deepseek给出了 “罪魁祸首” -> `Kubernetes 服务自动注入变量`

并给出解决方案：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  enableServiceLinks: false  # 关键配置！
  containers:
  - name: my-app
    image: my-image
```

笔者按照该样例对问题应用进行配置，应用启动正常，可以正确读取到配置文件内的配置变量！笔者进入pod查看环境变量，ES相关的环境变量全部消失了。

由此笔者得出了导致此次问题的原因：k8s的服务自动注入变量机制生成了”错误的配置环境变量值“，并被java程序取到，导致此次血案的发生。

### 进一步思索

1. 到底是“谁”读取环境变量的值，覆盖配置文件中的值？

笔者，第一时间想到的是es client，认为是es client在初始化阶段，显示地读取环境变量ES_PORT。于是乎翻阅了初始化es client源码，未果。

于是又求助deepseek探求真相，deepseek给出

```text
提问 : 为什么 Elasticsearch 配置优先使用环境变量

↓以下是deepseek给出的回答：

1. Spring Boot 自动配置机制
当使用 spring-boot-starter-data-elasticsearch 时，自动配置类 ElasticsearchRestClientAutoConfiguration 会读取属性：

Java
@Configuration(proxyBeanMethods = false)
@ConditionalOnClass(RestHighLevelClient.class)
@EnableConfigurationProperties(ElasticsearchRestClientProperties.class) // ⬅️ 关键类
public class ElasticsearchRestClientAutoConfiguration {
    // ...
}
其中的 ElasticsearchRestClientProperties 通过标准 Spring 机制绑定属性，遵守属性优先级规则。

2. 环境变量命名规则
Spring Boot 自动将环境变量名转为 Spring 属性名：

配置文件属性：spring.elasticsearch.uris=http://localhost:9200
等效环境变量名：SPRING_ELASTICSEARCH_URIS=http://localhost:9201
如果设置了 SPRING_ELASTICSEARCH_URIS 环境变量，它会覆盖配置文件中的值。
```

至此，真相水落石出。deepseek给出了解决方案：

```properties
# application.properties
spring.config.use-environment-overrides=false
```

**PS: spring boot程序读取配置优先级如下（后者覆盖前者）:**

1. 默认属性（通过 SpringApplication.setDefaultProperties 设置）
2. @Configuration 类上的 @PropertySource
3. 配置文件 (application.properties 或 application.yml)
4. 随机属性 (random.*)
5. 操作系统环境变量
6. Java 系统属性 (System.getProperties())
7. JNDI 属性