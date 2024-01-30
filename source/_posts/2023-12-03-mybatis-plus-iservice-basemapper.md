---
id: mybatis-plus-iservice-basemapper
title: "MyBatis-Plus 中的 IService 和 BaseMapper"
description: "MyBatis-Plus 提供了 BaseMapper 和 IService 两个核心接口，但有些相似之处：它们如何使用及使用场景分别是什么？"
date: 2023.12.03 10:34
categories:
    - Java
tags: [Java, MyBatis-Plus]
keywords: MyBatis-Plus, BaseMapper, IService, ServiceImpl
cover: /contents/mybatis-plus-iservice-basemapper/IService.png
---

原文地址：https://wyiyi.github.io/amber/2023/12/01/mybatis-plus/

[MyBatis-Plus](https://mybatis.plus/guide/) 作为一个优秀的 ORM 框架，致力于简化和提高 Java 应用程序对数据库访问的效率。

在使用的过程中，发现 MyBatis-Plus 提供了 BaseMapper 和 IService 两个核心接口，但有些相似之处：它们如何使用及使用场景分别是什么？

![BaseMapper](/contents/mybatis-plus-iservice-basemapper/BaseMapper.png)

![IService](/contents/mybatis-plus-iservice-basemapper/IService.png)

## BaseMapper 接口

[BaseMapper](https://baomidou.com/pages/49cc81/#mapper-crud-%E6%8E%A5%E5%8F%A3) 接口是 MyBatis-Plus 提供的通用 Mapper 接口，它继承自 mybatis-plus 的 Mapper 接口，并扩展了一些常用的数据库操作方法。

> 说明:
>
> - 通用 CRUD 封装 `BaseMapper` 接口，为 `Mybatis-Plus` 启动时自动解析实体表关系映射转换为 `Mybatis` 内部对象注入容器
> - 泛型 `T` 为任意实体对象
> - 参数 `Serializable` 为任意类型主键 `Mybatis-Plus` 不推荐使用复合主键约定每一张表都有自己的唯一 `id` 主键
> - 对象 `Wrapper` 为 `条件构造器`


[BaseMapper](https://github.com/baomidou/mybatis-plus/blob/3.0/mybatis-plus-core/src/main/java/com/baomidou/mybatisplus/core/mapper/BaseMapper.java) 接口的主要作用是定义 DAO 层的数据库操作方法，例如数据的增删改查等。

开发者可以通过继承 BaseMapper 接口，并指定对应的实体类，即可直接使用这些通用方法，无需手动编写 SQL 语句，从而减少了代码量和重复劳动。

```java
@Mapper
public interface UserMapper extends BaseMapper<User> {
    //...
}
```

## IService 接口

[IService](https://github.com/baomidou/mybatis-plus/blob/3.0/mybatis-plus-extension/src/main/java/com/baomidou/mybatisplus/extension/service/IService.java) 接口是 MyBatis-Plus 提供的通用 Service 接口。

> 说明:
>
> - 通用 [Service CRUD](https://baomidou.com/pages/49cc81/#service-crud-%E6%8E%A5%E5%8F%A3) 封装 IService 接口，进一步封装 CRUD 采用 `get 查询单行` `remove 删除` `list 查询集合` `page 分页` 前缀命名方式区分 `Mapper` 层避免混淆
> - 泛型 `T` 为任意实体对象
> - 建议如果存在自定义通用 Service 方法的可能，请创建自己的 `IBaseService` 继承 `Mybatis-Plus` 提供的基类
> - 对象 `Wrapper` 为 `条件构造器`

开发者可以通过继承 IService 接口，并指定对应的实体类，即可直接使用这些通用方法，无需手动编写业务逻辑代码，使得代码更加简洁和易于维护。

```java
public interface UserService extends IService<User> {
    // 定义常用的业务逻辑方法
    // ...
}
```

## ServiceImpl

[ServiceImpl](https://github.com/baomidou/mybatis-plus/blob/3.0/mybatis-plus-extension/src/main/java/com/baomidou/mybatisplus/extension/service/impl/ServiceImpl.java#L60C22-L60C22)是 IService 默认实现类，ServiceImpl 是针对业务逻辑层的实现，并调用 BaseMapper 来操作数据库。

```java
public class ServiceImpl<M extends BaseMapper<T>, T> implements IService<T> {
    //...
}
```

传入的参数为 M 和 T：
- M：Mapper 接口类型
- T：对应实体类的类型

## 使用场景

1. 简单的数据库操作可以继承 BaseMapper 并添加新的数据库操作；
2. 简单的业务逻辑可以只使用 IService，IService 是对 BaseMapper 的扩展但仍需调用 Mapper；
3. BaseMapper 和 IService 主要区别： IService 提供批量处理操作（IService 和 BaseMapper 需一起使用），BaseMapper 则没有；

BaseMapper 、IService、ServiceImpl 三者的类关系从源码中可看出：
- 最简单的方式：自定义 Mapper 接口并继承 BaseMapper，则不需要去实现其内部方法，依靠 mybatis 的动态代理即可实现 CRUD 操作；

```java
@Mapper
public interface UserMapper extends BaseMapper<User> {
    //...
}
```

- 如果自定义 Service 接口并继承 IService，则需实现 IService 中的方法；

```java
public interface UserService extends IService<User> {
    // ...
}

@Service
public class UserServiceImpl extends ServiceImpl<UserMapper, User> implements UserService {

    @Resource
    UserMapper userMapper;

    public boolean updateSaveBatch(List<User> userList){
        return super.saveBatch(userList);
    }

    public int updateById(User user){
        return userMapper.updateById(user);
    }
}
```

## 既用之，则听之

大家对于 mybatis plus 的 `BaseMapper`以及 `IService` 以及 `ServiceImpl` 还是存在很大争议，并在 [issue](https://github.com/baomidou/mybatis-plus/issues) 中火热讨论（如下链接），最后还是以官方为主，若有改动文章在做后续调整。
- [关于改进 IService 和 ServiceImpl 的建议](https://github.com/baomidou/mybatis-plus/issues/5764)
- [关于 mybatis plus 中的 BaseMapper<T> 以及 IService<T> 以及 ServiceImpl<M extends <Basemapper>，T> 这几个类](https://github.com/baomidou/mybatis-plus/issues/59)
- [mybatis-plus 的一种很别扭的用法](https://github.com/baomidou/mybatis-plus/issues/926)