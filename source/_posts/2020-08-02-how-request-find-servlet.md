---
id: how-request-find-servlet
title: "Tomcat 是怎么找到用来处理请求的 Servlet 的？"
description: "很多事来不及思考，就这样自然发生了"
date: 2020.08.02 10:34
categories:
    - Tomcat
tags: [Java, Tomcat, Servlet]
keywords: Java, Tomcat, Servlet, Mapper, MapperListener, Service, Engine, Host, Context, Wrapper, ContextVersion
cover: /contents/how-request-find-servlet/cover.jpg
---

在 [Servlet 注册到了哪？](https://alphahinex.github.io/2020/04/30/where-are-servlets/) 中，我们找到了配置的 Servlet 被包装成了一个 `StandardWrapper`，以注册的 Servlet name 为 key 放入了其父容器（Context）一个 HashMap 里。那么当 Tomcat 收到一个请求的时候，是怎么找到对应的 Servlet 以对请求进行处理的呢？

先放一张图：

![Tomcat Server](/contents/how-request-find-servlet/tomcat-server.png)

总的来说，这个过程分为两部分：

1. 读取所有 Servlet 的配置，放入 Mapper 中；
2. 将请求匹配到具体的 Servlet 上。

> 注：本文以 [Tomcat v9.0.35](https://github.com/apache/tomcat/tree/9.0.35) 版本源码为例进行说明。


## 读取所有 Servlet 的配置，放入 Mapper 中

在 Tomcat [Server](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/Server.java) 启动时，会将其所包含的所有 [Service](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/Service.java) 也一同启动。

[StandardServer.java#L927-L932](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/core/StandardServer.java#L927-L932)：
```java
// Start our defined Services
synchronized (servicesLock) {
    for (Service service : services) {
        service.start();
    }
}
```

每个 Service [对应一个 Mapper](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/Service.java#L151)，[Mapper](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/mapper/Mapper.java) 是本文的主角，包含了 Servlet 的映射信息。在 Service 启动时，会同时启动一个 mapperListener。

[StandardService.java#L431](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/core/StandardService.java#L431)：
```java
mapperListener.start();
```

[MapperListener](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/mapper/MapperListener.java) 可以 [通过 Service 来构造](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/core/StandardService.java#L105)，里面包含了这个 Service 以及 Service 中的 Mapper。

MapperListener 在 start 时，会获取 Service 对应的 Engine，并将 Engine 中的所有 Host 进行注册。

[MapperListener.java#L94-L116](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/mapper/MapperListener.java#L94-L116)：
```java
@Override
public void startInternal() throws LifecycleException {

    setState(LifecycleState.STARTING);

    Engine engine = service.getContainer();
    if (engine == null) {
        return;
    }

    findDefaultHost();

    addListeners(engine);

    Container[] conHosts = engine.findChildren();
    for (Container conHost : conHosts) {
        Host host = (Host) conHost;
        if (!LifecycleState.NEW.equals(host.getState())) {
            // Registering the host will register the context and wrappers
            registerHost(host);
        }
    }
}
```

registerHost 中会注册其中的 Context。

[MapperListener.java#L305-L309](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/mapper/MapperListener.java#L305-L309)：
```java
for (Container container : host.findChildren()) {
    if (container.getState().isAvailable()) {
        registerContext((Context) container);
    }
}
```

registerContext 时，将 Context 中的 [Wrapper](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/Wrapper.java)（包含一个 Servlet） 包装成 [WrapperMappingInfo](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/mapper/WrapperMappingInfo.java)，

[MapperListener.java#L381-L390](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/mapper/MapperListener.java#L381-L390)：
```java
List<WrapperMappingInfo> wrappers = new ArrayList<>();

for (Container container : context.findChildren()) {
    prepareWrapperMappingInfo(context, (Wrapper) container, wrappers);

    if(log.isDebugEnabled()) {
        log.debug(sm.getString("mapperListener.registerWrapper",
                container.getName(), contextPath, service));
    }
}
```

并进行了如下操作。

[MapperListener.java#L392-L394](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/mapper/MapperListener.java#L392-L394)：
```java
mapper.addContextVersion(host.getName(), host, contextPath,
        context.getWebappVersion(), context, welcomeFiles, resources,
        wrappers);
```

[addContextVersion](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/mapper/Mapper.java#L262) 方法根据 Context 创建了一个 ContextVersion 对象，并通过 [addWrappers](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/mapper/Mapper.java#L443) 及 [addWrapper](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/mapper/Mapper.java#L463) 方法将 WrapperMappingInfo 中的 Wrapper 及相关信息，添加进 ContextVersion 里。

[ContextVersion](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/mapper/Mapper.java#L1709) 是 Mapper 中定义的内部类，包含了如下属性：

[Mapper.java#L1714-L1717](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/mapper/Mapper.java#L1714-L1717)：
```java
public MappedWrapper defaultWrapper = null;
public MappedWrapper[] exactWrappers = new MappedWrapper[0];
public MappedWrapper[] wildcardWrappers = new MappedWrapper[0];
public MappedWrapper[] extensionWrappers = new MappedWrapper[0];
```

分别对应按 [如下方式](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/mapper/Mapper.java#L467-L514) 匹配的 Servlet：

|prop|url mapping|
|:--|:--|
|defaultWrapper|`/`|
|exactWrappers|完全匹配|
|wildcardWrappers|以 `/*` 结尾|
|extensionWrappers|以 `*.` 开头|

`addContextVersion` 方法将构造好的 ContextVersion 对象，放入 [contextObjectToContextVersionMap](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/mapper/Mapper.java#L76) 中备用。

```java
contextObjectToContextVersionMap.put(context, newContextVersion);
```

[Mapper.java#L72-L77](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/mapper/Mapper.java#L72-L77)：
```java
/**
 * Mapping from Context object to Context version to support
 * RequestDispatcher mappings.
 */
private final Map<Context, ContextVersion> contextObjectToContextVersionMap =
        new ConcurrentHashMap<>();
```

并同时将 ContextVersion 放入 Mapper 里的 [MappedHost[] hosts](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/mapper/Mapper.java#L62) 的 [ContextList contextList](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/mapper/Mapper.java#L1586) 的 [MappedContext[] contexts](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/mapper/Mapper.java#L1661) 里。

[Mapper.java#L289-L315](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/mapper/Mapper.java#L289-L315)
```java
ContextList contextList = mappedHost.contextList;
MappedContext mappedContext = exactFind(contextList.contexts, path);
if (mappedContext == null) {
    mappedContext = new MappedContext(path, newContextVersion);
    ContextList newContextList = contextList.addContext(
            mappedContext, slashCount);
    if (newContextList != null) {
        updateContextList(mappedHost, newContextList);
        contextObjectToContextVersionMap.put(context, newContextVersion);
    }
} else {
    ContextVersion[] contextVersions = mappedContext.versions;
    ContextVersion[] newContextVersions = new ContextVersion[contextVersions.length + 1];
    if (insertMap(contextVersions, newContextVersions,
            newContextVersion)) {
        mappedContext.versions = newContextVersions;
        contextObjectToContextVersionMap.put(context, newContextVersion);
    } else {
        // Re-registration after Context.reload()
        // Replace ContextVersion with the new one
        int pos = find(contextVersions, version);
        if (pos >= 0 && contextVersions[pos].name.equals(version)) {
            contextVersions[pos] = newContextVersion;
            contextObjectToContextVersionMap.put(context, newContextVersion);
        }
    }
}
```

**至此，所有根据请求匹配到具体 Servlet 的准备工作都已完成。**


## 将请求匹配到具体的 Servlet 上

先放一张官网的 [图片](http://tomcat.apache.org/tomcat-9.0-doc/architecture/requestProcess/request-process.png)

![Apache Tomcat 9 Architecture Request Process Flow](/contents/how-request-find-servlet/request-process.png)

链接虽然是在 Tomcat 9.0 的文档中，但图片中的内容有些已经过时了，比如 [Http11Protocol 在 9.0 中已经移除了](https://github.com/apache/tomcat/blob/8.5.x/java/org/apache/coyote/http11/Http11Protocol.java#L24)。

对上面流程简单分下组：

![Apache Tomcat 9 Architecture Request Process Flow with group](/contents/how-request-find-servlet/request-process-pkg.jpg)

可以看到，整个流程涉及到的类大致分布在 `tomcat`、`coyote` 和 `catalina` 三个包下。

在 tomcat 9.0.35 版本中，org.apache 包下面共有 [七个包](https://github.com/apache/tomcat/tree/9.0.35/java/org/apache)：


```text
├── catalina
├── coyote
├── el
├── jasper
├── juli
├── naming
└── tomcat
```

`org.apache.tomcat` 包下为网络、线程、连接池、WebSocket 及一些工具类。其余各包作用可见下图：

![Components](/contents/how-request-find-servlet/components.png)

CoyoteAdapter 的 [postParseRequest](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/connector/CoyoteAdapter.java#L567) 方法中，根据 connector 找到了其对应的 Service，进而找到 Service 对应的 Mapper，并进行了 map 操作。

```java
// This will map the the latest version by default
connector.getService().getMapper().map(serverName, decodedURI,
        version, request.getMappingData());
```

map 方法根据请求找到对应的 MappedHost 的 MappedConext，进而找到之前放入的 ContextVersion，详细过程可见 Mapper 中的 [internalMap](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/mapper/Mapper.java#L736) 方法。

在 `internalMap` 方法中，会调用 [internalMapWrapper](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/mapper/Mapper.java#L862) 方法进行 Wrapper 的 Mapping，会根据不同的规则，匹配 ContextVersion 中不同的 MappedWrapper，并将匹配到的 Wrapper 放入 request 的 MappingData 中。比如 [internalMapWildcardWrapper](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/mapper/Mapper.java#L1093) 里 [1134](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/mapper/Mapper.java#L1134) 行：

```java
mappingData.wrapper = wrappers[pos].object;
```

随后在 StandardContextValve 的 [invoke](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/core/StandardContextValve.java#L62) 方法中，便可通过 [request.getWrapper()](https://github.com/apache/tomcat/blob/9.0.35/java/org/apache/catalina/core/StandardContextValve.java#L76) 获取到请求对应的 Wrapper。之后的流程与上面时序图中的过程就基本一致了。


参考资料
-------

* [Tomcat请求处理流程](https://www.jianshu.com/p/17a236e1b04a)
* [Tomcat连接器：Coyote框架](https://blog.csdn.net/wangchengsi/article/details/2973012)
* [Tomcat 组件介绍](https://www.cnblogs.com/earendil/p/6834738.html)
* [Tomcat组件梳理--Catalina](https://www.cnblogs.com/cenyu/p/11072543.html)


附录
---

附两张手稿

![初始化](/contents/how-request-find-servlet/init.jpg)

![匹配](/contents/how-request-find-servlet/map.jpg)
