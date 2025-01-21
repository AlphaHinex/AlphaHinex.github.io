---
id: spring-test-context-caching
title: "Spring Test 模块中的上下文缓存特性"
description: ""
date: 2025.01.26 10:26
categories:
    - Book
tags: [Book]
keywords: Deep Learning, Supervised Learning, Unsupervised Learning, Reinforcement Learning, Neural Networks, Convolutional Neural Networks (CNN), Residual Networks (ResNet), Self-Attention, Generative Adversarial Networks (GAN), Variational Autoencoders (VAE)
cover: /contents/covers/spring-test-context-caching.png
---

// TODO 👆

# 上下文缓存概述

[Context Caching][cc] 是 [Spring Framework](https://spring.io/projects/spring-framework) 中的 [Spring TestContext Framework](https://docs.spring.io/spring-framework/reference/testing/testcontext-framework.html) 所提供的 [Context Management](https://docs.spring.io/spring-framework/reference/testing/testcontext-framework/ctx-management.html) 上下文管理能力对测试所需使用的应用上下文的缓存支持，以减少初始化相同的应用上下文导致的时间浪费。


# 初始化多个 context 对构建时间的影响

当执行测试用例时，若未能完全复用缓存中的 context，将会无谓的拖慢测试阶段的耗时，进而影响快速反馈的效果。

那么初始化多个 context 会对构建时间产生多大的影响呢？

这个问题会因环境而异：不同的初始化次数、容器中初始化的不同的 bean，都会产生不同的结果。

举两个例子直观感受一下：

|模块|多个上下文|一个上下文|
|:---|-------:|-------:|
| A | 40+s | 10+s |
| B | 60+s | 13+s |

> 模块 A 在测试阶段会在缓存中创建两个 context，构建模块 A 耗时大约为 40+s，在将测试用例所使用的 context 调整为一个后，构建模块 A 耗时大约为 10+s。

> Spring Boot 应用可以通过观察日志中打印的 banner 次数统计初始化上下文的次数。


# 初始化多个 context 的原因

> Once the TestContext framework loads an `ApplicationContext` (or `WebApplicationContext`) for a test, that context is cached and reused for all subsequent tests that declare the same unique context configuration within the same test suite.
>
> —— [Context Caching][cc]

首次初始化的上下文在缓存之后，会在相同测试套件（test suite）的相同且唯一（unique）的上下文配置中复用。任一条件未满足时，则会引起新上下文的初始化，并放入缓存中备用。

缓存的上下文数量超过上限导致早期缓存的上下文被驱逐后，也可能导致新的上下文初始化过程。

## 缓存大小及清理策略

在 [spring-framework](https://github.com/spring-projects/spring-framework) 的 `spring-test` 模块中有一个 [ContextCache](https://github.com/spring-projects/spring-framework/blob/main/spring-test/src/main/java/org/springframework/test/context/cache/ContextCache.java) 接口， 并提供了 [DefaultContextCache](https://github.com/spring-projects/spring-framework/blob/main/spring-test/src/main/java/org/springframework/test/context/cache/DefaultContextCache.java) 默认实现。其中的私有属性 `contextMap` 即测试所使用的上下文的缓存：

```java
private final Map<MergedContextConfiguration, ApplicationContext> contextMap =
            Collections.synchronizedMap(new LruCache(32, 0.75f));
```

缓存 Map 初始化及默认的大小是 `32`（[DEFAULT_MAX_CONTEXT_CACHE_SIZE](https://github.com/spring-projects/spring-framework/blob/001ccca5e6a3eee2b3e71bf57421762915da2d9e/spring-test/src/main/java/org/springframework/test/context/cache/ContextCache.java#L67C6-L67C36)），可通过 [spring.test.context.cache.maxSize](https://github.com/spring-projects/spring-framework/blob/001ccca5e6a3eee2b3e71bf57421762915da2d9e/spring-test/src/main/java/org/springframework/test/context/cache/ContextCache.java#L80C49-L80C82) 参数调整缓存的最大数量。

缓存采用 LRU（least recently used，最近最少使用）策略清理，缓存命中相关统计信息可以通过将 `org.springframework.test.context.cache` 包的日志级别设置为 `DEBUG` 在日志中查看。

缓存 Map 所使用的 key，即为上下文缓存的唯一标识。

## 缓存唯一标识

[CacheAwareContextLoaderDelegate](https://github.com/spring-projects/spring-framework/blob/main/spring-test/src/main/java/org/springframework/test/context/CacheAwareContextLoaderDelegate.java) 负责通过 `ContextCache` 加载或清除缓存的上下文。其默认实现 [DefaultCacheAwareContextLoaderDelegate](https://github.com/spring-projects/spring-framework/blob/main/spring-test/src/main/java/org/springframework/test/context/cache/DefaultCacheAwareContextLoaderDelegate.java) 在 `loadContext` 方法中操作 `ContextCache` 提供的类似 `Map` 的 `get` 和 `put` 方法，控制缓存的读取和放入。

`ContextCache` 使用 [MergedContextConfiguration](https://github.com/spring-projects/spring-framework/blob/main/spring-test/src/main/java/org/springframework/test/context/MergedContextConfiguration.java) 作为缓存的唯一标识，用来判断是否可以复用已缓存的上下文。

`MergedContextConfiguration` 覆盖了基类的 [equals](https://github.com/spring-projects/spring-framework/blob/001ccca5e6a3eee2b3e71bf57421762915da2d9e/spring-test/src/main/java/org/springframework/test/context/MergedContextConfiguration.java#L486-L531) 和 [hashCode](https://github.com/spring-projects/spring-framework/blob/001ccca5e6a3eee2b3e71bf57421762915da2d9e/spring-test/src/main/java/org/springframework/test/context/MergedContextConfiguration.java#L539-L550) 方法，如下内容都一致的两个 `MergedContextConfiguration` 被认为是相等的：

> - `locations` (from `@ContextConfiguration`)
> - `classes` (from `@ContextConfiguration`)
> - `contextInitializerClasses` (from `@ContextConfiguration`)
> - `contextCustomizers` (from `ContextCustomizerFactory`) – this includes `@DynamicPropertySource` methods as well as various features from Spring Boot’s testing support such as `@MockBean` and `@SpyBean`.
> - `contextLoader` (from `@ContextConfiguration`)
> - `parent` (from `@ContextHierarchy`)
> - `activeProfiles` (from `@ActiveProfiles`)
> - `propertySourceDescriptors` (from `@TestPropertySource`)
> - `propertySourceProperties` (from `@TestPropertySource`)
> - `resourceBasePath` (from `@WebAppConfiguration`)
> 
> —— [Context Caching][cc]

> `resourceBasePath` 是在 [WebMergedContextConfiguration](https://github.com/spring-projects/spring-framework/blob/main/spring-test/src/main/java/org/springframework/test/context/web/WebMergedContextConfiguration.java) 中比较的。

`DefaultCacheAwareContextLoaderDelegate` 加载新的 context 后，会在 DEBUG 级别打印日志：`Storing ApplicationContext in cache under key ...`，并将新的 context 追加至 contextCache。


## 测试套件

`DefaultCacheAwareContextLoaderDelegate` 使用静态变量初始化上下文缓存：

```java
    /**
     * Default static cache of Spring application contexts.
     */
    static final ContextCache defaultContextCache = new DefaultContextCache();
```

所以运行在不同进程中的测试，无法共享上下文缓存。故，测试套件（test suite），在这里指的是运行在相同 JVM 中的所有测试用例集合。


# 如何避免初始化多个 context

关键就是保证缓存的 key 是相同的，即测试用例所使用的 `MergedContextConfiguration` 是一致的。

[Context not being reused in tests when MockBeans are used](https://github.com/spring-projects/spring-boot/issues/7174) 中给出了一个解决由在不同的测试用例中使用 `@MockBean` 导致的 context 未被复用的例子，思路是创建一个抽象基类，将所有需要使用 `@MockBean` 的定义在基类中统一定义，供所有测试用例使用，以达到 `contextCustomizers` 及其他 `MergedContextConfiguration` 中属性完全一致的效果：

> ```java
> @RunWith(SpringRunner.class)
> @WebMvcTest
> public abstract class AbstractTest {
>     protected @MockBean FooBarService service;
> }
> 
> public class FooTest extends AbstractTest {...}
> ```


[cc]: https://docs.spring.io/spring-framework/reference/testing/testcontext-framework/ctx-management/caching.html