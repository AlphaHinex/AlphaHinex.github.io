---
id: use-stream-to-find-duplicated-elements
title: "使用 Java 8 Stream 优雅的找出重复数据"
description: "用 Stream API 提升代码表达力"
date: 2021.12.05 10:34
categories:
    - Java
tags: [Java, Stream]
keywords: stream, java, 重复, 重复数据, 重复元素
cover: /contents/covers/use-stream-to-find-duplicated-elements.png
---

原文地址：https://wyiyi.github.io/amber/2021/11/30/stream/

最近经常遇到问题：要获取到集合中某一属性值重复的数据，除了for 循环，还有更简单得处理方式？

先来引入 Stream 流的概念。
 
## Stream 阐述
` Stream API(java.util.stream.*)` 是 Java 8 中新增重要特性。
Stream 将要处理的元素集合看作一种流，由于`java.util.stream.Stream` 是一个 `Interface` ，在其中提供了函数方法，
使流在管道中进行一系列处理（如过滤，映射，聚合等）后生成的结果集合，类似于在数据库执行 SQL 语句。
这个过程通常不会对数据源造成影响。
 ```
 List<String> myList = Arrays.asList("a1", "a2", "b1", "c2", "c1");
   myList.stream()
     .filter(s -> s.startsWith("c"))
     .map(String::toUpperCase)
     .sorted()
     .forEach(System.out::println);    // C1 C2
 ```
在以上示例中, 创建 Stream 流，filter，map 和 sorted 是中间操作，而 forEach 是一个终端操作。Stream操作链称为操作管道。

## Stream 用法

 可以从各种数据源中创建 Stream 流，其中以 Collection 集合最为常见。
 如 List 和 Set 均支持 stream() 方法来创建顺序流 stream() 或者是并行流 parallelStream()。
### 一、常用创建 Stream 流方法 
1.使用 Collection 下的 stream() 和 parallelStream() 方法来创建 Stream
 ```
 List<String> list = new ArrayList<>();
 Stream<String> stream = list.stream(); //获取一个顺序流
 Stream<String> parallelStream = list.parallelStream(); //获取一个并行流
 ```
2.Arrays 提供了创建流的静态方法 stream()，将数组转成流
 ```
 Integer[] nums = new Integer[10];
 Stream<Integer> stream = Arrays.stream(nums);
 ``` 
3.使用 Stream 中的静态方法：of()、iterate()、generate()
 ``` 
 Stream<Integer> stream = Stream.of(1,2,3,4,5,6);
 
 Stream<Integer> stream2 = Stream.iterate(0, (x) -> x + 2).limit(6);
 stream2.forEach(System.out::println); // 0 2 4 6 8 10
 Stream<Double> stream3 = Stream.generate(Math::random).limit(2);
 stream3.forEach(System.out::println);
 ``` 
4.使用 Pattern.splitAsStream() 方法，将字符串分隔成流
  ``` 
 Pattern pattern = Pattern.compile(",");
 Stream<String> stringStream = pattern.splitAsStream("a,b,c,d");
 stringStream.forEach(System.out::println);
 ``` 
5.一些类也提供了创建流的方法:
 ``` 
 IntStream.range(start, stop);
 BufferedReader.lines();
 Random.ints();
 ``` 
### 二、中间操作 Stream 流
1.filter：用于通过设置的条件过滤出元素，其中`java.util.Objects`提供了空元素的过滤
  
2.映射 map 方法用于映射每个元素到对应的结果

3.排序 sorted：使用 `java.util.Comparator`或者 `reversed` 更方便的对流进行升降排序

4.distinct：通过流中元素的 hashCode() 和 equals() 去除重复元素

5.skip(n)：跳过n元素，配合limit(n)可实现分页

6.limit(n)：用于获取指定数量的流...

### 三、终端操作 Stream 流
1.forEach()  迭代流中的每个元素，`java.util.function.Consumer`接受参数没有返回值
 ```
 Stream.of(1,2,3,4,5).forEach(System.out::println);
 ```
2.collect() 可用于返回列表或字符串，`java.util.Collectors` 类中有求和、计算均值、取最值、字符串连接等多种收集方法。
 ```
 List<String> strings = Arrays.asList("abc", "", "bc", "efg", "abcd", "", "jkl");
 List<String> count = strings.stream().filter(string -> string.isEmpty()).collect(Collectors.toList());
 System.out.println(count.size()); // 2    
 ```
3.reduce 用于对stream中元素进行聚合求值，操作函数 accumulator 接受两个参数x,y返回r
    
4.anyMatch()、allMatch()、noneMatch() 接收参数Predicate，返回boolean。

5.findFirst()、findAny()、count()、max()、min() ...

## 使用 Stream 流解决集合中数据重复问题	
我们以 Employee 为实体，对比 获取重复code值的 写法：

Employee 实体：
 ```
public class Employee extends Model<Employee> {
    @ApiModelProperty(value = "ID")
    @TableField("ID")
    private Long id;
    @ApiModelProperty(value = "编码")
    @TableId("CODE")
    private String code;
    @ApiModelProperty(value = "姓名")
    @TableField("NAME")
    private String name;
    @ApiModelProperty(value = "年龄")
    @TableField("AGE")
    private Integer age;
    ...  
}	
 ```
  
for 写法：

 ```
 List<String> duplicate_code = new ArrayList<>();
 List<Employee> employeeList = fromDB();
 if (employeeList.size() > 0) {
     for (int i = 0; i < employeeList.size(); i++) {
         Employee employee = employeeList.get(i);
         for (Employee entity : employeeList) {
             String code = entity.getCode();
             if (StringUtils.isBlank(code) && StringUtils.isBlank(employee.getCode()) && code.equals(employee.getCode())) {
                duplicate_code.add(code);
             }
         }
     }
 }
 ```
 
 Stream 写法：

 ```
 List<String> duplicate_code = new ArrayList<>();
 List<Employee> employeeList = fromDB();
 Map<Object, Long> map = employeeList.stream().collect(Collectors.groupingBy(employee -> employee.getCode(), Collectors.counting()));
 Stream<Object> stringStream = map.entrySet().stream().filter(entry -> entry.getValue() > 1).map(entry -> entry.getKey());
 stringStream.forEach(str -> {
    duplicate_code.add(String.valueOf(str));
 });
 ```
  
由此可见，使用Java 8 的 Stream 流方式获取到集合中某一属性值重复数据的问题更方便、简洁！

**了解更多有关 Java8 Stream 流的相关信息，请参考 [Stream Javadoc 阅读官方文档](https://docs.oracle.com/javase/8/docs/api/)。**