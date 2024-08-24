---
id: popular-agent-frameworks
title: "典型智能体框架介绍及实战"
description: "介绍了智能体及当前流行的智能体框架，并提供了几个实例"
date: 2024.08.18 10:34
categories:
    - AI
tags: [AI Agent, AI]
keywords: Agent, Dify, Coze, LLM, workflow, RAG, FastGPT, DB-GPT, bisheng, ModelScope-Agent
cover: /contents/popular-agent-frameworks/agents.png
---

# 对于智能体框架的理解

## 什么是智能体？

智能体，英文名称为 Agent，原意为代理人，当前语境下特指基于大语言模型的人工智能代理（LLM-powered agents、LLM based agents）。

关于智能体，目前还没有一个被广泛接受的定义。

> “An autonomous agent is a system situated within and a part of an environment that senses that environment and acts on it, over time, in pursuit of its own agenda and so as to effect what it senses in the future.” 
> 
> —— Franklin and Graesser (1997)

自主智能体是一个系统，它位于环境内部并是环境的一部分，能够感知该环境并在其中行动。随着时间的推移，它根据自身的议程采取行动，以影响它在未来感知到的环境。

### A Survey on Large Language Model based Autonomous Agents

![agent1](/contents/popular-agent-frameworks/agent1.png)

人民大学的论文[《A Survey on Large Language Model based Autonomous Agents》](https://arxiv.org/pdf/2308.11432)将智能体架构分为五部分：
1. 大语言模型（LLM）作为智能体的大脑；
2. Profile 模块：用于智能体的自我认知和角色设定；
3. Memory 模块：记忆模块，用来存储、获取、检索信息；
4. Planning 模块：制定计划，可根据过去的行为与目标动态规划下一步的行动；
5. Action 模块：执行模块，执行智能体的具体决策。

### The Rise and Potential of Large Language Model Based Agents: A Survey

![agent2](/contents/popular-agent-frameworks/agent2.png)

复旦大学的论文[《The Rise and Potential of Large Language Model Based Agents: A Survey》](https://arxiv.org/pdf/2309.07864)认为智能体由三部分组成：
1. Brain：大脑，负责自然语言理解及交互、知识存储及应用、长短期记忆及检索、推理及计划、迁移与泛化能力；
2. Perception：感知，包括对文字、图像及音视频等输入的感知；
3. Action：行动，包括自然语言对话、工具的运用、具身行为等。

### Introduction to LLM Agents

![agent3](/contents/popular-agent-frameworks/agent3.png)

Nvidia 技术博客[《Introduction to LLM Agents》](https://developer.nvidia.com/blog/introduction-to-llm-agents/)认为一个智能体有四个关键组件：
1. Agent Core：包括智能体的整体目标、可用工具、如何使用不同计划模块的解释、相关的记忆、智能体角色；
2. Memory module：记忆模块，包括短期记忆和长期记忆；
3. Tools：一组可执行的工作流程、API 等供智能体使用的工具集；
4. Planning module：计划模块，负责任务和问题分解、反思和改善。

### 简单概括

***智能体 = LLM + 记忆 + 工具 + 流程***

## 什么是智能体框架？

**抽象**构建智能体应用的通用过程，

**封装**不变步骤，

提供便捷**定制**及调整智能体各部分组件方式的智能体构建**工具**，

并提供独立、内嵌、API 等形式的智能体能力**发布**访问形式。

## 为什么要用智能体框架？

**快速**构建智能体应用。

# 智能体框架的分类

按如下两个维度，对目前我们评估过的智能体框架进行分类：
1. 开源（可私有化部署）/ 闭源（公网服务）
2. 基于编码 / 基于流程图

![agents](/contents/popular-agent-frameworks/agents.png)

|开源框架|GitHub Star 数量|贡献者数量|
|:------|--------------:|-------:|
|[Dify](https://github.com/langgenius/dify)|42k|377|
|[FastGPT](https://github.com/labring/FastGPT)|16.3k|84|
|[DB-GPT](https://github.com/eosphoros-ai/DB-GPT)|13k|94|
|[bisheng](https://github.com/dataelement/bisheng)|8.5k|24|
|[ModelScope-Agent](https://github.com/modelscope/modelscope-agent/)|2.5k|40|

> 统计日期：2024 年 08 月 17 日

# 基于流程图的智能体框架普遍使用流程

## 1. 构建知识库
准备用于扩展 LLM 的知识内容，导入到知识库中，实现检索增强生成（RAG）；
## 2. 流程编排
通过预先编排好的流程，弥补开源大语言模型任务分解编排能力不足的缺陷；或设定领域业务流程；
## 3. 调试
即时查验智能体能力，并能够追溯回复内容的来源和耗时等；
## 4. 发布
将构建好的智能体应用，发布为独立应用、内嵌页面或 API 接口等形式。

# 实例

## RAG —— 博客内容问答

在这些智能体框架/平台中，构建一个简单的 RAG 应用是非常方便的。将文档/知识导入到知识库，等待平台完成分段索引后，即可进行问答。

以 Dify 和 Coze 为例，将本博客的 [markdown 文档](https://github.com/AlphaHinex/AlphaHinex.github.io/tree/develop/source/_posts) 导入到知识库后，可以看到智能体回答的内容更加准确了。

### Dify 内网应用对比效果

![rag-dify](/contents/popular-agent-frameworks/rag-dify.png)

### Coze 发布至公众号对比效果

![rag-coze](/contents/popular-agent-frameworks/rag-coze.png)

## Workflow —— 多轮对话补全参数

在与智能体的交互中，可能需要通过多轮对话的方式，由智能体引导用户以问答的形式提供必要的信息，进而完成后续的任务。

### Dify 内网应用效果

在 Dify 最近发布的 [0.7.0](https://github.com/langgenius/dify/releases/tag/0.7.0) 版本中，增加了 [会话变量 & 变量赋值节点](https://mp.weixin.qq.com/s/lA4CxGLUiaXveL06aJVOwA)，可以实现门诊导诊类流程：

![workflow-dify](/contents/popular-agent-frameworks/workflow-dify.png)

流程的 DSL 可在这里下载：[门诊导诊.yml](https://github.com/AlphaHinex/AlphaHinex.github.io/blob/develop/source/contents/popular-agent-frameworks/%E9%97%A8%E8%AF%8A%E5%AF%BC%E8%AF%8A.yml)。

### Coze 发布至公众号效果

在 Coze 中，通过工作流的 [问答节点](https://www.coze.cn/docs/guides/question_node)，可以设置需要询问的内容。多个问答节点可以实现多轮对话效果：

![workflow-coze](/contents/popular-agent-frameworks/workflow-coze.png)

![workflow-wechat](/contents/popular-agent-frameworks/workflow-wechat.jpeg)