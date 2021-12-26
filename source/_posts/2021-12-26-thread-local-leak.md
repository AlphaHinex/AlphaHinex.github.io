---
id: thread-local-leak
title: "ThreadLocal 泄露实例"
description: "用后一定要记得清理"
date: 2021.12.26 10:26
categories:
    - Java
tags: [Java, JVM]
keywords: ThreadLocal, remove, Context, jstat, G1, OOM
cover: /contents/covers/thread-local-leak.jpeg
---

ThreadLocal 是什么
=================

Java 中，`ThreadLocal` 是线程本地变量，可用来在多线程环境，为每个线程保存一份独立的变量，不会被其他线程所操作。

关于 ThreadLocal 详细的介绍及用法，可以查阅 [An Introduction to ThreadLocal in Java](https://www.baeldung.com/java-threadlocal) 。


为什么会出现泄漏
=============

线程的创建和销毁是很昂贵的操作，需多线程执行时，一般会使用线程池。当线程池和 ThreadLocal 同时使用时，因为线程在使用完成后会归还给线程池，供下次使用，而并非销毁再重新创建，所以如果之前线程存入的本地变量没有进行清理，后续再使用这个线程时，还是会看到之前的线程本地变量内容。


实例
====

https://github.com/AlphaHinex/threadlocal-leak-demo 构造了一个能够重现 ThreadLocal 泄露的实例。

```bash
# 使用 Maven Wrapper 编译，也可使用本地安装好的 Maven
$ ./mvnw clean package -DskipTests
# 为尽快重现，将最大堆内存设置为 100mb
$ java -Xms100m -Xmx100m -jar target/threadlocal-leak-demo-0.0.1-SNAPSHOT.jar
```

编译及运行后，访问 http://localhost:8080/leak/100000 ，通过 GET 请求触发，根据路径参数中指定的循环次数（100000），使用线程池中线程异步执行向线程本地变量放入 1KB 数据的操作。

可使用 [找出 Java 应用频繁 Full GC 的原因](https://alphahinex.github.io/2021/12/12/find-the-reason-of-full-gc/) 中介绍的工具，观察分析 gc 情况：

```bash
$ jstat -gcutil 31804 2s
  S0     S1     E      O      M     CCS    YGC     YGCT    FGC    FGCT     GCT
  0.00  24.93  67.42   2.05  92.68  89.88      3    0.017     1    0.020    0.036
  0.00  24.93  67.42   2.05  92.68  89.88      3    0.017     1    0.020    0.036
  0.00  24.93  67.42   2.05  92.68  89.88      3    0.017     1    0.020    0.036
 99.83   0.00  34.28  30.37  93.15  90.81      6    0.198     1    0.020    0.218
  0.00  14.13   3.81  51.37  93.16  90.83     13    0.283     1    0.020    0.303
 18.91   0.00  47.13  69.98  93.17  90.83     20    0.323     1    0.020    0.343
 29.23   0.00  93.33  83.31  93.17  90.83     24    0.352     1    0.020    0.372
 44.52   0.00   2.97  81.56  93.17  90.83     28    0.377     2    0.315    0.692
  0.00  61.57   0.00  95.68  93.17  90.83     31    0.395     3    0.315    0.710
  0.00   0.00  52.19 100.00  92.90  90.44     31    0.395     5    0.919    1.314
  0.00   0.00  84.68  99.91  92.90  90.44     31    0.395     8    1.414    1.810
  0.00   0.00 100.00  99.85  92.90  90.44     31    0.395    13    2.081    2.476
  0.00   0.00 100.00  99.89  92.90  90.44     31    0.395    19    3.090    3.485
  0.00   0.00 100.00  99.82  92.90  90.44     31    0.395    28    4.610    5.005
  0.00   0.00 100.00  99.82  92.90  90.44     31    0.395    40    6.372    6.767
  0.00   0.00  99.69  99.90  92.90  90.44     31    0.395    54    8.407    8.802
  0.00   0.00 100.00  99.89  92.90  90.44     31    0.395    67   10.297   10.692
  0.00   0.00 100.00  99.87  92.90  90.44     31    0.395    81   12.378   12.774
  0.00   0.00 100.00  99.87  92.90  90.46     31    0.395   104   14.362   14.758
```

可以看到，迅速出现了 YGC 不增加，频繁 FGC 的情况。此时在应用日志中，可以观察到线程计数，执行了 7.3w 次左右时，出现类似 `java.lang.OutOfMemoryError: GC overhead limit exceeded` 的异常，且应用无响应。

查看堆内存的分配及使用情况：

```bash
$ jmap -heap 31804
...
Heap Usage:
PS Young Generation
Eden Space:
   capacity = 18350080 (17.5MB)
   used     = 18350080 (17.5MB)
   free     = 0 (0.0MB)
   100.0% used
From Space:
   capacity = 8388608 (8.0MB)
   used     = 0 (0.0MB)
   free     = 8388608 (8.0MB)
   0.0% used
To Space:
   capacity = 7864320 (7.5MB)
   used     = 0 (0.0MB)
   free     = 7864320 (7.5MB)
   0.0% used
PS Old Generation
   capacity = 70254592 (67.0MB)
   used     = 69874480 (66.63749694824219MB)
   free     = 380112 (0.3625030517578125MB)
   99.4589506690182% used
...
```

如果将堆 dump，使用 MAT 可以看到堆中空间主要被线程池中的线程所占，而线程的本地变量中，存在大量随机生成的数据。


不同的垃圾收集器能屏蔽这个问题吗
===========================

Java 8 默认使用的是 Parallel GC，改用其他收集器能否屏蔽这个问题呢？可以用上面的实例来验证一下。

```bash
# 改用 G1 收集器
$ java -XX:+UseG1GC -Xms100m -Xmx100m -jar target/threadlocal-leak-demo-0.0.1-SNAPSHOT.jar
```

改用 G1 收集器后，再次访问 http://localhost:8080/leak/100000 ，可以通过日志中的线程计数器，看到执行了 8.9w 次左右，比使用默认收集器时的 7.3w 次，多了 1w 多次。

```log
DEBUG 26589 --- [         task-6] i.g.a.t.service.DemoService              : task-6 add 1kb to context, No.89548
```

此时再查看堆内存情况：

```bash
$ jmap -heap 26589
...
Heap Usage:
G1 Heap:
   regions  = 100
   capacity = 104857600 (100.0MB)
   used     = 103868872 (99.05707550048828MB)
   free     = 988728 (0.9429244995117188MB)
   99.05707550048828% used
G1 Young Generation:
Eden Space:
   regions  = 0
   capacity = 0 (0.0MB)
   used     = 0 (0.0MB)
   free     = 0 (0.0MB)
   0.0% used
Survivor Space:
   regions  = 0
   capacity = 0 (0.0MB)
   used     = 0 (0.0MB)
   free     = 0 (0.0MB)
   0.0% used
G1 Old Generation:
   regions  = 0
   capacity = 104857600 (100.0MB)
   used     = 103868872 (99.05707550048828MB)
   free     = 988728 (0.9429244995117188MB)
   99.05707550048828% used
...
```

可以看到 G1 将所有的 region 都分给了老年代，年轻代里的容量都变为了 0，这也能解释为什么用 G1 能比默认的垃圾收集器多跑了 1w 多次存入数据的操作。

所以结论是：使用不同的垃圾收集器，并不能屏蔽这个问题，但有可能延长出现问题的时间，缓解症状。


如何避免
=======

记得 remove
----------

那么如何根治这个问题呢？最有效的办法，就是及时清理不再需要的 ThreadLocal 对象。在 ThreadLocal 类中，提供了一个 `remove()` 方法，在恰当的时机，进行调用，如 [DemoContext:30](https://github.com/AlphaHinex/threadlocal-leak-demo/blob/main/src/main/java/io/github/alphahinex/threadlocalleakdemo/context/DemoContext.java#L30) 。

使用插件进行代码检查
-----------------

在 IDEA 中，如果使用了 `Alibaba Java Coding Guidelines` 插件，有一个 “必须回收自定义的ThreadLocal变量” 的规则，会对自定义的 ThreadLocal 变量进行检查，如果没有对其执行过 `remove` 操作，会在编辑器中给出黄色告警信息。

如果希望在编译过程中，对这个问题进行检查，可以加入 [maven-pmd-plugin](https://maven.apache.org/plugins/maven-pmd-plugin/index.html)，并配置 [p3c-pmd](https://github.com/alibaba/p3c/tree/master/p3c-pmd) 中增加的规则，在代码构建阶段进行检查，以便及时发现问题。

具体 `pom.xml` 中需增加的内容如下：

```xml
<properties>
   <pmd.version>6.15.0</pmd.version>
</properties>

<build>
   <plugins>
      <plugin>
         <groupId>org.apache.maven.plugins</groupId>
         <artifactId>maven-pmd-plugin</artifactId>
         <version>3.8</version>
         <configuration>
            <rulesets>
               <!--<ruleset>rulesets/java/ali-comment.xml</ruleset>-->
               <ruleset>rulesets/java/ali-concurrent.xml</ruleset>
               <ruleset>rulesets/java/ali-constant.xml</ruleset>
               <ruleset>rulesets/java/ali-exception.xml</ruleset>
               <ruleset>rulesets/java/ali-flowcontrol.xml</ruleset>
               <ruleset>rulesets/java/ali-naming.xml</ruleset>
               <ruleset>rulesets/java/ali-oop.xml</ruleset>
               <ruleset>rulesets/java/ali-orm.xml</ruleset>
               <ruleset>rulesets/java/ali-other.xml</ruleset>
               <ruleset>rulesets/java/ali-set.xml</ruleset>
            </rulesets>
            <printFailingErrors>true</printFailingErrors>
         </configuration>
         <dependencies>
            <dependency>
               <groupId>net.sourceforge.pmd</groupId>
               <artifactId>pmd-core</artifactId>
               <version>${pmd.version}</version>
            </dependency>
            <dependency>
               <groupId>net.sourceforge.pmd</groupId>
               <artifactId>pmd-java</artifactId>
               <version>${pmd.version}</version>
            </dependency>
            <dependency>
               <groupId>net.sourceforge.pmd</groupId>
               <artifactId>pmd-javascript</artifactId>
               <version>${pmd.version}</version>
            </dependency>
            <dependency>
               <groupId>net.sourceforge.pmd</groupId>
               <artifactId>pmd-jsp</artifactId>
               <version>${pmd.version}</version>
            </dependency>
            <dependency>
               <groupId>com.alibaba.p3c</groupId>
               <artifactId>p3c-pmd</artifactId>
               <version>2.1.0</version>
            </dependency>
         </dependencies>
      </plugin>
   </plugins>
<build>
```

完整的 `pom.xml` 文件可见 [这里](https://github.com/AlphaHinex/threadlocal-leak-demo/blob/main/pom.xml)。

配置后，执行 `mvn pmd:check` 可以检查代码，并给出所有违反检查规则的位置及问题。

```bash
$ mvn pmd:check
...
[INFO] --- maven-pmd-plugin:3.8:check (default-cli) @ threadlocal-leak-demo ---
[INFO] PMD Failure: io.github.alphahinex.threadlocalleakdemo.context.DemoContext:9 Rule:ThreadLocalShouldRemoveRule Priority:2 ThreadLocal字段【CONTEXT】应该至少调用一次remove()方法。.
[INFO] ------------------------------------------------------------------------
[INFO] BUILD FAILURE
[INFO] ------------------------------------------------------------------------
[INFO] Total time: 1.771 s
[INFO] Finished at: 2021-12-25T16:27:14+08:00
[INFO] ------------------------------------------------------------------------
[ERROR] Failed to execute goal org.apache.maven.plugins:maven-pmd-plugin:3.8:check (default-cli) on project threadlocal-leak-demo: You have 1 PMD violation. For more details see: /Users/alphahinex/github/origin/threadlocal-leak-demo/target/pmd.xml -> [Help 1]
...
```