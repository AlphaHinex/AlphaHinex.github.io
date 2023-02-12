---
id: rawgraphs
title: "数据不直观？试试 RAWGraphs"
description: "开源，可离线使用、所见即所得的数据可视化工具"
date: 2023.02.12 10:26
categories:
    - JavaScript
tags: [Data Visualization, D3]
keywords: rawgraphs, chart, svg, vector graphics, sankey diagram
cover: /contents/rawgraphs/cover.png
---

大大小小的决策离不开数据的支撑，然而从数据的海洋中挖掘或分析出有价值的信息，没有好的工具几乎是不可能完成的任务。

比如下面的数据：

![Energy flows in UK (2050)](/contents/rawgraphs/data.png)

这是一份来自 [www.gov.uk](https://www.gov.uk/government/publications/2050-pathways-calculator-with-costs) 的关于英国 2050 年能源流动的预测数据。

从二维的数据表格中，很难直观的看到数据想要说明的内容。但如果这份数据是以下面这种形式展示的呢：

![Sankey Diagram](/contents/rawgraphs/sankey.png)

相同的空间，相同的数据，适当的图表，能够比数据表格传递出更多更有价值的信息。

那么怎么把枯燥的数据表格变成吸人眼球的图表呢？

Excel？太繁琐；专业的数据可视化工具？成本太高……

我只是想把格式化好的数据变成各种类型的图表，有没有简单高效的方法？

RAWGraphs
=========

[RAWGraphs](https://www.rawgraphs.io/) 便是一个免费开源的数据可视化工具。在 GitHub 上有 [RAWGraphs 组织](https://github.com/rawgraphs)，里面包含了 RAWGraphs 核心类库 [rawgraphs-core](https://github.com/rawgraphs/rawgraphs-core)、Web 应用 [rawgraphs-app](https://github.com/rawgraphs/rawgraphs-app) 和图表 [rawgraphs-charts](https://github.com/rawgraphs/rawgraphs-charts) 等开源项目，其主要特性包括：

1. 开源，Apache 2.0 协议
1. 内置 30 多种图表，并支持自定义扩展
1. 数据安全，传入的数据仅在浏览器中使用，无需后端服务
1. 可导出图片或矢量图格式，方便后续使用做图软件继续美化

在线版本
-------

可通过浏览器直接访问 https://app.rawgraphs.io/ 使用 RAWGraphs 提供的在线版 Web 应用。

离线版本
-------

也可使用 [rawgraphs-app](https://github.com/rawgraphs/rawgraphs-app) 仓库源码编译，部署在自建环境中，离线使用。

[这里](/contents/rawgraphs/build.zip) 提供一个编译好的 Web 静态资源包，可发布到 HTTP 服务器（Apache、Nginx、Tomcat 等）中直接使用。


用法
===

接下来让我们看看如何借助 RAWGraphs 使用开头的表格数据生成桑吉图。

## 1. 装载数据

![Load your data](/contents/rawgraphs/step1.png)

RAWGraphs 提供了多种装载数据的方式。演示数据包含在官方提供的样例数据中，按下图选择即可。

## 2. 选择图表

![Choose a chart](/contents/rawgraphs/step2.png)

样例数据下面提示了适合进行可视化展现的图表，如样例数据的桑吉图。

## 3. 数据映射

![Mapping](/contents/rawgraphs/step3.png)

将数据维度与图表的变量进行映射。维度与变量都有数据类型的图标提示，需选择符合的类型进行映射。

## 4. 定制调整

![Customize](/contents/rawgraphs/step4.png)

图表为所见即所得，并可以进行画布、图表、颜色、标签等定制调整。

## 5. 导出图表

![Export](/contents/rawgraphs/step5.png)

完成调整后，可以将图表输出为所需的类型，供后续使用或处理。