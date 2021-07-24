---
id: truthy-and-falsy
title: "JavaScript 中的 Truthy 和 Falsy"
description: "可用在需要布尔类型的上下文中"
date: 2021.07.25 10:26
categories:
    - JavaScript
tags: [JavaScript]
keywords: truthy, falsy, true, false, internal method, internal slot, document.all, [[IsHTMLDDA]]
cover: /contents/truthy-and-falsy/cover.png
---

## Truthy

在 JavaScript 中，`Truthy` 是指在一个需要 Boolean 值的上下文中，会被认为是 `true` 的值，例如：

```js
> Boolean(true)
true
> Boolean({})
true
> Boolean([])
true
> Boolean(42)
true
> Boolean('0')
true
> Boolean('false')
true
> Boolean(new Date())
true
> Boolean(-42)
true
> Boolean(12n)
true
> Boolean(3.14)
true
> Boolean(Infinity)
true
> Boolean(-Infinity)
true
```

与 `Truthy` 相对的，即是 `Falsy`，所有不是 `Falsy` 的值，都是 `Truthy`。

## Falsy

完整的 JavaScript 中 falsy 值 [列表](https://developer.mozilla.org/en-US/docs/Glossary/Falsy) 如下：

|object|describe|
|:----|:-------|
|false| The keyword `false`. |
|0|The Number zero (so, also `0.0`, etc., and `0x0`). |
|-0|The Number negative zero (so, also `-0.0`, etc., and `-0x0`). |
|0n|The BigInt zero (so, also `0x0n`). Note that there is no BigInt negative zero — the negation of 0n is 0n. |
|"", '', ``|Empty string value.|
|null|null — the absence of any value.|
|undefined|undefined — the primitive value.|
|NaN|NaN — not a number.|
|document.all|Objects are falsy if and only if they have the [[IsHTMLDDA]] internal slot.That slot only exists in document.all and cannot be set using JavaScript.|

注意最后一个值：`document.all`

### Document.all

[Document.all](https://developer.mozilla.org/en-US/docs/Web/API/Document/all) 是一个不建议再被使用的特性，但为了考虑旧代码的兼容性，目前依然被保留了下来。

通过 `document.all` 获得到的是一个 `HTMLAllCollection` 对象，例如：

```js
> document.all
HTMLAllCollection(22) [html.focus-outline-visible, head, meta, title, style, custom-style, style, custom-style, style, custom-style, style, custom-style, style, style, body, ntp3p-most-visited, script, link, dom-module#cr-hidden-style, template, dom-module#cr-icons, template, cr-hidden-style: dom-module#cr-hidden-style, cr-icons: dom-module#cr-icons]
```

现代浏览器中，`Boolean(document.all)` 得到的是 `false`；在 IE11 中也是 `false`，但在更老版本的 IE 中，`Boolean(document.all)` 得到的是 `true`：

![ie11](/contents/truthy-and-falsy/ie11.png)

![ie10](/contents/truthy-and-falsy/ie10.png)

![ie5](/contents/truthy-and-falsy/ie5.png)

在老 web 页面中，经常会使用 [如下方式](https://stackoverflow.com/questions/10350142/why-is-document-all-falsy) 检测脚本是否运行在古董浏览器中：

```js
if (document.all) {
  // code that uses `document.all`, for ancient browsers
} else if (document.getElementById) {
  // code that uses `document.getElementById`, for “modern” browsers
}
```

为了兼容这种写法，最简单的方式，就是将 `document.all` 设置为 `falsy`。

从 ES9 起，ECMAScript 语言规范中添加了一个 [[[IsHTMLDDA](https://262.ecma-international.org/9.0/#sec-IsHTMLDDA-internal-slot)]] internal slot，明确了这个内部槽是专门为 `document.all` 所设，并且规范了如下操作：

1. `Boolean(document.all) === false`
1. `typeof(document.all) === 'undefined'`
1. `document.all == null && document.all == undefined && null == document.all && undefined == document.all`

### Internal slot

关于 `internal slot`，在 ES12 中有 [Object Internal Methods and Internal Slots](https://262.ecma-international.org/12.0/#sec-object-internal-methods-and-internal-slots) 专门描述，`internal slot` 相当于 Object 的内部状态，不是对象的属性，不会被继承，也没有直接访问对象的 `internal slot` 的方式。在 ES 规范中，internal method 和 internal slot 均通过双中括号 `[[ ]]` 的形式来表示。

这部分内容不太好理解，Stack Overflow 上也有 [What is an “internal slot” of an object in JavaScript?](https://stackoverflow.com/questions/33075262/what-is-an-internal-slot-of-an-object-in-javascript) 的提问，感兴趣的读者可以再深入挖掘一下。

## Truthy 之间和 Falsy 之间值的比较

> 这里的比较指的是 `x == y` 的形式，非严格等于（`===`）。

可以参照 [Abstract Equality Comparison](https://262.ecma-international.org/12.0/#sec-abstract-equality-comparison) 提供的算法。

Truthy 一般包含具体的数据值，如果类型相同，直接执行严格等于的比较；如果类型不同，一般会先进行类型转换。

Falsy 中：

1. `false`、`0`、`''` 互等
1. `null`、`undefined` 和 `document.all` 互等，但不与 false、0 或空字符串相等
1. x 或 y 中有任意一个值为 `NaN`，比较结果即为 false