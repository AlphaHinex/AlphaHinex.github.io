---
id: this-in-javascript
title: "【转】探索前端的 this 指向"
description: "本文将深入探讨 this 在前端开发中的应用场景以及不同情况下的指向规则，更好地理解和运用 this 指向。"
date: 2023.09.03 10:34
categories:
    - JavaScript
tags: [JavaScript]
keywords: this, use strict, call, apply, bind, context, function, class, global
cover: /contents/covers/this-in-javascript.jpg
---

原文地址：https://wyiyi.github.io/amber/2023/09/01/this/

在前端开发中，this 是一个常见的概念。
它代表了当前执行上下文中的对象或函数，并且在不同的情况下，this 的指向也会有所不同。

本文将深入探讨 `this` 在前端开发中的应用场景以及不同情况下的指向规则，更好地理解和运用 `this` 指向。

# 小试牛刀
## 1、普通函数、箭头函数组合使用

```js
var name = "TOM"
let obj={
  name:"Jerry",
  SayHi:()=>{
   return function(){
      console.log(this.name) //问题1 这个this又指向谁
    }
  },
  SayFoo:function(){
    return ()=>{
      console.log(this.name) //问题2 这个this又指向谁
    }
  }
}
obj.SayHi()()
obj.SayFoo()()
```

## 2、改变 this 指向

```js
var name = 'win';
const obj = {
    name: 'obj',
    a: () => {
        console.log(this.name);
    }
};
const obj1 = {
    name: 'obj1'
};
obj.a.call(obj1);
```

别急，答案和解析逐步揭晓。

# this 
在 `JavaScript` 中，函数的 `this` 关键字与其他语言有一些不同。
它也在[严格模式](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Strict_mode)和非严格模式下有一些区别。

在大多数情况下，`this` 的值取决于函数的调用方式（运行时绑定）。
`this` 不能在执行期间被赋值，在每次函数被调用时 this 的值也可能会不同。

# 语法
`this` 的值取决于它出现在哪个上下文中：函数、类、或者全局。

- 在非严格模式下，始终是对象的引用。当函数被调用时，`JavaScript` 会自动设置 `this` 的值。
  - 如果函数作为对象的方法调用，`this` 指向该对象
  - 如果函数独立调用，`this` 指向全局对象
  
- 在严格模式下，它可以是任何值。`this` 的值不再是默认绑定到全局对象，而是根据调用方式和上下文来确定。
  - 如果函数作为对象的方法调用，this 将绑定到该对象
  - 如果使用 `call()`、`apply()` 或 `bind()` 显示指定 `this` 值，将绑定到相应的值
  - 如果函数是使用构造函数调用，`this` 将绑定到新创建的对象
  - 对于箭头函数，没有自己的 `this` 绑定，而是集成了外部函数的 `this` 值

## 函数上下文

函数中的 `this` 的值取决于函数的调用方式，可将 `this` 视为函数的隐藏参数，就像函数定义中声明的参数一样，当函数体被执行时，会创建这个绑定 `this`。

- 对象方法调用：如果函数是作为对象的方法调用时，`this` 指向调用该方法的对象。换句话说，如果函数调用形式为 `obj.f()`，那么 `this` 指向 `obj`。

    ```js
    const obj = {
      name: "John",
      greet: function() {
        console.log("Hello, " + this.name + "!"); // this 指向 obj 对象
      }
    };
    
    obj.greet(); // 输出 "Hello, John!"
    ```
  
- 函数调用：如果函数是作为普通函数调用时，this 指向全局对象。
  
    ```js
    function sayHello() {
        console.log("Hello, " + this.name + "!"); // this 指向全局对象
    }
    sayHello(); // 输出 "Hello, undefined!"（假设全局对象的 name 属性未定义）
    ```

## 回调
当函数被作为回调传递时，`this` 的值取决于回调的调用方式，这由 API 实现者决定。

