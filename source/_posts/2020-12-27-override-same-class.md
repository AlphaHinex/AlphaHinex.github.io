---
id: override-same-class
title: "Override same class"
description: "How to"
date: 2020.12.27 10:26
categories:
    - Servlet
tags: [Servlet, Java, Tomcat]
keywords: Servlet, Class Loader, Web Application Class Loader, Tomcat
cover: /contents/covers/tomcat-class-loader.jpg
---

实际 Java Web 项目中经常会遇到这样的场景：希望对依赖的某个三方库中的行为进行覆盖式的定制（修改三方库中的某些行为），但并不希望发布定制的版本至私服。

通常在使用 WAR 包发布应用时，可将定制的类编译成 class 文件，放入 `WEB-INF/classes` 路径中，即可覆盖放置在 `WEB-INF/lib` 路径下的三方库中同名类，达到定制的目的。

那么为什么可以这样？

在两个相同的 class 必须都存在于 JAR 包中时，又怎么实现这种需求呢？

## 为什么可以这样？

### Servlet 规范

在 [Java(TM) Servlet Specification 2.4 Final Release][servlet-2.4] 中 SRV.9.5 Directory Structure 有如下要求：

> The Web application class loader must load classes from the WEB-INF/ classes
directory first, and then from library JARs in the WEB-INF/lib directory. Also, any
requests from the client to access the resources in WEB-INF/ directory must be
returned with a SC_NOT_FOUND(404) response.

规定了 Web 应用的 Class Loader 必须先从 `WEB-INF/classes` 目录加载类文件，之后才能从 `WEB-INF/lib` 路径加载 JAR 文件。

### Web Application Class Loader

在 SRV.9.7.2 Web Application Class Loader 中有如下建议：

> It is recommended also that the application class loader be implemented so
that classes and resources packaged within the WAR are loaded in preference to
classes and resources residing in container-wide library JARs.

建议 WAR 包中的 class 优先于 JAR 包中的 class 进行加载。

### Tomcat Class Loader

[Apache Tomcat 8 Class Loader HOW-TO][class-loader-how-to] 中，描述了 Tomcat 初始化时创建的 Class Loader：

```text
    Bootstrap
        |
     System
        |
     Common
     /     \
Webapp1   Webapp2 ...
```

