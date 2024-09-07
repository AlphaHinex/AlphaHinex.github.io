---
id: java-reflection
title: "【转】掌握 Java 反射机制"
description: "通过实例讲解 Java 反射机制的基本概念、常用类和应用场景。"
date: 2024.09.08 10:26
categories:
    - Java
tags: [Java]
keywords: reflection, Field, Method, Class, proxy, annotation, dynamic proxy, InnocationHandler
cover: https://wyiyi.github.io/amber/contents/2024/reflection.JPEG
---

原文地址：https://wyiyi.github.io/amber/2024/09/01/Reflection/

## 反射机制概述
`Java` 反射机制允许程序在运行时取得任何类的内部信息，并能直接操作任意对象的内部属性及方法。

### 反射机制常用的类
- `java.lang.Class`：代表类和接口，提供了获取类信息的方法。
- `java.lang.reflect.Constructor`：代表类的构造函数。
- `java.lang.reflect.Field`：代表类的成员变量。
- `java.lang.reflect.Method`：代表类的方法。
- `java.lang.reflect.Modifier`：访问修饰符的查询。


## Class 类
在 `Java` 中，`Class` 类用于表示类的字节码。它是反射的入口，包含了与类有关的信息。

`Class` 对象在类加载时由 `Java` 虚拟机自动创建。

可以通过以下几种方式获取：

1. 使用`Class.forName()` 通过类的全限定名：
```Java
Class<?> cls = Class.forName("java.lang.String");
```
2. 使用`.class`语法：
```Java
Class<?> cls = String.class;
```
3. 使用`object.getClass()`方法：
```Java
String s = "Hello";  
Class<?> cls = s.getClass();
```


## 通过反射创建对象

可以通过以下方式创建对象：

1. `Class.newInstance()`：使用 `Class` 对象的 `newInstance()` 方法，要求类有一个无参的构造器，并且构造器是可访问的。
2.  `Class.getConstructor()` 和 `newInstance()`：使用 `Class` 对象的 `getConstructor()` 方法获取指定的构造器，在调用 `newInstance()` 方法，可以传递参数给构造器。
3. `Constructor.newInstance(Object... initargs)`：适用于已经存在`Constructor` 对象，使用 `Constructor` 对象的 `newInstance()` 方法，可以直接传递参数给构造器。


## 通过反射操作属性和方法
反射允许访问和操作类的私有属性和方法：

### 访问字段：使用 `Field` 类的 `get` 和 `set` 方法。

1. 获取目标类的 `Class` 对象
```Java
Class<?> clazz = Class.forName("com.example.TargetClass");
```
2. 使用 `Class` 对象的 `getDeclaredField()` 方法来获取指定的私有字段
```Java
Field field = clazz.getDeclaredField("fieldName");
```
3. 设置 `Field` 对象的可访问性（如果字段是私有的）
```Java
field.setAccessible(true);
```
4. 创建目标类的实例（如果字段不是静态的）
```Java
Object obj = clazz.getDeclaredConstructor().newInstance();
```
5. 通过 `Field` 对象读取字段的值
```Java
Object value = field.get(obj);
```
6. 通过 `Field` 对象修改字段的值
```Java
// 假设 newValue 是要设置的新值
field.set(obj, newValue); 
```

### 访问方法：使用 `Method` 类的 `invoke` 方法。


1. 获取目标类的 `Class` 对象
```Java
Class<?> clazz = Class.forName("com.example.TargetClass");
```
2. 使用 `Class` 对象的 `getDeclaredMethod()` 方法来获取指定的私有方法
```Java
Method method = clazz.getDeclaredMethod("privateMethodName", int.class);
```
3. 设置 `Method` 对象的可访问性（如果方法是私有的）
```Java
method.setAccessible(true);
```
4. 创建目标类的实例（如果方法不是静态的）
```Java
Object obj = clazz.getDeclaredConstructor().newInstance();
```
5. 通过 `Method` 对象调用目标对象的方法，可以传递参数
```Java
Object returnValue = method.invoke(obj, 10); // 假设方法需要一个 int 类型的参数
```
  
## 反射应用场景
1. 框架开发：如 Spring 框架使用反射来实现依赖注入（DI）和面向切面编程（AOP）。
2. 动态代理：Java 的代理模式可以通过反射实现动态代理，这在许多框架中也十分常见。
3. 对象序列化与反序列化：在序列化和反序列化过程中，可能会用到反射来创建对象和恢复对象状态。
4. 数据库访问框架：如 Hibernate、MyBatis 等框架，通过反射来映射数据库表和 Java 对象。
5. 工具类开发：例如 JavaBean 的属性拷贝工具，通过反射来获取和设置属性值。
6. 测试工具：如 JUnit，通过反射来运行测试用例。