通常情况下，回调函数会以 `undefined` 作为 `this` 值进行调用（直接调用而没有附加到任何对象上），这意味着如果函数是非严格模式的话，`this` 的值就是全局对象（`globalThis`）。
[迭代数组方法](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array#iterative_methods) 和 [Promise()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/Promise) 构造函数等都是这种情况。

```js
function logThis() {
  "use strict";
  console.log(this);
}

[1, 2, 3].forEach(logThis); // undefined, undefined, undefined
```

有些 API 允许你为回调的调用设置 `this` 值。
如：所有迭代数组方法以及相关的方法如 [Set.prototype.forEach()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Set/forEach) 都接受一个可选的 `thisArg` 参数。

```js
[1, 2, 3].forEach(logThis, { name: "obj" });
// { name: 'obj' }, { name: 'obj' }, { name: 'obj' }
```

偶尔，某些回调会以非 `undefined` 的值作为 `this` 进行调用。
如：[JSON.parse()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON/parse) 的 `reviver` 参数和 [JSON.stringify()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON/stringify) 的 `replacer` 参数会以当前被解析/序列化属性所属的对象作为 `this` 进行调用。

## 箭头函数
[箭头函数](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/Arrow_functions) 通过继承封闭上下文的 `this` 值来简化函数的定义。
换句话说，它们不会创建自己的 `this` 绑定，而是将 `this` 捕获为函数创建时的值，无论如何调用函数，`this` 都将保持不变。

在全局代码中，无论是否使用严格模式，`this` 始终是 `globalThis`，这是由于全局上下文的绑定：
```js
const globalObject = this;
const foo = () => this;
console.log(foo() === globalObject); // true
```

当使用 [call()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function/call)、[apply()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function/apply) 或 [bind()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function/bind) 调用箭头函数时，`thisArg` 参数会被忽略。但仍然可以使用这些方法传递其他参数。

区别：
call 和 apply 调用时候立即执行，bind 调用返回新的函数。
当需要传递参数时候，call 直接写多个参数，apply 将多个参数写成数组，
bind 在绑定时候需要固定参数时候，也是直接写多个参数。

```js
const obj = { name: "obj" };

// 使用 call 设置 this
console.log(foo.call(obj) === globalObject); // true

// 使用 bind 设置 this
const boundFoo = foo.bind(obj);
console.log(boundFoo() === globalObject); // true
```

## 构造函数
当函数作为构造函数使用（使用 `new` 关键字），它的 `this` 会绑定到正在构建的新对象上，而不管构造函数在哪个对象上被访问。
`this` 的值将成为 `new` 表达式的值，除非构造函数返回另一个非原始值。

```js
function C() {
  this.a = 37;
}

let o = new C();
console.log(o.a); // 37

function C2() {
  this.a = 37;
  return { a: 38 };
}

o = new C2();
console.log(o.a); // 38
```

在上面 C2 的例子中，由于构造过程中返回了一个对象，因此绑定到 `this` 的新对象被丢弃了。
（这实际上使语句 `this.a = 37`; 成为无效代码。虽然它被执行了，但可以被消除而没有外部影响。）

### super 
在使用 `super.method()` 形式调用函数时，
方法函数内部的 `this` 的值与 `super.method()` 调用周围的 `this` 值相同，并且通常与 `super` 引用的对象不相等。
因为 `super.method` 不是像上述的对象成员访问一样，它是具有不同绑定规则的特殊语法。
详细示例，请参阅 [super 的相关文档](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/super#calling_methods_from_super)。

简而言之，super 可以用来访问和调用父类的内容。

## 类上下文
一个类可以拆分为两个上下文：静态和实例。
- [构造函数](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes/constructor)、方法和实例字段初始值设定项（公共或私有）属于实例上下文。
- [静态](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes/static)方法、静态字段初始值设定项和[静态初始化块](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes/Static_initialization_blocks)属于静态上下文。
`this` 的值在每个上下文中的值都不同。

```js
class C {
  instanceField = this;
  static staticField = this;
}

const c = new C();
console.log(c.instanceField === c); // true
console.log(C.staticField === C); // true
```

## 派生类构造函数
与基类构造函数不同，派生构造函数没有初始的 `this` 绑定。
调用 [super()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/super) 会在构造函数内部创建一个 `this` 绑定。
其中，`Base` 是基类。

```js
this = new Base();
```

**警告**：在调用 `super()` 之前引用 `this` 将会抛出错误。

派生类必须在调用 `super()` 之前不返回任何值，除非构造函数返回一个对象（因此覆盖了 [this]() 值），或者该类根本没有构造函数。
```js
class Base {}
class Good extends Base {}
class AlsoGood extends Base {
  constructor() {
    return { a: 5 };
  }
}
class Bad extends Base {
  constructor() {}
}

new Good();
new AlsoGood();
new Bad(); // 报错：必须在派生类构造函数中调用 super() 才能访问 'this' 或返回出派生构造函数。
```

## 全局环境

在全局环境下，`this` 值取决于脚本执行的上下文中运行。`this` 指向全局对象（通常是 window 对象）。
指在浏览器环境中，全局作用域下使用 this 可以直接访问 window 对象的属性和方法。

在脚本的顶层，`this` 引用 [globalThis](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/globalThis) 无论是否处于严格模式，这通常与全局对象相同。
 
```js
console.log(this === window); // true
 ```

# 公布答案及解析，你的战绩如何？
## 小试牛刀 1

**答案**：TOM、Jerry

**解析**：
问题1：`SayHi` 函数返回一个新的匿名函数，所以主要看谁调用了它，没人具体的调用者，所以this 指向 window。
问题2：`SayFoo` 函数返回一个新的匿名箭头函数，所以主要看定义该箭头函数其父级的 this，其父级的 this 指向的是该函数的调用者，所以 this 指向 obj。

## 小试牛刀 2

**答案**：win。

**解析**：
使用箭头函数定义了对象 obj 的属性 a。
箭头函数不会绑定自己的 this 值，而是继承外层作用域的 this 值。
在全局作用域中，this 指向全局对象（例如浏览器中的 window 对象），所以 this.name 实际上是在全局作用域中查找 name 变量的值。
在 obj1 对象上使用了 call 方法来显式设置 obj.a 函数中的 this 值为 obj1，但由于箭头函数不受 this 绑定的影响，它仍然会继承全局作用域中的 this 值。

# Ending...
要正确理解和使用 this，需要了解当前代码的执行上下文，合理运用 this 指向，使得代码更加灵活和易于维护。

了解更多请参考[文档](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/this#description)。
希望这篇文章对您理解和使用 this 有所帮助。