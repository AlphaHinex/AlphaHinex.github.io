---
id: float-binary-conversion
title: "十进制浮点数与二进制数转换"
description: "包含符号位、指数位和小数位"
date: 2021.03.28 10:26
categories:
    - Others
tags: [Java, JavaScript]
keywords: 十进制, 二进制, 浮点数, float, double, ieee 754, binary
cover: /contents/float-binary-conversion/cover.png
---

## 什么是浮点数

> 在计算机科学中，浮点（英语：floating point，缩写为FP）是一种对于实数的近似值数值表现法，由一个有效数字（即尾数）加上幂数来表示，通常是乘以某个基数的整数次指数得到。以这种表示法表示的数值，称为浮点数（floating-point number）。利用浮点进行运算，称为浮点计算，这种运算通常伴随着因为无法精确表示而进行的近似或舍入。 —— [维基百科][fp]

可以简单的将浮点数理解为小数（有限或无限的），如：-0.25、π、1.99714e5 等。

## 浮点数的表示形式

IEEE 二进制浮点数算术标准（[IEEE 754][ieee754]）是目前最广泛使用的浮点数算术标准，为许多 CPU 与浮点运算器所采用。

IEEE 754 标准中，定义了五个基本的浮点数表示格式，其中包括三个二进制浮点数格式（32 位单精度、64 位双精度和 128 位四倍精度格式）和两个十进制浮点数格式。

我们通常所说的 Java 中的 float 类型即为 32 位单精度浮点类型，占 4 字节；double 类型即为 64 位双精度浮点类型，占 8 字节。

按照 IEEE 754 标准，浮点数的二进制表示由三部分组成：

1. 符号位（sign）
1. 指数位（exponent）
1. 小数位（fraction）

单精度及双精度浮点的相关格式如下：

|名称|常用名|小数位位数|指数位位数|指数偏移量|
|:--|:----|:--------|:-------|:-------|
|binary32|单精度|24|8|2^7-1=127|
|binary64|双精度|53|11|2^10-1=1023|

单精度浮点数的二进制表示形式为：

![float](/contents/float-binary-conversion/float.png)

双精度浮点数的二进制表示形式为：

![double](/contents/float-binary-conversion/double.png)

## 十进制小数转换为二进制浮点数的方法

一个小数可能由整数和小数两部分组成，如 85.125，整数部分为 85，小数部分为 0.125。在转换为二进制时，需将整数部分和小数部分分别进行转换，转换方式也略有不同。

### 转换整数部分

整数部分的转换方式，可见 [十进制整数与二进制数转换](https://alphahinex.github.io/2021/03/21/decimal-binary-conversion/)，85 转换为二进制的结果为 `1010101`。

### 转换小数部分

小数部分转换时，将小数乘 2，取乘积的整数部分放在二进制数的高位，之后将乘积去掉整数部分再重复执行前面步骤，直到乘积为 0 时终止，或者超出精度范围后终止。

以上例中的 0.125 为例，运算过程如下：

|小数部分 * 2|乘积|乘积整数部分|
|:---------|:---|:---------|
|0.125 * 2 |0.25|0|
|0.25 * 2  |0.5|0|
|0.5 * 2 | 1.0 |1|
|0.0 * 2 | 0.0 |0|

故 0.125 转换之后的结果为 `0.001`。

连接 85.125 转换后的整数和小数部分，得到 `1010101.001`。

> 因为二进制运算中，乘以 2 相当于左移一位，除以 2 相当于右移一位，故 2^(-n) 的转换也可以按如下方式计算：
> 
> * 2^(-1) = 1.0/2=0.5 => 1.0(2) << 2 = 0.1(2)
> * 2^(-2) = 0.5/2=0.25 => 0.1(2) << 2 = 0.01(2)
> * 2^(-3) = 0.25/2=0.125 => 0.01(2) << 2 = 0.001(2)
> * 2^(-4) = 0.125/2=0.0625 => 0.001(2) << 2 =0.0001(2)

### 转换为指数形式

`1010101.001` 转换为二进制的科学计数法，为 `1.010101001 * 2^6`。

### 填充符号位

以转换为单精度格式为例，先填充符号位，正数填 0，负数填 1：

![sign](/contents/float-binary-conversion/sign.png)

### 填充指数位

`1.010101001 * 2^6` 的指数为 6，单精度浮点的偏移量为 127（双精度偏移量为 1023），故指数位应填入 `127 + 6 = 133`，转换为二进制为 `10000101`，直接填入指数位中：

![exponent](/contents/float-binary-conversion/exponent.png)

### 填充小数位

小数部分直接填入空位即可：

![mantissa](/contents/float-binary-conversion/mantissa.png)

如有空闲低位，直接补零，故 85.125 的单精度浮点数二进制表示为：

![85.125](/contents/float-binary-conversion/85.125.png)

## 二进制浮点数转换为十进制

二进制浮点数转换为十进制时，可按上述过程反向运算。以单精度浮点数为例：

![single](/contents/float-binary-conversion/float.png)

符号位为 0 代表正数；

指数位为 `0111 1100` = `124`，即 `127 + (-3)`，故上述浮点数的二进制科学计数法表示为：

`1.01 * 2^(-3)` = `0.00101`

转换为十进制时，可按如下方式：

|2^(-1)|2^(-2)|2^(-3)|2^(-4)|2^(-5)|
|:-----|:-----|:-----|:-----|:-----|
|0|0|1|0|1|

即 `2^(-3) + 2^(-5) = 0.125 + 0.03125 = 0.15625`。

## 转换工具

* [IEEE-754 Floating Point Converter](https://www.h-schmidt.net/FloatConverter/IEEE754.html)
* [IEEE-754 Analysis](https://babbage.cs.qc.cuny.edu/IEEE-754/)
* [js-ieee754](https://github.com/jarvma18/js-ieee754)

## 参考资料

* [How to Convert a Number from Decimal to IEEE 754 Floating Point Representation](https://www.wikihow.com/Convert-a-Number-from-Decimal-to-IEEE-754-Floating-Point-Representation)
* [Double-precision floating-point format](https://en.wikipedia.org/wiki/Double-precision_floating-point_format)

[fp]:https://zh.wikipedia.org/wiki/%E6%B5%AE%E7%82%B9%E6%95%B0
[ieee754]:https://en.wikipedia.org/wiki/IEEE_754