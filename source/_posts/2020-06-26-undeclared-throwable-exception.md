---
id: undeclared-throwable-exception
title: "谁动了我的异常？"
description: "明明抛出的是一个检查型异常，为什么捕获到的异常被包装成了 UndeclaredThrowableException？"
date: 2020.06.26 19:26
categories:
    - Spring
tags: [Java, Spring]
keywords: Java, Spring, AOP, Proxy, CGLIB, UndeclaredThrowableException, Checked Exception, Unchecked Exception
cover: /contents/covers/undeclared-throwable-exception.jpg
---


## 场景描述

通常来讲，为方便开发，我们会对异常进行统一的处理。会定义一个异常基类，针对基于这个基类的自定义异常进行统一处理。

当异常基类为检查型异常（Checked Exception）时，如果自定义异常是通过切面等代理抛出的，被代理的方法本身并未抛出且也未声明此异常时，就会遇到这个问题：

统一异常处理方法中，捕获到的异常，已不是代理类中抛出的自定义异常，而是一个将自定义异常包装在内的 `java.lang.reflect.UndeclaredThrowableException`。

那么为什么会这样呢？


## 追根溯源

以使用 [Spring Framework v5.0.13.RELEASE](https://github.com/spring-projects/spring-framework/tree/v5.0.13.RELEASE) 及切面场景为例。

Spring 文档中关于 [AOP 代理](https://docs.spring.io/spring/docs/5.0.13.RELEASE/spring-framework-reference/core.html#aop-introduction-proxies) 的描述如下：

```doc
5.1.3. AOP Proxies
Spring AOP defaults to using standard JDK dynamic proxies for AOP proxies. This enables any interface (or set of interfaces) to be proxied.

Spring AOP can also use CGLIB proxies. This is necessary to proxy classes rather than interfaces. CGLIB is used by default if a business object does not implement an interface. As it is good practice to program to interfaces rather than classes; business classes normally will implement one or more business interfaces. It is possible to force the use of CGLIB, in those (hopefully rare) cases where you need to advise a method that is not declared on an interface, or where you need to pass a proxied object to a method as a concrete type.

It is important to grasp the fact that Spring AOP is proxy-based. See Understanding AOP proxies for a thorough examination of exactly what this implementation detail actually means.
```

几个重点：

1. Spring AOP 是基于代理来实现的。
1. Spring AOP 默认使用 JDK 动态代理来为切面创建代理。这使得所有接口的实现类都可以被代理。
1. Spring AOP 也可以使用 CGLIB 创建代理。当一个类未实现任何接口时，会默认使用 CGLIB 的方式创建代理。也可以强制使用 CGLIB 进行代理。

在 [DefaultAopProxyFactory](https://github.com/spring-projects/spring-framework/blob/v5.0.13.RELEASE/spring-aop/src/main/java/org/springframework/aop/framework/DefaultAopProxyFactory.java) 中可以看到对应的逻辑：

```javadoc
* <p>Creates a CGLIB proxy if one the following is true for a given
* {@link AdvisedSupport} instance:
* <ul>
* <li>the {@code optimize} flag is set
* <li>the {@code proxyTargetClass} flag is set
* <li>no proxy interfaces have been specified
* </ul>
*
* <p>In general, specify {@code proxyTargetClass} to enforce a CGLIB proxy,
* or specify one or more interfaces to use a JDK dynamic proxy.
```

```java
@Override
public AopProxy createAopProxy(AdvisedSupport config) throws AopConfigException {
  if (config.isOptimize() || config.isProxyTargetClass() || hasNoUserSuppliedProxyInterfaces(config)) {
    Class<?> targetClass = config.getTargetClass();
    if (targetClass == null) {
      throw new AopConfigException("TargetSource cannot determine target class: " +
          "Either an interface or a target is required for proxy creation.");
    }
    if (targetClass.isInterface() || Proxy.isProxyClass(targetClass)) {
      return new JdkDynamicAopProxy(config);
    }
    return new ObjenesisCglibAopProxy(config);
  }
  else {
    return new JdkDynamicAopProxy(config);
  }
}
```

使用 `ObjenesisCglibAopProxy` 创建代理时，会调用 [org.springframework.aop.framework.CglibAopProxy#getProxy(java.lang.ClassLoader)](https://github.com/spring-projects/spring-framework/blob/v5.0.13.RELEASE/spring-aop/src/main/java/org/springframework/aop/framework/CglibAopProxy.java#L159) 方法，其中 [192](https://github.com/spring-projects/spring-framework/blob/v5.0.13.RELEASE/spring-aop/src/main/java/org/springframework/aop/framework/CglibAopProxy.java#L192) 行配置了一个 [ClassLoaderAwareUndeclaredThrowableStrategy](https://github.com/spring-projects/spring-framework/blob/v5.0.13.RELEASE/spring-aop/src/main/java/org/springframework/aop/framework/CglibAopProxy.java#L973) 策略。

```java
enhancer.setStrategy(new ClassLoaderAwareUndeclaredThrowableStrategy(classLoader));
```

在 `ClassLoaderAwareUndeclaredThrowableStrategy` 策略的 [generate](https://github.com/spring-projects/spring-framework/blob/v5.0.13.RELEASE/spring-aop/src/main/java/org/springframework/aop/framework/CglibAopProxy.java#L984) 方法调用父类 UndeclaredThrowableStrategy => DefaultGeneratorStrategy 的 generate 方法时，可以获得到增强后的字节码。


### Fork

说到这时会发现一个问题，在 Spring Framework 的代码仓库中，没有上面提到的 `UndeclaredThrowableStrategy` 和 `DefaultGeneratorStrategy` 的源码，而这两个类明明是包含在 `spring-core` 的 jar 包中的。

spring-core 模块的构建文件 [spring-core.gradle](https://github.com/spring-projects/spring-framework/blob/v5.0.13.RELEASE/spring-core/spring-core.gradle) 给我们揭晓了答案：

```spring-core.gradle
...

// spring-core includes asm and repackages cglib, inlining both into the spring-core jar.
// cglib itself depends on asm and is therefore further transformed by the JarJar task to
// depend on org.springframework.asm; this avoids including two different copies of asm.
def cglibVersion = "3.2.6"

...

task cglibRepackJar(type: Jar) { repackJar ->
	repackJar.baseName = "spring-cglib-repack"
	repackJar.version = cglibVersion

	doLast() {
		project.ant {
			taskdef name: "jarjar", classname: "com.tonicsystems.jarjar.JarJarTask",
					classpath: configurations.jarjar.asPath
			jarjar(destfile: repackJar.archivePath) {
				configurations.cglib.each { originalJar ->
					zipfileset(src: originalJar)
				}
				// Repackage net.sf.cglib => org.springframework.cglib
				rule(pattern: "net.sf.cglib.**", result: "org.springframework.cglib.@1")
				// As mentioned above, transform cglib's internal asm dependencies from
				// org.objectweb.asm => org.springframework.asm. Doing this counts on the
				// the fact that Spring and cglib depend on the same version of asm!
				rule(pattern: "org.objectweb.asm.**", result: "org.springframework.asm.@1")
			}
		}
	}
}

...
```

所以在 [cglib v3.2.6](https://github.com/cglib/cglib/tree/RELEASE_3_2_6) 的仓库中，我们可以找到 [UndeclaredThrowableStrategy](https://github.com/cglib/cglib/blob/RELEASE_3_2_6/cglib/src/main/java/net/sf/cglib/transform/impl/UndeclaredThrowableStrategy.java) 和 [DefaultGeneratorStrategy](https://github.com/cglib/cglib/blob/RELEASE_3_2_6/cglib/src/main/java/net/sf/cglib/core/DefaultGeneratorStrategy.java)，以及 [可获取增强后字节码的地方](https://github.com/cglib/cglib/blob/RELEASE_3_2_6/cglib/src/main/java/net/sf/cglib/core/DefaultGeneratorStrategy.java#L23-L27)：

```java
public byte[] generate(ClassGenerator cg) throws Exception {
    DebuggingClassWriter cw = getClassVisitor();
    transform(cg).generateClass(cw);
    return transform(cw.toByteArray());
}
```

> 断点加在 `cw.toByteArray()` 处，将其输出为 `.class` 文件，即可获得增强后的字节码，也就是 AOP 的代理类。

### Join

回到主线。反编译输出出来的 `.class` 文件，可与源码进行对比。

源码：

```java
@PostMapping
public ResponseEntity post() {
    return responseOfPost("success");
}
```

反编译代理类：

```java
public final ResponseEntity post() {
    try {
        MethodInterceptor cglib$CALLBACK_2;
        MethodInterceptor cglib$CALLBACK_0;
        if ((cglib$CALLBACK_0 = (cglib$CALLBACK_2 = this.CGLIB$CALLBACK_0)) == null) {
            CGLIB$BIND_CALLBACKS(this);
            cglib$CALLBACK_2 = (cglib$CALLBACK_0 = this.CGLIB$CALLBACK_0);
        }
        if (cglib$CALLBACK_0 != null) {
            return (ResponseEntity)cglib$CALLBACK_2.intercept((Object)this, TestController$$EnhancerBySpringCGLIB$$ef60194e.CGLIB$post$5$Method, TestController$$EnhancerBySpringCGLIB$$ef60194e.CGLIB$emptyArgs, TestController$$EnhancerBySpringCGLIB$$ef60194e.CGLIB$post$5$Proxy);
        }
        return super.post();
    }
    catch (RuntimeException | Error ex) {
        throw;
    }
    catch (Throwable t) {
        throw new UndeclaredThrowableException(t);
    }
}
```

> 顺便吐个槽：老牌反编译软件 [jd-gui](https://github.com/java-decompiler/jd-gui) 反编译上面这段时，内容明显不对。[Luyten](https://github.com/deathmarine/Luyten) 反编译出了上述结果，但 [Luyten v0.5.4 Rebuilt](https://github.com/deathmarine/Luyten/releases/tag/v0.5.4_Rebuilt_with_Latest_depenencies) 里的 [Mac 版](https://github.com/deathmarine/Luyten/releases/download/v0.5.4_Rebuilt_with_Latest_depenencies/luyten-OSX-0.5.4.zip) 无任何响应。上述结果为在 Windows 下编译得到。

总结一下，扣个题：

代理类将被代理调用的方法整个使用 try/catch 包了起来，将除 RuntimeException 和 Error 之外的异常，都包装成了 `UndeclaredThrowableException` 再向外抛出。


## 对症下药

所以遇到这个问题的时候，可以通过如下方式处理：

1. 在被代理的方法上，显示抛出检查型异常
1. 切面里抛出 RuntimeException，替代检查型异常
1. 不能更改异常类型又不想在方法上定义方法本身未进行抛出的异常时，可以使用一些迂回策略，比如在切面中直接按照统一异常处理的规则，返回将异常处理好的封装类型


参考资料
-------

* [java.lang.reflect.UndeclaredThrowableException的解决](https://www.jianshu.com/p/7edab536e4b9)
* [JDK动态代理UndeclaredThrowableException异常](https://msd.misuland.com/pd/3255817997595446638)
* [java.lang.reflect.Proxy](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/Proxy.html)
* [java.lang.reflect.InvocationHandler](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/InvocationHandler.html)
* [java.lang.reflect.UndeclaredThrowableException](https://docs.oracle.com/javase/8/docs/api/java/lang/reflect/UndeclaredThrowableException.html)
* [AOP Proxies](https://docs.spring.io/spring/docs/5.0.13.RELEASE/spring-framework-reference/core.html#aop-introduction-proxies)
