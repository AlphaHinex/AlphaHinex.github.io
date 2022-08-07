---
id: mybatis-plus-update-null
title: "解决Mybatis-Plus更新对象时字段更新为空值的问题"
description: "三种可以将字段更新为空值的方法"
date: 2022.08.07 10:34
categories:
    - Java
tags: [MyBatis, MyBatis-Plus]
keywords: MyBatis-Plus, update, null, @TableField, UpdateWrapper, GlobalConfiguration
cover: /contents/covers/mybatis-plus-update-null.png
---

## 问题
mybatis-plus（简称：mp）执行更新操作，将某些字段值置为 空 或者 null，持久层执行后，需要更新为空值的字段仍然保持原本的值。 
显然和我们预期的结果不一致。

**我们可以参照以下三种方案处理 mp 执行更新操作空值的情况。**

## 方案一：注解方式
针对实体类中字段的注解，在 [mybatis-plus 的 @TableField](https://www.mybatis-plus.com/guide/annotation.html#tablefield)
有 FieldStrategy-字段验证策略 和 FieldFill-自动填充 两种方式：

FieldStrategy 字段策略的3个使用场景：
- insertStrategy insert操作时的字段策略，是否进行空值判断，插入空值
- updateStrategy update操作时的字段策略，是否进行空值判断，插入空值
- whereStrategy where条件组装时的字段策略，是否进行控制判断，将空值作为查询条件

这里我们主要说 mp 执行更新操作，某一字段值为空未被更新的情况：
就是注解中的：`updateStrategy` 和 `fill` 两个属性。

### 1、updateStrategy（字段验证策略之 update）

#### 1.1 当执行更新操作时，该字段拼接set语句时的策略：
* IGNORED: `update table_a set column=#{columnProperty}`, 属性为null/空string都会被set进去
* NOT_NULL: `update table_a set <if test="columnProperty != null">column=#{columnProperty}</if>`
* NOT_EMPTY: `update table_a set <if test="columnProperty != null and columnProperty!=''">column=#{columnProperty}</if>` 如果针对的是非 CharSequence 类型的字段则效果等于 NOT_NULL

#### 1.2 FieldStrategy 有三种策略：
- IGNORED：忽略
- NOT_NULL：非 NULL，默认策略
- NOT_EMPTY：非空

当更新字段为 空字符串 或者 null 的需求时，需要对 FieldStrategy 策略进行调整对应的策略值。
示例：

```java
@TableField(value = "ENDDATE", updateStrategy=FieldStrategy.IGNORED)
private Date enddate;
```

#### 1.3 注意
在 [官方文档中给出的 “方式二：调整字段验证注解”](https://www.mybatis-plus.com/guide/faq.html#%E6%8F%92%E5%85%A5%E6%88%96%E6%9B%B4%E6%96%B0%E7%9A%84%E5%AD%97%E6%AE%B5%E6%9C%89-%E7%A9%BA%E5%AD%97%E7%AC%A6%E4%B8%B2-%E6%88%96%E8%80%85-null) 
的 `@TableField(strategy=FieldStrategy.NOT_EMPTY)` ，其写法在 `3.1.2` 版本后 `strategy` 方法被弃用，更新为 `insertStrategy`、`updateStrategy` 和 `whereStrategy` 。

```java
/**
 * 字段验证策略
 * <p>默认追随全局配置</p>
 *
 * @deprecated 3.1.2 , to use {@link #insertStrategy} and {@link #updateStrategy} and {@link #whereStrategy}
 */
@Deprecated
FieldStrategy strategy() default FieldStrategy.DEFAULT;
```

### 2、[FieldFill](https://www.mybatis-plus.com/guide/annotation.html#fieldfill)

#### 2.1 在 @TableField 注解中有属性：`fill` ，字段自动填充策略。

`fill` 自动填充指的是某些字段只有在特定的场景下才会被填充，例如表里的数据：create_time （创建时间）和 update_time（更新时间）, 
创建时间是在数据插入的时候会被填充的，而更新时间是在这条数据被更新时填充的，如下代码所示，fill 注解自动填充可以很好的实现这个。

```java
@TableField(value = "create_time",fill = FieldFill.INSERT)
private Date createTime;
@TableField(value = "update_time",fill = FieldFill.INSERT_UPDATE)
private Date updateTime;
```

#### 2.2 FieldFill 字段填充策略枚举类如下：

|       值       |     描述     |
|:-------------:|:----------:|
|    DEFAULT    |   默认不处理    |
|    INSERT     |  插入时填充字段   |
|    UPDATE     |  更新时填充字段   |
| INSERT_UPDATE | 插入和更新时填充字段 |

- 当 fill = FieldFill.INSERT 表示在执行 INSERT 语句时，该字段才会被填充。
- 当 fill = FieldFill.INSERT_UPDATE 表示在执行 INSERT、UPDATE 语句时，该字段才会被填充。
- ...

#### 2.3 FieldStrategy 与 FieldFill 
对于 FieldStrategy 和 FieldFill，
[判断注入的 insert 和 update 的 sql 脚本是否在对应情况下忽略掉字段的 if 标签生成，
FieldFill 优先级是高于 FieldStrategy 的。](https://github.com/baomidou/mybatis-plus/blob/3.0/mybatis-plus-annotation/src/main/java/com/baomidou/mybatisplus/annotation/FieldFill.java#L24)

## 方案二：全局配置
根据方案一中，FieldStrategy 的三种策略：IGNORED、NOT_NULL、NOT_EMPTY，
可以在 application.yml 配置文件中注入配置 GlobalConfiguration 属性 update-strategy，
将 update-strategy 策略调整为 IGNORED，即忽略判断策略。即可调整全局的验证策略。
如下所示：

```yml
# yml 配置：
mybatis-plus:
  global-config:
    db-config:
      update-strategy: IGNORED
```

全局性配置会对所有的字段都忽略判断，如果有特殊字段处理，可以单独配置，修改字段的策略。

设定全局配置，可以减少一个一个字段去指定增加的麻烦。

## 方案三：使用 UpdateWrapper (3.x) 更新
mp 提供了 UpdateWrapper 类简化更新的操作，
针对方法级进行操作，只需操作其更新方法，相比较方案一和方案二，方案三影响范围较小。

由于 BaseMapper 的继承 Mapper ，在 [BaseMapper](https://github.com/baomidou/mybatis-plus/blob/3.0/mybatis-plus-core/src/main/java/com/baomidou/mybatisplus/core/mapper/BaseMapper.java#L143)
的源码中写道：

```java
/**
 * 根据 whereEntity 条件，更新记录
 *
 * @param entity        实体对象 (set 条件值,可以为 null)
 * @param updateWrapper 实体对象封装操作类（可以为 null,里面的 entity 用于生成 where 语句）
 */
int update(@Param(Constants.ENTITY) T entity, @Param(Constants.WRAPPER) Wrapper<T> updateWrapper);
```

可看出，实体对象可以 set 条件值且为可以为 null，说明有两种方法可以实现更新操作（采用 lambda 表达式）：

### 1、将需要更新的字段，设置到 entity 中
```java
mapper.update(
   new User().setName("mp").setAge(3),
   Wrappers.<User>lambdaUpdate()
           .set(User::getEmail, null) //把email设置成null
           .eq(User::getId, 2)
);
```

### 2、将 entity设置为 null ，将需要更新的字段设置到 UpdateWrapper 中
```java
mapper.update(
    null,
    Wrappers.<User>lambdaUpdate()
       .set(User::getAge, 3)
       .set(User::getName, "mp")
       .set(User::getEmail, null) //把email设置成null
       .eq(User::getId, 2)
);
```

## 参考资料

* mp-annotation：https://www.mybatis-plus.com/guide/annotation.html
* mp-BaseMapper：https://github.com/baomidou/mybatis-plus/blob/3.0/mybatis-plus-core/src/main/java/com/baomidou/mybatisplus/core/mapper/BaseMapper.java
* mp-FAQ: https://www.mybatis-plus.com/guide/faq.html