---
id: spring-boot-external-config-file
title: "Spring Boot 配置文件拾遗"
description: "总有一款适合你"
date: 2021.05.09 10:26
categories:
    - Spring
tags: [Spring Boot]
keywords: Spring Boot, config, application, properties, yml, yaml, override, location
cover: /contents/covers/spring-boot-external-config-file.png
---

说到 Spring Boot 的配置文件，大家应该都不陌生，Spring Boot 也为其外部配置文件提供了一些参数，使我们能够更加灵活的对其中的参数进行设定及覆盖，一起来查缺补漏吧。

## spring.config.name

默认情况下，Spring Boot 的配置文件为 `application.properties` 或 `application.yml`，而这个配置文件的文件名（不包括扩展名），可以通过 `spring.config.name` 参数进行修改。

**注意：为了其他人更容易找到配置文件，不建议修改这个参数的默认值。**

## spring.config.location

Spring Boot 应用启动时，默认情况下会自动按顺序从如下路径加载 `application.properties` 或 `application.yml` 文件：

1. 当前路径的 `/config` 子路径内：`file:./config/`
1. 当前路径：`file:./`
1. classpath 路径下的 `/config` 包内：`classpath:/config/`
1. classpaht 根路径：`classpath:/`

上面的路径按加载的优先级排序，即排在上面路径中的配置文件中的内容，会覆盖下面路径中的配置文件内容。

**其中，`当前路径` 指的是 `java` 命令的执行路径，不是 fat jar 所在路径。**

可以使用 `spring.config.location` 参数，对上面的路径进行**覆盖**，**注意，是覆盖，不是附加。**

例如，当通过如下命令启动应用时

```bash
$ java -jar myproject.jar --spring.config.location=classpath:/custom-config/,file:./custom-config/
```

配置文件不再从上面默认的四个位置加载，而是变为按优先级从如下两个位置加载：

1. `file:./custom-config/`
1. `classpath:/custom-config/`

`file:./custom-config/` 中的内容会覆盖 `classpath:/custom-config/` 中的内容。

## spring.config.additional-location

如果仅希望通过参数额外指定几个优先级比默认路径更高的加载配置文件的路径，可以使用 `spring.config.additional-location` 参数。

例如使用如下命令启动应用：

```bash
$ java -jar myproject.jar --spring.config.additional-location=classpath:/custom-config/,file:./custom-config/
```

加载配置文件的路径及优先级为：

1. `file:./custom-config/`
1. `classpath:/custom-config/`
1. `file:./config/`
1. `file:./`
1. `classpath:/config/`
1. `classpath:/`

通常情况下，多模块时我们不会把所有配置都放到一个配置文件里。运行时需要指定环境限定的参数时，使用 `spring.config.additional-location` 会比 `spring.config.location` 更加实用。

## 指定 profile 时

当通过 `spring.profiles.active` 参数指定了 profile 时，`application-{profile}.yml` 的优先级，会比 `application.yml` 的优先级高，不论 `application-{profile}.yml` 文件在哪个路径内。

例如：

```bash
$ java -jar myproject.jar --spring.config.additional-location=classpath:/custom-config/,file:./custom-config/ --spring.profiles.active=prod
```

有 `classpath:/custom-config/application.yml` 和 `file:./config/application-prod.yml` 两个配置文件，后者中的值依然会覆盖前面配置文件中的内容。 

当通过 `spring.profiles.active` 参数指定多个 profile 时，后面 profile 会覆盖前面的。如 `spring.profiles.active=prod,live` 时，`application-live.yml` 会覆盖 `application-prod.yml`。

> 如果使用 `spring.config.location` 参数指定的不是路径而是具体的文件时，如 `spring.config.location=./application.yml`，则此时即使指定了 profile，`./application-{profile}.yml` 也不会生效。

更多参数及用法，可以参阅 Spring Boot 官方文档，如 [Spring Boot 2.4.5 Reference][boot]。

[boot]:https://docs.spring.io/spring-boot/docs/2.4.5/reference/htmlsingle/#boot-features-external-config-files