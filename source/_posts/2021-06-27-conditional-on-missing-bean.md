---
id: conditional-on-missing-bean
title: "玩转 @ConditionalOnMissingBean"
description: "学废了吗"
date: 2021.06.27 10:26
categories:
    - Spring
tags: [Spring Boot, Spring, Java]
keywords: ConditionalOnMissingBean, K8s
cover: /contents/covers/conditional-on-missing-bean.jpg
---

在 [男人，不能说不行！](https://alphahinex.github.io/2021/06/20/to-father/) 中，留了两个问题：

1. 为什么名为 `testServiceImpl` 的 Bean 会被注册？
1. 为什么无法注入 TestService 的实例？

先从可运行环境 https://github.com/AlphaHinex/conditional-on-missing-bean-demo 看下结果。

在测试用例中，通过 `@Autowired` 注解注入了 TestService，但调用时，报了空指针异常，说明容器中没有 TestService 类型的实例。

那么是 `@ConditionalOnMissingBean` 不行吗？

看下 bean 的定义：
```java
@Service
@ConditionalOnMissingBean(TestService.class)
public class TestServiceImpl implements TestService
```

## debug

打开 `org.springframework` 的 `debug` 级别日志，可以看到：

```text
   TestServiceImpl:
      Did not match:
         - @ConditionalOnMissingBean (types: com.example.demo.service.TestService; SearchStrategy: all) found beans of type 'com.example.demo.service.TestService' testServiceImpl (OnBeanCondition)
```

`@ConditionalOnMissingBean` 没有生效的原因，是因为其条件没有满足，即 `found beans of type 'com.example.demo.service.TestService' testServiceImpl`。

这就矛盾了啊：

1. 因为找到了 TestService 类型的 bean，所以没有注册 TestServiceImpl 这个 bean，但找到的那个 bean 的名称，是 testServiceImpl ，也就是 —— TestServiceImpl 自己！
1. 既然 `@ConditionalOnMissingBean` 没有生效，说明有这个 bean，但注入的时候还注入了个 null！

## 一探究竟

先来看下 [ConditionalOnMissingBean](https://github.com/spring-projects/spring-boot/blob/v2.5.1/spring-boot-project/spring-boot-autoconfigure/src/main/java/org/springframework/boot/autoconfigure/condition/ConditionalOnMissingBean.java#L53-L56) 中的注释文字：

> The condition can only match the bean definitions that have been processed by the application context so far and, as such, it is strongly recommended to use this condition on auto-configuration classes only. If a candidate bean may be created by another auto-configuration, make sure that the one using this condition runs after.

可以得出几个要点：

1. 强烈建议仅在自动配置类上使用此注解
1. 这个条件仅能匹配已经被当前的应用上下文处理过的 bean 定义
1. 如果候选 bean 是被其他配置类创建的，需确保这个条件在其后运行

所以一般我们很少见到本例中这样直接在 `@Service` 类上使用 `@ConditionalOnMissingBean` 的情况，大多数都是如源码中建议所示：

```java
@Configuration
public class MyAutoConfiguration {

    @ConditionalOnMissingBean
    @Bean
    public MyService myService() {
        ...
    }

}
```

虽说不建议，但也不是不行。从日志中也可以看出，这个条件确实被运行了，只不过并未满足条件。

继续往下看，条件进行计算时，会从当时已经处理过的 bean 定义中进行匹配，也就是说，TestServiceImpl 这个 bean 在进行条件判断时已经注册到 Spring 容器中了。

在 Spring 中，Bean 被抽象为 [BeanDefinition](https://github.com/spring-projects/spring-framework/blob/v5.3.8/spring-beans/src/main/java/org/springframework/beans/factory/config/BeanDefinition.java)，注册到 [BeanDefinitionRegistry](https://github.com/spring-projects/spring-framework/blob/v5.3.8/spring-beans/src/main/java/org/springframework/beans/factory/support/BeanDefinitionRegistry.java) 中。

注册时，通过 BeanDefinitionRegistry 中的 `registerBeanDefinition` 方法，将 bean 以 beanName 为 key，beanDefinition 为 value，注册到 BeanDefinitionRegistry 具体实现类的一个 Map 中。

```java
void registerBeanDefinition(String beanName, BeanDefinition beanDefinition)
        throws BeanDefinitionStoreException;
```

在 [BeanDefinitionReaderUtils.java#L164](https://github.com/spring-projects/spring-framework/blob/v5.3.8/spring-beans/src/main/java/org/springframework/beans/factory/support/BeanDefinitionReaderUtils.java#L164) 打断点，可以观察到 bean 被注册的情况。

可以看到 `testServiceImpl` 这个 bean，被根据启动类获得到的 basePackages 扫描到了，进而注册到了容器中。

之后会从 ConfigurationClassParser 中获得所有用户自定义的配置类：

```java
Set<ConfigurationClass> configClasses = new LinkedHashSet<>(parser.getConfigurationClasses());
```

再由 ConfigurationClassBeanDefinitionReader 读取配置类中的 bean 定义：

```java
this.reader.loadBeanDefinitions(configClasses);
```

ConfigurationClassBeanDefinitionReader 在读取 bean 定义时，会使用 TrackedConditionEvaluator 先进行是否要跳过这个 bean 的判断，如果需要跳过，则从 registry 中将这个 bean 移除：

```java
if (trackedConditionEvaluator.shouldSkip(configClass)) {
    String beanName = configClass.getBeanName();
    if (StringUtils.hasLength(beanName) && this.registry.containsBeanDefinition(beanName)) {
        this.registry.removeBeanDefinition(beanName);
    }
    this.importRegistry.removeImportingClass(configClass.getMetadata().getClassName());
    return;
}
```

TrackedConditionEvaluator 的 shouldSkip 方法，会使用 ConditionEvaluator 进行条件计算：

```java
skip = conditionEvaluator.shouldSkip(configClass.getMetadata(), ConfigurationPhase.REGISTER_BEAN);
```

而 ConditionEvaluator 是使用 BeanDefinitionRegistry 构造的：

```java
public ConditionEvaluator(@Nullable BeanDefinitionRegistry registry,
			@Nullable Environment environment, @Nullable ResourceLoader resourceLoader)
```

所以在进行条件计算时，registry 中有 `testServiceImpl` 的定义，此时 `@ConditionalOnMissingBean(TestService.class)` 条件不满足，故 skip 为 true，`testServiceImpl` 结束了其短暂的生命周期，被从 registry 中移除掉了，这也就解释了在测试用例中，无法再 `@Autowired` 进来 `TestService` 实例的原因。

## 总结

再回顾一下 `@ConditionalOnMissingBean` 的三个要点：

### 强烈建议仅在自动配置类上使用此注解

本例中，如果是以如下方式定义这个 bean，则不会出现本例中条件失效，无法从容器中获取此 bean 的情况：

```java
@Bean
@ConditionalOnMissingBean(TestService.class)
public TestService testService() {
    return new TestService() {
        @Override
        public String helloWorld() {
            return this.getClass().getName() + " says hello world";
        }
    };
}
```

### 这个条件仅能匹配已经被当前的应用上下文处理过的 bean 定义

因为会先扫描 basePackages 中的 bean，再读取配置类中的 bean，条件的计算是在二者之间，所以上面两种定义 TestService bean 的方式，会得到两个不同的结果。

### 如果候选 bean 是被其他配置类创建的，需确保这个条件在其后运行

如果已经在 A 配置类中定义了 TestService bean，在 B 配置类中要使用 TestService 进行条件判断，则需保证 B 的配置类在 A 之后被处理，此时可以使用 `@AutoConfigureBefore` 或 `@AutoConfigureOrder` 进行配置类先后顺序的控制。