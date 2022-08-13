---
id: techmark-review
title: "态马商战复盘"
description: "三个产品，三个地区，九个细分市场，两天一晚，一场令人难忘的商业决策模拟"
date: 2022.07.31 10:34
categories:
    - Others
tags: [Others]
keywords: TechMark, 态马商战
cover: /contents/techmark-review/cover.png
---


态马商战简介
==========

> TechMark是一种形式新颖的创新的管理培训课程，它凭借强大的计算机系统创造了一个仿真度极高的商业竞争环境，为学员带来集知识性、趣味性、仿真性和实践性为以一体的商战训练。 —— [TechMark是什么](http://www.techmarkleader.com/service/)

在态马商战（TechMark）的世界里，有三种虚拟产品，三个模拟地区，参与者分组成立临时公司，以相同的起点起步，在两天一晚的时间里，根据已知的信息和 TechMark 系统计算出的实际数据，进行六轮模拟商业决策，角逐满足各项经营指标且股价最高的 TechMark 冠军荣誉。


战前准备
=======

正所谓兵马未动粮草先行，熟谙已知信息，是在面对未知环境时仍然可以任凭风吹浪打，我自闲庭信步的底气。

根据课前发放的预习资料及课程讲义，我们分析、汇总了如下内容。

市场特点
-------

![](/contents/techmark-review/market-feature.png)

* 北美联盟：成熟的市场，注重质量也关注价格，产品性能参数需求离散；
* 亚太共和：人口众多，价格敏感，市场增长率不确定，同样的商品，在亚太共和生产比从北美联盟生产再运到亚太共和销售，销量会提升 30%；
* 欧联邦：消费能力强，相对于价格，他们更在意商品本身的性能参数与产品质量，产品参数需求集中，同样的产品，欧联邦生产的质量要强于北美联盟。

前四个财季订单数预测数据表示：
* `墨晶1` 在北美市场需求最大，但呈下降趋势；
* `墨晶2` 前期以北美市场需求量大，中期欧联邦需求强势增长；
* `墨晶3` 在北美市场有巨大的市场需求。

产品研发费用
----------

每个产品的参数特性，被抽象为了两个维度：`感抗`、`内阻`。

在课前的预习资料中，给出了调整每个产品的每个维度参数的试验数据，如：

### 实验室中的模拟试验 —— 墨晶2
|特性|原有的特性水平|要求的特性水平|研发预算投入（百万）|研发的结果|
|:--|:-----------|:-----------|:---------------|:-------|
|感抗<br>内阻|3.5<br>1.5|4.5<br>1.1|$0.18|失败|
|感抗<br>内阻|2.6<br>1.4|1.9<br>2.3|$1.150|成功|

根据上面的两条数据，假设调整感抗参数所需的研发费用为 `x`，调整内阻参数所需的研发费用为 `y`，可以列出如下二元一次方程组：

```formula
  1x + 0.4y >  0.18
0.7x + 0.9y <= 1.150
```

这里有一点需要注意，每个维度的值无论是增大还是减少，都按照 `|原有的特征水平 - 要求的特征水平|` 计算系数，即取两个值差的**绝对值**。

根据所有的试验数据，我们可以为每个产品列出一组方程，通过计算，可以得出每个产品的 x 和 y 值的范围，即至少投入多少研发费用，能够保证特性水平调整成功。


其他信息
-------

* 多个小组参与竞争，每个小组处于相同起点，将来的发展取决于各组的决策
* 产品参数初始状态（感抗: 3.0, 内阻: 3.0）
* 调整产品参数需要研发费用支持，研发费用不足，可能导致产品研发失败，产品参数回到本次调整前状态
* 初期各产品产地均在北美联盟
* 产品参数及市场需求的预测数据只有前四期的，后两期没有提供预测数据
* 产地调整决策当期不生效，下期才能完成产地更换
* 产品参数当期调整当期生效
* 当期新招聘的销售人员，要到下个季度才能正常工作
* 下期销售代表的数量，受上期业绩影响，有上限，不能随意设置


第一财季 1A
==========

第一个财季的决策，贴心的被分成了 `1A`、`1B` 两次完成，方便大家互相熟悉以及对态马商战游戏规则快速适应。`1A` 需要提交的决策内容为产品参数、研发费用、下期产地以及公司的组织架构和职责分工：

![](/contents/techmark-review/1a.png)

决策过程
-------

根据战前准备中分析的市场特点，我们将第一财季的产品目标市场锁定为北美联盟，并为 `墨晶2` 产品从下期开始进入欧联邦市场做准备。

### 研发方向

* `墨晶1`：为兼顾亚太共和和北美联盟市场，产品参数取两个市场预测值的中间位置；
* `墨晶2`：考虑到北美联盟市场需求的离散性特点、北美联盟对 `墨晶2` 产品的参数需求发展趋势（见下图），以及下期目标市场欧联邦对 `墨晶2` 的产品参数需求，经 CXO 们讨论决定，我们暂不调整 `墨晶2` 的产品参数；
* `墨晶3`：同样因为需求的离散型，以及控制研发成本，内阻按预测值进行了调整，感抗参数减小了按预测值方向调整的幅度。

![](/contents/techmark-review/trend.png)

确定好产品参数后，根据之前计算出的每个产品调整每项参数所需的费用范围，对产品研发费用进行了预算，并在计算结果基础上增加了一定的费用，以保证产品研发成功。

### 下期产地

为进入欧洲市场，本期将 `墨晶2` 的下期生产地，调整到了欧联邦；其余两个产品继续在北美联盟生产。

结果分析
-------

在 1A 决策结果发布时，有小组出现了研发失败，导致未能按预期收获目标市场的订单数量。我们虽然有数据支撑保证了产品研发的成功，但在北美联盟目标市场的订单数量上，并没有那些产品参数更贴近预测值的小组收获的市场份额大，即使北美联盟的消费者样本调查显示其对产品参数的需求是非常离散的。这意味着我们需要更加精准的市场定位，在之后的产品参数调整中，我们需要产品更贴近目标市场的理想值。


第一财季 1B
==========

`1B` 需要决策的内容为，每个市场每种产品的销售价格，和运往每个市场的每种产品的发货数量：

![](/contents/techmark-review/1b.png)

决策过程
-------

基于成本预测分析，在仅有市场预测份额及预计销收入的情况下，我们单一维度的测算了生产成本及发货量，没有整体的思考销售成本及参考份额的重要性。

在产品参数不是非常精确的情况下，我们尝试通过市场手段影响消费者的需求，使我们的产品参数能够更加符合目标市场的理想值，并按较大产量生产产品以期获得更高的利润。

结果分析
-------

从 `1B` 决策的结果来看，显然有其他小组做的比我们更出色。

我们在三个目标市场取得的市场份额排名分别为：`美1`（北美联盟，`墨晶1`）第二，`美2` 第四，`美3` 第四。虽然在兼顾的 `亚1`（亚太共和，`墨晶1`）市场，我们取得了第二的市场份额并且 `亚1` 市场贡献了九个细分市场中排名第二的销售收入，但由于 `美3` 的定价略高且市场份额占有率较低，供过于求，产生了较多的存货。

通常情况下，我们会认为供不应求是产品受欢迎的一个表现，而供不应求会造成库存进而产生成本。但从第一财季的损益表数据来看，期末存货会从当期的直接成本中进行扣除；有存货的 `墨晶3` 产品在各个市场上的实际销量都要比订货量有所增加，而没有存货的 `墨晶1` 和 `墨晶2` 两个产品，实际市场销量都要比订货量下降，这意味着一些本应属于我们的市场份额，由于供货不足，被其他竞争对手吃掉了。这给了我们下期增大产量的信号。

由于产品参数的不精准及 `1A` 决策后我们的产品订货量市场份额不够出色，导致我们的产量决策略显保守，在本期销售收入减去直接成本及营运费用后，我们的当期利润是负值。

### 研发方向及市场份额排名汇总

|期间|墨晶1|墨晶2|墨晶3|
|:---|:---|:---|:---|
|第一财季|美1（#2）|美2（#4）|美3（#4）|


第二财季
=======

从第二财季开始，每期所要做的决策都是下图中的完整内容：

![](/contents/techmark-review/decision.png)

要决策的内容非常多，时间非常紧张。一个好的组织架构，可以对决策顺利完成产生非常大的帮助。有的小组在这个过程中也会对其组织结构进行调整，以适应快节奏的决策制定。

决策过程
-------

可以说在第一财季，我们的执行是完美的，主要的问题出在目标上。吸取了第一财季的经验及教训，我们在第二财季决策过程中，首先明确了目标市场：`美1`、`欧2`、`美3`。

在产品研发决策中，我们严格按照目标市场产品预测值调整产品研发参数，并为保证研发成功，对研发经费的投入加入了一些冗余。

为使得六期决策后，我们公司的股价能够达到要求的最低值，在每轮决策的间隙，老师帮我们分析了影响股价的因素，以及预测股价的方法，并提醒我们期末毛利率需要大于等于 35% 这个指标。这些财务知识的补充，都给我们为产品定价提供了方向。

按照第一财季的结果分析，我们在第二财季继续加大产品产量，以保证在目标市场有充足的产品供应，并能够借此抢占一部分竞争对手的市场份额。

结果分析
-------

第二财季决策结果公布时，我们在目标市场上的产品特性，更加贴近市场的理想值，并且在保证研发成功的同时，能够很好的控制研发费用。在三个目标市场取得的市场份额排名分别为：`美1` 第三，`欧2` 第二，`美3` 第四。得益于出色的产品特性、定价策略及品牌知名度，`墨晶1` 在三个地区的市场贡献了近一半的销售收入；`墨晶3` 在北美联盟虽然市场份额仅排第四（21.6%），但凭借北美联盟市场的体量，`美3` 的销售收入在九个细分市场中拔得头筹，占据了总收入的近三成。精准的目标及优秀的执行，使我们在本期决策后，取得了当期利润及累计利润双冠王的成绩。

不过老师在讲解中的一句话 —— 增长能够掩盖一切问题，还是为我们的喜悦之情注入了一丝清醒。虽然本期决策成功的弥补了我们在第一期决策中的不足，但也同样可以发现一些问题：产品研发精准按照预测值调整的参数，与市场的理想值还是存在一定的偏差；`美1`、`美3` 市场期末库存量为 `0`，意味着我们本可以在这两个市场取得更好的成绩；`亚1`、`欧1` 期末库存量较大，对于 `墨晶1` 的产量分配可以更加合理。好在我们还有很多次决策机会，CXO 们对于决策也愈发的驾轻就熟了。

### 研发方向及市场份额排名汇总

|期间|墨晶1|墨晶2|墨晶3|
|:---|:---|:---|:---|
|第一财季|美1（#2）|美2（#4）|美3（#4）|
|第二财季|美1（#3）|欧2（#2）|美3（#4）|

第三财季
=======

决策过程
-------

第三财季，我们依然首先明确了目标市场：`美1`、`欧2` 和 `美3`。

在产品参数调整时，我们分析了前两期各目标市场产品参数的预测值及实际的市场理想值，决定本期按照实际理想值的变化趋势，来调整目标市场产品参数。

以 `欧2` 为例，填入历史数据后，根据实际理想值的趋势，我们预测了本期 `欧2` 的理想值 ——（`4.2`，`2.8`）：

![](/contents/techmark-review/history.png)
![](/contents/techmark-review/predict.png)

结果分析
-------

第三财季决策结果发布，产品特性成为了我们的绝对优势。以 `欧2` 为例，我们的产品特性为（`4.2`，`2.8`），市场理想值为（`4.21`，`2.72`）。决策时，产品参数只能精确到十分位，我们在目标市场上的三个产品，比所有竞争对手的参数都要精准，这得益于 CTO 团队的群策群力，CEO 的充分信任，以及 CXO 们的鼎力支持。

本期三个目标市场的市场份额排名分别为：`美1` 第四，`欧2` 第二，`美3` 第三。

`美3` 的排名及份额均有所提升，依然是九个细分市场中的收入排名 No1，但 `美3` 依然出现了期末库存为 0 的情况，导致市场销量比订货量大幅下降。

`欧2` 保持着市场领导者的地位，并且销售收入排名第二，毛利率排名第一，是非常优质的第二曲线，不过 `欧2` 市场定价偏低，可能稍微影响了一些品牌形象，在 `欧2` 市场我们应该可以取得更好的成绩。

`美1` 较之前排名有所下滑，品牌知名度和销量都不如以往，这与 `美1` 市场整体需求下滑的大环境也有一些关联。在 `墨晶1` 产品的目标市场上，我们需要做出一些调整了。

### 研发方向及市场份额排名汇总

|期间|墨晶1|墨晶2|墨晶3|
|:---|:---|:---|:---|
|第一财季|美1（#2）|美2（#4）|美3（#4）|
|第二财季|美1（#3）|欧2（#2）|美3（#4）|
|第三财季|美1（#4）|欧2（#2）|美3（#3）|


第四财季
======

决策过程
-------

考虑到第三期结果中 `美1` 市场呈现的萎缩趋势，以及 `亚1` 市场需求的增大和生产成本优势，本期我们进行了 `墨晶1` 产品产地的调整。因为产地的调整需要到下期才能生效，第四财季的目标市场，依然是 `美1`、`欧2` 和 `美3`。

有了前几期积累下来的产品参数预测模型和研发费用预测公式，我们依然将产品特性精准的调教到了目标市场的预测理想值上。

在定价和发货决策上，我们也不断摸索、调整，形成了可视化的计算表格，并通过上一财季的数据预估下期订单，用市场参考价值调整市场策略，基于库存余量判断下一期生产产值，为 CEO 提供了决策依据。

![](/contents/techmark-review/market-predict.png)

结果分析
-------

第四财季结果公布，三个目标市场的市场份额排名分别为：`美1` 第二，`欧2` 第四，`美3` 第三。

`欧2` 虽然市场份额及排名下降了不少，但优秀的定价策略使其首次超过 `美3` 成为最大的收入来源，

北美联盟品牌知名度大幅上升，贡献了近一半的销售收入，`美1` 的市场份额也重新回到领头位置。

`美3` 全力生产，市场销量较订货量有所上升，且期末库存为 0，是我们当之无愧的现金牛。

赛程过半，老师在决策中间穿插的讲解中，开始提醒我们除了关注增长的同时，还要关注每项 KPI 指标：期终股票价格、期末销售增长率、期末毛利率、期末存货资产比、期末资产负债率。只有这五项指标全部满足要求，且股票价格最高的组才能获得大奖。我们开始更多的关注存货及成本的控制。

### 研发方向及市场份额排名汇总

|期间|墨晶1|墨晶2|墨晶3|
|:---|:---|:---|:---|
|第一财季|美1（#2）|美2（#4）|美3（#4）|
|第二财季|美1（#3）|欧2（#2）|美3（#4）|
|第三财季|美1（#4）|欧2（#2）|美3（#3）|
|第四财季|美1（#2）|欧2（#4）|美3（#3）|


第五财季
=======

决策过程
-------

第五财季，我们的 `墨晶1` 产品已完成了生产地向亚太共和的迁移，可以更好的利用亚太共和的生产成本优势以及其市场的保护性行为，在亚太共和市场取得更好的表现。本期我们的目标市场：`亚1`、`欧2` 和 `美3`。

本期开始，已经没有了产品参数和市场需求的预测值，后两轮的决策，更多依靠的是我们在前几轮积累下来的模型和经验。

在产品参数调整时，`欧2` 的感抗参数按趋势预测，已达到其极限值 `5.0`，考虑到市场上还没出现过参数到达极限值的情况，我们将 `欧2` 的感抗参数在保持趋势的同时，进行了一定的下调。

结果分析
-------

本期产品特性市场理想值发布后，我们发现 `欧2` 感抗偏差略大，斜率放缓的程度比我们预期的还要大。根据这个数据，我们将预测模型进行了微调。

三个目标市场的市场份额排名分别为：`亚1` 第一，`欧2` 第三，`美3` 第二。

首次进入 `亚1` 市场，市场给我们的反馈让我们看到了决策的正确及坚定该市场投入的决心。

在本轮的决策结果公布时，有小组出现了销售额大幅增长，不仅当期利润第一，也完成了累计利润夺冠的逆袭（上期倒数第二）。老师在恭喜他们本轮出色决策的同时，也给我们提了个醒：第六期财务目标的五项指标中，有一项要求是期末销售额增长率大于等于 5%，这也意味着，逆袭组在第六期决策时，想要保持乃至超越本期的销售额，都有非常大的难度。他们的竞争对手，从我们变成了他们自己。而我们组，在本期的五项指标考核中，仍然有一项指标 —— 存货资产比，超出了要求的范围。最后一期的决策，对我们来讲，也变得至关重要。

![](/contents/techmark-review/5th.jpg)

### 研发方向及市场份额排名汇总

|期间|墨晶1|墨晶2|墨晶3|
|:---|:---|:---|:---|
|第一财季|美1（#2）|美2（#4）|美3（#4）|
|第二财季|美1（#3）|欧2（#2）|美3（#4）|
|第三财季|美1（#4）|欧2（#2）|美3（#3）|
|第四财季|美1（#2）|欧2（#4）|美3（#3）|
|第五财季|亚1（#1）|欧2（#3）|美3（#2）|

第六财季
=======

决策过程
-------

在前五期决策后，五个小组中只有两个小组达成了五项指标全部在合格范围内。我们组股票价格目前排在第三，且有一项指标未达标。

想要获得冠军，摆在我们面前的是两个问题：1. 保证五项指标全部达标；2. 继续提高股价。

我们制定的策略是：保持稳扎稳打的决策作风，继续主打 `亚1`、`欧2` 和 `美3` 三个市场。通过调整后的预测模型，进行更加精准的产品研发及费用预算；在主打市场扩大生产，其他市场以消耗库存为主。

在这一期决策时，我们还咨询了老师股票回购的意义，并在决策时进行了尝试，希望能够进一步提升股价。

结果分析
-------

随着老师将各项指标揭晓，可以看出每组都在最后一轮全力以赴，甚至做出了一些冒险的决策。市场证明了我们决策的成功，在保持之前各项指标在合格范围内的基础上，我们将存货资产比，也降到了合格范围内，成为了唯一一组五项指标全部合格的公司，最终赢得了这场在木星上墨晶产品商业决策模拟的胜利。

|资产负债率<25%|存货资产比4%~9%|当期销售额增长率>5%|毛利率>35%|股票价格>$168|
|:----|:----|:----|:----|:----|
|0%|5%|16%|51%|$340|

### 研发方向及市场份额排名汇总

|期间|墨晶1|墨晶2|墨晶3|
|:---|:---|:---|:---|
|第一财季|美1（#2）|美2（#4）|美3（#4）|
|第二财季|美1（#3）|欧2（#2）|美3（#4）|
|第三财季|美1（#4）|欧2（#2）|美3（#3）|
|第四财季|美1（#2）|欧2（#4）|美3（#3）|
|第五财季|亚1（#1）|欧2（#3）|美3（#2）|
|第六财季|亚1（#1）|欧2（#1）|美3（#2）|

总结
===

在最终结果公布之前，我们都是很忐忑的。大家紧张又兴奋的等待着，并对这两天一晚的商战旅程进行了初步的复盘。从最初的手忙脚乱，到过程中的力挽狂澜，每个人都在这个课程中完成了角色的转变，为了共同的目标，全身心的投入到这个模拟商战中。引用老师讲义中的一句话：

> Tell me and I forget; Teach me and I remember; Involve me and I learn

有了这个经历，每个人都是这场商战的主角，每一组都是这次商战的冠军。