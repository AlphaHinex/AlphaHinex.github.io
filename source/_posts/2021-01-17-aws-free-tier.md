---
id: aws-free-tier
title: "薅 AWS 羊毛"
description: "体验免费套餐"
date: 2021.01.17 10:34
categories:
    - Cloud
tags: [AWS, GFW, Cloud]
keywords: AWS, EC2, GFW, VPS
cover: /contents/aws-free-tier/cover.jpg
---

[AWS][aws]，即 Amazon Web Services，是由 Amazon 提供的云服务。在 [Gartner][gartner] 新的 [2020 年云基础设施和平台服务 (CIPS) 魔力象限][cips-mq] 中，Gartner Research 将 AWS 定位在“领导者象限”中。在此魔力象限中，CIPS（Cloud Infrastructure and Platform Services）被定义为“标准化、高度自动化的产品，其中基础设施资源（例如计算、联网和存储）由集成式平台服务加以补充。”

![Magic Quadrant for Cloud Infrastructure and Platform Services, 2020](/contents/aws-free-tier/cips-mq.jpg)

## 免费套餐

作为领导者，AWS 提供的福利也是很厚道的，为每个账号都提供了免费套餐，包括试用、12 个月免费和永久免费三种类型的多种产品，详细可见：

* [AWS 海外区域账户免费套餐][aws-free]
* [AWS 中国（宁夏）区域免费套餐][aws-cn-free]

关于免费套餐的内容，官网有如下说明：

> 12 个月免费：这些免费套餐产品仅适用于新 AWS 客户，在自注册 AWS 之日起 12 个月内可用。当 12 个月的免费使用期过期或您的应用程序使用量超过了免费套餐限额，您只需支付标准的按使用量付费的服务费率（请参阅每个服务页面上的完整定价详情）。存在限制条件；有关更多详细信息，请参阅优惠条款。
> ‍
> 永久免费：这些免费套餐产品在 12 个月的 AWS 免费套餐期限到期后不会自动过期，而是无期限地提供给现有的和新的 AWS 客户。
> ‍
> 试用：这些免费套餐产品是短期试用产品，始于第一次试用开始时。试用期过后，您只需支付标准的按使用量付费的服务费率（请参阅每个服务页面上的完整定价详情）。
> ‍
> 客户在全球区域中使用的套餐服务使用量，均将计入 Amazon AWS 免费套餐中。AWS 免费套餐中的免费使用量每月计算一次（所有区域）并自动应用到账单中，免费使用量不能累计。目前，我们尚未在 AWS GovCloud（美国）区域和中国（北京）区域提供 AWS 免费套餐。

**即，免费使用不假，但是是有 [限额][free-tier-limits] 的，超过限额是仍然要付费的，别问我怎么知道的。**

## 怎么薅

### 注册账号

到 [AWS][aws] `创建 AWS 账户`，注册过程中需要填写银行卡信息，可以使用信用卡，注册后会产生 1 美元的预授权交易。完成注册信息填写后，需要等待服务激活，官方说法 `您的服务可能需要24小时才能完全激活`。进度会通过注册邮箱进行通知。

服务激活后，即可选择开通免费套餐中的服务了。

> 免费套餐是为每个账号提供的，账号通过邮箱注册，注册信息中，手机号、银行卡号等信息，可以重复使用，只要邮箱不同即可，这意味着。。。

### 开通服务

以开通 EC2 服务为例，EC2 是 AWS 的 `Virtual Servers in the Cloud`。

先在 `AWS 管理控制台` 中选择区域，如 `亚太地区 (东京)ap-northeast-1`，然后在 `Services` 中选择 `EC2`，在东京开通一台 EC2 服务。

点击 `启动实例`，选择系统镜像，勾选 `仅免费套餐`，选择一个符合条件的镜像，如 `Amazon Linux 2 AMI (HVM), SSD Volume Type`。之后选择符合免费套餐条件的实例类型 `t2.micro`。配置安全组时，可以开放一些端口供后续使用，也可以在需要时再进行设置。

完成设置准备启动时，会提示 `选择现有密钥对或创建新密钥对`，创建一个新密钥对，并下载私钥文件后，即可启动实例。

> 注意过程中的提示：您必须下载私有密钥文件(*.pem 文件)才能继续操作。请将其存储在安全且易于访问的位置。您无法在创建文件后再次下载此文件。

实例启动成功后，可至实例信息界面，点击 `连接`，选择 `EC2 Instance Connect`、`会话管理器`、`SSH 客户端` 方式连接至 EC2 实例。

### 限额

羊毛虽好，但不要无节制的薅。

免费套餐是有时限和限额的。

* 12 个月免费是指 **从注册之日** 起 12 个月内
* 还要注意服务用量的叠加，如 EC2 服务 12 个月内免费，但每月免费时长是 750 小时，所以在免费套餐内，可以连续使用一个 Linux 实例一个月，或者使用十个 Linux 实例，每个每月 75 小时

用量接近限额时，会收到邮件提醒，一定要注意免费套餐的限额，否则会收费。

另外 EC2 服务会带有一个外网 IP，即使时限没超过用量，带宽超过也是会收费的，如：

|Bandwidth||$0.15|
|:--|:--|:--|
|$0.000 per GB - data transfer in per month|16.818 GB|$0.00|
|$0.000 per GB - data transfer out under the monthly global free tier|15.000 GB|$0.00|
|$0.000 per GB - regional data transfer under the monthly global free tier|0.007 GB|$0.00|
|$0.114 per GB - first 10 TB / month data transfer out beyond the global free tier|1.299 GB|$0.15|

在账单界面可以看到具体限额和用量：

|服务|免费套餐的使用量限额|
|:--|:----------------|
|Amazon Elastic Compute Cloud|750 hours per month of Amazon EC2 Linux, RHEL, or SLES t2.micro or t3.micro instance dependent on region|
|Amazon Elastic Compute Cloud|30 GB of Amazon Elastic Block Storage in any combination of General Purpose (SSD) or Magnetic|
|AWS Data Transfer|15 GB of bandwidth out aggregated across all AWS services|
|AWS Key Management Service|20,000 free requests per month for AWS Key Management Service|

### 套餐到期

12 个月的免费套餐到期时，开通的服务不会自动停止。服务继续运行将会产生费用。如不再使用，需手动停止服务。

以 EC2 服务为例，选择对应实例，停止或终止实例即可。停止后可再次启动实例，终止后则不能。

> 注意：停止或终止实例均会导致 IP 发生变化。重启实例不会改变 IP。

> 可通过控制台查询公网 IP 地址，也可以在主机中通过 `curl http://169.254.169.254/latest/meta-data/public-ipv4` 进行查询。

另外，12个月免费期不是指 365 天，具体过期时间，可以收到的到期提醒邮件为准，大致为整月结算。


[aws]:https://amazonaws-china.com/cn/
[gartner]:https://www.gartner.com/en
[cips-mq]:https://blogs.gartner.com/raj-bala/2020/09/10/gartner-publishes-the-magic-quadrant-for-cloud-infrastructure-and-platform-services-2020/?_ga=2.190865065.247882349.1610534360-616680468.1610534360
[aws-free]:https://amazonaws-china.com/cn/free
[aws-cn-free]:https://www.amazonaws.cn/free/
[free-tier-limits]:https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/free-tier-limits.html