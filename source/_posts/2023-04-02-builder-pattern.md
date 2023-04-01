---
id: builder-pattern
title: "Builder Pattern"
description: "Builder 设计模式是一种创建型设计模式，它允许您创建不同类型和表示的对象，同时避免构造函数污染和过多的可选参数。在本文中，我们将深入探讨 Builder 设计模式的概念、实现和使用场景。"
date: 2023.04.02 10:34
categories:
    - Design Patterns
tags: [Design Patterns]
keywords: Design Patterns, Builder, Product, ConcreteBuilder, Director
cover: /contents/covers/builder-pattern.png
---

原文地址：https://wyiyi.github.io/amber/2023/04/01/builderPattern/

# Builder Pattern 

## Builder Pattern ？
Builder 设计模式是一种创建型设计模式，旨在处理相对复杂的对象的构造。也称 **建造者模式**。

Builder 模式可以通过使用另一个对象（生成器）来构造对象来分离实例化过程。

这样就可以使用相同的构建过程来创建不同类型和表示的对象。

### 意图
将一个复杂对象的构建与它的表示分离，使得同样的构建过程可以创建不同的表示。

### 适用性
在以下情况使用 Builder 模式：
- 当创建复杂对象的算法应该独立于该对象的组成部分以及它们的装配方式时
- 当构造过程必须允许被构造的对象有不同的表示时

### 结构
![](/contents/covers/builder-pattern.png)

- Product：表示被构造的复杂对象；包含定义组成部件的类，包括将这些部件装配成最终产品的接口。
- Builder：为创建一个 Product 对象的各个部件指定抽象接口。如：制造商、发动机、颜色、轮子、价格属性。
- ConcreteBuilder: 实现 Builder 的接口以构造和装配该产品的各个部件；定义并明确它所创建的表示；提供一个检索产品的接口。
如：梅特赛斯的厂家、V8的引擎、红颜色、4个轮子、50的价格。
- Director: 构造一个使用 Builder 接口的对象。如：驾车的人员。
  它包含一个负责组装的方法 void Construct(Builder builder)，
  在这个方法中调用 builder 的方法，并进行设置 builder，
  就可以通过 builder的 getProduct() 方法获得最终的产品。

## Builder Pattern 实现
1、 当前汽车类 Car 是由制造商、发动机、颜色、轮子、价格组成。

注意访问修饰符声明为 private，因为不希望外部能直接访问这个类，
构造函数也是私有的，只有分配给此类的生成器才能访问它。
构造函数中设置的所有属性都是从我们作为参数提供的构建器对象中提取的。
````java
@Data
public class Car {
    private String make;
    private String engine;
    private String color;
    private int wheels;
    private int price;
    public static class CarBuilder {
        // builder code
    }
}
````

2、 在类中定义静态内部类 CarBuilder 
````java
public static class CarBuilder {
        private Car car = new Car();
        public CarBuilder() {
        }
        public CarBuilder addMake(String make) {
            this.car.setMake(make);
            return this;
        }
        public CarBuilder addEngine(String engine) {
            this.car.setEngine(engine);
            return this;
        }
        public CarBuilder addColor(String color) {
            this.car.setColor(color);
            return this;
        }
        public CarBuilder addWheels(int wheels) {
            this.car.setWheels(wheels);
            return this;
        }
        public CarBuilder addPrice(int price) {
            this.car.setPrice(price);
            return this;
        }
        public Car build() {
            return this.car;
        }
    }
````

3、 build 方法调用外部类的私有构造函数，并将自身作为参数传递，
输入对应值的信息，最终构建出我们需要的汽车信息。
````java
public static void main(String[] args) {
    Car car = new Car.CarBuilder()
            .addMake("梅特赛斯")
            .addEngine("V8")
            .addColor("red")
            .addWheels(4)
            .addPrice(50)
            .build();
    System.out.println(car); 
}
````

4、 输出日志信息：
````
Car(make=梅特赛斯, engine=V8, color=red, wheels=4, price=50)
````

## 简单写法：lombok的 @Builder 注解
CarBuilder 内部类似乎有点繁琐，使用 `lombok` 的 `@Builder` 注解，即可省去手写 CarBuilder 内部类。

lombok 的 @Builder 注解是一种实现 builder 设计模式的方式。

lombok 的 @Builder 注解可以生成一个构造器类，通过这个类使用链式调用的方式就可以初始化该对象。
````java
import lombok.Builder;
import lombok.Data;
@Data
@Builder
public class Car {
    private String make;
    private String engine;
    private String color;
    private int wheels;
    private int price;
}
````
````java
public static void main(String[] args) {
    Car car =  Car.builder()
            .make("梅特赛斯")
            .engine("V8")
            .color("red")
            .wheels(4)
            .price(50)
            .build();
    System.out.println(car);
}
````
使用注解可以看到编译后的代码，输出日志与手写一致，均能获得到汽车相关信息。

## [Spring—ResponseEntity.BodyBuilder](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/http/ResponseEntity.BodyBuilder.html "Spring—ResponseEntity.BodyBuilder")
在 Spring 中 Builder 的设计模式也有体现，在 `ResponseEntity`
类中提供了 BodyBuilder 接口，用于构建 HTTP 响应，包括：状态码 status()、头信息 header() 和 响应体 body() 等。

### 如何构建
根据请求的不同情况来设置不同的状态码和响应体，以及添加不同的头信息，并使用 builder.build() 方法来构建最终的 ResponseEntity 对象。

1. 创建一个 HTTP 状态码为 200 的响应体
```java
ResponseEntity.BodyBuilder builder = ResponseEntity.ok();
```
2.  使用 builder 对象来设置响应体的内容，使用`builder.body()`方法来设置响应体的主体内容
```java
builder.body("Hello World");
```
3. 使用 builder.header() 方法来设置响应头，自定义设置成响应头
```java
builder.header("Content-Type", "text/plain");
```
4. builder.build() 方法来构建最终的 ResponseEntity 对象。构建一个 HTTP 状态码为 200、响应体为 `"Hello World"` 、自定义响应头 `"Content-Type", "text/plain"` 的响应体：
```java
@GetMapping("/hello")
public ResponseEntity<String> hello() {
        ResponseEntity.BodyBuilder builder = ResponseEntity.ok();
        builder.header("Content-Type", "text/plain");
        builder.body("Hello, World!");
        return builder.build();
  }
```

## 参考文档

- [设计模式-可复用面向对象软件的基础](https://book.douban.com/subject/34262305/)
- [Builder Design Pattern](https://www.baeldung.com/creational-design-patterns#builder)
- [ResponseEntity.BodyBuilder](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/http/ResponseEntity.BodyBuilder.html)