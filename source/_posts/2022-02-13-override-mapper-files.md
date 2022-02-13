---
id: override-mapper-files
title: "覆盖 MyBatis Mapper 文件"
description: "通过两个实例说明如何覆盖 MyBatis 和 MyBatis-Plus 的 Mapper 文件"
date: 2022.02.13 10:26
categories:
    - Java
tags: [Spring Boot, Java, MyBatis]
keywords: MyBatis, MyBatis-Plus, Mapper 文件, 覆盖, 替换, Spring Boot 应用, 不重新打包, 不修改 jar 包 
cover: /contents/covers/override-mapper-files.png
---

在 [通过 -Xbootclasspath/a 参数修改 Spring Boot 应用行为实例](https://alphahinex.github.io/2022/01/23/bootclasspath-in-action/) 的 场景2 中，我们通过 `-Xbootclasspath/a` 参数，对 Spring Boot 应用 JAR 包中的 Mapper 文件进行了覆盖，但美中不足的是需要将未修改的 Mapper 文件也重新附加进去。

本文将演示两种仅需将改动的 Mapper 文件覆盖进去的方式。


不全部替换会怎么样？
================

先让我们看一下，在使用 MyBatis 时，如果仅将修改了的 Mapper 文件（即非全部 Mapper 文件）添加到 `bootclasspath` 时，会发生什么。

还是使用 [bootclasspath][demo] 中的演示代码：

```bash
# 对代码进行编译打包
$ mvn clean package -DskipTests

# 从编译路径删除未修改的 UserMapper 文件
$ rm -f hacked/target/classes/sql/db/mapper/UserMapper.xml

# 按照 Case 2 的语句启动服务
$ java -Xbootclasspath/a:./hacked/target/classes/sql -jar app/target/app-0.0.1-SNAPSHOT.jar

# 访问服务
$ curl localhost:8080
```

此时在控制台中，可以看到异常信息：

```text
2022-01-30 10:02:19.704 ERROR 17294 --- [nio-8080-exec-1] o.a.c.c.C.[.[.[/].[dispatcherServlet]    : Servlet.service() for servlet [dispatcherServlet] in context with path [] threw exception [Request processing failed; nested exception is org.apache.ibatis.binding.BindingException: Invalid bound statement (not found): io.github.alphahinex.bootclasspath.dao.UserDAO.customCount] with root cause

org.apache.ibatis.binding.BindingException: Invalid bound statement (not found): io.github.alphahinex.bootclasspath.dao.UserDAO.customCount
	at org.apache.ibatis.binding.MapperMethod$SqlCommand.<init>(MapperMethod.java:235) ~[mybatis-3.5.9.jar!/:3.5.9]
	at org.apache.ibatis.binding.MapperMethod.<init>(MapperMethod.java:53) ~[mybatis-3.5.9.jar!/:3.5.9]
	at org.apache.ibatis.binding.MapperProxy.lambda$cachedInvoker$0(MapperProxy.java:108) ~[mybatis-3.5.9.jar!/:3.5.9]
    ……
```

即无法找到 UserDAO 对应的 Mapper 文件。

按照上面的启动命令，此应用中有两个路径都包含 Mapper 文件：

1. `file [./hacked/target/classes/sql/db/mapper]` —— 仅包含修改的 CountryMapper 文件（没有 UserMapper，所以上面报找不到 UserDAO 对应的 Mapper 文件也正常）
1. `URL [jar:file:./app/target/app-0.0.1-SNAPSHOT.jar!/BOOT-INF/classes!/db/mapper]` —— 包含全部 Mapper 文件

如果我们将 `mybatis.mapper-locations` 参数由 `classpath:db/mapper/*Mapper.xml` 修改为 `classpath*:db/mapper/*Mapper.xml`（`classpath` 后面加一个 `*`） 会怎么样呢？

```bash
$ java -Xbootclasspath/a:./hacked/target/classes/sql -jar app/target/app-0.0.1-SNAPSHOT.jar --mybatis.mapper-locations=classpath:db/mapper/*Mapper.xml
```

应用在启动时，会直接报错：

```text
org.springframework.beans.factory.UnsatisfiedDependencyException: Error creating bean with name 'demoController' defined in URL [jar:file:/Users/alphahinex/github/origin/bootclasspath/app/target/app-0.0.1-SNAPSHOT.jar!/BOOT-INF/classes!/io/github/alphahinex/bootclasspath/controller/DemoController.class]: Unsatisfied dependency expressed through constructor parameter 0; nested exception is org.springframework.beans.factory.UnsatisfiedDependencyException: Error creating bean with name 'userDAO' defined in URL [jar:file:/Users/alphahinex/github/origin/bootclasspath/app/target/app-0.0.1-SNAPSHOT.jar!/BOOT-INF/classes!/io/github/alphahinex/bootclasspath/dao/UserDAO.class]: Unsatisfied dependency expressed through bean property 'sqlSessionFactory'; nested exception is org.springframework.beans.factory.BeanCreationException: Error creating bean with name 'sqlSessionFactory' defined in class path resource [org/mybatis/spring/boot/autoconfigure/MybatisAutoConfiguration.class]: Bean instantiation via factory method failed; nested exception is org.springframework.beans.BeanInstantiationException: Failed to instantiate [org.apache.ibatis.session.SqlSessionFactory]: Factory method 'sqlSessionFactory' threw exception; nested exception is org.springframework.core.NestedIOException: Failed to parse mapping resource: 'URL [jar:file:/Users/alphahinex/github/origin/bootclasspath/app/target/app-0.0.1-SNAPSHOT.jar!/BOOT-INF/classes!/db/mapper/CountryMapper.xml]'; nested exception is org.apache.ibatis.builder.BuilderException: Error parsing Mapper XML. The XML location is 'URL [jar:file:/Users/alphahinex/github/origin/bootclasspath/app/target/app-0.0.1-SNAPSHOT.jar!/BOOT-INF/classes!/db/mapper/CountryMapper.xml]'. Cause: java.lang.IllegalArgumentException: Mapped Statements collection already contains value for io.github.alphahinex.bootclasspath.dao.CountryDAO.cc. please check file [/Users/alphahinex/github/origin/bootclasspath/hacked/target/classes/sql/db/mapper/CountryMapper.xml] and URL [jar:file:/Users/alphahinex/github/origin/bootclasspath/app/target/app-0.0.1-SNAPSHOT.jar!/BOOT-INF/classes!/db/mapper/CountryMapper.xml]
……
Caused by: java.lang.IllegalArgumentException: Mapped Statements collection already contains value for io.github.alphahinex.bootclasspath.dao.CountryDAO.cc. please check file [/Users/alphahinex/github/origin/bootclasspath/hacked/target/classes/sql/db/mapper/CountryMapper.xml] and URL [jar:file:/Users/alphahinex/github/origin/bootclasspath/app/target/app-0.0.1-SNAPSHOT.jar!/BOOT-INF/classes!/db/mapper/CountryMapper.xml]
	at org.apache.ibatis.session.Configuration$StrictMap.put(Configuration.java:1037) ~[mybatis-3.5.9.jar!/:3.5.9]
	at org.apache.ibatis.session.Configuration$StrictMap.put(Configuration.java:993) ~[mybatis-3.5.9.jar!/:3.5.9]
	at org.apache.ibatis.session.Configuration.addMappedStatement(Configuration.java:791) ~[mybatis-3.5.9.jar!/:3.5.9]
	at org.apache.ibatis.builder.MapperBuilderAssistant.addMappedStatement(MapperBuilderAssistant.java:297) ~[mybatis-3.5.9.jar!/:3.5.9]
	at org.apache.ibatis.builder.xml.XMLStatementBuilder.parseStatementNode(XMLStatementBuilder.java:113) ~[mybatis-3.5.9.jar!/:3.5.9]
	at org.apache.ibatis.builder.xml.XMLMapperBuilder.buildStatementFromContext(XMLMapperBuilder.java:138) ~[mybatis-3.5.9.jar!/:3.5.9]
	at org.apache.ibatis.builder.xml.XMLMapperBuilder.buildStatementFromContext(XMLMapperBuilder.java:131) ~[mybatis-3.5.9.jar!/:3.5.9]
	at org.apache.ibatis.builder.xml.XMLMapperBuilder.configurationElement(XMLMapperBuilder.java:121) ~[mybatis-3.5.9.jar!/:3.5.9]
	... 68 common frames omitted
```

即两个路径内的 CountryMapper 文件冲突了。


如何精准覆盖？
===========

两种方式可以解决上述问题。

修改 MyBatis 源码
----------------

根据异常堆栈（`at org.apache.ibatis.session.Configuration$StrictMap.put(Configuration.java:1037) ~[mybatis-3.5.9.jar!/:3.5.9]`），找到报错位置源码：

```java
    @Override
    @SuppressWarnings("unchecked")
    public V put(String key, V value) {
      if (containsKey(key)) {
        throw new IllegalArgumentException(name + " already contains value for " + key
            + (conflictMessageProducer == null ? "" : conflictMessageProducer.apply(super.get(key), value)));
      }
      if (key.contains(".")) {
        final String shortKey = getShortName(key);
        if (super.get(shortKey) == null) {
          super.put(shortKey, value);
        } else {
          super.put(shortKey, (V) new Ambiguity(shortKey));
        }
      }
      return super.put(key, value);
    }
```

可以看到，在加载 Mapper 文件时，如果已经存在了相同的 key，再 put 时就会抛出异常。

因为我们的本意即为覆盖，所以一定会存在 key 相同的情况。根据 [Override same class](https://alphahinex.github.io/2020/12/27/override-same-class/) 中描述的类覆盖的先后顺序，通过 `-Xbootclasspath/a` 参数指定的路径会优先加载，所以可以在出现相同 key 时，直接忽略掉后加载的 Mapper 文件。修改方式如下：

```diff
@@ -1013,9 +1013,11 @@ public class Configuration {
     @Override
     @SuppressWarnings("unchecked")
     public V put(String key, V value) {
+      System.out.println("HACKED::Put key [" + key + "] with value [" + (value instanceof MappedStatement ? ((MappedStatement)value).getResource() : value) + "]");
       if (containsKey(key)) {
-        throw new IllegalArgumentException(name + " already contains value for " + key
+        System.out.println(name + " already contains value for " + key
             + (conflictMessageProducer == null ? "" : conflictMessageProducer.apply(super.get(key), value)));
+        return null;
       }
       if (key.contains(".")) {
         final String shortKey = getShortName(key);
```

bootclasspath 演示项目的 [mybatis-override][mbo] 分支提供了修改的 `Configuration.java` 类和可运行的代码，参照 README 中描述，将修改的 Mapper 文件和修改的 MyBatis 代码附加到原始 JAR 包中运行：

```bash
$ java -Xbootclasspath/a:./hacked/target/classes/sql:./hacked/target/classes:/Users/alphahinex/.m2/repository/org/mybatis/mybatis/3.5.9/mybatis-3.5.9.jar -jar app/target/app-0.0.1-SNAPSHOT.jar --mybatis.mapper-locations=classpath*:db/mapper/*Mapper.xml
```

> 注意替换上面的 mybatis-3.5.9.jar 路径，以及增加 `mybatis.mapper-locations` 参数指定 `classpath*:`前缀

应用启动不再报错，之后访问 http://localhost:8080 可以看到，`Country count` 的值从原 JAR 包中的 `151`，变更为了 SQL 修改后的 `26`，`User count` 值未发生改变。

```bash
$ curl localhost:8080
User count: 3
Country count: 26
```

即完成了 Mapper 文件的精准覆盖。


使用 MyBatis-Plus
----------------

相比修改 MyBatis 源码，更简单的方式是可以直接引入 [MyBatis-Plus](https://baomidou.com/)。

### 可修改源码重新打包

能够修改源码重新打包应用时，只需要引入 MyBatis-Plus 的依赖即可，例如在 [演示项目][demo] 的 `main` 分支做如下调整并重新打包，即可实现仅从 JAR 包外部加载变更的 Mapper 文件：

```diff
diff --git a/app/pom.xml b/app/pom.xml
index f3e5ec4..2b494ab 100644
--- a/app/pom.xml
+++ b/app/pom.xml
@@ -26,6 +26,11 @@
             <artifactId>mybatis-spring-boot-starter</artifactId>
             <version>2.2.1</version>
         </dependency>
+        <dependency>
+            <groupId>com.baomidou</groupId>
+            <artifactId>mybatis-plus-boot-starter</artifactId>
+            <version>3.1.2</version>
+        </dependency>

         <dependency>
             <groupId>com.h2database</groupId>
diff --git a/app/src/main/resources/application.properties b/app/src/main/resources/application.properties
index d8b39d2..ef5435a 100644
--- a/app/src/main/resources/application.properties
+++ b/app/src/main/resources/application.properties
@@ -1,4 +1,4 @@
 spring.datasource.url=jdbc:h2:mem:bootclasspath
+mybatis-plus.mapper-locations=classpath:db/mapper/*Mapper.xml
 spring.sql.init.schema-locations=classpath:db/sql/*ddl.sql
 spring.sql.init.data-locations=classpath:db/sql/*dml.sql
-mybatis.mapper-locations=classpath:db/mapper/*Mapper.xml
```

> 在引入了 MyBatis-Plus 后，注意将指定 Mapper 文件路径的参数，由 `mybatis.mapper-locations` 替换为 `mybatis-plus.mapper-location`

修改后的效果及演示，可在演示项目的 [plus][mbp] 分支查看：

```bash
$ mvn clean package -DskipTests

$ java -Xbootclasspath/a:./hacked/target/classes/sql -jar app/target/app-0.0.1-SNAPSHOT.jar --mybatis-plus.mapper-locations=classpath*:db/mapper/*Mapper.xml

$ curl localhost:8080
User count: 3
Country count: 26
```

### 无法重新打包

若无法修改源码或重新打包 Spring Boot 应用时，可参照 [如何给 Spring Boot 外挂 classpath？](https://alphahinex.github.io/2021/03/14/spring-boot-launcher/) 提供的方式，修改启动命令，将 MyBatis-Plus 相关 JAR 包添加进去（不建议使用 `-Xbootclasspath/a` 参数）。

需添加的 JAR 包如下，以放到 `./libs` 路径为例：

```bash
$ tree libs
libs
├── mybatis-plus-3.1.2.jar
├── mybatis-plus-annotation-3.1.2.jar
├── mybatis-plus-boot-starter-3.1.2.jar
├── mybatis-plus-core-3.1.2.jar
└── mybatis-plus-extension-3.1.2.jar

0 directories, 5 files
```

假设使用演示项目 [mybatis-override 分支][mbo] 构建出来的 JAR 包，可使用如下命令启动，并查看效果：

```bash
$ java -cp app/target/app-0.0.1-SNAPSHOT.jar -Dloader.path=./hacked/src/main/resources/sql,./libs org.springframework.boot.loader.PropertiesLauncher --mybatis-plus.mapper-locations=classpath*:db/mapper/*Mapper.xml
```

有两点需要注意：

1. `-Dloader.path` 参数中的多个路径使用 `,` 间隔
1. 因原始 JAR 包中使用的是 MyBatis，通过启动命令动态加入了 MyBatis-plus，故需添加 `mybatis-plus.mapper-locations` 参数指定 Mapper 文件路径

访问 http://localhost:8080 ，可看到外部挂载的 Mapper 文件内容已生效。

```bash
$ curl localhost:8080
User count: 3
Country count: 26
```

参考资料
=======

* [MyBatis-Plus 中 Mapper 重载踩坑指南](https://jishuin.proginn.com/p/763bfbd63a31)

[demo]:https://github.com/AlphaHinex/bootclasspath
[mbo]:https://github.com/AlphaHinex/bootclasspath/tree/mybatis-override
[mbp]:https://github.com/AlphaHinex/bootclasspath/tree/plus