## 反射应用实例

### 获得自定义注解标记点属性并赋值

1. 自定义注解类 `MyAnnotation`

```java
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
public @interface MyAnnotation {
    String value() default "default";
}
```

2. 定义一个类，在类的属性上使用注解 `MyClass`

```java
public class MyClass {
    @MyAnnotation(value = "initialValue")
    private String annotatedField;

    public MyClass() {
        this.annotatedField = "initialValue";
    }

    public String getAnnotatedField() {
        return annotatedField;
    }

    public void setAnnotatedField(String annotatedField) {
        this.annotatedField = annotatedField;
    }
}
```

3. 获得自定义注解标记点属性并赋值

```java
import java.lang.reflect.Field;

public class ReflectionExample {
    public static void main(String[] args) throws Exception {
        MyClass obj = new MyClass();
        Class<?> clazz = obj.getClass();

        // 获取 MyClass 中所有声明的字段
        Field[] fields = clazz.getDeclaredFields();
        for (Field field : fields) {
            // 检查字段是否带有 MyAnnotation 注解
            if (field.isAnnotationPresent(MyAnnotation.class)) {
                // 获取注解
                MyAnnotation annotation = field.getAnnotation(MyAnnotation.class);
                // 获取注解的值
                String value = annotation.value();
                System.out.println("Annotation value: " + value); //输出：Annotation value: initial_value

                // 设置字段可访问（如果字段是私有的）
                field.setAccessible(true);
                // 修改字段的值
                field.set(obj, "newValue");
                System.out.println("New field value: " + field.get(obj)); // 输出：New field value: newValue
            }
        }
    }
}
```

### 使用反射创建接口的动态代理类

1. 定义一个接口（不定义实现类）`SimpleInterface`

```Java
public interface SimpleInterface {

    String sayHello(String name);
}
```

2. 创建动态代理类，实现SimpleProxyHandler 接口，用于修改方法的返回值

```Java
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;

public class SimpleProxyHandler implements InvocationHandler {

    private Object target;

    public SimpleProxyHandler(Object target) {
        this.target = target;
    }

    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        System.out.println("Before method call: " + method.getName());

        Object result = method.invoke(target, args);

        System.out.println("After method call: " + method.getName());

        return result;
    }
}
```

3. 使用反射创建接口的动态代理类，并调用接口方法得到结果

```Java
public static void main(String[] args) {
        SimpleInterface proxyInstance = (SimpleInterface) Proxy.newProxyInstance(
                SimpleInterface.class.getClassLoader(),
                new Class<?>[]{SimpleInterface.class},
                new SimpleProxyHandler(new SimpleInterface() {

                    // 匿名内部类实现SimpleInterface接口
                    @Override
                    public String sayHello(String name) {
                        return "Hello, " + name + "!";
                    }
                })
        );

        String greeting = proxyInstance.sayHello("World");
        System.out.println(greeting); // 输出: Hello, World!
    }
```


### 使用动态代理修改接口实现

1. 自定义接口 `SimpleInterface` 和实现类 `SimpleInterfaceImpl`

```Java
public interface SimpleInterface {

    int performOperation(int a, int b);
}
```

```Java
public class SimpleInterfaceImpl implements SimpleInterface{
    @Override
    public int performOperation(int a, int b) {
        return a + b;
    }

    @Override
    public String sayHello(String name) {
        return "Hello, " + name;
    }
}
```

2. 创建一个动态代理类，实现`InvocationHandler`接口，用于修改方法的返回值

```Java
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;

public class SimpleInterfaceHandler implements InvocationHandler {
    private final Object target;

    public SimpleInterfaceHandler(Object target) {
        this.target = target;
    }

    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        Object result = method.invoke(target, args);

        // 修改返回值：将结果 * 2
        if (result instanceof Integer) {
            result = (Integer) result * 2;
        }

        return result;
    }
}
```

3. 使用动态代理来修改实现类中的方法行为

```Java
public static void main(String[] args) {
        SimpleInterface implementation = new SimpleInterfaceImpl();

        SimpleInterface proxyInstance = (SimpleInterface) Proxy.newProxyInstance(
                SimpleInterface.class.getClassLoader(),
                new Class<?>[]{SimpleInterface.class},
                new SimpleInterfaceHandler(implementation)
        );

        int result = proxyInstance.performOperation(5, 3);

        System.out.println("Result of operation: " + result); // 输出: Result of operation: 16
    }
```
