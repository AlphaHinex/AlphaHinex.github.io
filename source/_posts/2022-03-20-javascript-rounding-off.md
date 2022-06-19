---
id: javascript-rounding-off
title: "JS 中的四舍五入"
description: "通过最小的浮点数或科学记数法减少误差"
date: 2022.03.20 10:34
categories:
    - JavaScript
tags: [JavaScript]
keywords: js, 四舍五入, toFixed, Number.EPSILON
cover: /contents/covers/javascript-rounding-off.jpeg
---

由于 JS 中 Number 对象的 toFixed 方法在对某些值进行四舍五入计算时 [存在误差](https://alphahinex.github.io/2021/07/04/to-fixed/)，而这种误差在进行货币金额计算时是不能接受的，那么在 JS 中我们应该如何正确的进行四舍五入呢？

以保留两位小数为例，选取几种典型的方法，其中 `n` 为要进行四舍五入运算的浮点数。

## 方法 A

为 n 添加一个小的偏移量，再进行四舍五入：

```js
(n + Number.EPSILON).toFixed(2)
```

## 方法 B

保留两位小数时，先将 n 扩大 10^2 倍，然后通过 `Math.round` 获得最接近的整数，缩小 10^2 倍后再进行四舍五入：

```js
(Math.round(n * 100) / 100).toFixed(2)
```

## 方法 C

为 n 添加一个小的偏移量后，再进行方法 B 中的操作：

```js
(Math.round((n + Number.EPSILON) * 100) / 100).toFixed(2)
```

## 方法 D

通过科学记数法进行方法 B 的操作：

```js
(+(Math.round(n + "e2")  + "e-2")).toFixed(2)
```

## 对比计算结果

|n                   |期望值|方法 A   |方法 B  |方法 C   |方法 D   |
|:-------------------|:----|:-------|:-------|:-------|:-------|
|0.995               |1.00 |1.00 (√)|1.00 (√)|1.00 (√)|1.00 (√)|
|2.005               |2.01 |2.00 (X)|2.01 (√)|2.01 (√)|2.01 (√)|
|5.475               |5.48 |5.47 (X)|5.48 (√)|5.48 (√)|5.48 (√)|
|1.005               |1.01 |1.01 (√)|1.00 (X)|1.01 (√)|1.01 (√)|
|9.495               |9.50 |9.49 (X)|9.49 (X)|9.49 (X)|9.50 (√)|
|0.014999999999999965|0.01 |0.02 (X)|0.01 (√)|0.02 (X)|0.01 (√)|
|1.496e-7            |0.00 |0.00 (√)|0.00 (√)|0.00 (√)|NaN  (X)|

可以看到，每种方法都有计算结果与预期不符的情况，但方法 D 仅在 n 只能使用科学计数法进行表示时才会出现与预期不符（`NaN`）的情况。

## 负数

当 n 为负数时，直接使用上面的四个方法均得不到正确的结果，因为上面的方法主要是采用增加偏移量和 `Math.round` 来进行计算的。

|n                   |期望值|方法 A   |方法 B  |方法 C   |方法 D   |
|:-------------------|:----|:-------|:-------|:-------|:-------|
|-1.125              |-1.13|-1.12(X)|-1.12(X)|-1.12(X)|-1.12(X)|

n 为正数时，增加偏移量，n 为负数时，应该减少偏移量；

`Math.round` 在小数部分为 `0.5` 时，会取下一个最接近正无穷的最小整数：

> If the fractional portion is exactly 0.5, the argument is rounded to the next integer in the direction of +∞. **Note that this differs from many languages' round() functions, which often round this case to the next integer away from zero**, instead giving a different result in the case of negative numbers with a fractional part of exactly 0.5.

**如果 n 为负数，可先取绝对值后用上述方法进行四舍五入，之后再将结果转换为负数。**

## 结论

总体来说，方法 D 的适用性最好，可以用来作为在 JS 中进行四舍五入运算的主要方式。

```js
# n 为浮点数，代表要四舍五入的数
# m 为整数，代表小数部分保留的位数

n > 0 ? (+(Math.round(n + "e" + m)  + "e-" + m)).toFixed(m) : -((+(Math.round(-n + "e" + m)  + "e-" + m)).toFixed(m))
```