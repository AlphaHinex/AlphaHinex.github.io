---
id: easy-java-and-spring-test
title: "写测试用例都这么简单了，你不来试试？"
description: "面向 Java 和 Spring 的常见测试场景"
date: 2022.04.17 10:34
categories:
    - Java
    - Spring
    - Spring Roll
tags: [Java, Spring, Spring Roll, Spring Boot, Integration test, Automation test]
keywords: 测试用例, 单元测试, 集成测试, Groovy, Spock Framework, Mockito
cover: /contents/easy-java-and-spring-test/cover.jpg
---

测试用例
=======

提到测试，所有人都知道它的重要性，但大部分开发人员都会觉得测试应该交给测试人员来做，或者直接到环境上执行一下、点一点看看没有问题就可以了。

究其原因，个人觉得是因为写单元测试的成本太高了，尤其是对外部环境依赖较多的项目，开发环境想运行起来都要依赖特定的组件，就更别提测试用例的运行了。

一个好的测试用例，应该是自动化的、可重复执行的，容易理解、容易运行的，且有明确的断言，以便在代码出现不符合预期的结果时，能够快速发现且定位到问题的。

本文以一些面向 Java 和 Spring 的常见测试场景为例，介绍一种简单的测试用例写法。

Scaffold
========

先来介绍几个脚手架，可以有效降低写测试用例的难度。

Groovy
------

