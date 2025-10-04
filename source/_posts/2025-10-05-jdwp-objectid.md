---
id: jdwp-objectid
title: "【转】Debug调试时 Object@xxx表示什么"
description: "调试时可见的 JVM 中对象唯一 ID"
date: 2025.10.05 10:34
categories:
    - Java
tags: [Java]
keywords: Java, debug, JDWP, Java Debug Wire Protocol, ObjectID, JVM, IDEA
cover: /contents/jdwp-objectid/cover.png
---

- 原文链接：[Debug调试时 Object@xxx表示什么](https://blog.csdn.net/baichoufei90/article/details/84102509)
- 原文作者：[迷路剑客](https://blog.csdn.net/baichoufei90?type=blog)

# 0x01 摘要

再用IDEA等工具调试Java代码时，往往会看到类似`Person@434`这样的信息。关于`@`符号后面数字表示的含义，这里解释一下。

![summary](https://alphahinex.github.io/contents/jdwp-objectid/summary.png)

# 0x02 不是HashCode

首先这里要说下，这个数字不是`HashCode`，也不是其16进制形式。

`Object`对象有一个默认的`toString`方法如下：

```java
public String toString() {
    return getClass().getName() + "@" + Integer.toHexString(hashCode());
}
```

可以看到他将Object的hashCode转为了16进制格式输出。整体的输出格式和我们好奇的输出格式是一样的，但是值却不同：

![toString](https://alphahinex.github.io/contents/jdwp-objectid/toString.png)

这两者之间也没有什么进制转换关系，至少我没发现。。。

# 0x03 ObjectID

在stackoverflow发现了这个问题的答案：

[Deciphering variable information while debugging Java](https://stackoverflow.com/questions/2322903/deciphering-variable-information-while-debugging-java)

这个数字是ObjectID，隶属于JDWP(Java Debug Wire Protocol, Java调试线协议)。

JDWP被用来在`debugger`和他所调试的目标JVM之间通信。

JDWP是可选实现的，也就是说一些JDK的实现版本没有JDWP。

实现了JDWP，可以允许相同debugger工作在以下位置：

1. 同一台计算机上的不同进程中
1. 在远程计算机上

ObjectID 最多8字节，具体由VM指定。ObjectID可以唯一标识目标VM中的对象。 一个特定对象将通过JDWP命令中的一个objectID来标识，整个生命周期中不变，除非已经明确处理完了一个ObjectID，否则不会重复使用ObjectID来标识不同的对象，无论引用的对象是否已被垃圾回收。

objectID为`0`表示null对象。

**注意，对象ID的存在不会阻止对象的垃圾回收。** 任何使用其对象ID访问垃圾收集对象的尝试都将导致INVALID_OBJECT错误代码。 可以使用DisableCollection命令禁用垃圾收集，但通常不需要这样做。

更多信息，请参考[Java Debug Wire Protocol](https://docs.oracle.com/javase/8/docs/technotes/guides/jpda/jdwp-spec.html)
