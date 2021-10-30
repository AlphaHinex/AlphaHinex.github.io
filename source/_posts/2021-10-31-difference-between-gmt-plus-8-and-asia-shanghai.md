---
id: difference-between-gmt-plus-8-and-asia-shanghai
title: "GMT+8 和 Asia/Shanghai 的区别"
description: "设定时区时，应该用哪个？"
date: 2021.10.31 10:34
categories:
    - Java
tags: [TimeZone, Java]
keywords: TimeZone, GMT, UTC, Asia/Shanghai, GMT+8, 夏令时
cover: /contents/difference-between-gmt-plus-8-and-asia-shanghai/cover.png
---

时区
===

> 现今全球共分为24个时区。实际上，常常1个国家或1个省份同时跨着2个或更多时区，为了照顾到行政上的方便，常将1个国家或1个省份划在一起。所以时区并不严格按南北直线来划分，而是按自然条件来划分。例如，中国幅员宽广，差不多跨5个时区，但为了使用方便简单，实际上在只用东八时区的标准时即北京时间为准。 —— 引自百度百科 [时区](https://baike.baidu.com/item/%E6%97%B6%E5%8C%BA/491122)

时区可以使用名称（如：东八区、西五区）、偏移量（如：`UTC+8`、`UTC-5`）、[缩写](https://www.timeanddate.com/time/zones/)（如：`PST`、`CST`），或 [时区数据库][tz] 中 `Area/Location` 的形式（如 `Asia/Shanghai`、`America/Chicago`）来表示。

因为缩写具有不唯一性，如 `CST` 既可以表示 `China Standard Time`（UTC+8），也可以表示 `Central Standard Time`（UTC-6），所以设置时区时，一般不使用这种方式。

使用偏移量表示时区时，如东八区，可以使用 `UTC+8`，也可以使用 `GMT+8`，`UTC` 为 [Universal Time Coordinated，协调世界时](https://baike.baidu.com/item/%E5%8D%8F%E8%B0%83%E4%B8%96%E7%95%8C%E6%97%B6)，`GMT` 为 [Greenwich Mean Time，格林尼治标准时间](https://baike.baidu.com/item/%E6%A0%BC%E6%9E%97%E5%B0%BC%E6%B2%BB%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4/586530)。`UTC` 更加科学更加精确，但在不需要精确到秒的情况下，通常将 GMT 和 UTC 视作等同。

在需要使用统一的 `北京时间` 时，可以将时区设定为 `GMT+8`，也可以使用时区数据库中的时区代码 `Asia/Shanghai`，同样都能表示东八区，他们还有什么不同吗？

让我们以 Java 为例，来看一看。

Java
====

为方便，我们使用 Java 9 新增的 JShell 来进行说明。

> JShell is a Java read-eval-print loop which was first introduced in the JDK 9. 

```jshell
$ jshell
|  欢迎使用 JShell -- 版本 11.0.3
|  要大致了解该版本, 请键入: /help intro

jshell> 
```

在 Java 9 以上环境，终端中输入 `jshell` 进入 JShell，之后可以直接使用 Java 语法，注意需要 `import` 对应的类。

Java 中的 `UTC` 和 `GMT`
-----------------------

先来看下 Java 中 `UTC` 和 `GMT` 的区别：

```jshell
jshell> Date now = new Date()
now ==> Thu Oct 30 16:59:27 CST 2021

jshell> import java.text.*

jshell> DateFormat df = DateFormat.getInstance()
df ==> java.text.SimpleDateFormat@ca92313f

jshell> df.setTimeZone(TimeZone.getTimeZone("GMT+8"))

jshell> df.format(now)
$5 ==> "2021/10/30 下午4:59"

jshell> df.setTimeZone(TimeZone.getTimeZone("UTC+8"))

jshell> df.format(now)
$7 ==> "2021/10/30 上午8:59"

jshell> df.setTimeZone(TimeZone.getTimeZone("UTC"))

jshell> df.format(now)
$9 ==> "2021/10/30 上午8:59"

jshell> df.setTimeZone(TimeZone.getTimeZone("GMT"))

jshell> df.format(now)
$11 ==> "2021/10/30 上午8:59"

jshell> df.setTimeZone(TimeZone.getTimeZone("abc"))

jshell> df.format(now)
$13 ==> "2021/10/30 上午8:59"
```

**从上面的输出可以看出，在当前使用的 Java 版本中，设定时区偏移量时，是不能使用 `UTC` 的，只能使用 `GMT`！另外，使用非法的时区 ID 时，会将时区设定为零时区。**

`GMT+8` 和 `Asia/Shanghai`
--------------------------

再来看一下 `GMT+8` 和 `Asia/Shanghai`。

通常我们会将日期表示成格式化的字符串，如 `2021-10-31 10:34:00`，然后将其解析为日期类型并使用，需要打印时再将日期类型转换为字符串，例如：

```jshell
jshell> import java.text.*

jshell> SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss")
sdf ==> java.text.SimpleDateFormat@4f76f1a0

jshell> DateFormat df = DateFormat.getInstance()
df ==> java.text.SimpleDateFormat@ca92313f

jshell> df.setTimeZone(TimeZone.getTimeZone("Asia/Shanghai"))

jshell> df.format(sdf.parse("2021-10-31 10:34:00"))
$6 ==> "2021/10/31 上午10:34"

jshell> df.setTimeZone(TimeZone.getTimeZone("GMT+8"))

jshell> df.format(sdf.parse("2021-10-31 10:34:00"))
$8 ==> "2021/10/31 上午10:34"
```

一模一样，所以没区别？别着急，我们继续看。

```jshell
jshell> df.setTimeZone(TimeZone.getTimeZone("Asia/Shanghai"))

jshell> df.format(sdf.parse("1986-05-04 02:00:00"))
$10 ==> "1986/5/4 上午3:00"

jshell> df.setTimeZone(TimeZone.getTimeZone("GMT+8"))

jshell> df.format(sdf.parse("1986-05-04 02:00:00"))
$12 ==> "1986/5/4 上午2:00"
```

当我们使用 `1986-05-04 02:00:00` 这个时间戳时：
* 时区设置为 `GMT+8`，字符串转日期，再将日期转成字符串，得到的日期和时间跟输入的时间戳是一样的
* 时区设置为 `Asia/Shanghai`，经过转换之后，输出的时间变成了上午三点，比输入的上午两点多了一小时

发生了什么？这就要说到 `夏令时` 了。

夏令时
=====

[夏令时][cdt]（Daylight Saving Time: DST），也叫 `夏时制`，是指为了节约能源，在天亮的早的夏季，人为将时间调快一小时，以充分利用光照资源，节约照明用电。

在冬季光照时间变短后，将时间再拨回一小时的标准时间，也称为冬令时。

中国在 1986 年至 1991 年也实行过夏令时：

> 1986年4月，中国中央有关部门发出“在全国范围内实行夏时制的通知”，具体做法是：每年从四月中旬第一个星期日的凌晨2时整（北京时间），将时钟拨快一小时，即将表针由2时拨至3时，夏令时开始；到九月中旬第一个星期日的凌晨2时整（北京夏令时），再将时钟拨回一小时，即将表针由2时拨至1时，夏令时结束。从1986年到1991年的六个年度，除1986年因是实行夏时制的第一年，从5月4日开始到9月14日结束外，其它年份均按规定的时段施行。在夏令时开始和结束前几天，新闻媒体均刊登有关部门的通告。1992年起，夏令时暂停实行。 —— 引自百度百科 [夏令时][cdt]

![](/contents/difference-between-gmt-plus-8-and-asia-shanghai/cdt.jpg)

这样就能解释上面的现象了，即：


`GMT+8` 和 `Asia/Shanghai` 的区别
================================

* `GMT+8` 因为没有位置信息，所以无法使用夏令时
* `Asia/Shanghai` 使用夏令时

**时间戳字符串中不包含时区信息时，解析到的具体时区如果是使用夏令时的，就会跟不使用夏令时的时区，时间不一致。**


[tz]:https://github.com/eggert/tz
[cdt]:https://baike.baidu.com/item/%E5%A4%8F%E4%BB%A4%E6%97%B6/1809579