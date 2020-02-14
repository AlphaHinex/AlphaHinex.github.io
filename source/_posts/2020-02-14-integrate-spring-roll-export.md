---
id: integrate-spring-roll-export
title: "集成 Spring Roll 的通用导出列表数据为 Excel 功能"
description: "集成 roll-export 包，实现列表数据的通用导出"
date: 2020.02.14 13:43
categories:
    - Spring Roll
tags: [Java, Spring, Excel, Spring Roll]
keywords: Java, Spring, RestController, Export, Excel, Spring Roll, POI, 通用导出
cover: https://it.wisc.edu/wp-content/uploads/DoIT-C-ITWiscEdu-Excel-675x300-News-Images.png
---

[Spring Roll](https://github.com/AlphaHinex/spring-roll) 中提供了一个基于业务 REST Controller 实现的通用 Excel 导出功能，可将列表页查询结果直接导出为 Excel 文件。

本文描述如何集成 [roll-export](https://github.com/AlphaHinex/spring-roll/tree/v0.0.7.RELEASE/modules/blocks/roll-export) 模块，获得通用导出功能。


添加依赖
-------

`Spring Roll` 的包目前发布在 `GitHub Packages` 中，可参照 [GitHub Packages in Action](https://alphahinex.github.io/2020/01/17/github-packages-in-action/) 或官方文档，对构建工具进行配置。

之后可在 Maven 中添加：

```xml
<dependency>
    <groupId>io.github.spring-roll</groupId>
    <artifactId>roll-export</artifactId>
    <version>0.0.7.RELEASE</version>
</dependency>
```

或在 Gradle 中添加 `io.github.spring-roll:roll-export:0.0.7.RELEASE` 。


扫描 Spring Roll 中组件
---------------------

在相关配置类中增加 `@ComponentScan(basePackages = "io.github.springroll")`

> 若之前使用了 `@SpringBootApplication` 注解所在类作为默认包扫描路径，在添加上述配置后，需要额外再显示声明一下扫描包路径。


提供从查询接口获得导出数据的实现类
----------------------------

### 基本原理

将对业务接口的调用信息封装到请求中，调用通用导出接口。通用导出接口负责将请求转发给实际业务接口，并对业务接口返回对象进行处理，获得到要导出的数据，再将数据填入 Excel 中，并输出到 Response 里。

### 接口签名

通用导出接口为 `/export/excel/{title}`，提供 `GET` 及 `POST` 两种形式：

#### GET

```java
@GetMapping("/export/excel/{title}")
public void export(@PathVariable String title, @RequestParam String cols, @RequestParam String url, String tomcatUriEncoding, HttpServletRequest request, HttpServletResponse response) throws Exception
```

#### POST

```java
@PostMapping("/export/excel/{title}")
public void export(@PathVariable String title, @RequestBody ExportModel model, HttpServletRequest request, HttpServletResponse response) throws Exception
```

```java
public class ExportModel {

    /**
     * 列表中对 columns 的定义
     */
    private List<ColumnDef> cols;
    /**
     * 查询数据请求 url
     */
    private String url;
    /**
     * tomcat server.xml 中 Connector 设定的 URIEncoding 值，若未设置，默认为 ISO-8859-1
     */
    private String tomcatUriEncoding;
    /**
     * 业务请求的 Request Body
     */
    private Map bizReqBody;

}
```

### 参数描述

针对业务接口可能存在 GET 和 POST 两种形式，通用导出接口也提供了两种类型。GET 时将所有参数（包括通用导出接口所需参数，及业务接口所需参数两部分）放入请求参数中，POST 时将参数放入请求体中。参数说明如下：

|通用导出接口所需参数|参数描述|是否必填|
|:--|:--|:--|
|title|导出文件名|必填|
|cols|列表（前端）中对 columns 的定义，支持 EasyUI、QUI 及 ElementUI 中表格组件对属性和名称的定义|必填|
|url|具体业务的查询 url。GET 时将业务接口参数直接拼接到 url 后面，注意需进行 URL Encode；POST 时使用 bizReqBody 参数传递业务接口请求体|必填|
|tomcatUriEncoding|tomcat `server.xml` 中 Connector 设定的 URIEncoding 值，若未设置，默认为 `ISO-8859-1`|非必填|
|bizReqBody|调用 POST 接口时，使用此属性传递业务接口请求体|POST 时必填|

通用导出功能会根据 url 参数及调用导出接口所使用的 HTTP Method 去构造一个访问业务查询接口的请求，并对业务接口的返回对象使用实现了 [PaginationHandler](https://github.com/AlphaHinex/spring-roll/blob/v0.0.7.RELEASE/modules/blocks/roll-export/src/main/java/io/github/springroll/export/excel/handler/PaginationHandler.java) 接口的组件集合进行解析，获得具体业务数据之后，将其按照 cols 中的定义，输出到 Excel 中。

故在集成时，需根据业务接口的返回类型，提供获得具体业务数据的 `PaginationHandler` 接口的实现。

例如：

```java
@Component
public class WrapperResponseIQueryPaginationHandler implements PaginationHandler {

    @Override
    public Optional<Collection> getPaginationData(Object rawObject) {
        Optional<Collection> result = Optional.empty();
        if (rawObject instanceof WrapperResponse) {
            Object object = ((WrapperResponse) rawObject).getData();
            if (object instanceof IQuery) {
                result = Optional.ofNullable(((IQuery)object).getResult());
            }
        }
        return result;
    }

}
```

`cols` 参数结构目前（v0.0.7.RELEASE）支持 EasyUI、QUI 及 ElementUI 三种前端类库中表格组件对属性和名称的定义：

|框架|`属性`字段|`名称`字段|
|:--|:--|:--|
|EasyUI|field|title|
|QUI|name|display|
|ElementUI|prop|label|


验证
---

集成之后可访问通用导出接口进行验证，如：

[GET 请求示例 URL](http://localhost:8080/demo/export/excel/%E5%AF%BC%E5%87%BA?cols=%5B%7B%22name%22%3A%22clctId%22%2C%22display%22%3A%22%E9%87%87%E9%9B%86%E5%AE%9E%E4%BE%8BID%22%7D%2C%7B%22name%22%3A%22clctSttId%22%2C%22display%22%3A%22%E7%BB%9F%E8%AE%A1%E4%BB%BB%E5%8A%A1ID%22%7D%2C%7B%22name%22%3A%22bizTotlCnt%22%2C%22display%22%3A%22%E4%B8%9A%E5%8A%A1%E6%80%BB%E9%87%8F%22%7D%5D&url=%2Fbiz%2Fquery%2Fpage%3FpageSize%3D9999%26pageNumber%3D1)。

或 POST 请求 curl

```bash
curl 'http://localhost:8080/export/excel/test' -H 'Content-Type: application/json;charset=UTF-8' --data-binary '{"bizReqBody":{"userName":"","age":""},"cols":[{"name":"userName","display":"员工姓名"},{"name":"userId","display":"员工编号"}],"title":"员工信息","url":"http://localhost:8080/user/queryUserListByPage"}'
```
