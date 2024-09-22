---
id: ddd-in-action
title: "领域驱动设计实战"
description: "一个简化的外卖系统 DDD 设计实践"
date: 2024.09.22 10:26
categories:
    - DDD
tags: [DDD]
keywords: DDD, 统一建模语言, 事件驱动架构, 限界上下文, 领域事件, 工程结构
cover: /contents/ddd-in-action/events.png
---

# 需求概述

需求为一个简化的外卖平台，包括下订单、支付、取消、商家接单、准备、派送等功能。

# 架构风格选择

采用领域驱动设计方法进行问题空间分析及解空间设计。划分顾客、商家、骑手、订单、通知五个限界上下文，每个上下文成为一个微服务。服务内部采用分层架构。服务之间以开放主机服务及事件驱动架构。数据库逻辑隔离，通过事件机制保证最终一致性。

# 统一建模语言

- 商家（Merchant）
- 注册
- 顾客（Consumer）：自然人通过商家提供的服务，注册成为顾客
- 签约
- 骑手（Courier）：商家签约自然人为骑手
- 骑手状态（CourierStatus）：
    1. 可分配接单（Available）：订单派送完成后立即空闲
    1. 不可分配接单（Unavailable）
- 账户（Account）
- 账户状态（AccountStatus）
    1. 激活（Actived）
    1. 锁定（Locked）
- 预存款（Charge）：顾客向账户内预存款（充值）
- 菜单商品（MenuItem Product）
- 商品状态（MenuItemStatus）
    1. 待上架（Pending）
    1. 已上架（Up）
    1. 已下架（Down）
- 订单（Order）
- 订单商品（OrderItem）：订单可以包含多个订单商品，订单商品包含金额和数量
- 订单状态（OrderStatus）：
    1. 已创建（Pending）：未支付
    1. 已提交（Approved）：已支付，产生消费记录
    1. 商家已接受（Accepted）：指接受工单，需有空闲骑手
    1. 准备中（Preparing）
    1. 准备完成（ReadForPickup）
    1. 派送中（Pickedup）
    1. 派送完成（Delivered）
    1. 已取消（Cancelled）
- 支付
- 消费记录（Accounting）：顾客支付订单的消费记录
- 消费记录状态（AccountingStatus）
    1. 待支付（Pending）
    1. 已支付（Paid）
    1. 已退款（Returned）
- 退款：订单取消时产生退款
- 工单（Ticket）：
顾客支付订单后，订单变为已提交状态，并自动创建工单。
商家浏览工单，并对工单进行接受或拒绝。
接受工单时，会创建配送任务，并设置预计派送时间。在预计派送时间前后30分钟内有空闲骑手（无已分配的派送任务）时，随机挑选一个骑手，，修改派送为已分配状态，接受工单成功。
工单接受失败（商家无法准备、没有空闲骑手）会导致工单取消、订单取消，并退款。
- 工单状态（TicketStatus）：
    1. 已创建（Pending）：待接单
    1. 已接受（Accepted）
    1. 已备餐（Prepared）
    1. 待取餐（ReadyForPickup）
    1. 已取餐（PickedUp）
    1. 已取消（Cancelled）
- 派送（Delivery）
- 派送状态（DeliveryStatus）
    1. 待分配（Pending）
    1. 已分配（Accepted）
    1. 已送达（Delivered）
    1. 已取消（Cancelled）
- 预计派送时间：商家接受工单的时间
- 计划送达时间：计划派送时间 + 30 分钟
- 实际派送时间：骑手取得订单商品开始派送的时间
- 实际送达时间：骑手实际完成送达时间
- 通知（Notification）：为顾客、骑手、商家发送手机通知
订单已支付后，给顾客发送支付提醒
账户有退款时，给顾客发送退款提醒
顾客注册时，给顾客发送短信验证码
有新的已分配派送时，给骑手发送派单提醒
派单取消时，给骑手发送派单取消提醒
工单准备完成时，给骑手发送提醒

# 快速建模法

## 名词建模

> 识别业务服务规约中的**名词**

## 动词建模

> 识别业务服务规约中的**动词**，判断动词对应的领域行为是否产生了**过程数据**，如果有，则将该过程数据识别为领域概念

## 归纳抽象

> 针对有定语修饰的领域概念进行**归纳**和**抽象**

## 确定关系

> 确定领域概念之间的关系

# 领域分析模型精炼

# 领域分析模型与限界上下文

1. 领域分析模型
2. 区分实体和值对象，设计聚合
3. 限界上下文及上下文映射图

![bounded-context](/contents/ddd-in-action/bounded-context.png)

# 领域事件及 Topic

事件风暴方法分析命令、领域事件及聚合：

![domain-event](/contents/ddd-in-action/domain-event.png)

![events](/contents/ddd-in-action/events.png)

# 事件驱动机制及事务管理机制

- 本地事件表保存事件以保证事务一致性
- 定时轮询事件表中未发送事件，将其转换为消息发送至消息队列
- 消息生产者通过事件表的乐观锁保证消息的成功发送，消费者保证消息处理的幂等性

# 工程结构设计

## 参考结构

![mapping](/contents/ddd-in-action/mapping.png)

![package](/contents/ddd-in-action/package.png)

> 以上两张图片引自 [《解构领域驱动设计》](https://alphahinex.github.io/2024/08/25/ddd-explained/)

## 实际结构

### 服务名

1. `order`：订单
2. `consumer`：顾客
3. `merchant`：商家
4. `courier`：骑手
5. `notification`：通知

### 包划分

1. `com.neusoft.hackathon.order.north`：北向网关，包括本地和远程调用；相当于领域模型对其他限界上下文暴露的接口；前后端接口的适配也可以在这个包里完成，如 `north.controller`
2. `com.neusoft.hackathon.order.domain`：领域模型，尽量保持稳定，需求不变领域模型尽量不变
3. `com.neusoft.hackathon.order.south`：南向网关，包括端口和适配器，用来调用其他限界上下文接口以及资源库