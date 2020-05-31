---
id: microservices-integration-test-in-action
title: "微服务的自动化集成测试实战"
description: "在持续集成环境，借助容器进行微服务的自动化集成测试实例"
date: 2020.02.05 18:56
categories:
    - Test
    - Microservices
    - DevOps
tags: [Integration test, Automation test, Microservices, DevOps, GitHub Actions, Docker]
keywords: Integration test, Automation test, Microservices, DevOps, CI, GitHub Actions, Docker, Docker Compose, 集成测试, 自动化测试, 微服务, 持续集成
cover: /contents/covers/microservices-integration-test-in-action.jpg
---

场景
---

利用 [How to integrate SEATA AT mode with Spring Cloud](https://alphahinex.github.io/2020/01/22/how-to-integrate-seata-at-mode-with-spring-cloud/) 中定义好的微服务，进行集成测试。

包含以下服务：

1. 库存服务（storage）
1. 用户账户服务（account）
1. 订单服务（order）
1. 业务服务（business）

业务服务作为直接被调用的接口，组织关联其他三个服务。下订单时，服务的调用顺序如下：

```
1. 减库存（storage）
2. 创建订单
2.1. 扣减用户账户（account）
2.2. 生成订单（order）
```

服务之间存在依赖关系，各服务对基础设施也有依赖（数据库、注册中心、分布式事务协调者等）。

集成测试包含两个测试用例：

1. 业务服务成功调用：验证请求成功
1. 业务服务调用出现异常：验证分布式事务生效，异常节点之前的服务数据已回滚


工具链
-----

* [Spring Boot](https://spring.io/projects/spring-boot)：借助 Spring Boot 对测试框架的集成和支持，运行测试用例
* [JUnit](https://junit.org/junit4/)：集成测试用例编写
* [Gradle](http://gradle.org/)：构建工具执行集成测试，自动化执行的基础
* [docker](https://www.docker.com/)：各服务运行环境在容器中运行，便捷搭建集成测试环境
* [docker-compose](https://docs.docker.com/compose/)：容器编排
* [GitHub Actions](https://github.com/features/actions)：持续集成平台，负责自动执行集成测试
* [wait-for-it](https://github.com/vishnubob/wait-for-it)：约束有依赖关系的服务进行启动等待


实战
---

### 编写集成测试用例

借助 Spring Boot 的支持（如 [Testing with a running server](https://docs.spring.io/spring-boot/docs/2.2.4.RELEASE/reference/html/spring-boot-features.html#boot-features-testing-spring-boot-applications-testing-with-running-server)），在随机端口启动一个 Spring Boot 应用，执行对业务服务的调用。

本例中基于集成测试基类（[AbstractIntegrationTest.groovy](https://github.com/AlphaHinex/spring-roll/blob/master/modules/dev-kits/roll-test/src/main/groovy/io/github/springroll/test/AbstractIntegrationTest.groovy)），按场景中描述编写了两个测试用例，完整代码可参见 [IntegrationTest.groovy](https://github.com/AlphaHinex/seata-at-demo/blob/seata-at/modules/integration-test/src/test/groovy/io/github/alphahinex/demo/seata/at/integration/test/IntegrationTest.groovy)：

```groovy
@Test
void successRequest() {
    vo.put('amount', 100)
    post(url, JsonOutput.toJson(vo), HttpStatus.CREATED)
}

@Test
void failedRequest() {
    def storage = resOfGet("http://localhost:8081/at/storage/$commodityCode", HttpStatus.OK).count

    // 生成订单服务抛出异常
    vo.put('amount', -10)
    post(url, JsonOutput.toJson(vo), HttpStatus.INTERNAL_SERVER_ERROR)

    // 应用全局事务，库存数据回滚，不会变更
    def newStorage = resOfGet("http://localhost:8081/at/storage/$commodityCode", HttpStatus.OK).count
    assert newStorage == storage
}
```

### 容器化部署所有服务

为简化集成测试运行环境，将所有服务运行在容器中，通过 Docker Compose 进行编排，部署在单节点。

因为服务之间存在依赖关系，被依赖的服务若未完成启动，可能会导致有依赖的服务也不能正常运行。为解决这个问题，仅依赖 Docker Compose 中提供的 [depends_on](https://docs.docker.com/compose/compose-file/#depends_on) 是不够的，因为 `depends_on` 仅能保证服务的启动顺序，不能保证服务启动完成（能正常提供服务）之后再启动后续服务。

官方文档中针对此问题也给出了 [方案](https://docs.docker.com/compose/startup-order/)，可利用 `wait-for-it` 脚本强制服务进行等待。例如：

```yaml
order:
  image: propersoft/docker-jre:8u171-jre
  volumes:
    - ./modules/order/build/libs/order-0.0.1-SNAPSHOT.jar:/usr/local/demo/order.jar
    - ./docker/wait-for-it.sh:/wait-for-it.sh
  depends_on:
    - mysql
    - nacos
    - storage
    - account
    - seata-server
  command: ["./wait-for-it.sh", "-t", "0", "storage:8081", "--", "./wait-for-it.sh", "-t", "0", "account:8082", "--", "java", "-jar", "/usr/local/demo/order.jar"]
  ports:
    - "8083:8083"
```

完整的配置可参考 [docker-compose](https://github.com/AlphaHinex/seata-at-demo/blob/seata-at/docker-compose.yml)。

这里可能还会遇到一个问题：Feign 接口首次调用失败。

服务之间通过 `@FeignClient` 进行 RESTful API 的调用，在默认配置下，Ribbon 是懒加载的，在首次请求时，才会开始初始化相关类，而这可能就会导致各服务启动完毕后，首次被 Feign Client 调用时，调用失败。

为解决这个问题，可以启用 Ribbon 的 `eager load`，并配置相应客户端，如：

```yaml
ribbon:
  eager-load:
    enabled: true
    clients: account, storage
```

完整配置文件可参考 [这里](https://github.com/AlphaHinex/seata-at-demo/blob/seata-at/modules/order/src/main/resources/application-dev.yml)。

### 运行集成测试

在 [docker-compose.yml](https://github.com/AlphaHinex/seata-at-demo/blob/seata-at/docker-compose.yml) 所在路径执行

```bash
$ docker-compose up -d
```

即可启动所有服务。因为服务间依赖及强制等待，所有服务启动完毕需要一段时间。

可访问最后一个服务（ http://localhost:8084 ），或查看容器日志，确认服务是否完成启动。

之后可在源码中直接运行集成测试查看效果。

#### 集成测试与单元测试分别执行

因为集成测试需要启动服务而单元测试不需要，且集成测试的执行时间一般都要比单元测试的时间长（主要消耗在环境准备上），故利用构建工具执行测试时，最好将单元测试与集成测试分开执行。

可将集成测试单独放到一个模块内，在常规测试任务中，将这个模块排除，并重新注册一个执行集成测试的任务，如：

```
├── account
├── business
├── integration-test
├── order
└── storage
```

```gradle
test {
  exclude '**/integration/**'
}

task integrationTest(type: Test, dependsOn: test) {
  include '**/integration/**'
}
```

完整配置可见 [integration-test.gradle](https://github.com/AlphaHinex/seata-at-demo/blob/seata-at/modules/integration-test/integration-test.gradle)。

之后可通过 `gradlew test` 执行单元测试，通过 `gradlew integrationTest` 执行集成测试。

> 单元测试中，涉及调用其他服务时，可通过注解 `@MockBean` 来模拟其他微服务的行为，例如 [BusinessApplicationTest.groovy](https://github.com/AlphaHinex/seata-at-demo/blob/seata-at/modules/business/src/test/groovy/io/github/alphahinex/demo/seata/at/business/BusinessApplicationTest.groovy)

在本地环境可验证集成测试执行结果为通过。

那么如何在持续集成环境自动化完成这个过程呢？

### 持续集成环境配置

完成以上步骤后，要完成自动化测试，理论上只剩下在 CI 上启动服务和执行集成测试任务了。

本例中选用的 CI 平台是 GitHub Actions，对于托管在 GitHub 上的项目，要使用 GitHub Actions，需要做的就是在代码仓库中增加配置文件，如 [./github/workflows/check.yml](https://github.com/AlphaHinex/seata-at-demo/blob/seata-at/.github/workflows/check.yml)。

So easy 是吧，但在 GitHub Actions 中运行本例的集成测试时，依然遇到了两个问题：

1. **无法映射到 3306 端口**：不确定 GitHub Actions 环境中 3306 端口是不是给 mysql 的 action 预留了，docker 无法将容器端口映射到宿主的 3306 上。修改为其他端口即可。
1. **wait-for-it 无效**：在 GitHub Actions 环境下 wait-for-it 脚本虽然能正常执行但没有起到实际作用，此处没有找到太好的解决办法，通过增加一个等待的 action，在执行 `docker-compose up` 后强行等待一段时间，等服务都启动完成后再去执行集成测试。具体例子可见 [check.yml#L43-L46](https://github.com/AlphaHinex/seata-at-demo/blob/seata-at/.github/workflows/check.yml#L43-L46)。

在 GitHub Actions 上的集成测试执行情况可见：https://github.com/AlphaHinex/seata-at-demo/actions?query=workflow%3ACheck

本文完整实例可见：https://github.com/AlphaHinex/seata-at-demo