> Therefore, from the perspective of a web application, class or resource loading looks in the following repositories, in this order:
>
> * Bootstrap classes of your JVM
> * /WEB-INF/classes of your web application
> * /WEB-INF/lib/*.jar of your web application
> * System class loader classes (described above)
> * Common class loader classes (described above)
>
> If the web application class loader is configured with `<Loader delegate="true"/>` then the order becomes:
>
> * Bootstrap classes of your JVM
> * System class loader classes (described above)
> * Common class loader classes (described above)
> * /WEB-INF/classes of your web application
> * /WEB-INF/lib/*.jar of your web application

Servlet 规范中的要求及推荐，以及 Tomcat 的具体实现，保证了 `/WEB-INF/classes` 优先于 `WEB-INF/lib` 进行加载，那么为什么优先加载就能实现覆盖呢？

### Class Loader

这就要提到 JVM 的类加载机制了。详细内容可查阅 [The Class Loader and Class File Verifier](class-loader) 等资料，简单概括如下。

JVM 中的 Class Loader 可以分为两类：

1. 根 Class Loader，使用 C 或者其他编写 JVM 的语言编写，内置在 JVM 中，作为 JVM 的一部分，负责加载受信的类。这类 Class Loader 有且只有一个。
1. JVM 上的应用可以自由的继承 `java.lang.ClassLoader` 抽象类，构造定制的 Class Loader，负责从各种不同的源加载类。这类 Class Loader 不是 JVM 的一部分，使用 JAVA 编写。这类 Class Loader 可以没有或者有很多。

类不是在初始化阶段全部加载好的，而是在需要使用的时候才去加载的。

一个 Class Loader 在加载一个类的时候，同时负责加载这个类所依赖的其他类。每个 Class Loader 负责从指定的来源加载类，但并不能限定每个类只引用同一来源的类。

比如自定义的类 A 需要使用 `java.lang.String` 类。类 A 由自定义的 AClassLoader 负责加载，则 AClassLoader 也负责加载 String 类。在加载 String 类时，AClassLoader 可以自行进行加载，但这是没有必要的，因为根 Class Loader 知道如何加载受信包下的类。

在 java.lang.ClassLoader 抽象类中，默认的加载类（loadClass）的方式为：如果已加载的类中没有这个类，则递归调用 parent Class Loader 的 loadClass 方法进行加载，只有当所有的父加载器都无法完成此类的加载时，才在当前 Class Loader 中尝试加载。

以上即为所谓的类加载器委派模型（Class Loader Delegation Model），即每个（第二类 Class Loader）类加载器接到加载类的任务时，都先将加载任务委派给父加载器。

[ClassLoader.loadClass][load-class] openjdk 中的代码实现如下：
```JAVA
protected Class<?> loadClass(String name, boolean resolve)
    throws ClassNotFoundException
{
    synchronized (getClassLoadingLock(name)) {
        // First, check if the class has already been loaded
        Class<?> c = findLoadedClass(name);
        if (c == null) {
            long t0 = System.nanoTime();
            try {
                if (parent != null) {
                    c = parent.loadClass(name, false);
                } else {
                    c = findBootstrapClassOrNull(name);
                }
            } catch (ClassNotFoundException e) {
                // ClassNotFoundException thrown if class not found
                // from the non-null parent class loader
            }

            if (c == null) {
                // If still not found, then invoke findClass in order
                // to find the class.
                long t1 = System.nanoTime();
                c = findClass(name);

                // this is the defining class loader; record the stats
                PerfCounter.getParentDelegationTime().addTime(t1 - t0);
                PerfCounter.getFindClassTime().addElapsedTimeFrom(t1);
                PerfCounter.getFindClasses().increment();
            }
        }
        if (resolve) {
            resolveClass(c);
        }
        return c;
    }
}
```

规范要求类加载器先从 `WEB-INF/classes` 中加载 class，所以当一个在 `WEB-INF/classes` 路径下的类被加载了之后，就不会再从 `WEB-INF/lib` 的 JAR 包中加载相同的类了。

## 两个相同的 class 都存在于 JAR 包中时怎么办？

那么假如 `WEB-INF/lib` 路径下不同的两个 JAR 包中包含两个相同的类（包名、类名完全相同）时，类加载器会选择加载哪个呢？

Servlet 规范中，对此并没有明确的要求，所以这种情况下的类加载顺序，可能会在不同的场景（比如操作系统）下有不同的行为。

### How Tomcat load jarfiles in WEB-INF/lib？

Tomcat 中是按什么顺序加载 `WEB-INF/lib` 路径下的 JAR 包的呢？

从 [Order of loading jar files from lib directory][order-from-lib] 的问答中可以看到，在 Tomcat 8.x 之前，是按照字母序顺序进行加载的。但从 8.x 开始，Tomcat 不再人为的增加这种排序，而是把这个顺序交给了具体的操作系统的实现。

从 [Regression. Load WEB-INF/lib jarfiles in alphabetical order][alphabetical-order] 邮件列表的讨论中，可以看到，关于这个问题的争论，从 2014 年开始，一直持续到了 2020 年 9 月份，并且仍然没有一个结论，所以 Tomcat 8.x 之后的版本，依然不能认为 JAR 包名字字母序排序在前的 JAR 一定会被优先加载。

PS. 感兴趣的童鞋可以围观一下上面的邮件列表，里面的讨论不乏言辞激烈的针锋相对，但依旧没有使决策者因为妥协而改变，而是必须要有充足的理由才能做出决定。虽然按序加载 JAR 包会带来一定的好处，但个人也是倾向于不要依赖这种顺序。

### Work around

那么有没有其他的变通方法来解决这种情况下的这个特定的问题呢？有，从 JAR 包里去掉一个重复的类，保证只有想要加载的类存在于所有 JAR 包中。

如果这两个有相同类的 JAR 包都没有源码，只能通过 Maven 依赖到项目中的时候怎么办呢？

可以借助持续集成工具，在构建最终的发布包时，通过脚本等方式，对 JAR 包进行拆包、去重及重新打包，以达到目标。

[class-loader]:(http://medialab.di.unipi.it/web/doc/JNetSec/jns_ch5.htm)
[class-loader-how-to]:http://tomcat.apache.org/tomcat-8.0-doc/class-loader-howto.html
[servlet-2.4]:https://download.oracle.com/otndocs/jcp/servlet-2.4-fr-spec-oth-JSpec/
[load-class]:https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/java/lang/ClassLoader.java#L563
[alphabetical-order]:(https://bz.apache.org/bugzilla/show_bug.cgi?id=57129)
[order-from-lib]:(https://stackoverflow.com/questions/5474765/order-of-loading-jar-files-from-lib-directory)