[Groovy](http://www.groovy-lang.org/) 是一种运行在 JVM 上的动态语言，与 Java 有着极佳的兼容性，并且有着更加简洁的语法。

使用 Groovy 的 [Killer App](http://www.groovy-lang.org/ecosystem.html) 也有不少，比如著名的 [Gradle](https://github.com/gradle/gradle) 和 [Grails](https://github.com/grails)，如果在生产环境中使用还有顾虑，不妨先在测试用例中体会 Groovy 的魅力。

说 Groovy 与 Java 有着极佳的兼容性，是因为直接将一个 Java 文件的扩展名从 `.java` 改为 `.groovy` 你就得到了一个合法的 Groovy 文件，可以在 `.groovy` 的文件中混合使用 Java 和 Groovy 的语法，非常的方便。IDEA 对 Groovy 也有着开箱即用的支持，可以借助 IDEA 的提示，边用边学 Groovy 的语法。

通过一个嵌套 Map 和类型转换的例子，简单对比一下相同功能的 Java 和 Groovy 代码：

Java:
```java
Map<String, String> nested = new HashMap<>();
nested.put("nested_key", "nested_value");
Map<String, Object> outer = new HashMap<>();
outer.put("outer_key", "outer_value");
outer.put("nested", nested);

System.out.println(((Map)outer.get("nested")).get("nested_key"));
```

Groovy:
```groovy
def outer = [outer_key: 'outer_value', nested: [nested_key: 'nested_value']]

println outer.nested.nested_key
```

感受到 Groovy 的简洁了吧！

在一个 Java 项目中，可以将 Java 源码放在 `src/main/java` 目录下，将 Groovy 测试用例源码放在 `src/test/groovy` 目录下，并为项目添加 Groovy 的相关插件，这样就可以在 `src/test/groovy` 目录下直接运行 Groovy 的测试用例了。

Gradle 项目中添加 Groovy 相关插件比较简单，只需在 `build.gradle` 文件中添加如下内容：

```groovy
plugins {
    id 'groovy'
}

dependencies {
    implementation 'org.codehaus.groovy:groovy'
}
```

Maven 项目需要在 `pom.xml` 文件中添加如下内容：

```xml
<dependencies>
    <dependency>
        <groupId>org.codehaus.groovy</groupId>
        <artifactId>groovy</artifactId>
    </dependency>
</dependencies>

<plugins>
    <plugin>
        <groupId>org.codehaus.gmavenplus</groupId>
        <artifactId>gmavenplus-plugin</artifactId>
    </plugin>
</plugins>
```

在 Spring Initializr（ https://start.spring.io/ ）中，可以直接生成 Groovy 语言的 Maven 或 Gradle 项目，可用作配置的参考。

Spock Framework
---------------

[Spock Framework](https://spockframework.org/) 是一个面向 Java 和 Groovy 应用的测试框架，基于这个框架写出的测试用例，具有更高的可读性，例如：

```groovy
@Unroll
def "Pinyin of #input is #result"() {
    expect:
    result == PinyinUtil.quanpin(input)

    where:
    input       | result
    ''          | ''
    null        | ''
    '好似'       | 'haosi'
    '似的'       | 'shide'
    '混1a搭'     | 'hun1ada'
    '绿'         | 'lv'
}
```

上面的测试用例，会使用一组输入数据（`input`）传入拼音工具类的全拼方法中，并校验转换结果是否与结果列（`result`）中对应的值一致，在出现不一致的情况时，会直接输出具体失败的那组数据，如 `Pinyin of 似的 is shide` 用例执行失败。

![spock](/contents/easy-java-and-spring-test/spock.png)

Spring Roll
-----------

[Spring Roll](https://github.com/AlphaHinex/spring-roll) 是一个 Side Project，其中的 [roll-test](https://github.com/AlphaHinex/spring-roll/tree/develop/modules/dev-kits/roll-test) 模块集成了 Spock Framework，并提供了一些测试类的基类，引入 `roll-test` 模块的方法可参考 [How to use](https://github.com/AlphaHinex/spring-roll#how-to-use)。

目前，Spring Roll 主要提供以下三个基类：

1. `AbstractSpringTest`：用于需要 Spring 上下文的测试用例，包含常用的 RESTful 接口测试方法
1. `AbstractSpringTxTest`：继承自 `AbstractSpringTest`，并提供了事务支持，可用于需要事务的测试用例
1. `AbstractIntegrationTest`：提供一种集成测试方案，会在随机端口真正启动 Web 应用，并提供与 `AbstractSpringTest` 一致的 RESTful 接口测试用法

下面基于一些常见的测试场景，来介绍测试用例的写法。


测试 Java 类
===========

当要测试的类是一个 POJO（Plain Old Java Object），并不依赖 Spring 框架时，可直接使测试类继承 Spock Framework 提供的 `Specification` 基类，如：

```groovy
class AntResourceUtilSpec extends Specification {

    def "Support multi-locations separated by comma"() {
        def res = AntResourceUtil.getResources('classpath*:**/ant1.test,classpath*:**/springroll/**/*.test')

        expect:
        // According to actual files under path pattern
        res.length == 2
    }

}
```

在 `expect:` 上面，可以编写测试的准备工作代码，如准备 `res` 的内容；`expect:` 下面，编写测试用例的断言，即期望的行为。如果需要使用一批数据，校验方法的行为，可像上面拼音工具类的测试用例一下，在 `expect:` 部分后面增加一个 `where:` 块，用来提供测试数据。


测试 Spring Bean
================

在基于 Spring 进行开发时，更多的情况下我们的测试目标类可能是一个 Spring Bean，这时可使测试类继承自 `AbstractSpringTest`。

例如我们有一个 `ExportExcelController` 如下：

```java
@Controller
@RequestMapping("/export/excel")
public class ExportExcelController {

    @GetMapping("/{title}")
    public void export(@PathVariable String title, @RequestParam String cols, @RequestParam String url,
                       String tomcatUriEncoding, HttpServletRequest request, HttpServletResponse response) throws Exception {
        // ...
    }

}
```

测试用例中，希望验证这个 Get 接口的行为，可以这样写：

```groovy
class ExportExcelControllerTest extends AbstractSpringTest {

    @Test
    void test() {
        def cols = '[{"display":"名称","name":"name","showTitle":true,"field":"name","hidden":false,"label":"名称","prop":"name","title":"名称"},{"label":"名称","prop":"name","width":"40"}]'
        cols = URLEncoder.encode(cols, 'UTF-8')
        def url = URLEncoder.encode('/test/query', 'UTF-8')

        get("/export/excel/abc?cols=$cols&url=$url", HttpStatus.OK)
    }
}
```

其中，`get("/export/excel/abc?cols=$cols&url=$url", HttpStatus.OK)` 意为使用 Get 方法调用 `/export/excel/abc` 接口，传入两个必须的参数，并预期返回状态码为 `200`。

与 `MvcResult get(String url, HttpStatus statusCode)` 类似，在 `AbstractSpringTest` 基类中，还提供了 `post`、`put`、`delete` 等 RESTful 接口常用的各类方法的测试方法。为方便对接口返回内容进行进一步的验证，还有 `resOfGet`、`resOfPost` 和 `resOfPut` 方法，直接获取接口的返回对象，例如：

```groovy
@Test
void test() {
    assert resOfGet('/app/node', HttpStatus.OK).data.startsWith('http')
}
```

`AbstractSpringTest` 中定义的属性和方法如下图，大部分均为 `protected` 修饰，可被子类直接使用。

![outline](/contents/easy-java-and-spring-test/outline.png)


测试数据库相关操作
===============

事务
----

在测试数据库相关的操作时，一般情况下不希望测试数据被真正的插入到数据库中，造成垃圾数据或测试方法之间的互相影响，此时可以使测试类继承 `AbstractSpringTxTest` 基类，测试数据会在测试用例执行完毕后自动回滚。

如果需要真正将数据插入到数据库中，可以在类或方法上使用 `@NoTx` 注解。

使用内存数据库减少测试环境依赖
-------------------------

为了测试用例能够更容易的被执行，应尽量减少测试用例对环境的依赖。数据库就是其中一个最主要的依赖。如果你的项目使用了一些数据库无关的 ORM 框架，可以方便的将测试环境所使用的数据库切换到内存数据库上。但如果你的项目是与具体数据库绑定的，这件事做起来就没有那么容易了。

如果你的项目使用的是 MySQL，项目中包含了必需的数据库脚本，那么可以尝试使用 `roll-test` 模块所提供的 `MysqlTranslateToH2Executor` 来自动完成 MySQL 脚本至 H2 脚本的转换，并在 H2 中执行这些脚本。

在项目中依赖了 `roll-test` 模块后，可以通过设置 `roll.test.datasource.type=mysql2h2` 参数来启用此功能，默认会扫描符合 `classpath*:sql/**/*.sql` 路径模式的所有脚本文件，可通过 `roll.test.datasource.mysql-scripts` 参数调整扫描路径。


集成测试
=======

继承 `AbstractSpringTest` 的测试用例，是通过 `MockMvc` 对象来模拟 HTTP 请求的。如果希望通过真实的 HTTP 请求调用 RESTful 接口，可以继承 `AbstractIntegrationTest` 基类，比如想测试一下项目配置的 `AllowCrossOriginFilter` 是否生效：

```groovy
class AllowCrossOriginFilterTest extends AbstractIntegrationTest {

    @Test
    void checkResponseHeaders() {
        def connection = get('/test', HttpStatus.NOT_FOUND)
        def headers = connection.headerFields
        assert headers.containsKey('Access-Control-Allow-Credentials')
        assert headers.containsKey('Access-Control-Allow-Headers')
        assert headers.containsKey('Access-Control-Allow-Methods')
        assert headers.containsKey('Access-Control-Allow-Origin')
        assert headers.containsKey('Access-Control-Expose-Headers')
        assert headers.containsKey('Access-Control-Max-Age')

        options('/test', HttpStatus.OK)
    }

}
```

`AbstractIntegrationTest` 基类提供了与 `AbstractSpringTest` 类似的测试 RESTful 接口的方法，这意味着可以简单的修改测试类的基类，以在单元测试和集成测试之间切换。

![integration](/contents/easy-java-and-spring-test/integration.png)

集成测试基类会将服务运行在一个随机端口上，测试用例中可通过基类中的 `port` 属性获取服务运行的端口号。


测试条件 Bean
============

当项目中存在条件 Bean 时，例如使用 `@ConditionalOnProperty` 注解来指定当某个属性为某个值时，该 Bean 才会被加载，在测试用例中可通过 `@TestPropertySource` 注解或直接使用 `@SpringBootTest` 注解来指定测试条件的属性值，例如：

```groovy
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.DEFINED_PORT,
    properties = [
        'sms.templateId=123456',
        'sms.url=http://localhost:8080',
])
@TestPropertySource(properties = ['sms.type = phone'])
class SmsSendServiceImplTest extends AbstractIntegrationTest {

    @Autowired
    SmsSendService service

    @Test
    void test() {
        assert service.sendSms([
            Sms.builder().smsPhone('123456').smsContent('content1').build(),
            Sms.builder().smsPhone('123456').smsContent('content2').build()
        ]) == 2
    }

}
```

假设上例中，`SmsSendService` 有多种实现类，根据不同的 `sms.type` 进行注册：

```java
@ConditionalOnProperty(value = "sms.type", havingValue = "phone")
public class SmsSendServicePhoneImpl implements SmsSendService {
    // ...
}
```

`@TestPropertySource(properties = ['sms.type = phone'])` 相当于在配置文件中设置了 `sms.type=phone`，这样 `SmsSendServicePhoneImpl` 就会被注入到 `service` 属性中。


测试依赖三方服务的类
=================

本地 Controller 替代三方 HTTP 服务
-------------------------------

上例中的 `SmsSendServicePhoneImpl` 实现类会向 `sms.url` 地址所代表的短信网关发送一个 HTTP 请求，在获得 `200` 响应后，认为短信发送成功。

因为测试环境可能也没有短信网关环境，这时候可以将集成测试启动在本地的固定端口（`8080`）上，并将短信网关的地址指向集成测试服务，即上例中的：

```groovy
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.DEFINED_PORT,
    properties = [
        'sms.templateId=123456',
        'sms.url=http://localhost:8080',
])
```

这样就可以在测试用例中，编写响应替代短信网关服务接口的 RestController，来完成测试用例的内容了。

MockBean
--------

除了实现替代接口外，还可以使用 Mock 的方式，为三方服务接口模拟响应。

还是以上面的短信服务为例，假设 `SmsService` 接口的 `SmsServiceRestImpl` 实现是通过 `RestTemplate` 从一个外部接口获得短信列表，
在测试用例中，可通过 `@MockBean` 和 [Mockito](https://site.mockito.org/) 来模拟调用 `RestTemplate` 方法时的返回内容，例如：

```groovy
class SmsServiceRestImplTest extends AbstractSpringTest {

    @Autowired
    private SmsService smsService

    @MockBean
    private RestTemplate restTemplate

    @Test
    void test() {
        def vo = new PageVO()
        vo.list = [
                [smsContent: 'a'],
                [smsContent: 'b'],
                [smsContent: 'c']
        ]
        def res = new ResponseEntity<PageVO>(vo, HttpStatus.OK)
        Mockito.when(restTemplate.getForEntity(Mockito.anyString(), Mockito.any(Class.class))).thenReturn(res)

        smsService.restTemplate = restTemplate

        def result = smsService.list()
        assert result.size() == vo.list.size()
        assert result[1].getSmsContent() == vo.list[1]['smsContent']
    }

}
```


[敏捷开发之测试驱动开发从入门到放弃]:https://alphahinex.github.io/slides/topics/tdd-from-entry-to-abandon/#/