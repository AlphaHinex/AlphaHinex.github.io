---
id: new-features-of-java-versions
title: "【转】Java 8 到 Java 24 新特性一览"
description: "列举了关键特性及应用场景和示例代码，值得了解"
date: 2025.05.18 10:34
categories:
    - Java
tags: [Java, JDK]
keywords: Lambda, Stream, Record, Pattern Matching, Sealed Class, Scoped Values, Virtual Threads, Pattern Matching for Switch, ZGC, G1
cover: /contents/covers/new-features-of-java-versions.jpeg
---

![](https://alphahinex.github.io/contents/covers/new-features-of-java-versions.jpeg)

- 版权声明：本文为博主原创文章，遵循 [CC 4.0 BY-SA](http://creativecommons.org/licenses/by-sa/4.0/) 版权协议，转载请附上原文出处链接和本声明。
- 本文链接：https://blog.csdn.net/weixin_53933896/article/details/147856986

# 文章说明

1. 本文整理了 Java 8 至 Java 24 各版本的新特性，内容包括每个版本的新增功能分类（如语法增强、性能优化、工具支持等）、详细的代码示例，并结合官方文档资料，分析每项特性的应用场景及优缺点。
2. Java 8 发布于 2014 年，此后 Java 进入快速迭代模式，每半年发布一个新版本。一路走来，Java 8 到 Java 24 带来了大量重要的新特性。
3. 本文持续更新中…

# Java 8 新特性

**发行时间**： 2014 年 3 月

## 语言特性

- **Lambda 表达式与函数式接口**：Java 8 引入了 **Lambda 表达式**，使我们能够将匿名函数作为一等公民传递和使用。例如，可以使用 `Comparator<String> cmp = (a, b) -> a.length() - b.length();` 来实现字符串长度比较。这依赖于 **函数式接口**（只含单一抽象方法的接口），如 `Comparator` 或自定义接口，Lambda 会被推断成该接口的实现。有了 Lambda，代码变得更加简洁，可读性提高，尤其适用于集合的过滤、映射等操作。
```java
// 示例：使用 Lambda 表达式对列表进行过滤和映射
List<String> names = Arrays.asList("Alice", "Bob", "Ann");
List<String> filtered = names.stream()
                             .filter(s -> s.startsWith("A"))
                             .map(s -> s.toUpperCase())
                             .collect(Collectors.toList());
System.out.println(filtered); // 输出: [ALICE, ANN]
```
- **方法引用**：除了 Lambda，Java 8 还支持 **方法引用**，可以用 `Class::method` 简洁地引用已有方法或构造器。例如，`names.forEach(System.out::println)` 会打印列表中每个元素，相当于对每个元素执行 System.out.println。方法引用与 Lambda 一样，也必须对应一个函数式接口目标类型。
- **接口默认方法和静态方法**：接口现在可以包含带实现的 **默认方法**（`default`方法）和 **静态方法**。这使得在不破坏已有实现类的前提下向接口添加新方法成为可能。默认方法可被实现类继承或重写；静态方法则只能通过接口名调用，不能被子类重写。例如：
```java
interface MyInterface {
    static void staticMethod() {
        System.out.println("接口静态方法");
    }
    default void defaultMethod() {
        System.out.println("接口默认方法");
    }
    void abstractMethod();
}
class MyClass implements MyInterface {
    @Override
    public void abstractMethod() { }
    // 未重写 defaultMethod()，将继承接口的默认实现
}
MyInterface.staticMethod();       // 调用接口静态方法
new MyClass().defaultMethod();    // 调用接口默认方法，实现类未重写则执行接口中的实现
```
**应用场景**： 默认方法解决了接口演化的问题，比如 Java 8 为 `Collection` 接口添加了 `stream()` 默认方法，从而所有实现类无需修改就自动拥有流操作能力。静态方法则方便在接口中组织工具函数。
- **重复注解（Repeatable Annotation）**： 允许在同一声明或类型上多次应用同一个注解类型。Java 8 引入了 `@Repeatable` 元注解，通过定义“容器注解”类型来实现重复注解支持。应用场景如定义多个过滤器、多个权限注解等，使代码更直观。例如：
```java
@Schedule(day="Mon"), @Schedule(day="Tue")
void scheduledTask() { ... }
```
- **类型注解**： Java 8 扩展了注解使用的场景，注解现在可以加在任何类型使用处（Type Use），如泛型类型参数、强制转换、实现声明等。结合 JSR 308，可用于开发更强的类型检查工具（如空指针分析）。

## 核心库新特性

- **Stream API**： Java 8 的 **Stream API** 为集合批量操作提供了声明式、链式的语法。开发者可以使用类似 SQL 风格的操作（`filter`, `map`, `reduce` 等）来处理数据流。`Stream` 的操作分为**中间操作**（惰性求值）和**终止操作**（触发计算）。例如：
```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);
int sum = numbers.stream()
                 .filter(n -> n % 2 == 1)      // 筛选奇数
                 .mapToInt(n -> n * n)         // 平方映射
                 .sum();                       // 终止操作求和
System.out.println(sum); // 输出: 35（1^2 + 3^2 + 5^2）
```
**应用场景**： Stream API 大大简化了集合的复杂操作，避免了繁琐的迭代和临时集合管理。例如，可以轻松进行过滤、汇总统计、分组分区等操作。缺点是初学者需要学习 Lambda 表达式和流式思维，但一旦掌握，能编写出高可读性的流水线处理代码。
- **Optional 类**： 引入了 `java.util.Optional<T>`，用于优雅地表示“可能为空”的值。Optional 提供了诸如 `isPresent()`, `ifPresent()`, `orElse()` 等方法，可以替代显式的空检查，减少空指针异常风险。例如：
```java
public Optional<User> findUser(String name) {
    User result = ... // 查找用户
    return Optional.ofNullable(result);
}
// 使用Optional避免显式null判断
findUser("Alice").ifPresent(user -> System.out.println(user.getId()));
User user = findUser("Bob").orElse(new User("Bob")); // 未找到则返回默认User
```
**应用场景**： Optional 常用于方法返回值，表示“可能没有结果”。这比返回 `null` 更具语义，也迫使调用方处理不存在的情况。需要注意不要滥用在域对象上，Optional设计主要用于返回值，而非序列化或字段类型。
- **全新的日期时间 API**： Java 8 推出了 `java.time` 包（JSR 310），提供了不变且线程安全的日期时间类，包括 `LocalDate`, `LocalTime`, `LocalDateTime`, `ZonedDateTime` 等，以及用于周期和持续时间的 `Period`, `Duration`。新的 API 改进了旧版` java.util.Date` 和 `Calendar` 的诸多问题，提供了更加自然的时间操作接口。例如：
```java
LocalDate today = LocalDate.now();
LocalDate birthday = LocalDate.of(1990, Month.APRIL, 1);
Period period = Period.between(birthday, today);
System.out.printf("年龄: %d 年 %d 月 %d 日%n", 
                  period.getYears(), period.getMonths(), period.getDays());
```
**应用场景**： 新日期API提供了清晰的方法来操作日期时间，支持时区、夏令时、安全不变。此外还提供了格式化和解析（`DateTimeFormatter`），大幅简化日期处理，避免了旧 API 各种不一致和缺陷。
- **并发增强（CompletableFuture 等）**： Java 8 在并发库方面增加了 `CompletableFuture`，支持以**链式回调**的方式处理异步结果，实现了Promise模式。例如可以组合多个异步计算、设置依赖和异常处理。此外，新增的并发工具包括并行数组排序（`Arrays.parallelSort`）、并发Accumulator、Adder等，改进了并行计算性能。
- **其它常用库改进**： 例如 `Map.computeIfAbsent` 等函数式风格的方法，方便地对 Map 执行条件更新；Base64 编码解码器（`java.util.Base64`）也在 Java 8 加入成为标准库。

## JVM 与性能优化

- **永久代移除**： Java 8 移除了 HotSpot VM 的永久代（PermGen），取而代之的是 **元空间（Metaspace）**。元空间在本地内存中分配且按需增长，大幅减少了因固定永久代空间不足导致的 `OutOfMemoryError` 情况，提高了内存管理的灵活性。开发者在升级时需要注意移除了永久代相关的 JVM 参数（如 `-XX:PermSize`）。
- **垃圾回收优化**： Java 8 中虽然默认垃圾回收器仍是 Parallel GC，但引入了一些改进。例如引入**串行/并行 Full GC** 等优化；此外为 G1 垃圾收集器（实验性）打下基础。虽然 G1 直到 Java 9 才成为默认 GC，但在 Java 8 已可通过 `-XX:+UseG1GC` 使用，其目标是低停顿，更适合大堆内存应用。
- **HashMap 性能改进**： 为了应对哈希碰撞，Java 8 改进了 `HashMap` 和 `ConcurrentHashMap` 的实现。当桶中链表长度超过阈值时，将链表转换为 `红黑树` 存储，从平均 O(n) 查找降为 O(log n)。这显著改善了哈希冲突严重时的性能 **（优点），代价是结构更复杂（可能略增插入删除成本）**。但总体而言，这让 HashMap 在最坏情况下性能更可控。

## 工具和其他

- **Nashorn JavaScript引擎**： Java 8 内置了全新的 JavaScript 引擎 **Nashorn**，替代了原有的 Rhino 引擎。Nashorn 利用 InvokeDynamic 提高了 JS 运行性能，可通过 `jjs` 命令运行 .js 脚本，也能在Java程序中使用 `ScriptEngine` 执行JS代码。在需要在 JVM 中嵌入脚本、实现动态逻辑的场景下，Nashorn 提供了更高性能和ES5兼容性。不过需要注意 Nashorn 在后续 Java 15 已被移除，建议长期方案还是GraalVM多语言支持。
- **增强的注解处理和反射**： Java 8 对反射和注解处理也有一些改进，如引入 `Parameter` 类来支持获取方法参数名（需加 `-parameters` 编译），以及 `AnnotatedElement` 接口新增方法直接获取重复注解等。这些增强使框架开发者更方便地获取运行时信息，构建更丰富的注解驱动逻辑。

**总结**： Java 8 是一个里程碑版本，引入的 Lambda 和 Stream 等特性使Java正式进入函数式编程时代。默认方法等特性改善了接口演进能力。核心库的加强和全新时间API填补了多年痛点。在性能上，永久代的移除和集合优化提升了稳定性。Java 8 的诸多新功能为之后的Java版本奠定了基础，也是目前许多项目仍在使用的版本。

# Java 9 新特性

**发行时间**： 2017 年 9 月

## 语言和语法增强

- **模块化系统（Project Jigsaw）**： Java 9 最重要的变化是引入**模块化系统**。JDK 本身被重组为约 94 个模块，允许按需组合所需模块来构建定制的 Java 运行时（可使用下面提到的 jlink 工具）。开发者可以通过创建模块描述符 `module-info.java` 将应用拆分为模块。模块定义了所包含的包以及导出的内容和所需依赖，例如：
```java
// module-info.java 示例
module com.example.app {
    requires com.example.utils;    // 声明依赖模块
    exports com.example.app.api;   // 导出包供其他模块使用
}
```
模块系统解决了 classpath 下包命名冲突和封装不严的问题，实现**强封装**。只有模块导出的包才能被外部访问，未导出的内部实现包将被严格封装。这样提高了代码的可维护性和安全性。**应用场景**： 大型应用可以通过模块划分更好地管理依赖关系，同时在部署时使用 jlink 剔除无关模块减小体积。不过模块化也带来了学习曲线，且现有项目迁移需要调整访问限制（可以通过 `--add-exports` 等选项做兼容）。
- **接口私有方法**： 除了 Java 8 的接口默认方法外，Java 9 支持接口定义 **私有方法** 来给多个默认方法复用业务逻辑。这提高了接口内部实现的封装性，避免默认方法之间代码重复。私有接口方法只能在接口内部被默认或静态方法调用，不会暴露给实现类。
- **try-with-resources 改进**： try-with-resources 语法在 Java 9 更加方便。现在如果已有实现 `AutoCloseable` 的资源对象(final或 effectively final)，可以直接在 try 语句中使用该变量，而不必再次声明。例如：
```java
// Java 8 及之前需要在 try 内新声明
try (BufferedReader br = Files.newBufferedReader(path)) { ... }
// Java 9 可以在 try 中直接使用已有的变量 br
BufferedReader br = Files.newBufferedReader(path);
try (br) {
    // 使用 br 读取...
}
```
这减少了不必要的代码臃肿，让语法更简洁。

## 核心库增强

- **集合工厂方法**： Java 9 为集合接口添加了方便创建不可变集合的静态工厂方法。例如：`List.of(1,2,3)`, `Set.of("a","b")`, `Map.of("key1","val1","key2","val2")` 等，可以快捷地创建包含固定元素的集合。这些集合是**不可修改**的（修改会抛异常）。相比手动创建集合然后 `Collections.unmodifiableX`，新方法更直观高效。应用场景： 用于快速创建常量集合、简化测试用例数据准备等。
- **Stream API 改进**： Java 9 为 Stream 增加了一些实用的新方法，如 `takeWhile`, `dropWhile` 和 `ofNullable` 等。其中 `takeWhile(predicate)` 会从 Stream 开头起连续获取满足条件的元素，直到遇到不满足条件者停止；`dropWhile(predicate)` 则丢弃开头连续满足条件的元素。还有 `Stream.iterate` 支持提供断言来结束迭代。例如：
```java
Stream.of(1,2,3,4,5).takeWhile(n -> n < 4)  // 得到 [1,2,3]
Stream.of(1,2,3,4,5).dropWhile(n -> n < 4)  // 得到 [4,5]
Stream.iterate(1, x -> x+1).takeWhile(x -> x<=5).forEach(System.out::println);
```
此外，`Optional` 也增加了 `ifPresentOrElse`, `or` 等方法，提高 Optional 的易用性。这些改进让流操作和 Optional 更加完备，减少手动处理。
- **进程 API**： 新增 `ProcessHandle` 接口，提供了更现代的进程管理 API。通过 `ProcessHandle.current()` 可以获取当前进程信息，包括 PID 等；还能列出现有进程，观察进程树关系，设置监听等。相比以前只能通过 `Runtime.getRuntime().exec()` 启动进程、基本无反馈，新的 API 丰富了进程交互能力。例如：
```java
ProcessHandle self = ProcessHandle.current();
long pid = self.pid();
self.info().command().ifPresent(cmd -> System.out.println("命令: " + cmd));
```
这在需要监控或管理操作系统进程的应用中非常有用，如实现自定义的进程守护、获取子进程退出事件等。
- **响应式流（Reactive Streams）**： Java 9 在 `java.util.concurrent` 下引入了 **发布-订阅框架**：`Flow` API，包括 `Flow.Publisher`, `Subscriber`, `Subscription`, `Processor` 四个接口。这实际上与 Reactive Streams 标准兼容，为反应式编程提供背压（backpressure）支持。虽然Java 9没有提供具体实现，但像 RxJava、Akka Streams 等库可直接与这套接口集成。应用在需要异步数据流且要考虑消费速率的场景。
- **HTTP/2 客户端（孵化）**： Java 9 引入了一个新的 HTTP 客户端 API 的孵化版本（位于 `jdk.incubator.httpclient` 模块），支持 HTTP/2 和 WebSocket。虽然后来在 Java 11 才正式成为标准 API，这里值得一提。这新客户端支持异步非阻塞调用，比旧的 `HttpURLConnection` 更易用、性能更佳。

## JVM 和性能

- **G1 成为默认 GC**： Java 9 将 **G1 垃圾收集器** 设置为默认垃圾回收器，取代了之前的 Parallel Scavenge/Parallel Old 组合。G1（Garbage First）是一种低暂停收集器，擅长处理大堆内存，尽量避免了全堆的长时间停顿。在 Java 9 中，G1 的 Full GC 仍是单线程的，因此极端情况下可能出现长暂停。对此在 Java 10 又做了并行化改进。**应用场景**： 对延迟敏感的服务，可从默认使用G1中获益（前提是仔细调优以适应应用负载）。
- **字符串存储优化**： Java 9 引入了 **Compact Strings**，即在内部用 byte 数组存储字符串字符（Latin-1 和 UTF-16 动态选择），而不再总是用 char 数组。对于只包含ASCII的字符串，可节省一半内存。这个改动对开发者透明，但在字符串处理密集的应用中降低了内存占用，提高了CPU缓存利用率。
- **AOT 编译（实验）**： 新增了 `jaotc` 工具，允许将 Java 类提前编译为本地代码（Ahead-Of-Time）。AOT 编译器基于 Graal，可生成本地库，在应用启动时加载，从而加快启动速度。不过这是实验性功能，实际使用较少，在后续版本中也被移除。场景：需要极致优化启动时间的场合可以探索，但一般而言JIT已经足够。
- **VarHandle 和内存栅栏**： Java 9 提供了 `java.lang.invoke.VarHandle` 类，作为对 `sun.misc.Unsafe` 的更安全替代。VarHandle 可以视作特定变量的引用，支持原子操作和内存可见性控制，比如读取写入内存栅栏（类似于 C++ 中的 `std::atomic`）。这为开发并发框架、实现锁自由算法提供了标准化的工具。
- **多版本 JAR**： 支持 **多版本 JAR** 文件，即在一个 JAR 中根据不同Java版本包含不同的类实现（通过 META-INF/versions 目录）。运行时将选择匹配当前JVM版本的类，实现库对新旧版本的兼容发布。例如，你可以在 JAR 中同时包含 Java 8 的实现和利用Java 9特性的实现。这样第三方库可以渐进地利用新特性，同时不失对旧版本的支持。

## 工具与其他

- **JShell**： Java 9 带来了官方的交互式 REPL 工具 **JShell**。开发者可以在不创建类和 main 方法的情况下，直接输入Java表达式或语句，即时查看执行结果。例如：
```java
jshell> int x = 5 * 20
x ==> 100
jshell> "hello, " + "jshell"
$2 ==> "hello, jshell"
```
JShell 极大地方便了试验性编程和学习。可以用它快速验证一段逻辑、探索API用法等，降低了写一个`Hello World`的门槛。对于教学、原型开发非常实用。
- **jlink**： Java 9 引入了 `jlink` 工具，可以根据模块依赖创建自定义的精简运行时镜像。开发者指定应用模块后，jlink 会打包只包含所需模块的最小化 JRE。这对于发布自包含的Java应用很有帮助，特别是在容器、物联网设备上，可减少体积并避免目标环境需要预装完整JDK。
- **JUnit 5 等生态升级**： 随着Java 9发布，测试框架JUnit 也升级到5，支持Java 8+特性如Lambda断言等。这虽不是JDK自带，但与语言新特性配套出现，标志着Java生态正拥抱新版本。

**总结**： Java 9 通过模块系统对Java平台进行了**结构性革新**。虽然社区对模块化褒贬不一，但不可否认它提高了代码封装和定制部署能力。除此之外，Java 9 在语法上小幅改进（私有接口方法、钻石操作符支持匿名类等**未提及细节**），在API和工具上为开发者提供了许多便捷，如JShell、集合工厂等。它为之后的版本铺平了道路，标志着Java进入了**快速发布**的新时代。

# Java 10 新特性

**发行时间**： 2018 年 3 月

## 语言特性

- **局部变量类型推断（`var`）**： Java 10 最引人注目的特性是引入了新的关键字 `var`，用于局部变量类型推断。开发者在定义局部变量时，可以用 `var` 代替具体类型，编译器会根据初始化表达式自动推断类型：
```java
var list = new ArrayList<String>();
var sum = 0;
for (var item : list) {
    // 在循环中，item 的类型也会被推断
}
```
在上述代码中，编译器会推断出 `list` 的类型为` ArrayList<String>`，`sum` 的类型为 `int`。**注意： `var` 不是**动态类型或弱类型，Java 类型系统仍是静态的，只是让编译器替我们填写类型。因此，`var` 只能用于有初始化的局部变量、for循环索引等，不可用于成员变量、方法参数，也不可将 `null` 赋给 `var`（无法推断类型）。另外，使用 `var` 可能降低代码可读性，应该在**类型明显**或**冗长**的情况下使用，如复杂泛型类型。对于简单变量，直接写出类型可能更清晰。

**应用场景**： `var` 可减少样板代码，特别是当类型本身冗长（如泛型嵌套）时。例如：
```java
Map<String, List<Integer>> data = new HashMap<>();
// 使用 var 推断类型
var dataMap = new HashMap<String, List<Integer>>();
```
这在一定程度上让Java具有了脚本语言的简洁性，但依然保留了静态类型检查的安全性。

## 核心库增强

- **不可变集合拷贝**： 在 Java 9 提供集合工厂方法基础上，Java 10 为集合增加了 `List.copyOf`, `Set.copyOf`, `Map.copyOf` 静态方法。这些方法会返回传入集合的`不可变拷贝`。例如：
```java
List<String> src = new ArrayList<>(List.of("a", "b"));
List<String> copy = List.copyOf(src);
src.add("c");
System.out.println(copy); // 输出 [a, b]，copy 不受原列表修改影响
copy.add("d"); // UnsupportedOperationException，不可修改
```
**应用场景**： 当需要确保集合不被修改时，可以方便地获取其不可变版本，尤其在方法参数和返回值中传递集合时，使用 `copyOf` 能防止意外修改源集合。另外，Collectors 增加了 `Collectors.toUnmodifiableList()` 等方法，直接收集 Stream 元素为不可变集合。
- **Optional 增强**： Java 10 为 `Optional` 新增了 `orElseThrow()` 方法，它等价于 `.orElseThrow(NoSuchElementException::new)`。虽然功能与 `get()` 相似，但命名更明确，语义更清晰（get() 在Optional语境下不直观）。此外还引入了 `Optional.or(() -> alternativeOptional)` 来在当前Optional为空时提供另一个Optional。这些方法让Optional的链式操作更丰富，使用更加流畅。
- **并行垃圾回收器接口**： 引入 `java.lang.ref.Cleaner` 提供替代 `finalize()` 的清理机制。尽管不直接属于核心“库”，但Java 10重新整理了垃圾收集器的内部接口，将不同 GC 实现的共性提取出来。这对最终用户没有直接影响，但使得 HotSpot 更易于添加新GC。这体现了JDK内部代码的演进。

## 性能和 JVM 改进

- **G1 并行 Full GC**： 虽然 G1 在 Java 9 成为默认 GC，但它的 Full GC 仍是单线程。Java 10 通过 JEP 307 实现了 **G1 Full GC 并行化**。现在当 G1 不得不触发 Full GC 时，会使用多个线程并行标记清除，减少停顿时间。这提升了 G1 在高内存占用下的最坏情况表现，使其更接近预期的低延迟目标**（优点）**。对于内存非常紧张、可能触发Full GC的场景，这一改进能显著降低停顿时长。当然，在正常情况下，G1 仍会努力避免 Full GC 的发生。
- **应用类数据共享（AppCDS）**： 类数据共享（CDS）功能早在 JDK 5 就存在，用于将JDK的核心类预加载到共享归档，从而加快启动并减少内存占用。Java 10 通过 JEP 310 将 CDS 扩展到应用层面，允许**应用类**也加入共享归档。原理是先在一次运行中记录所加载的应用类列表，生成归档文件；下次启动时直接映射此归档，加速类加载并减少重复占用的元空间。**应用场景**： 对于多实例部署的相同应用，使用 AppCDS 可减少整体内存占用；对单实例应用也能略微提升启动性能。不过配置上有一定复杂度（需要一次试运行生成列表），Java 13 又引入了动态CDS归档以简化流程。
- **线程局部握手（Thread Local Handshake）**： Java 10 改进了 JVM 停止线程执行的机制。以前 Stop-The-World 操作通常需要全局安全点，在同一时刻挂起所有线程。引入线程本地握手后，JVM 可以在不停止全部线程的情况下，对单个线程执行小任务或检查。例如可以挂起单个线程以回收它的栈，其他线程不受影响**（优点）**。这一特性提升了调优GC和其他VM功能的灵活性，是 JVM 内部优化，但最终有助于降低停顿、提升并发性能。
- **备用内存设备上的堆**： 允许 JVM 将 Java 堆分配在非主内存设备上（如NVDIMM持久内存）。这对于使用特殊硬件（比如大容量的持久内存）的应用有意义，可以扩大有效堆容量或持久化堆数据。这属于非常专业的优化特性，普通场景用不到，但体现了Java对新硬件技术的支持。

## 工具和平台

- **实验性 Java JIT 编译器 - Graal**： Java 10 将基于Java实现的 JIT 编译器 `Graal` 引入为实验性选项。启用参数为` -XX:+UnlockExperimentalVMOptions -XX:+UseJVMCICompiler`，仅限Linux/macOS的64位环境。Graal 致力于更高级的优化和多语言支持，是后续GraаlVM的基础。尽管默认仍是C2编译器，但尝试者可以用Graal看看是否带来性能改进。这一特性表明了JIT实现也可以用Java自身来编写，利于未来的维护和演进。
- **根证书开源**： Oracle 将 JDK 内置的 root CA 证书库开源，替代以前Oracle JDK与OpenJDK差异的一部分。这意味着OpenJDK自带了可信证书库，使HTTPS通信开箱即用（以前OpenJDK默认缺少很多可信证书）。这对开发者是无感知的改进，但对于OpenJDK采用者是福音。

**总结**： 虽然 Java 10 属于非 LTS 的短期版本，但引入的 var 关键字极大地简化了日常编码。集合、Optional的小改进也增强了标准库的便利性。在性能方面，G1 并行Full GC、AppCDS 都是偏底层却意义重大的优化，让Java在大内存和大规模部署场景下表现更好。Java 10 还预示了未来的发展方向，如Graal编译器的引入为后续多语言支持铺路。作为承上启下的版本，Java 10 为后来Java 11的重大变化做好了准备。

# Java 11 新特性

**发行时间**： 2018 年 9 月 25 日 （LTS长期支持版）

## 语言特性

- **Lambda 参数的局部变量语法**： Java 11 允许在 Lambda 表达式的参数中使用局部变量语法，即可以用 `var` 来声明参数类型。例如：
```java
Comparator<String> cmp = (var a, var b) -> Integer.compare(a.length(), b.length());
```
这对Lambda本身功能没有变化，但允许我们添加参数注解时更方便（因为只能用显式类型才能加注解）。总体来说，这一特性用途有限，仅在某些需要注解lambda参数的场景下提供了语法便利。
- **直接启动单文件程序**： Java 11 可以直接运行单个Java源文件，命令如：`java Hello.java`。Java编译器会隐式地先编译这个源文件再执行。这使得**脚本化**使用Java成为可能，方便编写临时的小程序或教学演示。例如，新手可以直接写 `System.out.println("Hello");` 保存为 Hello.java，然后 `java Hello.java` 即可运行。需要注意的是：该源文件的所有依赖类都必须在同一文件中或者在类路径上。
**应用场景**： 这一特性降低了Java的入门门槛和使用Java编写脚本的成本，可以拿来写简单的工具脚本、验证性程序等，提升了开发者体验。配合 JShell，Java 在快速试验和脚本方面的短板进一步缩小。

## 核心库增强

- **标准化 HTTP 客户端**： Java 11 将新 HTTP 客户端 API 正式加入标准库（位于 `java.net.http` 包）。这个 API 支持 HTTP/1.1 和 HTTP/2，并提供了同步和异步（基于 CompletableFuture）两种调用方式。示例：
```java
HttpClient client = HttpClient.newHttpClient();
HttpRequest request = HttpRequest.newBuilder(new URI("https://api.github.com"))
                                 .header("Accept", "application/json")
                                 .GET().build();
HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
System.out.println(response.body());
```
新客户端比旧的 `HttpURLConnection` 使用更简洁，功能更丰富（如内置 WebSocket 支持）。**应用场景**： 调用 REST 服务、执行HTTP请求等在企业开发中很常见，新API提高了开发效率，并发支持和HTTP/2多路复用也带来性能优势。
- **字符串API增强**： Java 11 对 `String` 添加了若干实用方法：
- - `isBlank()`：判断字符串是否为空白（空串或只含空白字符）。
- - `strip()`：类似 `trim()`，但能正确处理 Unicode 空白（并有 `stripLeading`, `stripTrailing`）。
- - `repeat(int count)`：重复当前字符串 count 次，返回新串。
- - `lines()`：将字符串按行拆分为一个流（Stream）。
例如：`" foo\n".strip()` 将得到 `"foo"`； `"".isBlank()` 返回 true； `"ab".repeat(3)` 返回 `"ababab"`。这些方法使常见字符串处理更方便。应用在清理用户输入、生成简单重复文本等场景。
- **文件方法和集合增强**： 引入了 `Files.readString(Path)` 和 `Files.writeString(Path, CharSequence)` 来简化文件读写操作（以前需要自行使用流读取或写入）。集合接口也增加了一些默认方法，如 `Collection.toArray(IntFunction generator)` 可以方便地生成正确类型的数组。`Optional` 新增了 `isEmpty()` 方法，与 `isPresent()` 相对，更直观地判断空Optional。
- **关键字 var 用于Lambda**： 前面提及的 lambda 参数使用 `var` 实际上属于语言变化，但一起提及：这使得我们可以在 lambda 参数上加注解。例如 `(var x, var y) -> x + y`，如果不需要注解，一般直接 `(x, y)` 就好，所以此特性主要为注解服务。

## 性能与内存

- **ZGC（可伸缩低延迟 GC）**： Java 11 引入了实验性的 `Z Garbage Collector (ZGC)`。ZGC是一种着眼于超大堆内存的低延迟垃圾收集器，采用着色指针和读屏障，实现了几乎全部并发的收集过程。ZGC 的目标是在任意堆大小下将GC停顿控制在十毫秒级别以内。这对需要超低延迟且使用大内存的应用（如内存数据库）很有意义。启用ZGC需要加VM参数如 `-XX:+UseZGC`（仅限64位 Linux，当时）。虽然ZGC在Java 11是实验状态，但它展示了JVM GC技术的新方向。
- `Epsilon GC`： 另一个实验性GC —— `Epsilon` 也在Java 11中提供。Epsilon是一个`空GC`，它`不回收内存`，只负责分配内存，等内存用完即让程序崩溃。这个听似奇怪的GC主要用于性能测试和内存压力测试场景：比如对比不同GC的分配性能，或在短生命周期应用中避免GC开销。Epsilon不适合实际生产，但提供了一个极端基线。
- `低开销 Heap Profiling`： 引入了一种低开销的堆采样机制，可通过 JVM TI 获取堆上对象分配的信息。这有助于分析内存使用，而对性能影响较小。对于线上问题诊断（内存泄漏分析）会很有帮助。
- `Flight Recorder 开源`： 商业JDK中的 Java Flight Recorder (JFR) 在 Java 11 正式开源纳入OpenJDK。JFR是低开销的性能分析和事件收集工具，与JDK紧密集成。现在所有Java开发者都能使用`-XX:StartFlightRecording`来收集应用运行数据，用于诊断性能瓶颈。它特别适合在生产环境持续监控，因为开销很低。随JFR一起开放的还有Mission Control可视化工具（独立下载）。
- `TLS 1.3`： Java 11 实现了 TLS 1.3 协议，将安全套接字协议升级到最新标准。TLS 1.3 有更简洁的握手过程和更安全的密码套件。对于使用SSL/TLS的Java应用，这意味着开箱即用支持最新安全标准，提升安全性和性能（减少握手延迟）。

## 工具与其他

- **移除和弃用**： Java 11 是一个LTS版本，也移除了不少遗留特性。例如彻底移除了 Java EE 和 CORBA 模块（在Java 9就标记deprecated），包括 `javax.xml.bind`、`javax.ws.rs` 等，这些由独立的Jakarta EE实现替代。还移除了Applet API等过时技术。另外 Nashorn JavaScript 引擎在Java 11被标记为弃用（最终移除于Java 15）。这些变化提示开发者需要从JDK中迁移相应依赖到独立库。
- **Java 命令新选项**： `java` 命令增加了 `--show-version` 等选项，更方便地查看版本。`keytool` 等安全工具也支持更多算法和更方便的选项。

**总结**： 作为长期支持版本，**Java 11 集大成**，巩固了Java 9和10的变化并提供了一些关键的新功能。HttpClient的正式加入填补了长期以来标准库缺乏现代HTTP客户端的空白。一系列细小的API改进（字符串、文件、集合等）提升了日常开发体验。ZGC等革新的GC技术虽然仍是实验性质，但展现了Java在大内存低延迟领域的潜力。Java 11 开源了之前商用的JFR，统一了Oracle JDK和OpenJDK的差异，这对Java生态意义重大。可以说，Java 11 为随后版本的演进打下了稳定基础，也成为许多企业下一步升级的目标版本。

# Java 12 新特性

**发行时间**： 2019 年 3 月

## 语言特性（预览）

- **Switch 表达式 (预览)**： Java 12 对 `switch` 进行了增强，推出了 **Switch 表达式** 作为预览特性。它允许 `switch` 直接返回值并使用简洁的“箭头语法”或`yield`语句，避免了繁琐的`break`。例如，在Java 12中可以这样写：
```java
// 新的switch表达式语法（Java 12+，需 --enable-preview）
int numDays = switch(day) {
    case MON, FRI, SUN -> 6;
    case TUE -> 7;
    case THU, SAT -> 8;
    case WED -> 9;
    // 对于多行的逻辑，可使用 yield 返回值
    default -> {
        System.out.println("Unknown day: " + day);
        yield 0;
    }
};
```
这种语法消除了忘写`break`导致贯穿的风险，每个分支的结果要么用`->`后的表达式，要么使用`yield`语句返回。Switch 表达式使得 `switch` 可用于内嵌在赋值或返回语句中，更加**表达式化。** **应用场景**： 需要根据枚举或常量计算结果的场合会更简洁，例如将老式的 `switch`-`case` 结构转换为一行返回值的表达式。Java 12 此特性需通过`--enable-preview`启用，经过12、13的反馈，最终在Java 14成为正式特性。
- **Instanceof 模式匹配 (预览)**： Java 12 引入了**模式匹配的 instanceof**（同为预览特性）。简化了在进行类型检查后再强制转换的常见模式。新语法允许：
```java
if (obj instanceof String str) {
    // 进入此块则自动完成类型转换，可直接使用 str
    System.out.println(str.toUpperCase());
}
```
这样，无需再写 `(String) obj` 的强转和单独声明变量。这使代码更紧凑，避免了转换错误。**应用场景**： 广泛存在于对参数进行不同类型处理的时候。例如一个 `Object` 可以是多种类型，根据不同类型有不同逻辑，用传统 instanceof 需要繁琐的强转，有了模式匹配就简洁安全得多。Instanceof 模式匹配在Java 16转正。

## 核心库增强

- **String 新方法**： Java 12 为 `String` 添加了两个方便的方法：
- - **String.indent(int n)**：调整字符串每行的缩进。正数n表示在每行前添加n个空格，负数n表示去除每行前最多n个空白字符。这对格式化多行字符串很有用。
- - **String.transform(Function<String,R> f)**：将字符串通过给定的函数转换为另一种对象。这相当于 `f.apply(str)`，只是使调用更流畅，可用于串联调用。例如 `"foo".transform(s -> s + "bar")` 结果是 `"foobar"`。
这些方法提升了处理字符串的便利性。例如，indent配合文本块（在Java 13预览）可以很容易地调整代码或文案的缩进。
- **Files.mismatch**： 在 `java.nio.file.Files` 中新增了 `Files.mismatch(Path, Path)` 方法，用于高效比较两个文件的内容是否相同。它返回第一个不匹配的字节的位置，若返回-1表示文件完全相同。这对比对大型文件很有帮助，利用底层字节比较，可能比逐行读更快。
- **NumberFormat 压缩数字**： `java.text.NumberFormat` 新增了**紧凑数字格式**（Compact Number Formatting）。这允许以“K”“M”等简写方式格式化数字。例如：
```java
NumberFormat fmt = NumberFormat.getCompactNumberInstance(Locale.US, Style.SHORT);
System.out.println(fmt.format(1000));    // 输出 "1K"
System.out.println(fmt.format(1_000_000)); // 输出 "1M"
```
对需要友好展示统计数据的场合很实用，比如在界面上显示“2.3万”这样的格式（中文 Locale 会输出类似“2万3千”）。
- **Collector.Teeing**： Java 12增加了一个很有用的`Collector：Collectors.teeing`，可以让流拆分成两个子流，各自收集后再合并结果。例如可以同时计算平均值和总和。这对于需要一次遍历计算多个结果的情况很方便。

## JVM 与垃圾回收

- **Shenandoah GC**： 由 RedHat 开发的低停顿垃圾收集器 **Shenandoah** 在 Java 12 正式引入（实验性）。Shenandoah 的目标是无论堆多大，GC 停顿都在10ms以内，它通过并发压缩来实现低停顿。Shenandoah 与 ZGC 类似，都是面向低延迟场景，但 Shendandoah 更早在 JDK 8u 上投入生产使用。对主要使用 OpenJDK 8 的企业来说，Shenandoah 提供了一个升级路径。启用参数为`-XX:+UseShenandoahGC`。
- **G1 优化**： Java 12 对默认 GC G1 进行了一些改进。其中包括 JEP 344：可中止的混合收集，使 G1 在达到暂停目标时可以提前终止当前垃圾收集循环；以及 JEP 346：空闲时取消分配堆内存，使 G1 在应用空闲时将未使用的堆内存返还给操作系统。这些改进进一步降低了 G1 的延迟并提高内存使用效率，对于长时间运行且内存使用波动的应用有帮助。

## 工具和其他

- **Microbenchmark Harness (试验)**： Java 12 引入了一个基于 Java 的微基准测试框架（JEP 230），方便进行性能测试。但普通开发者接触较少，该框架事实上就是后来广泛使用的 JMH（Java Microbenchmark Harness）的基础。
- **JVM 常量 API**： 提供了一套新的 `java.lang.invoke.ConstantBootstraps API`，用于在字节码中加载动态常量（JEP 309，在Java 11预览，在Java 12正式）。这对语言实现者或框架来说有用，可以更灵活地处理常量池。

**总结**： Java 12 属于过渡版本，但预示了Java语言几个重要演进方向：Switch表达式和模式匹配都是为了让Java语法更简洁、更强大（这些特性在后续版本陆续定型)。核心库的小改进（字符串indent/transform等）贴近开发者需求，让日常编码更高效。Shenandoah GC 等则体现了 Java 在 GC 领域的持续创新，和 ZGC 一起为低延迟场景提供了解决方案。虽然变化不如大版本明显，但Java 12为后来的Java 13、14继续迭代打下了基础。

# Java 13 新特性

**发行时间**： 2019 年 9 月

## 语言特性（预览）

- **文本块 Text Blocks (预览)**： Java 13 引入了**文本块**作为预览特性。文本块使用三重引号 `"""` 包围多行字符串文字，支持保持代码中的排版格式，大大简化了多行字符串的书写。例如，以往我们需要：
```java
String json = "{\n" +
              "  \"name\": \"Alice\",\n" +
              "  \"age\": 25\n" +
              "}\n";
```
有了文本块，我们可以写成：
```java
String json = """
              {
                  "name": "Alice",
                  "age": 25
              }
              """;
```
以上文本块会自动包含换行符和缩进空格，使字符串内容看起来与源码格式一致。Java 13 的文本块还引入了两个新的转义序列：`\` 作为行结尾时表示忽略改行（连接行）、`\s` 表示空格。文本块显著提高了编写 JSON、HTML、正则、多行日志等字符串的可读性 **（优点）**，避免繁琐的换行符拼接和转义。需要注意文本块会保留缩进，可以用 later Java 14+的 `stripIndent()`方法去除多余缩进。Text Blocks 在Java15转正成为正式特性。
- **Switch 表达式第二次预览**： Java 13 对上一版的Switch表达式进行了改进，主要是引入了 `yield` 关键字来返回值而不是使用`break`。例如：
```java
String result = switch (day) {
    case MON, TUE, WED, THU, FRI:
        yield "Workday";
    case SAT, SUN:
        yield "Weekend";
    default:
        yield "Invalid";
};
```
在Java 12中，使用的是 `->` 箭头和直接返回值或者`break value`形式；Java 13统一改用`yield`关键字提高一致性。这个版本的Switch表达式依旧是预览，直到Java 14才正式定型。

## 核心库与其他

- **ZGC 改进**： Java 13 改善了ZGC，让其在空闲时能够将未使用的堆内存归还操作系统。这解决了之前ZGC不会释放堆的问题，更加“吝啬”地占用内存，从而降低应用的内存足迹。这对容器环境非常有用，当应用内存需求下降时可以把内存还给系统。
- **Socket API 重构**： Java 13 底层重写了传统 **Socket 实现**，引入 `NioSocketImpl` 取代旧的 `PlainSocketImpl`。新的实现使用更现代的机制（如基于 `java.util.concurrent` 的锁），提高了并发性能和可维护性。旧实现如有需要仍可通过系统属性切换回去（`-Djdk.net.usePlainSocketImpl=true`）。**应用场景**： 绝大部分应用无需关注此更改，但套接字通信的稳定性和性能都会从中受益。
- **文件系统API新方法**：在 `java.nio.file.FileSystems` 类中增加了简化从文件创建内存文件系统的几个 `newFileSystem(Path, ...)` 工厂方法。这允许开发者更方便地将 Zip 等文件当作文件系统来操作。这对需要浏览压缩包内容或特殊文件容器的场景更便利。
- **动态 CDS 归档**： Java 13 延伸了在Java 10引入的AppCDS功能，加入了**动态类数据归档**能力。现在不需要提前试跑生成类列表，可以在应用退出时由 JVM 动态地将加载的应用类归档保存。下次启动时读取这个归档即可。这提高了 AppCDS 的易用性，无需人为干预生成类列表 **（优点）**，让更多应用能够直接受益于共享类数据带来的启动性能提升。

## 工具和移除

- **JDK 13 没有大的工具变化**。值得注意的是，从JDK 13开始，Java不再内置部署栈（Java Web Start在JDK 11就移除，Applet在JDK 11弃用），所以在桌面和浏览器部署方面Java逐渐淡出，更多聚焦在后端和嵌入式场景。

**总结**： Java 13 延续了预览新特性的打磨，文本块让多行字符串处理在Java中首次变得愉悦；Switch表达式朝着最终定稿又迈进一步。虽然没有正式定稿的新语法，但这些预览特性在社区中引起了极大兴趣。底层方面，Socket API 的重构和ZGC的完善提高了性能和资源利用率。Java 13 的新特性数量相对不多，但“麻雀虽小五脏俱全”，为随后Java 14的大量新功能铺垫了环境。

# Java 14 新特性

**发行时间**： 2020 年 3 月

## JVM 改进

- **空指针异常详细提示**： Java 14 对长期困扰开发者的 NullPointerException进行了改进。当发生NPE时，错误信息现在会指出**具体哪个变量为空**。例如：
```java
// 假设 a、b 可能为空
a.b.c.i = 99;
```
之前的异常信息只是 “NullPointerException at … 第5行”，现在则会提示类似 “Cannot read field ‘c’ because ‘a.b’ is null”。这个更详尽的消息让开发者立刻知道空指针的原因，大幅减少了排查时间 **（优点）**。该功能通过 JVM 参数 `-XX:+ShowCodeDetailsInExceptionMessages` 打开（在Java 14中默认关闭，在Java 15中成为默认开启）。

## 语言特性

- **Switch 表达式正式推出**： 经过两个版本的预览，**增强型 switch** 在 Java 14 正式成为 Java 语言的一部分。现在无需任何预览标志，就可以使用前述的箭头语法和 `yield` 来编写 switch 表达式了。例如：
```java
String label = switch (day) {
    case "M", "W", "F" -> "MWF";
    case "T", "TH", "S" -> "TTS";
    default -> {
        if(day.isEmpty()) yield "Please insert a valid day.";
        else yield "Looks like a Sunday.";
    }
};
System.out.println(label);
```
在这个例子里，多个 case 可以用逗号合并（如 “M”, “W”, “F”），`default` 分支里演示了多语句块如何使用 `yield` 返回值。Switch 表达式相比传统 switch 简洁且更安全，避免了遗忘 break 的错误。它还能直接用作表达式赋值或返回，大大增强了 Java 表达能力。
- **Records（预览）**： Java 14 引入了一种全新的类型声明：**记录类**（Record），作为预览特性。Record是一种**浅不可变**的数据载体类，它可以用简洁的语法声明，不必编写样板代码。例如：
```java
public record Point(int x, int y) { }
```
编译器将为 `Point` 自动生成构造器、`x()`/`y()`访问器方法、`equals()`、`hashCode()` 和 `toString()`。所有字段默认是 `private final`，Record类自身被隐式声明为 `final`（不可子类化）。Record非常适合表示纯数据，如坐标点、范围、DTO等。它极大减少了冗余代码，提高了可读性，相当于Java内置了 Lombok 的 `@Data` 功能。**应用场景**： 用于值对象，特别是在API间传输数据的时候，使代码更简洁清晰。Record 在Java 16成为正式特性。
- **文本块（第二次预览）**： 文本块在Java 14继续预览，引入了新的转义：`\`（行尾忽略换行）和 `\s`（显式空格）。这些在Java 13就已加入预览。Java 14文本块的主要变化是针对前一轮反馈进行调整，比如结尾处的换行处理等。总之，文本块在这一版依然是预览，但已经相当成熟，最终在Java 15转正。
- **instanceof 模式匹配（第二次预览）**： Java 14 中，instanceof 模式匹配作为预览再次出现，没有语法变化，仅继续收集反馈。开发者已可熟练使用 `if(obj instanceof Type var)` 这种写法，直到Java 16成为正式特性。

## 核心库和工具

- **移除过时的CMS GC**： 并发标记清除（CMS）垃圾收集器自Java 9起弃用后，终于在Java 14中**移除**。CMS 曾经是低停顿GC的主力，但有新一代的G1、Shenandoah、ZGC替代。移除CMS可以减轻维护负担。对于仍在使用CMS的应用，需要转向其他GC（通常转G1）。
- **ZGC 扩展到 macOS/Windows**： Java 14 将ZGC从仅支持Linux扩展到了 macOS 和 Windows 平台。这意味着更多用户可以在各种主流系统上试验ZGC的低延迟特性 **（优点）**。也标志着ZGC逐渐成熟，不再局限于单一平台。
- **jpackage 工具（孵化）**： 提供了 `jpackage` 工具的早期版本，可将Java应用打包成原生安装包（exe、msi、pkg、deb等）。这对于需要交付桌面应用的场景很有价值，开发者可以直接生成包含运行时的安装程序。jpackage 在JDK 16转为正式。

## 安全和其他

- **Edwards-Curve 数字签名算法**： Java 15（而非14）才加入EdDSA，但在Java 14时已在着手了。Java 14主要安全改进体现在对TLS、加密库的细节修复，没有显著的API变化。

**总结**： Java 14 是一个内容相当丰富的版本。**Switch表达式**终于定型、**记录类**和**模式匹配**开始崭露头角。这些语言层面的增强让Java变得更简洁和富有表达力，逐步摆脱“样板代码多”的诟病。尽管Record和模式匹配仍是预览，但开发者已经可以尝鲜感受到它们的魅力。核心库方面，本版本改动不大，但像文本块等继续改进。JVM则在整理历史包袱（移除CMS）和推广新GC（ZGC跨平台）上迈进。总的来说，Java 14标志着Java语言在保持稳定性的同时，开始大胆引入新语法，为现代应用需求提供更优雅的解决方案。

# Java 15 新特性

**发行时间**： 2020 年 9 月

## 核心语言特性

- **文本块正式发布**： 经过两次预览，**Text Blocks** 在 Java 15 成为正式特性。现在多行字符串文字可以不加任何标志直接在代码中使用三重引号表示。与预览阶段相比，Java 15 的文本块已经非常稳定，之前提到的 `stripIndent()`、`translateEscapes()` 等辅助方法也都正式随之提供。
- **密封类（预览）**： Java 15 引入了 **密封类** 和 **密封接口**（Sealed Classes）作为预览特性。密封类允许开发者限制哪些子类可以继承它。使用 `sealed` 修饰类，并在类声明后使用 `permits 子类列表` 来显式列出允许继承的子类：
```java
public sealed class Person permits Employee, Manager {
    // ...
}
public final class Employee extends Person { ... }
public non-sealed class Manager extends Person { ... }
```
在上例中，`Person` 这个密封类只允许有 `Employee` 和 `Manager` 两个子类。而这两个子类必须要么声明为 `final` 完全封闭继承（如Employee），要么继续声明为 `sealed`（列出下一层许可继承），或者声明为 `non-sealed` 表示开放继承（如Manager，不再受限制）。密封类的好处是可以严格限定继承层次，确保代码覆盖时知道所有可能的子类，有助于模式匹配等特性的穷尽性检查。**应用场景**： 枚举类型的扩展，当枚举不适用时，可以用密封类+模式匹配代替；或者框架定义接口只允许特定实现等。密封类提高了系统建模的精确性。它在Java 17正式成为语言特性。
- **隐藏类（Hidden Classes）**： Java 15 加入了一种专门面向框架、JVM内部使用的类加载功能：Hidden Classes。隐藏类是一些在运行时动态生成的类，它们不可见于外部，也不能通过普通反射获取，主要用于字节码框架生成代理类、动态语言实现等场景。使用 MethodHandles.Lookup 定义隐藏类后，可避免污染应用的类命名空间。普通应用开发者可能感觉不到这个特性，但像动态代理、GraalVM多语言支持都会受益于此，更加安全。

## 核心库与安全

- **新增 CharSequence.isEmpty()**： 在 Java 15，`CharSequence` 接口添加了默认方法 `isEmpty()`。这使得所有实现了 CharSequence 的类（包括 String、StringBuilder等）都自动拥有了 `isEmpty()` 方法。以往我们只能用 `seq.length() == 0` 判断，现在调用更直观。类似地，`Collection`接口早有 `isEmpty()` 方法，如今字符串序列接口也统一了这个用法。
- **增强 TreeMap**： Java 15 为 `java.util.TreeMap` 增补了多个常用方法：`putIfAbsent`, `computeIfAbsent`, `computeIfPresent`, `compute`, `merge`。过去这些方法只在 `HashMap` 等中有，实现为直接调用这些接口的默认实现，现在 TreeMap 提供了自身优化实现。这使得使用 TreeMap 时也能方便地进行条件插入和合并操作，Collections API 更加一致。
- **新的数字签名算法 EdDSA**： Java 15 实现了 Edwards-Curve 数字签名算法（EdDSA）。它是一种现代的椭圆曲线签名方案，相比 ECDSA 算法，性能更好且安全性高（抗强力破解能力强）。Java 15 内置支持 Ed25519 和 Ed448 曲线，可以通过 `"Ed25519"` 算法名称使用。例如：
```java
KeyPairGenerator kpg = KeyPairGenerator.getInstance("Ed25519");
KeyPair kp = kpg.generateKeyPair();
Signature sig = Signature.getInstance("Ed25519");
sig.initSign(kp.getPrivate());
sig.update(data);
byte[] signature = sig.sign();
```
这将产生一个 Ed25519 签名。EdDSA 的加入让Java标准库紧跟加密领域前沿，为需要高性能签名（如区块链、JWT）的应用提供了新选择。

## JVM 和性能

- **ZGC 转正**： ZGC 在 Java 15 终于结束了实验状态，变为生产可用的垃圾收集器。虽然默认GC仍是G1，但现在可以放心地在生产环境使用ZGC（通过`-XX:+UseZGC`启用）来获取低延迟优势。同时，Java 15 的ZGC已支持多平台并修复了早期问题，日趋成熟。应用场景： 针对超低延迟要求的服务或大内存应用，可以考虑尝试ZGC并调优。需要注意的是，ZGC此时仍非默认，意味对普通场景还是G1更通用，而ZGC提供特殊场景选项。
- **弃用 Nashorn**： Java 15 正式移除了 Nashorn JavaScript 引擎（在Java 11就标记了弃用）。由于JavaScript流行生态(如Node.js)已在JVM之外发展成熟，Nashorn的使用率和维护价值下降。今后在JVM内运行JS需要使用独立项目（如GraalJS）。这提醒开发者：内嵌脚本功能应逐步迁移到新的解决方案上。

## 预览/非正式特性

- **记录类第二次预览**： Record 在 Java 15 继续预览，做了一些改进比如允许局部类中定义Record等。语法基本维持不变，为最终转正做最后准备。
- **模式匹配 instanceof 第二次预览**： 也基本保持不变，只收集更多使用反馈。

**总结**： Java 15 虽然是短期版本，但特性相当丰富。**文本块**在这一版终于尘埃落定，使多行字符串处理不再繁琐。**密封类**的引入让Java的类型系统更加强大，配合记录类、pattern matching，Java正朝着模式匹配和代数数据类型的方向迈进。库方面小幅增强了集合、字符序列、密码学算法。ZGC成熟和Nashorn移除则反映了JVM内部技术迭代。对于开发者来说，Java 15 提供了更多工具来编写简洁、安全、高性能的代码，是一款值得关注的版本。

# Java 16 新特性

**发行时间**： 2021 年 3 月

## 语言特性

- **Records（记录类）正式发布**： Java 16 将**记录类**从预览转为正式特性。开发者可以不用任何额外开关，直接使用 `record` 关键字定义不可变数据类。如：
```java
public record Point(int x, int y) { }
```
编译器自动生成构造器、getter（以字段名为方法名）、`equals/hashCode`、`toString` 等。相比Java中的普通类，Record极大减少了样板代码，并且语义明确地表示这是一个值类型。值得注意的是，Java 16 对Record作了一些调整：允许**内部类**定义Record，并支持在接口中定义静态Record嵌套类等。**应用场景**： Record非常适合作为数据传输对象（DTO）、只读配置类等。例如在 Spring MVC 中，一个请求的响应可以直接用Record来建模，由于其自带`toString`/`equals`，打印日志和比较都方便许多。大量原本需写构造器和getter的类现在一行就搞定，开发效率和代码可读性大幅提升。
- **模式匹配的 instanceof 正式发布**： Java 16 将前几版预览的 **instanceof 模式匹配** 特性定型发布。现在，`if (obj instanceof String s)` 成为正式语法，`s` 变量的作用域在该 `if` 分支内有效，类型自动转换为 String。与预览版相比，唯一语义改动是模式变量不再隐式是 `final` 的（Java 16 起可以修改 `s` 的引用）。**应用场景**： 几乎所有需要类型检查再强转的地方都能用这特性简化。例如：
```java
Object obj = ...;
if (obj instanceof Integer data) {
    System.out.println(data + 1); // 直接使用 data，无需强转
}
```
省去了典型的模板代码，提高了代码安全性（不易出错）和可读性。
- **密封类第二次预览**： Java 16 再次提供了 sealed classes 的预览，主要改进了编译器对于密封继承关系的一些检查，更加严格地确保密封约束。语法层面与Java 15类似。该特性在Java 17成为正式。

## 核心库增强

- **Vector API (孵化)**： Java 16 引入了一个全新的孵化模块 —— **向量API**。它提供了在Java代码中使用 SIMD 指令进行向量化计算的能力，可显著提升数据并行处理性能。Vector API 以 `jdk.incubator.vector` 模块提供，包含向量算术、掩码操作等。示例：使用 Vector API 计算两个浮点数组和：
```java
FloatVector v1 = FloatVector.fromArray(FloatVector.SPECIES_256, arr1, 0);
FloatVector v2 = FloatVector.fromArray(FloatVector.SPECIES_256, arr2, 0);
FloatVector vSum = v1.add(v2);
vSum.intoArray(result, 0);
```
这利用CPU的SIMD指令实现了并行加法。虽然Vector API 对一般应用不是直接可见的变化，但对数值计算、高性能应用来说是个重要工具。它在Java 20已孵化到第5次。
- **Foreign Memory Access API (孵化)**： 继Java 14/15 的外部函数API探索后，Java 16 提供了 **外部内存访问 API** 的第三次孵化。这个 API 提供了安全访问堆外内存的方法，包括 `MemorySegment`（表示一段内存）和 `MemoryAddress` 等。与 JNI 不同，它完全在 Java 层面操纵内存，受语言安全检查，可替代 `sun.misc.Unsafe` 的很多用途。在Java 16，此API仍需加入`--add-modules jdk.incubator.foreign`使用，但它是 Project Panama 的一部分，最终在Java 17预览、Java 19预览，Java 21正式推出 (JEP 442)。**应用场景**： 需要与本地内存交互的高性能代码，如调用本地数据库缓存、跨语言共享内存等，可以使用该API避免C代码，提升安全性和开发效率。
- **JDK 内部 API 强封装**： Java 16 开启了对**内部API强封装** 的最后一步。早在Java 9模块化时，JDK内部非导出包就不对外开放，但当时提供了 `--illegal-access=permit` 默认打开非法访问用于兼容旧程序。Java 16 中，这个默认变成 `deny`，即默认完全禁止不合法的反射访问内部API（如 `sun.*` 包），曾经的警告现在变成报错。这可能导致旧库在未调整下无法运行，需要开发者明确使用 `--add-opens` 打开特定内部包才能继续。这一步骤强调了使用标准API的重要性，也敦促生态完成向模块化的过渡。
- **其它小改进**：
- - `java.nio.channels` 包现在支持 **Unix 域套接字** 连接（JEP 380），包括在Windows上也能使用这种本地IPC通信。方便进程间高效通信。
- - 新的 `java.net.InetAddress` 实现替换了旧的 Inet4Address`/`Inet6Address 双实现，使代码更简洁，DNS解析SPI（在Java 18实现）。
- - Stream API增加了 `Stream.toList()` 默认方法，这是个便利方法，效果等同于 `.collect(Collectors.toList())` 但返回不可修改列表。这样获取流结果更简洁。

## 工具与 JVM

- **jpackage 工具正式发布**： 之前孵化的 jpackage 在 Java 16 正式加入 `java.tool` 工具集。开发者现在可以用 jpackage 将应用打包为平台原生安装包，支持Windows的 msi/exe、macOS的 pkg、Linux的 deb/rpm 等。它还能将应用所需的模块一并打包（用jlink技术），让用户无需安装Java即可运行。**应用场景**： 制作桌面应用发行版时，jpackage一站式解决打包和自带JRE的问题，替代了过去需借助Install4j等第三方工具的局面。
- **迁移至 Git/GitHub**： Java 16 完成了 OpenJDK 源码从 Mercurial 仓库迁移到 Git/GitHub 的流程。这虽然对使用者无直接影响，但标志着Java社区融入更广泛的开源协作平台，降低了参与门槛，也加速了开发。比如现在可以方便地在GitHub浏览JDK源码、提交PR。
- **Alpine/Linux AArch64 移植**： Java 16 官方支持在 Alpine Linux（musl C库）以及 Windows/AArch64 平台上的运行。这意味着对轻量容器和 ARM 服务器的支持更完善。对于在这些环境部署Java应用，这是利好消息，比如可以直接使用OpenJDK 16跑在 Alpine 容器中而无需传统glibc兼容层。

**总结**： Java 16 是一个重要的**过渡版本**。它完成了若干预览特性的正化（Records, 模式匹配）和JDK内部重构（强封装），使Java语言和平台更加现代安全。记录类的加入改变了Java定义数据结构的习惯，大幅减少样板代码，受到开发者欢迎。与此同时，Java 16 在高性能计算领域布局：Vector API和外部内存API的孵化，为Java迈向系统编程领域铺平道路。对于一般开发者，Java 16的直接提升在于更简洁的代码和更一致的API，而对高级用户，则看到了Java在性能和底层操作上的野心。总的来说，Java 16继续平稳演进，为即将到来的下一个LTS版本(Java 17)做好了准备。

# Java 17 新特性

**发行时间**： 2021 年 9 月 14 日 （LTS长期支持版）

## 语言特性

- **密封类（正式）**： 继两轮预览后，**Sealed Classes**在Java 17正式成为语言特性。现在可以用 `sealed` 修饰类或接口，并用 `permits` 子句列出允许的子类/实现类。所有继承者必须是列出的类型，否则编译报错；而继承者本身也需显式声明为 `final`、`sealed` 或 `non-sealed`。密封类使得类层次结构变得**封闭且可预测**。**应用场景**：需要控制继承的场景，如安全框架只希望特定子类，否则抛错；或者用密封接口加模式匹配，可以在编译期检查匹配是否穷尽所有实现。例如：
```java
sealed interface Shape permits Circle, Rectangle, Square { }
final class Circle implements Shape { }
final class Rectangle implements Shape { }
final class Square implements Shape { }
```
以上接口只有这三种实现，未来也不可能出现第4种，实现了逻辑上的完备性。
- **Switch 模式匹配（预览）**： Java 17 提供了 **switch 的模式匹配** 作为预览特性（JEP 406）。它扩展了 switch，可以直接对类型进行匹配。结合前述密封类，可以在 switch 的 case 中使用类型模式。例如：
```java
static String formatShape(Shape s) {
    return switch(s) {
        case Circle c    -> "Circle radius=" + c.radius();
        case Rectangle r -> "Rectangle w=" + r.width();
        case Square sq   -> "Square side=" + sq.side();
        default          -> "Unknown shape";
    };
}
```
在这个预览特性中，`switch` 的 case 可以是带变量的类型（如 `Circle c`），匹配成功则自动将 s 转型为对应类型绑定到 c。这是模式匹配在 switch 上的首次尝试。对于密封类，编译器还能检查 default 分支是否必要（如上例如穷尽所有子类，可省略default）。Switch模式匹配让多态处理更加简洁强大，不过该特性在Java 17仅预览，最终于Java 19正式发布。

## 核心库

- **增强的伪随机数生成器**： Java 17 通过 JEP 356 引入了一系列新的 **随机数生成器接口和实现**。主要包括：
- - 新接口 `RandomGenerator` 统一了随机数类的抽象，`java.util.Random`、`SplittableRandom`、`ThreadLocalRandom` 都实现了该接口。
- - 提供了多种新算法实现，如`Xoroshiro128Plus`, `SplitMix64`, `L128X256MixRandom` 等，放在 `java.util.random` 包下，它们各有特点，性能和随机质量较传统 Random 更好。
- - 增加了`RandomGeneratorFactory`，可以枚举和创建不同算法的随机数生成器。
**应用场景**： 科学计算、仿真、游戏等需要高质量随机数的领域，可以直接使用这些新实现。例如：
```java
RandomGenerator rand = RandomGenerator.of("L128X256MixRandom");
int n = rand.nextInt();
```
这样获取的随机数在统计质量和速度上都会优于传统的 `java.util.Random`。此外统一的接口让代码更灵活，可以在不改变代码逻辑情况下切换不同生成器算法。
- **跨平台渲染管线**： 针对 macOS 平台，JEP 382 引入了基于 Metal 的 Java 2D 渲染管线替代原先的 OpenGL 管线。这样在Apple弃用OpenGL后，Java的GUI渲染还能继续高效工作。这对使用 Swing/JavaFX 的桌面应用非常重要，不过对服务器开发无直接影响。
- **弃用安全管理器**： Java 17 将久未更新的 **Security Manager** 标记为弃用，将来版本中会移除（JEP 411）。安全管理器曾用于限制Java代码权限（沙箱机制），但由于设计过于复杂且很少使用，现在决定废弃。后续如果需要细粒度安全控制，会采用更现代的技术（如基于容器的隔离）。开发者需要注意，某些依赖安全管理器的库（例如一些老的测库或Applets相关代码）未来可能无法使用，需要及早寻找替代方案。**Java 24 中已完全禁止启用Security Manager。**
- **移除 RMI 激活机制**： Java 17 删除了远程方法调用（RMI）中几乎不用的**激活机制**（JEP 407）。RMI Activation 允许远程对象按需启动，但现实中少有用到且存在维护成本，故予以删除。普通的RMI功能仍可用，不受影响。
- **context-specific Deserialization Filters**： 提供了针对反序列化过程的新过滤API（JEP 415），允许在特定上下文设置反序列化过滤规则，从而防御反序列化漏洞。比如可以针对某次ObjectInputStream限定可接受类的白名单，增强安全性。这对于开发需要反序列化不受信数据的应用非常重要，是Java安全加固的一部分。

## 性能与内部

- **永久性强封装 JDK 内部**： 上文Java 16部分提到，Java 17 完成了内部 API 封装的最后工作，将非法反射访问默认禁止。因此许多以前打印警告的信息在Java 17下会直接报错退出。这要求各种框架升级以使用官方支持的API。例如ByteBuddy、cglib之类都已发布新版适配，否则可能无法在Java 17运行。如果遇到因无法访问`sun.misc`等内部类而报错，可通过`--add-opens`暂时开放对应模块包给相关库，但这只是过渡方案。
- **移除实验性 AOT/JIT 编译器**： Java 17移除了JDK 9引入的实验**AOT编译器**（jaotc）和**JIT编译器Graal**（JEP 410）。这些功能在实验阶段使用不广泛，并决定通过外部项目（如GraаlVM）继续发展，而不放在JDK中了。对大多数用户没有影响，因为默认HotSpot C1/C2编译器仍保留且性能良好。

## 适配与生态

作为LTS版本，Java 17 得到了各大框架和库的快速支持。Spring Boot 3 就要求最低Java 17运行。相较Java 11，Java 17的代码可读性更好（Record, Pattern Matching等）并且性能有所提升（如更好的GC选择和更优的随机数生成器）。迁移到Java 17需要注意以下：
- 检查并替换对内部API的非法调用，或在启动脚本中加入对应`--add-opens`参数以保持兼容。
- 确认所用三方库已兼容Java 17（多数流行库如Netty、Spring等都已支持）。
- 充分利用新特性提升代码质量，如用Record代替冗长的POJO，密封类约束继承关系等。

**总结**： Java 17 是继Java 11之后的又一个长期支持版本，也是“现代Java”功能集的大成者。密封类、Record、Pattern Matching这些Java近年推出的语法糖在此全部稳固下来。它极大地提高了Java的开发效率和表达力，让Java代码更加简洁、类型更加安全可控。在JDK底层，Java 17 清理了许多历史遗留（如安全管理器、老的RMI子系统等），并优化了Randome API等基础库。对于计划长期使用的项目，Java 17 无疑是一个理想的选择。Java 17发布后，Java社区进入半年发布的新常态，但有了LTS保障，企业也能每隔几年来一次平滑升级以享受新特性红利。

# Java 18 新特性

**发行时间**： 2022 年 3 月

## 平台与性能

- **默认字符集 UTF-8**： Java 18 通过 JEP 400 将**默认字符集**统一为 UTF-8。之前，`Charset.defaultCharset()` 会根据操作系统locale返回本地编码（例如中文Windows通常是GBK），这可能导致跨平台不一致的问题。Java 18 起，无论在哪运行，默认Charset一律是UTF-8。这意味着不指定编码时（如使用 `FileReader` 默认构造）都以UTF-8读写文件。这对多语言应用、跨平台程序是重大利好，避免了常见的乱码问题 **（优点）**。但需要注意如果有程序依赖以前平台默认编码，需要显式指定回原编码，否则可能行为改变。
- **简单的Web服务器**： JDK 18 内置了一个简单的纯Java实现**HTTP文件服务器**。只需运行命令 `jwebserver` 即可在当前目录启动一个静态文件服务，默认监听本地8000端口。这个Web服务器仅支持静态文件，不支持CGI、Servlet等动态内容，但非常适合临时共享文件或前端开发进行快速测试。开发者也可以通过 API (`com.sun.net.httpserver.SimpleFileServer`) 在自己的应用中启动一个文件服务器实例。**应用场景**： 例如要快速查看某个HTML文件效果，只需 `jwebserver` 即可，不必安装额外软件。
- **核心类重构（MethodHandle实现）**： JEP 416 用 Method Handle 重写了 Java 核心反射的部分实现。原先诸如 `Class::forName`、`Method::invoke` 等底层由JVM C++代码处理，现在部分改由Java实现，以提升维护性和可能的性能。这一改动对开发者透明，行为没有变化，但体现出OpenJDK渐进用更高级方式优化底层的思路。

## 新特性和API

- **代码段（Snippet）标签 for JavaDoc**： JEP 413 为 JavaDoc 文档引入了 `<pre><code>` 风格的**代码片段注释**。开发者可以在注释中使用 ``\`java 标记和 `{@snippet}` 等标签来插入代码示例，JavaDoc 会自动高亮和编号这些代码。这比以前需要手工使用HTML `<pre>` 标记更方便，也减少了转义的麻烦。对于撰写API文档的开发者来说，这提高了文档可维护性和可读性。
- **Vector API 第三次孵化**： Java 18 中 Vector API 进入第3轮孵化。相比Java 16版有一些性能和API优化。依然需要`--add-modules jdk.incubator.vector`使用。值得一提的是，随着孵化次数增加，Vector API 正趋于成熟，目标是实现CPU SIMD指令可被Java程序员直接利用以获得本地性能。
- **互联网地址解析 SPI**： JEP 418 引入了一个可插拔的**名称解析服务接口**。这允许应用替换JDK默认的DNS解析器，例如使用自定义DNS服务器或实现特殊解析规则。对大多数应用而言用不到，但在一些网络隔离或自定义解析环境很有用，比如将Java应用的DNS解析定向到应用内部服务。
- **外部函数 & 内存 API 第二次孵化**：Java 18 提供了Panama项目 **Foreign Function & Memory API** 的第二版孵化 (JEP 419)。它包括 `MemorySegment`、`MemoryAddress`、`CLinker` 等，继续让Java可以更安全地访问本地内存并调用本地函数。和Java 17里的Incubator相比，这次孵化进一步完善了API设计。虽然仍非正式，但已经有不少开发者尝试用它调用本地C库而不用JNI。随着这一API的成熟，Java有望在后续版本里跨入系统编程领域，该API最终在Java 21正式发布。
- **Switch 模式匹配第二次预览**：跟随Java 17的首次预览，Java 18 的 JEP 420 给出了**switch 模式匹配**的第二次预览，实现上无大变化，只是根据反馈调整了一些细节。例如，在增强 Exhaustiveness（穷尽检查）方面有所改进。当使用密封类时，编译器能更好地确定是否需要 default 分支。这项特性最终在Java 19完成预览并在Java 21正式推出。
- **弃用终结器 Finalization**：虽然Java 9开始就不推荐使用 finalize() 方法做清理操作，但直到Java 18 才通过 JEP 421 正式将终结器标记为废弃以移除。未来的Java版本将彻底移除终结器机制，转而推荐 Cleaner 等更可靠的清理方式。终结器由于不可预知的执行时机和可能的性能、安全问题，一直被认为是不良实践，此举督促开发者尽早移除 finalize 的用法。

## 安全与密码

- **默认禁止弱算法**： Java 18 在安全方面也做了一些更新，例如禁用了 TLS 1.0 和 1.1 协议默认支持、更严格的默认信任库等。这些变更虽不显著但体现了Java平台安全策略与时俱进。

**总结**： Java 18 新特性相对较少，而且很多是预览或孵化（Vector、外部内存、switch模式）。最大的“显性”变化对普通开发者来说莫过于**默认编码UTF-8和内置简易Web服务器**。UTF-8默认消除了长期以来跨平台编码不一致的问题，让Java更贴合互联网时代的数据交换标准。jwebserver则体现出Java对开发者体验的重视，即使是一个很小的工具，也能发挥作用。在底层性能上，Java 18 继续推进Panama和Vector等，使Java在系统编程和高性能计算上更具竞争力。作为非LTS版本，Java 18 提供了一个让社区试水新功能的平台，其反馈将作用于后续的Java 19和21中。

# Java 19 新特性

**发行时间**： 2022 年 9 月

## 并发与虚拟线程

- **虚拟线程（预览）**： Java 19 带来了备受期待的 **虚拟线程**（Virtual Threads）预览（JEP 425）。虚拟线程是由JVM管理的轻量级线程，实现了“纤程”的概念，每个虚拟线程由**多个虚拟线程映射到一个OS线程**执行，调度由JVM负责。创建虚拟线程的成本和内存占用都非常低，可以轻松创建数十万计线程而不会像平台线程那样耗尽资源**（优点）**。使用方式上，Java 19 提供了简化的 API，例如：
```java
Thread.startVirtualThread(() -> {
    // 虚拟线程执行的代码
    System.out.println("Hello from a virtual thread");
});
```
或通过 `Executors.newVirtualThreadPerTaskExecutor()` 创建虚拟线程的执行器。对于IO阻塞操作，虚拟线程在等待时会让出底层OS线程，不会“固定”占用它。这意味着高并发IO场景下，使用虚拟线程可以大幅提升吞吐，而编程模型仍然是简单的同步代码，不需要使用复杂的Async框架。**应用场景**： 特别适合服务器端处理大量并发连接的场景（如Web服务器、聊天服务器），过去用线程池+异步，现在可以一请求一线程且线程数非常多却无明显性能损失。虚拟线程在Java 19为预览，需要 `--enable-preview` 开启，并在Java 21正式发布（JEP 444）。
- **结构化并发（孵化）**： 随着虚拟线程引入，Java 19 还孵化了 **结构化并发 API**（Structured Concurrency，JEP 428）。它提供 `StructuredTaskScope` 类，帮助把一组关联的任务提交到多个线程并汇总结果，方便以结构化的方式启动并行操作并在作用域结束时自动管理线程生命周期。例如：
```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Future<String> user = scope.fork(() -> fetchUser());
    Future<String> order = scope.fork(() -> fetchOrder());
    scope.join();           // 等待所有任务完成
    scope.throwIfFailed();  // 若有任务异常则抛出
    // 获取结果
    String userInfo = user.resultNow();
    String orderInfo = order.resultNow();
}
```
这样的模式使得并行任务像局部代码块一样管理，有助于避免遗留线程无法控制的问题。这一API仍在孵化阶段（需显式加入 `jdk.incubator.concurrent`），最终目标是简化多线程代码的组织，提高可维护性。

## 语言和模式匹配

- **记录模式（预览）**： Java 19 引入 **Record Patterns** 预览（JEP 405）。它允许在模式匹配中对 **记录类** 进行解构。比如有记录类 `Point(int x, int y)`，可以这样匹配：
```java
Object obj = new Point(3, 5);
if (obj instanceof Point(int x, int y)) {
    System.out.println("x=" + x + ", y=" + y);
}
```
这里`instanceof Point(int x, int y)` 就是记录模式，它不仅判断 obj 是否为 Point，还进一步将内部的 x,y 解构出来赋给新的局部变量。Record Patterns 还可以嵌套使用，用于复杂结构的匹配。**应用场景**： 配合密封类和switch，可以用非常简洁的代码处理递归数据结构或组合数据。例如匹配一个包含两个点的 Line 记录：`case Line(Point(int x1, int y1), Point(int x2, int y2)) -> ...`。记录模式在Java 19为预览，Java 20进行了第二次预览，Java 21正式发布。
- **Switch 模式匹配第三次预览**： Java 19的switch模式匹配（JEP 427）进入第3轮预览。此次主要是与record模式更好地联动。例如可以在switch的case中使用记录模式、类型模式等组合匹配。此外，它根据之前反馈调整了一些细节，如guarded patterns的语法。总之，Java 19 的 switch 模式匹配已经相当成熟，为Java 21的正式上线奠定了基础。

## 外部接口和内存

- **外部函数与内存 API（预览）**： 前述Panama项目在Java 19终于进入预览阶段（JEP 424），意味着`Foreign Function & Memory API`可不带孵化模块直接使用（需启用预览）。它包括：
- -  `MemorySegment`/`MemoryAddress`：操作本地内存。
- - `CLinker`：用于链接C语言函数，支持将Java方法转换为函数指针、将本地函数符号加载为MethodHandle等。
- - `SegmentAllocator`：方便分配本地内存段。
通过这套API，Java 程序可以高效、类型安全地调用本地C函数和读写本地内存，不必使用JNI。例如：
```java
CLinker linker = CLinker.systemCLinker();
MethodHandle strlen = linker.downcallHandle(
        linker.lookup("strlen").get(), 
        FunctionDescriptor.of(ValueLayout.JAVA_LONG, ValueLayout.ADDRESS)
);
MemorySegment cString = CLinker.toCString("hello");
long len = (long) strlen.invokeExact(cString.address());
```
以上代码通过 CLinker 调用标准C函数 `strlen` 计算字符串长度。可以看到没有一行JNI代码，全部在Java中完成。这个特性对于需要和C库交互的应用来说极为便利 **（优点）**，性能也与JNI相当。经过Java 19、20两轮预览，最终在Java 21正式发布 (JEP 442)。

## 其他改进

- **虚拟线程Pinning问题优化**： Java 19 虚拟线程预览中已经实现了当虚拟线程在 `synchronized` 块中等待时，不会阻塞底层OS线程，可以提升并发度。不过更完善的非Pinning设计在Java 24（JEP 491）才完成。Java 19作为预览已经展示了虚拟线程良好的调度特性。
- **Linux/RISC-V 移植**： JEP 422 将OpenJDK移植到了Linux/RISC-V架构上。这对国内自主硬件生态是个好消息，Java可以运行在RISC-V服务器/设备上了。

**总结**： Java 19是一个亮点颇多的版本。**虚拟线程**的初次亮相标志着Java并发模型迎来巨大变革；**结构化并发**、**记录模式** 等则完善了并发和模式匹配的语法，使得Java代码能够写得更简洁清晰。外部函数/内存API的预览，则让Java开始真正涉足系统级编程。尽管这些重要特性多数仍在预览/孵化，但Java 19作为LTS之前的一个功能集合，已经让社区看到了Java未来的样子：**高并发、高性能、强大的模式匹配和数据表达能力**。对于愿意尝鲜的开发者，Java 19提供了极好的机会在实验环境试用这些新功能，并为迁移到Java 21LTS做技术准备。

# Java 20 新特性

**发行时间**： 2023 年 3 月

## 项目 Loom 持续改进

- **虚拟线程第二次预览**： Java 20 再次提供虚拟线程预览（JEP 436）。与Java 19相比改进了调试和JDK工具对虚拟线程的支持，并解决了一些bug。API基本不变。值得注意的是，结合虚拟线程的监控/分析工具也逐步更新，使得即使百万级线程的应用也能被有效诊断。Java 20 的虚拟线程已经非常接近最终形态（最终在Java 21正式推出）。
- **结构化并发第二次孵化**：Java 20 将结构化并发 API (StructuredTaskScope 等) 进行第二轮孵化（JEP 437）。本次主要是API调整和性能优化。开发者继续可以尝试用它来管理一组并行任务的范围，写出更整洁的并发代码。
- **作用域值（孵化）**： Java 20 引入了 **Scoped Values**（作用域值）孵化特性（JEP 429）。它提供了一种比 ThreadLocal 更安全高效的跨线程传递只读数据的方法。用 `ScopedValue` 可以将一个值绑定到当前线程（及其子线程）的动态作用域中，然后在这个作用域内的任意深度方法调用甚至新启动的线程中读取该值。例如：
```java
public static final ScopedValue<String> USER_ID = ScopedValue.newInstance();
// 在某作用域绑定 USER_ID
ScopedValue.where(USER_ID, "alice").run(() -> {
    // 在作用域内的任意代码都可读取 USER_ID
    processOrder();
});
void processOrder() {
    String uid = USER_ID.get();  // 获取当前作用域绑定的值 "alice"
    ...
}
```
相比 ThreadLocal，ScopedValue 的生命周期和线程结构更加明确，不会发生内存泄漏，并且对于大量虚拟线程场景，访问开销也更小。它非常适合保存一些上下文信息（如当前用户ID、请求ID等），供调用链路下游使用而无需层层传参。ScopedValue 在Java 20孵化，Java 21再次预览（JEP 487 第四次预览），预计Java 22+正式推出。

## 模式匹配和类型系统

- **记录模式第二次预览**： Java 20 延续了 Java 19 的记录模式预览（JEP 432）。改进包括允许在 `instanceof` 之外，也能在增强的 `for` 循环、switch中使用记录模式，并一些语法细节调整。例如：
```java
if (obj instanceof Point(var x, var y) p && x == y) { ... }
```
其中的 `(var x, var y)` 就是记录模式，使用了 var 来省略类型。记录模式的二次预览让它和其它模式（类型模式、常量模式）配合得更好。基本语法趋于稳定，为Java 21转正铺路。
- **Switch 模式匹配第四次预览**： 经过Java 17、18、19三次预览，Java 20 的 switch 模式匹配（JEP 433）进入第4次也应该是最后一次预览。这一版修复了一些角落情况并与记录模式整合。典型使用如：
```java
switch (shape) {
    case Circle c               -> handleCircle(c);
    case Rectangle(var w, var h)-> handleRect(w, h);
    case null                   -> handleNull();
    default                     -> handleOther();
}
```
这里既有类型模式（Circle）、又有记录模式（Rectangle解构），还有显式处理null的分支。Java 20 的预览几乎与最终版一致，之后Java 21正式推出时仅有极小调整。
- **泛型实例推断改进（预览）**： 虽然未在上文提及，但Java 20还预览了一个非常小的语法糖JEP 433的一部分：允许 `instanceof` 后的变量声明使用泛型实例。例如 `obj instanceof Box<String> b` 过去是不被允许的，现在作为预览可以。

## 外部接口

- **外部函数 & 内存 API 第二次预览**： Java 20 将 Java 19 的外部函数/内存API (Panama) 进行第二次预览（JEP 434）。这次预览对API命名和组织作了一些修改，比如将 MemorySession 拆分为 Arena 和 SegmentScope 等。总体而言功能更完善，为最终定型做准备。Java 21 该API第三次预览，Java 22 正式发布 (JEP 454)。

## 其他

- **JDK 20 无长期支持版**，生命周期只有6个月，因此没有特别重大的行为改变，更多是延续性改进和预览。值得一提的是 JDK 20 是 JDK 21（LTS）的前哨战，大部分Java 21的重磅功能（虚拟线程、模式匹配、FFM API等）都已在Java 20经过充分打磨。

**总结**： Java 20 在功能上和Java 19一脉相承，并无全新重量级特性亮相，但却将之前的创新推进到了最后阶段。**虚拟线程**更完善、**结构化并发**和**作用域值**为简化并发提供了全新思路；**记录模式**和**switch模式**几乎打磨成熟，为模式匹配全面落地做好准备。这些都预示了即将到来的Java 21将会是个非常强大的版本。因此对于期待LTS的开发者来说，Java 20 显得“波澜不惊”，但这正是暴风雨前的平静——所有新特性的铺垫都已就绪，等待在Java 21中释放。

# Java 21 新特性

**发行时间**： 2023 年 9 月 19 日 （LTS长期支持版）

Java 21 作为第5个LTS版本，融合了过去几版的预览特性，带来了**15项新特性**。这是一版里程碑式的发布，使Java在语法、并发、性能等方面迈上新台阶。

## 语言特性

- **字符串模板（预览）**： Java 21 引入了**字符串模板**（String Templates）预览（JEP 430）。它提供类似其他语言的内嵌表达式的字符串字面量，用 `${...}` 作为占位符，把变量值或表达式结果直接嵌入字符串中。例如：
```java
String user = "Bob";
int score = 42;
String msg = STR.`Hello, ${user}! Your score is ${score}.`;
System.out.println(msg); // 输出: Hello, Bob! Your score is 42.
```
使用时需在字符串前加 `STR`. 前缀来开启模板字符串字面量（这是预览期的语法要求）。模板中可以直接嵌入局部变量、字段、方法调用等。编译器会将模板转换为高效拼接代码，并可配合模板处理API进行高级用法（如SQL安全拼接等）。**应用场景**： 拼接字符串是最常见的需求，字符串模板让这件事变得安全又简单，再也不需大量引号加加号，也无需 `String.format` 的占位符，对新手友好、对老手高效。虽然Java 21为预览，需要 `--enable-preview`，但预计不久后转正，使Java终于拥抱与现代语言一致的字符串插值能力。
- **记录模式 & 模式匹配 for switch（正式）**： **Record Patterns** 和 **Pattern Matching for switch** 在经历多次预览后，终于在 Java 21 正式发布（JEP 440, 441）。这意味着我们可以在 `instanceof` 和 `switch` 中自由使用类型模式和记录模式进行解构匹配，无需启用预览。

记录模式允许匹配记录类并直接解构其组分，例如：
```java
if (shape instanceof Rectangle(int w, int h)) {
    System.out.println("长方形面积:" + w*h);
}
```
Switch模式匹配允许 switch 直接按类型/结构分支，例如结合密封类：
```java
switch (shape) {
    case Circle(double r)        -> System.out.println("圆面积:" + Math.PI*r*r);
    case Rectangle(int w, int h) -> System.out.println("矩形面积:" + w*h);
    case null                    -> System.out.println("空形状");
    default                      -> System.out.println("未知形状");
}
```
其中 `Circle(double r)` 是类型+变量模式，`Rectangle(int w, int h)` 是记录模式。由于 `Shape` 假设是密封接口，列举了所有子类，所以可以省略 default 或只用于 null 情况。**应用场景**： 模式匹配让 Java 处理复杂数据结构时如鱼得水。例如遍历一个 JSON 抽象语法树，不同节点类型（对象、数组、值）用 switch 匹配类型，既直观又安全。过去这些需要大量的 instanceof + 强转+if/else，而现在简洁明了。Java 21 的模式匹配使Java具备了代数数据类型模式匹配的威力，大大提高了代码可读性和可靠性。

- **未命名模式和变量（正式）**： Java 21 正式引入了 **未命名模式(\_)** 和 **未命名变量(\_)**（JEP 443）。简单来说，就是引入了下划线 `_` 作为通配符，可在模式匹配中忽略不需要的部分，以及作为一种“匿名变量”用于标识暂时用不到的本地变量。这两个用途不同：
- - **未命名模式**： 在模式匹配（instanceof或switch的模式）中，用 `_` 表示“匹配任何，不使用该值”。例如：
```java
if (point instanceof Point(int x, _)) {  // 只关心x，不在意y值
    System.out.println("x坐标:" + x);
}
```
这里第二个分量用了 `_`，表示匹配任何y而不绑定变量。这避免了像以前那样写一个无用的名字又不使用产生警告。
- - **未命名变量**： 允许定义本地变量时用单个下划线作为名称，但这样的变量无法使用（编译器也不允许使用），只是为了占位。例如：
```java
int _ = computeHeavy();  // 调用方法但不关心返回值，只是为了触发方法副作用
```
定义了一个名为`_`的int变量，但后续无法引用它。这样做的意义在于清晰表达“我故意忽略这个返回值”。这种写法主要用于兼容需要变量语法但我们不需要实际变量的场景（类似 `_ = in.read()` 读而不处理）。另外，未命名变量只能定义一次，不能重复定义或和其他变量重名。

**应用场景**： 未命名模式在复杂模式匹配时尤其实用，如果一个模式中有部分内容不关心，可以用 `_` 占位，使代码更简洁。未命名变量用得不多，但在调用返回值不需要的方法时可以表明意图。例如在测例中调用某初始化函数，只为触发内部逻辑，不关心结果，就可以 `Object _ = init()`;。需要注意，下划线作为关键字在这之前已不能当普通变量名使用，因此这项特性没有向后不兼容问题。

- **未命名类和实例 main 方法（预览）**： Java 21 提供了一个有趣的预览特性 JEP 445：**隐藏类名和实例主方法**。它允许编写更简洁的单文件程序：可以省略类声明，直接写语句，甚至 `main` 方法也可以写成实例方法。具体来说：
- - 可以在源文件中不显式声明类，Java编译器会为顶层语句隐含定义一个类。如：
```java
void main() {
    System.out.println("Hello World!");
}
```
这样写一个 `.java` 文件也能编译运行。编译器会自动包裹成 `class X { void main() {...} }` 形式并生成入口。
- - 允许 `main` 方法定义为实例方法而非静态，并且类可以不命名（编译器生成类名）。甚至可直接写 `void main(){}` 顶格在文件开头，不用类和方法签名。例如上例已经展示，无需 `public static void main(String[] args)` 那么啰嗦。

**应用场景**： 主要目的是降低初学者学习Java的门槛，以及让脚本式的小程序更简洁。过去新手写HelloWorld，一上来就要理解类、静态方法、字符串数组，对入门不友好。有了这个预览特性，可以更像脚本语言一样直接写代码执行。当然，这只是源代码层面的语法糖，实际编译还是会生成类。这个特性也显示了Java追求更“轻量”的一面。不过在大型项目中，还是会明确定义类和main，未命名类更多用于教学、快速脚本等场景。它在Java 21为预览，要启用预览才能使用。

## 并发和虚拟线程

- **虚拟线程正式发布**： Java 21 通过 JEP 444 将 **虚拟线程** (Virtual Threads) 定稿发布！这意味着不需任何标志，就可以在生产中使用 Project Loom 带来的虚拟线程能力了。从此，Java 有了两种线程：平台线程（传统操作系统线程）和虚拟线程（由JVM调度）。虚拟线程的使用方式和之前预览一致，例如：
```java
Thread vt = Thread.startVirtualThread(() -> {
    // ... 虚拟线程执行代码 ...
});
vt.join();
```
或通过 `Executors.newVirtualThreadPerTaskExecutor()` 来大量提交任务。虚拟线程的调度、同步都与普通线程一致，支持ThreadLocal、锁等，只是代价极低，可以创建百万级。**应用场景**： 几乎所有并发服务器负载都可以考虑迁移到虚拟线程模型。例如基于Spring、Tomcat的Web应用，可配置使用虚拟线程的执行器，每请求一个虚拟线程处理，简化复杂的异步逻辑。数据库驱动如果配合良好（阻塞IO释放OS线程），也能提升吞吐。总之，虚拟线程使编程模型和高并发性能实现了统一：我们可以用同步代码写出异步高并发效果。需要注意监控工具升级以识别大量线程，但JDK本身的jstack等已经支持很好。
- **Sequenced Collections（序列集合）**： Java 21 引入了新的集合接口族 **Sequenced** 集合（JEP 431）。主要包括 `SequencedCollection`、`SequencedSet`、`SequencedMap`。这些接口统一了“有顺序的集合”的抽象，提供了在集合两端操作元素的方法以及反转视图。比如：
```java
SequencedCollection<Integer> coll = new ArrayDeque<>();
coll.addFirst(1);
coll.addLast(2);
System.out.println(coll.getFirst()); // 1
System.out.println(coll.getLast());  // 2
SequencedCollection<Integer> reversed = coll.reversed();
```
在Java 21中，`ArrayList`、`LinkedList` 实现了 `SequencedCollection`；`LinkedHashSet` 实现了`SequencedSet`；`LinkedHashMap`实现了 `SequencedMap`。这样我们可以方便地对这些集合的头尾进行操作，而不必区分List或Deque接口。例如以前要获取List最后一个元素需要 `list.get(list.size()-1)`，现在 `list.getLast()` 即可。反转视图 `reversed()` 则返回一个与原集合顺序相反的同类型集合视图，操作视图相当于操作原集合两端。**应用场景**： 任何需要队列/双端队列操作的地方更方便了，而且统一接口后，可以写通用算法处理SequencedCollection，不用分别考虑List或Deque，实现接口分离更合理（Deque过于笼统，而Sequenced只关注顺序）。这个特性在集合框架演进史上是个重要调整，使得List, Set, Map在迭代顺序方面有了共同的父接口，更加一致。

## JVM 和性能

- **分代 ZGC（实验）**： Java 21 将 ZGC 升级为**分代式垃圾收集器**（Generational ZGC，JEP 439）。以前ZGC是非分代收集，Java 21引入分代概念，将堆分为新生代和老年代。如此一来，ZGC 可以针对新生对象和长期存活对象采用不同策略，提升整体吞吐量和内存回收效率。Gen ZGC 仍是实验状态，需要通过 `-XX:+ZGenerational` 开启。但测试表明 generational 模式下，ZGC 的 STW 停顿仍然保持极低，同时回收效率明显提高，在大部分场景下优于非分代模式。**应用场景**： 如果使用ZGC，可以考虑在Java 21上试验开启分代模式，以获得更好的性能。需要注意持续关注后续版本，因为目标是在验证效果后将 Gen ZGC 替换掉非分代ZGC。
- **禁用安全管理器**： Java 21 虽未完全移除 SecurityManager，但已经采取了进一步措施：完全禁止在启动时开启安全管理器。即使使用 `-Djava.security.manager` 也无法再启用它（会抛异常）。这是JEP 486的一部分。这意味着 SecurityManager 已经走到寿终正寝阶段，Java 21 开始不允许使用它。对于仍依赖安全管理器的应用，这是最后通牒，必须迁移（常用场景如SecurityManager控制脚本权限，现在可用沙箱ClassLoader等替代）。这个改动对大多数现代应用无影响，因为安全管理器早已很少使用。
- **虚拟线程同步非阻塞平台线程**： 前面提到，Java 21 正式版虚拟线程在阻塞时（包括进入 synchronized 区块）基本都不会固定占用平台线程。JEP 491 进一步优化了虚拟线程遇到 monitor 锁的处理：如果虚拟线程在同步锁等待，它后台的OS线程会释放出来去执行别的虚拟线程。这一机制确保即使有大量虚拟线程同时阻塞在锁上，也不会占满对应数量的OS线程，从而保持高度并发。这使得在使用传统锁的代码中引入虚拟线程也依然高效，并发能力不会下降。
- **类加载和链接缓存（预览）**： JEP 483 引入了“提前加载和链接”的机制，允许缓存类加载和链接结果，加速应用启动。通过在上次运行中记录已加载链接的类，在下次JVM启动时跳过重复工作，实现**40%以上的启动提速**。这类似于CDS，但作用于类链接阶段。Java 21 中这是预览需手动开启（`-XX:+EnableClassDataSharing` 等），未来可能默认启用来提升大应用启动性能（微服务、无服务器函数启动速度变快）。
- **类文件 API 正式发布**： 前几版孵化的**类文件解析 API** 在 Java 24 正式发布（Java 21中处于第二次预览JEP 451/456）。开发者可以使用标准API解析、生成和转换 `.class` 文件。这对于构建字节码操作工具（类似ASM）提供了官方支持。虽然普通业务开发用不到，但对于框架和工具作者是个好消息，避免依赖第三方库，增加可靠性。

## 新安全特性

- **密钥派生函数 API（预览）**： 虽然Java 21没有包含，但Java 24预览了 **KDF API** (JEP 478)。这将标准化PBKDF2、HKDF等密钥派生算法的使用。在Java 21，安全新增主要是一些TLS KEM算法和DH算法强化，不是主要特性。

**总结**： Java 21 是迄今**功能最强大**的Java版本之一。**虚拟线程**和**结构化并发**在并发编程领域给予Java巨大能量，**Sequenced集合**完善了集合框架，**模式匹配**全面落地使Java具备了代数数据类型的便利。诸多预览（字符串模板、隐藏类、KDF等）也预示着未来的发展方向。作为LTS版本，Java 21 具备足够的稳定性，又融入了现代语言的诸多精华，难怪被称为“继Java 8之后最重要的版本”。对于开发者来说，如果从Java 17升级上来，将明显感受到代码可以写得更简洁（Record, 模式匹配）, 性能可以更上一层楼（虚拟线程, 新GC）, 开发体验也更好（UTF-8默认, 文本块, 字符串模板等）。Java 21 为未来几年Java的发展奠定了基础，下一个LTS预计是Java 25，期间Java 22/23/24也会继续在这些方向演进。

# Java 22 新特性

**发行时间**： 2024 年 3 月

Java 22 虽为非LTS版本，但也引入了一些值得关注的新特性，共计约12项（其中多项为预览/孵化）。Java 22 基本上是在Java 21基础上的小幅增量。

## 语言与语法

- **未命名模式和变量转正**： 前文提到的下划线 `_` 模式和未命名变量在 Java 22 顺利成为正式特性。因此，在 Java 22+ 编码时，可以直接使用 `_` 来忽略模式中的某部分，无需任何开关。比如 `case Point(int x, _) -> ...` 这样的 switch 分支现在是标准写法。此举标志着模式匹配相关语法进一步完善，开发者可以更自在地使用通配模式，提高可读性。
- **外部函数和内存 API 正式发布**： Java 22 通过 JEP 454 将**Foreign Function & Memory API**正式加入标准库。这表示 Project Panama 历经多个版本终于落地。开发者无需再加孵化模块，可直接使用 `MemorySegment`, `MemorySession`（已更名为Arena）, `CLinker` 等类与本地交互。相比Java 21预览，Java 22 的API可能略有调整但大体一致。**应用场景**：底层系统编程、JNI替代方案，如直接调用操作系统函数、读取映射文件、高性能I/O等，现在都能用这套安全的API完成。由于已正式发布，各种框架和库也会开始利用它，例如Netty可以用MemorySegment管理直接内存，JNI层代码有望大幅减少。
- **多文件源代码程序启动**： Java 11 实现了单文件运行，Java 22 则更进一步引入**多源文件一起运行**的功能（JEP 458）。这允许我们使用 `java` 命令一次性运行多个源文件，无需手动编译链接。例如：
```java
java MyMain.java Utils.java Helper.java
```
Java 将同时编译这些源并执行包含 `main` 方法的类。这对写小型脚本程序又更方便了一步，打破了“一次只能运行一个源文件”的限制。**应用场景**： 在教学、快速试验时，可以把若干相关类放在不同文件，一条命令运行，避免每改一点就javac再java分步做。
- **构造函数中允许语句在 super() 之前（预览）**： JEP 447 在 Java 22 作为预览推出了**构造方法前置语句**功能。以往在构造函数中，调用父类构造 (`super(...)`) 或本类重载构造 (`this(...)`) 必须是第一条语句，不能有任何其他代码在其前面。这导致有时想在调用父类前做点检查或计算很麻烦。Java 22 放宽了这个限制，允许在构造器首行调用之前加入一些限定的语句，比如对参数的合法性检查、静态方法调用获取配置等。示例：
```java
class MyClass extends Base {
    MyClass(int x) {
        if(x < 0) x = 0;           // 现在可以在 super() 调用前执行
        super(calcValue(x));       // 然后调用父类构造
        System.out.println("Done");
    }
}
```
此特性可以减少在上一级构造做逻辑绕过的繁琐，代码意图更直接。但是仍有限制：不能访问未初始化的成员等。**应用场景**： 主要用于构造参数预处理，例如确保传给父类的参数符合要求。以前需要在子类构造方法之外先处理好参数再传，如今可以在构造内部做处理，更封装直观。

## 核心库与安全

- **类文件 API 第二次预览**： 尽管Java 24才正式发布类文件API (JEP 484)，Java 22 已经进行了第一次预览 (JEP 457) 和 Java 23 第二次预览 (JEP 456)。这意味着Java 22的开发者已经可以试用标准的类文件解析生成API，为后续正式版做准备。具体API见上文Java 24部分介绍。
- **流收集器 API（预览）**： Java 22 引入了流处理的新机制预览：**Stream::collect 使用自定义收集器（Gatherer）**，也称**Stream Gatherers** (JEP 461/473)。简单来说，它允许开发者定义自定义的流中间收集逻辑，通过新的`Stream.gather(Gatherer)`方法实现。这拓展了Stream API，能表达更复杂的操作如滑动窗口、批处理等。Java 22 预览后，Java 23 继续预览，Java 24 正式推出 (JEP 485)。这个特性复杂但功能强大，前文Java 24部分已详细说明。
- **Markdown 文档注释**： Java 23 正式加入了 **Markdown 支持的 JavaDoc** (JEP 467)，Java 22 可能已经对这一特性做好了准备或者在22预览，在23正式。因此Java 22/23写JavaDoc可以直接用Markdown语法，更方便地编写列表、链接等。

## 其他变化

- **G1 区域固定**： JEP 423 针对 G1 GC 引入了**区域固定**的能力。这使得JNI临界区中的对象可以避免被移动，从而减少复制开销，对某些场景下提高GC性能有帮助。但这属于JVM内部优化，开发者无感知。
- **Unsafe 内存访问方法弃用**：Java 22 正式弃用了`sun.misc.Unsafe`中一批直接内存访问方法（JEP 471）。因为有VarHandle和MemorySegment这些更安全的替代了。Unsafe依然能用，但调用这些方法会警告，未来版本将移除。这促使底层库向VarHandle/FFM API迁移。
- **端口和平台支持**：随着JDK进入高频发布，Java 22 没有大的移植JEP，因为21已涵盖RISC-V等。不过可能在22对Windows/AArch64、macOS/AArch64等新平台做了性能调优和问题修复。

**总结**： Java 22 作为 Java 21 之后的过渡版本，主要工作是**巩固**和**过渡**。大量Java 21预览的特性在Java 22得到正式发布（如 FFM API、Unnamed模式变量），使得Java语言和API更加完善。对开发者来说，升级到Java 22不会像21那样冲击大，但能开始稳定地使用21里预览的一些功能。例如，用MemorySegment替代ByteBuffer变得稳妥了，用模式匹配下划线占位也没问题了。这版也包含一些语法糖改进，如构造器中可以有前置语句，这些虽然小，但提升了编码便利性。Java 22 还为未来的新特性继续铺路，例如Stream自定义收集、模块导入声明（JEP 476，允许`import java.util.* from module java.base;`这样的简化语法，在22孵化）等。这些预览将在Java 23/24成熟。可以预见，Java 22 的变化累积到Java 25 (下一个LTS) 会带来更多惊喜。

# Java 23 新特性

**发行时间**： 2024 年 9 月

Java 23 延续了 22 的趋势，也是非LTS版本。根据目前信息，Java 23 包含约12项新特性。其中相当一部分是继续预览或最终定型上版的特性。

## 语言与语法

- **原始类型模式（预览）**：Java 23 通过 JEP 455 引入了 **对原始类型的模式匹配** 预览。这扩展了前面的模式匹配，使 `instanceof` 和 `switch` 可以直接匹配 primitive 类型的值。这其实在语法上表现为允许 instanceOf 右边出现基本类型，例如：
```java
Object obj = 123;
if (obj instanceof Integer i) { ... } // 之前只能这样
if (obj instanceof byte b)   { ... } // 现在可以直接匹配 byte 范围
```
如上，第二个判断如果 obj 是数值且在 byte 范围内，就匹配成功并转换为 byte。同理，switch 也允许case 是 long、double 等字面量。这使模式匹配对基本数据类型更友好。**应用场景**：通常从文本或网络得到Object，需要根据类型处理，比如 JSON节点可能是Double但实际表示整数，这时instanceOf double d -> 转 int 就方便了。不过原始类型模式属于锦上添花的特性，非核心。
- **类文件 API 第二次预览**：Java 23 继续预览类文件API (JEP 456/466)。根据JEP 484，在Java 24最终发布。Java 23也许主要更改了一些API命名、包结构等。
- **Markdown JavaDoc 正式**：Java 23 (JEP 467) 把JavaDoc的 Markdown 支持正式化。因此现在可以在JDK文档中看到格式良好的列表、代码等了。对开发者，写注释也更方便，不必纯HTML。
- **向量API 第八次孵化**：Java 23 的 Vector API 进入第8次孵化（JEP 469）。应该做了更多性能改进，可能已经接近转正式阶段（Java 25?）。
- **Stream 收集器第二次预览**：Java 23 通过 JEP 473 继续预览 Stream::gather（流收集器）功能。可能完善了Gatherer接口定义。Java 24 已正式推出 (JEP 485)。因此Java 23开发者已可试用 gather 功能进行复杂流处理。

## JVM 与安全

- **禁用 SecurityManager 完成**：Java 24 完全禁止开启安全管理器。Java 23 应该已经完全不支持 SecurityManager，在Java 21就已经禁止使用 `-Djava.security.manager` 了。因此Java 23在安全方面把老的 SecurityManager 体系彻底关停。
- **TLS/KEM 支持**：可能添加了一些后量子密码学支持，例如密钥封装机制（KEM）API等。但具体JEP (452 KEM API) 最终目标在Java 21/22实现，这里可能预览或完善。Java 24通过JEP 478预览KDF，目前KEM方面JEP 452已在21实现KeyAgreement中。
- **JVM性能优化**：Java 23 完成了Gen ZGC的发展。JEP 474 切换ZGC默认启用分代模式并弃用非分代模式。可能Java 23实验提供一个flag，Java 24就默认改为分代。
- **模块导入声明（预览）**：JEP 476 在Java 24预览。Java 23或22可能已经孵化。它允许在代码顶部导入整个模块导出的所有包，比如 `import static from javafx.graphics;` 这对模块化用户方便一些，但普通场景用处不大，目前也只是预览。

## 其他

- **RMI Registry 拓展**：Java 23 几乎不涉及RMI了，RMI Activation已移除，Registry部分或性能改善可能进行了一些微调，但无JEP说明。

**总结**： Java 23 是在 LTS (21) 之后，下一次 LTS (25) 之前的第二个常规版本。其主要作用是**巩固新功能**并**继续探索**。许多 Java 22 引入的预览在 Java 23 得到完善，例如原始类型模式、流收集器等。这些都在为下一个LTS做准备，使得 LTS 发布时新特性能更成熟稳定。对开发者而言，Java 23新增的稳定特性较少，更像是在21的基础上修修补补。但对于喜欢尝新的团队，可以在 Java 23中尝试前沿特性（如 gatherer、类文件API 等）并给出反馈。考虑到 Java 25将是LTS且会包含22-24的成果，Java 23的意义更多在于验证和过渡。

# Java 24 新特性

**发行时间**： 2025 年 3 月

根据官方消息，Java 24 带来了 **24 项新特性**（恰好与版本号相同的数量），是一个内容相当丰富的版本，甚至相当于Java 22和23新特性之和。它汇集了过去几版的预览成果，也有新的探索。以下列出几项主要新特性：

## 安全与密码学

- **密钥派生函数 API（预览）**：Java 24 引入了 **KDF(Key Derivation Function) API** 预览（JEP 478）。KDF算法如 HKDF、PBKDF2 用于从一个初始密钥派生出二次密钥。JDK 24 提供统一接口 `KDF` 来获取和使用这些算法。例如：
```java
KDF hkdf = KDF.getInstance("HKDF-SHA256");
AlgorithmParameterSpec params = HKDFParameterSpec.of(initialKey).thenExpand(info, 32);
SecretKey derivedKey = hkdf.deriveKey("AES", params);
```
这样就得到一个32字节的AES密钥。这个API使得密码学编程更加直观规范，避免开发者自己实现易出错。**应用场景**： 密码协议需要从会话密钥生成加密密钥、认证密钥等，例如TLS 1.3的密钥扩展，就可使用HKDF实现。KDF API 预览后预计在下一LTS(Java 25)转正，对那些需要自己拼凑调用 MessageDigest 的业务大有裨益。
- **完全禁用 Security Manager**：前文已述，Java 24 (JEP 486) 完全移除了安全管理器的启用可能。这标志着 SecurityManager 彻底退出历史舞台，相关API调用会直接抛异常。开发者应确认没有使用 `System.setSecurityManager` 等，以免升级引发错误。

## 性能与工具

- **类加载与链接缓存**：Java 24 通过 JEP 483 引入了 **Class Preloading & Linking**（提前类加载和链接）特性。它会在首次运行应用时缓存类加载+验证+链接结果，存储到类数据共享（CDS）的归档中。下次JVM启动加载相同应用时，可直接使用缓存，避免重复解析验证，大幅加速启动时间。实测对于大型Spring应用启动提升可超40%。此特性类似于CDS但更进一步。**应用场景**： 短命令行工具或Serverless函数的冷启动、频繁重启的服务等，将显著受益。Java 24 该功能预览，需要开启参数，未来Java可能默认启用这一优化。
- **类文件 API 正式发布**：Java 24 正式推出了 **ClassFile API**（JEP 484）。开发者可以使用它来读写 `.class` 文件而不依赖第三方库。API位于`java.lang.classfile`包下，包括`ClassFile`，`ClassModel`, `MethodModel` 等，可以方便地遍历类的字节码结构。例如，可以用它做一个简单的类浏览器或者字节码修改工具。这个特性更多惠及框架和工具作者，一般业务不会直接用。但有了官方API，像ASM等库可能会慢慢过渡或封装该API，以减少维护负担。
- **Stream::gather 正式发布**：Java 24 通过 JEP 485 增强了 Stream API，引入了 `Stream.gather(Gatherer)` 方法及 **Gatherer接口**。这允许自定义流的中间操作逻辑，实现之前难以表达的操作模式。举例来说，使用 gatherer 可以实现“跳过重复长度的字符串”这样的需求，如前文示例所示：用一个 HashSet 作为状态，在Gatherer每次收到元素时检查长度是否出现过，没出现过就 push 给下游，否则跳过。Gatherer 接口提供了类似状态机的钩子，使一个流可自定义内部行为。**应用场景**： 复杂数据流处理，如滑动窗口统计、跨元素的自定义去重、批量输出等，以前要借助外部变量或拆分流处理，现在 gatherer 使这些逻辑优雅地内聚在Stream管道中。这对高级Java数据处理开发者是个强力工具。

## 并发与内部改进

- **作用域值第四次预览**：ScopedValue 在 Java 24 进入第4次预览（JEP 487）。它的API进一步稳定，预计Java 25会正式推出取代ThreadLocal的大部分使用场景。Java 24的ScopedValue足够成熟，可以尝试在虚拟线程环境下用它传递上下文数据。相对于ThreadLocal，它不会引起内存泄漏且性能更好，是 Loom 计划的重要补充。
- **虚拟线程同步无Pinning**：之前Java 21中引入，此处在Java 24 (JEP 491) 已经默认生效：虚拟线程在锁中阻塞时会挂起自己，让出载体线程，实现无Pinning锁。对开发者而言，这意味着可以放心在虚拟线程中使用传统锁，不必担心阻塞OS线程导致并发度下降。这彻底解决了以往Fibers实现的一个缺陷，使虚拟线程更加Transparent地兼容现有同步代码。
- **jlink 无需 JMOD 文件**：Java 24 (JEP 493) 改进了 jlink 工具，打包定制运行时镜像时不再需要JDK自带的 .jmod 文件。这减少了JDK安装体积约25%，并且使得 jlink 使用更简单。对最终用户来说，Java 24的JDK包会更小，jlink运行时不会受影响。

## 预览/孵化

- **字符串模板第二次预览**： 虽然Java 24发布时间未来，但可以预计 String Templates 可能在Java 24继续预览甚至转正。JEP 430在Java 21预览，引起极大关注，Java 24 若提前成熟就可能正式发布，否则会第二次预览。无论如何，离成为正式特性不远了。
- **隐式类导入（预览）**： JEP 485?其实没此号，隐式模块导入JEP 476在Java 24预览了。它允许像一些脚本语言一样导入整个模块，不用逐个包声明import。但这个特性用处和接受度有限，尚不确定是否会最终发布。

**总结**：Java 24 作为非LTS版本，却引入了**史无前例多的新特性**。一方面，它将过去几年的预览几乎全部定型（FFM API、类文件API、流收集器等），另一方面也推出了像KDF API、Scope Values 等值得期待的新预览。此外，性能优化（类加载缓存、虚拟线程锁优化）使Java运行效率更上一层楼。Java 24对于追新的开发者无疑是一个盛宴，但要谨慎用于生产，因为变化很多且缺少长期支持。但可以预见，**Java 25** 作为下一个LTS，将包含Java 22-24的大量成果，届时Java语言的现代化转型可以说基本完成。因此Java 24不仅有自身价值，更是Java 25 前的重要一跃，值得关注和试用，为未来做准备。

---

**参考资料：**

- OpenJDK 官方 JEP 列表及发布说明。
- Oracle Blogs: Java Language Futures 系列文章。