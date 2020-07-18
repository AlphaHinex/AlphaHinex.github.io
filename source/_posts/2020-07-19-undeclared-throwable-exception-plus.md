---
id: undeclared-throwable-exception-plus
title: "谁动了我的异常 Plus"
description: "《谁动了我的异常？》中的未解之谜"
date: 2020.07.19 19:34
categories:
    - Spring
tags: [Java, Spring]
keywords: Java, Spring, AOP, Proxy, CGLIB, JDK Dynamic Proxy, UndeclaredThrowableException, Checked Exception, Unchecked Exception
cover: /contents/covers/cglib.png
---

书接上文，在 [谁动了我的异常？](https://alphahinex.github.io/2020/06/26/undeclared-throwable-exception/) 中，有几个问题没说清楚，本文将继续进行说明。
为了方便，相关示例代码上传至了 https://github.com/AlphaHinex/proxy-in-spring 。

## 前情回顾

示例代码中，定义了如下内容：

* 一个检查型异常：[CheckedException](https://github.com/AlphaHinex/proxy-in-spring/blob/master/src/main/java/io/github/alphahinex/proxyinspring/CheckedException.java)
* 一个统一的异常处理：[UnifyHandlerExceptionResolver](https://github.com/AlphaHinex/proxy-in-spring/blob/master/src/main/java/io/github/alphahinex/proxyinspring/UnifyHandlerExceptionResolver.java)
* 一个切面 [ControllerAspect](https://github.com/AlphaHinex/proxy-in-spring/blob/master/src/main/java/io/github/alphahinex/proxyinspring/ControllerAspect.java)，在切面中固定抛出检查型异常

在 [ClassController](https://github.com/AlphaHinex/proxy-in-spring/blob/master/src/main/java/io/github/alphahinex/proxyinspring/ClassController.java) 中定义了一个没有声明异常的方法 `post`。

在 [ProxyTest](https://github.com/AlphaHinex/proxy-in-spring/blob/master/src/test/groovy/io/github/alphahinex/proxyinspring/ProxyTest.groovy#L16) 中调用此方法时，会得到一个 [UndeclaredThrowableException](https://github.com/AlphaHinex/proxy-in-spring/blob/master/src/test/groovy/io/github/alphahinex/proxyinspring/ProxyTest.groovy#L16)。


## Puzzle 1

那么在上述情况下，如果在 post 方法上声明了抛出检查型异常时，会怎么样？

```java
@PostMapping("/throws")
public ResponseEntity<String> postWithThrows() throws CheckedException {
    return new ResponseEntity<>("success from class controller with throws", HttpStatus.CREATED);
}
```

此时在 `ProxyTest` 中进行调用时，可以看到正常捕获到了 [CheckedException](https://github.com/AlphaHinex/proxy-in-spring/blob/master/src/test/groovy/io/github/alphahinex/proxyinspring/ProxyTest.groovy#L22)。

这是为什么呢？

在 DefaultGeneratorStrategy.java#L26 处加断点，可以获得到此时的字节码，使用 IDEA 反编译之后，可得到如下内容：

```java
public final ResponseEntity postWithThrows() throws CheckedException {
    try {
        MethodInterceptor var10000 = this.CGLIB$CALLBACK_0;
        if (var10000 == null) {
            CGLIB$BIND_CALLBACKS(this);
            var10000 = this.CGLIB$CALLBACK_0;
        }

        return var10000 != null ? (ResponseEntity)var10000.intercept(this, CGLIB$postWithThrows$1$Method, CGLIB$emptyArgs, CGLIB$postWithThrows$1$Proxy) : super.postWithThrows();
    } catch (Error | CheckedException | RuntimeException var1) {
        throw var1;
    } catch (Throwable var2) {
        throw new UndeclaredThrowableException(var2);
    }
}
```

可以看到，声明了的异常，在被捕获之后又被抛了出去。其余的 Throwable，会被封装到 UndeclaredThrowableException 中再被抛出。


## Puzzle 2

相同情况下，如果代理类是通过 JDK 动态代理创建的，又会是怎么样的呢？

首先，如果希望使用 JDK 动态代理，需要使被代理类实现接口，如 [InterfaceOfController](https://github.com/AlphaHinex/proxy-in-spring/blob/master/src/main/java/io/github/alphahinex/proxyinspring/InterfaceOfController.java) 和 [InterfaceController](https://github.com/AlphaHinex/proxy-in-spring/blob/master/src/main/java/io/github/alphahinex/proxyinspring/InterfaceController.java)。

```java
@RestController
@RequestMapping("/interface")
public class InterfaceController implements InterfaceOfController {

    @Override
    @PostMapping
    public ResponseEntity post() {
        return new ResponseEntity<>("success from interface controller", HttpStatus.CREATED);
    }

    @Override
    @PostMapping("/throws")
    public ResponseEntity<String> postWithThrows() throws CheckedException {
        return new ResponseEntity<>("success from interface controller with throws", HttpStatus.CREATED);
    }

}
```

> 注意：此时需要将 spring web 的注解（@RequestMapping 等）同时写在接口及实现上，否则会找不到对应的接口。

然后在 Spring Boot 应用下，要注意指定 [如下参数](https://github.com/AlphaHinex/proxy-in-spring/blob/master/src/test/resources/application.properties#L1)，否则会强制使用 Cglib：

```properties
spring.aop.proxy-target-class=false
```

可参照 [这里](https://github.com/AlphaHinex/proxy-in-spring/blob/master/src/test/groovy/io/github/alphahinex/proxyinspring/ProxyTest.groovy#L39) 基于接口创建 JDK 动态代理，并输出字节码，观察代理类中相应方法情况。其中关键部分如下：

```java
public final ResponseEntity post() throws  {
    try {
        return (ResponseEntity)super.h.invoke(this, m3, (Object[])null);
    } catch (RuntimeException | Error var2) {
        throw var2;
    } catch (Throwable var3) {
        throw new UndeclaredThrowableException(var3);
    }
}
```

```java
public final ResponseEntity postWithThrows() throws CheckedException {
    try {
        return (ResponseEntity)super.h.invoke(this, m4, (Object[])null);
    } catch (RuntimeException | CheckedException | Error var2) {
        throw var2;
    } catch (Throwable var3) {
        throw new UndeclaredThrowableException(var3);
    }
}
```

可以看到情况与使用 Cglib 时基本一致：

* 未声明异常时，除 `RuntimeException` 和 `Error` 外，其余 `Throwable` 都被封装进了 `UndeclaredThrowableException` 再抛出；
* 当声明异常时，声明了的异常也会被直接抛出，不进行封装。
