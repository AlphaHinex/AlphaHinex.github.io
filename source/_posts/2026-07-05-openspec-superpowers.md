---
id: openspec-superpowers
title: "【转】OpenSpec + Superpowers: SDD+TDD 双驱动 AI 编程工作流"
description: "SDD 的一种实现路径"
date: 2026.07.05 10:34
categories:
    - AI
tags: [AI, AI Agent]
keywords: AI, OpenSpec, Superpowers, SDD, TDD, Vibe Coding, AI Agent
cover: /contents/openspec-superpowers/openspec+superpowers.jpg
---

- 原文地址：https://www.lixueduan.com/posts/ai/21-openspec+superpowers/
- 原文作者：[意琦行](https://github.com/lixd)

---

![](https://alphahinex.github.io/contents/openspec-superpowers/openspec+superpowers.jpg)

随着 Vibe Coding 的流行，开源社区也是涌现出了大量的 AI 编程工作流，例如： Superpowers、Everything Claude Code、Spec Kit、OpenSpec、gstack、Get Shit Done 等等。今天给大家分享的是 **OpenSpec + Superpowers** 的协同工作流。

## 项目介绍

### OpenSpec

官方的描述是：**Spec-driven development (SDD) for AI coding assistants.** 

即：**OpenSpec 就是为 AI 编程助手打造的 Spec 驱动开发（SDD）框架。**

在 Vibe Coding 时代，Spec 是很重要的，在开始之前很有必要和 AI 在需求上达成一致。

使用 OpenSpec 之后每个变更（Change）对应一个文件夹，包含以下四类结构化文档：

- **proposal.md：**变更意图，定义为什么做
- **specs/：**具体 Spec，定义做什么
- **design.md：**具体技术实现方案，定义怎么做
- **tasks.md：**具体实现顺序，将变更拆分为一个个小任务

简而言之：OpenSpec 可以让 AI 在写代码之前先和人对齐需求，并提供完整的 Spec 生命周期管理，便于追踪。

### Superpowers

官方的描述是：**An agentic skills framework & software development methodology that works.** 

即：**Superpowers 是一套 AI 编程 Agent 的技能体系 + 开发方法论。**

它的核心不是生成代码，而是通过一套可组合的"技能"系统，强制 AI 像资深工程师一样工作，遵循测试驱动开发、代码审查等最佳实践。

简而言之：Superpowers 可以让 AI 像资深工程师一样干活。

## 为什么选择 OpenSpec + Superpowers

### Why OpenSpec

在 Vibe Coding 时代，文档的重要性大幅提高。古法编程时代，需求对齐主要靠开会，Vibe Coding 时代，则需要通过具体的 Spec 变更文档来对齐。而 OpenSpec 则是提供了很好的 Spec 生命周期管理功能，可以通过 Spec 追溯到具体变更细节。

### Why Superpowers

AI 生成代码是很容易堆砌成屎💩山的（当然，古法编程也一样哈哈哈）。

因为 AI 上下文有限，很难掌控全局，因此每次 Vibe Coding 产出的或许都是局部最优解，但是放到整体看就不一定合适，另外 AI 生成的代码都不够精简，代码量是很大的，毕竟 Vibe Coding 主打一个快。

> 这也是为什么 Github 上很多开源项目都吐槽遭受到了 PR 攻击。Agent 批量扫描代码提交 PR，可能整个过程都没有人介入，但是维护者要挨个 review，面对成堆的 PR 直摇头。

Superpowers 通过强制的 TDD、YAGNI、DRY 等工程原则，能很大程度上能够提升代码质量。

### 协同工作流

协同工作的核心思想是：**用 OpenSpec 生成和管理 Spec，然后用 Superpowers 这个"资深工程师"来执行 Spec。**

单独使用各有短板，二者结合刚好形成**“规格驱动开发(SDD) + 测试驱动开发(TDD)”**的完整工作流。

- **OpenSpec (SDD)：**对齐设计需求，在编码前生成结构化变更提案(proposal)、需求规范(specs)、技术设计(design)和任务拆解(tasks)
- **Superpowers (TDD)：**保证代码质量，强制 AI 遵循 TDD、YAGNI、DRY 等工程原则

**单独使用 OpenSpec 时工作流**是这样的：

![openspec workflow](https://alphahinex.github.io/contents/openspec-superpowers/openspec-workflow.jpg)

流程简单，文档驱动，但**代码实现阶段（apply）的质量保障较弱。**

**单独使用 Superpowers 时的工作流**是这样的：

![superpowers workflow](https://alphahinex.github.io/contents/openspec-superpowers/superpowers-workflow.jpg)

产出代码质量高，但**前期的需求输入和最终的设计决策缺乏一个结构化的、可长期保存的载体**，容易丢失在聊天历史中。

**二者协作后的工作流**是这样的：

![combined workflow](https://alphahinex.github.io/contents/openspec-superpowers/combined-workflow.jpg)

就是使用 `/superpowers:brainstorm` → `/superpowers:write-plan` → `/superpowers:subagent-driven-development` 来替代比较弱的 `/opsx:apply` 以提升代码质量。

## 安装与使用

### OpenSpec

#### 安装

OpenSpec 直接通过 npm 安装：

```bash
# openspec
npm install -g @fission-ai/openspec@latest
```

然后在项目根目录进行初始化：

```bash
openspec init
```

需要在项目目录下执行 init 命令初始化，初始化之后就可以在 claude 终端里使用了。

之后，重新打开 claude 就可以用上 OpenSpec 了。

OpenSpec 使用整体流程就是围绕 proposal 的：

- 创建 proposal：根据需求生成完整的 spec
- 应用 proposal：定义好 spec 之后就开始实现
- 归档 proposal：实现完成后对 proposal 进行归档，至此这个任务就算是完成了。

#### 创建 proposal

```bash
# /opsx:propose "your idea"
/opsx:propose "创建一个 Todo 应用"
```

命令执行完成后会自动生成：`openspec/changes/create-todo-app/` 目录、提案文档、设计模板、任务清单。

#### 应用 proposal

当 proposal 完全确定下来之后，就可以让 AI 根据 Spec 一步一步实现了。

```bash
# /openspec:apply $proposal
/opsx:apply
```

#### 归档 proposal

当 proposal 实现完成后，就可以进行归档保存。

```bash
# /opsx:archive $proposal
/opsx:archive add-task-priority
```

### Superpowers 

#### 安装

Superpowers Claude Code 插件：

```bash
# 在 claude code 终端执行
/plugin marketplace add https://github.com/obra/superpowers-marketplace.git
/plugin install superpowers@superpowers-marketplace
```

#### 使用 

Superpowers 安装后会在 Claude Code 中注册多个技能，可手动触发，部分环节会自动流转，比如最常见的几个 Skill：

- `brainstorming`：头脑风暴，澄清需求和技术细节
- `write-plan`：基于 brainstorming 结果生成实现计划，brainstorming 完成后自动进入
- `subagent-driven-development`：按计划启动子代理逐任务实现，强制 TDD + 两阶段代码审查，plan 写好后自动开始

## Demo

### OpenSpec 生成 Spec

第一步：使用 OpenSpec 生成初步 Spec

```bash
/opsx:propose "创建一个单页网页版Todo应用。它必须包含以下核心功能：
1. 一个输入框和一个'添加'按钮，用于创建新任务。
2. 每个任务项显示为一行，包含任务文本。
3. 每个任务项前有一个复选框，点击可将任务标记为'已完成'（视觉上需有区分，如删除线）。
4. 每个任务项旁有一个'删除'按钮，点击可移除该任务。
5. 所有任务数据必须在浏览器刷新后依然保留（使用localStorage）。
额外要求：代码结构应清晰，便于未来添加'筛选'或'优先级'等功能。"
```

效果

```text
⏺ 所有产物已创建。以下是总结：

  变更：web-todo-app
  位置：openspec/changes/web-todo-app/

  已创建产物：
  - proposal.md — 动机：浏览器原生 Todo 应用，具备 localStorage 持久化功能，可作为未来扩展（筛选、优先级）的基础
  - design.md — 技术方法：原生 JS，3 文件结构（index.html + style.css + app.js），集中状态与显式重渲染周期，时间戳 ID
  - specs/ — 3 个能力规范：
    - task-management — 创建、切换完成状态、删除任务
    - task-persistence — localStorage 保存/加载，处理损坏数据
    - task-ui — 输入表单、任务列表渲染（删除线已完成）、空状态、键盘支持
  - tasks.md — 8 组共 21 个实现任务，涵盖项目结构 → 集成验证

  所有产物已创建！已准备好进行实现。运行 /opsx:apply 以开始实现。
```

### Superpowers 细化 Spec

第二步：使用 Superpowers 继续细化上一步的 Spec

```text
读取以下 OpenSpec change 文件（必须完整读取，不要摘要）：
- openspec/changes/<change-name>/proposal.md
- openspec/changes/<change-name>/design.md
- openspec/changes/<change-name>/tasks.md
- openspec/changes/<change-name>/specs/ 下所有 spec.md（如有）

然后使用 superpowers 进行头脑风暴，深度技术设计，并传入以下上下文：

---
Change: <change-name>
上游需求（来自 OpenSpec，不要重写）：
- 目标：<从 proposal.md 提取>
- 架构约束：<从 design.md 提取>
- 任务边界：<从 tasks.md 提取>

约束：
1. OpenSpec 是需求的事实源，不要重新定义需求，不要重写 proposal/spec
2. 你的任务是基于已有需求做深度技术设计：实现方案、技术风险、测试策略、边界条件
3. 如发现 delta spec 缺少验收场景，只能回写 OpenSpec delta spec，不要在 Design Doc 中创建第二份需求 spec
4. 跳过上下文探索，直接进入设计提问
---

完成后产出：
- Design Doc → docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md
  （frontmatter 包含：change: <change-name>, role: technical-design, canonical_spec: openspec）
- delta spec 补充（如有）→ openspec/changes/<change-name>/specs/<capability>/spec.md
```

输出如下：

```text
产出完成。

  Design Doc → docs/superpowers/specs/2026-05-26-web-todo-app-design.md
  - 7 个章节：实现方案（状态流、ID 生成、持久化、渲染策略、事件委托、添加流程、存储告警）、技术风
险矩阵、测试策略、边界条件表、扩展性分析

  Delta Spec 补充 → 回写到 OpenSpec 三个 spec 文件，新增 5 个缺失场景：

  ┌──────────────────┬──────────────────────────┬──────────────────────────────────┐
  │       Spec       │         新增场景         │               原因               │
  ├──────────────────┼──────────────────────────┼──────────────────────────────────┤
  │ task-management  │ whitespace-only 输入拒绝 │ "empty" 定义不完整               │
  ├──────────────────┼──────────────────────────┼──────────────────────────────────┤
  │ task-persistence │ localStorage 写入失败    │ 隐私模式/配额是真实故障路径      │
  ├──────────────────┼──────────────────────────┼──────────────────────────────────┤
  │ task-persistence │ 部分有效数据恢复         │ 单条损坏不应导致整个列表丢失     │
  ├──────────────────┼──────────────────────────┼──────────────────────────────────┤
  │ task-ui          │ 渲染 HTML/script 内容    │ XSS 是安全关键边界               │
  ├──────────────────┼──────────────────────────┼──────────────────────────────────┤
  │ task-ui          │ Enter 键空输入拒绝       │ 键盘路径需要与按钮路径相同的守卫 │
  └──────────────────┴──────────────────────────┴──────────────────────────────────┘

  关键技术决策摘要：
  - 渲染：DOM API (createElement + textContent)，绝不用 innerHTML — 从根本上防止 XSS
  - 事件：事件委托（dataset.action 派发）— 配合 full re-render 模式，避免监听器泄漏
  - ID：Date.now().toString(36) + 随机后缀 — 比纯时间戳更抗碰撞
  - 持久化失败：try/catch + 非阻塞告警横幅，应用在内存中保持正常运行
```

### Superpowers Write Plan

第三步：使用 Superpowers write plan，根据 Design 文档生成 Plan。

```text
使用 superpowers writing-plans，基于 Design Doc 创建实现计划。

计划要求：
- 保存至 docs/superpowers/plans/YYYY-MM-DD-<feature>.md
- 引用设计文档，拆分为可执行任务
- Plan 文件头必须包含：
  ---
  change: <openspec-change-name>
  design-doc: docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md
  base-ref: <先运行 git rev-parse HEAD 记录当前提交>
  ---

计划创建后：
1. 创建新分支：git checkout -b <change-name>
2. 使用 superpowers subagent-driven-development 执行实现

逐任务实现，每完成一个任务：
1. 在 tasks.md 中勾选（[ ] → [x]）
2. 提交代码，commit message 体现设计意图

实现中发现 spec 不完整时的处理：
- 缺少验收场景/边界条件 → 直接编辑 delta spec + design.md，追加 tasks.md 任务
- 接口变更/新组件/数据流变化 → 重新  superpowers brainstorming 更新 Design Doc
- 全新能力需求 → /opsx:new 创建新的 OpenSpec change
- 新增任务超过初始任务数的 50% → 考虑拆分为新 change
```

### Superpowers 实现

第四步：使用 Superpowers 的 subagent-driven-development 实现

输出

```text
⏺ 计划已创建。现在创建分支并提交计划。

⏺ Bash(git checkout -b web-todo-app)
  ⎿  Switched to a new branch 'web-todo-app'

⏺ Bash(git add docs/superpowers/plans/2026-05-26-web-todo-app.md && git commit -m "chore: add
      implementation plan for web-todo-app")
  ⎿  ok 1 file changed, 158 insertions(+)
     ok web-tod

⏺ 现在使用 subagent 驱动的开发来执行实现。每个任务都有一个专门的 agent。我将逐个任务地开始执行。

⏺ 开始执行。T1–T3
  是无依赖的骨架任务，我将按顺序实现它们（它们共享项目上下文，子代理将需要完整设计）。让我从 T1
  开始。

⏺ Agent(T1: Create index.html)
  ⎿  Initializing…

✢ Creating HTML structure… (1m 39s · ↓ 2.8k tokens)
  ⎿  ◼ T1: HTML structure
     ◻ T9: Integration verification
     ◻ T4: State operations + ID generation
     ◻ T5: Persistence layer
     ◻ T8: Completed task styling
      … +4 pending

......
......

 ⏺ 所有9项任务已实现并提交。这是摘要：

  分支：web-todo-app (11 次提交)

  交付物：
  - 实现计划：docs/superpowers/plans/2026-05-26-web-todo-app.md
  - 设计文档：docs/superpowers/specs/2026-05-26-web-todo-app-design.md
  - 增量规范（5个新场景已回写）：
    - task-management：空白输入拒绝
    - task-persistence：写入失败 + 部分有效数据恢复
    - task-ui：XSS 安全渲染 + 回车键空输入保护
  - 应用文件：index.html + style.css + app.js

  应用内关键设计决策：
  - textContent (从不 innerHTML) — XSS 安全
  - 事件委托，通过 dataset.action — 与全量重新渲染兼容，无监听器泄漏
  - generateId() = base-36 时间戳 + 随机后缀 — 碰撞安全
  - try/catch 在 saveTasks() 中 — 隐私浏览/配额失败 → 非阻塞横幅
  - isValidTask() 过滤器在 loadTasks() 中 — 部分损坏不会破坏整个列表
```

### 验证

第五步：OpenSpec + Superpowers 双重验证，分别验证是否完成。

```text
使用 openspec-verify-change 做完整验证，然后 superpowers 的 finishing-a-development-branch
处理分支。验证不通过则修复。
```

### OpenSpec 归档

第六步：OpenSpec 归档 Spec，纯 OpenSpec 操作：

```bash
/opsx:archive
```

所有变更将被保存至 `openspec/changes/archive/`，支持版本追溯与团队共享。

## Comet 工具分享

之前按照 Demo 中的流程，通过 Prompt 串联基本实现了 OpenSpec + Superpowers 的协同工作流。然后刚好最近在 Github 上发现了 [Comet](https://github.com/rpamis/comet) 工具，它把整个协作流程自动化了。

![comet](https://alphahinex.github.io/contents/openspec-superpowers/comet-runner.png)

### Comet 工作流

Comet 将 OpenSpec、Superpowers 串联为五阶段自动化流水线：

- **Open（打开变更）**：openspec-explore + openspec-propose，生成 proposal、specs、design、tasks
- **Design（深度设计）**：superpowers:brainstorm + writing-plans，细化技术方案，补充缺失场景
- **Build（实现）**：superpowers:subagent-driven-development，TDD 实现 + 两阶段代码审查
- **Verify（验证）**：openspec-verify-change + superpowers:finishing-a-development-branch，双重验证
- **Archive（归档）**：openspec-archive-change，同步 delta spec、标注状态

同时 Comet 注册了以下技能，其中 5 个主流程技能对应协同工作流的各个阶段，另外 2 个是快捷路径：

- `/comet`：主入口，自动检测当前阶段并分派到对应子命令
- `/comet-open`：阶段 1 — 打开变更（提案、设计、任务分解）
- `/comet-design`：阶段 2 — 深度设计（头脑风暴、设计文档）
- `/comet-build`：阶段 3 — 规划与构建（实现计划、代码提交）
- `/comet-verify`：阶段 4 — 验证与完成（测试、验证报告）
- `/comet-archive`：阶段 5 — 归档（delta spec 同步、状态标注）
- `/comet-hotfix`：快捷路径 — 快速 bug 修复，跳过头脑风暴，不需要能力设计
- `/comet-tweak`：快捷路径 — 小改动，如文案调整、配置调整、文档或 Prompt 优化

一般我们只会用到 `/comet` 命令，由 Comet 根据当前状态自动判断下一步该执行什么。

同时为了提升效率，对于一些小改动 comet 也提供了 `/comet-hotfix` 和 `/comet-tweak` 命令。

### 安装

comet 通过 npm 安装：

```bash
npm install -g @rpamis/comet
```

### 使用

首先到项目根目录进行初始化：

```bash
cd your-project
comet init
```

然后直接使用 comet 命令即可：

```bash
/comet "帮我实现一个 TODO 应用"
```

comet 会自动按照 `open-design-build-verify-archive` 五阶段工作流执行。

这里以 kcctl 命令优化为例，展示具体流程：

#### 开始

首先会判断当前处于什么阶段，这里是新需求，所以是重头开始：

```bash
$ /comet "帮我优化 kcctl 中的 operation 和 logs 命令，希望提高日志展示上的可读性"

# 先自动检测当前阶段
- 按照 Comet 流程，先检测活跃 Change 和 Preset。
# 判断，如果是 hotfix、tweak 会走简化流程
- 没有活跃 Change，这不是 hotfix 也不是 tweak（是功能优化改进），需要进入 /comet-open 创建新变更。
```

#### 阶段一：Open

然后自动进入第一阶段 Open，也就是 openspec-explore + openspec-propose 生成 Spec。

```text
# 进入第一阶段 open
- 按照 comet-open 流程，先探索问题空间。

⏺ Skill(openspec-explore)
  ⎿  Successfully loaded skill
  
⏺ Bash(openspec new change "improve-kcctl-operation-logs")
  ⎿  - Creating change 'improve-kcctl-operation-logs'...
     ✔ Created change 'improve-kcctl-operation-logs' at openspec/changes/improve-kcctl-operation-logs/ (schema: spec-driven)
     
 ⏺ 设计和规范已就绪，并行创建。
 ⏺ Change 创建完成。现在初始化 comet 状态并运行 open 阶段守卫。
```

阶段完成后会运行阶段守卫（就是一个检测脚本），确保当前阶段真的完成了。当前 open 阶段则是判断 OpenSpec 的 Spec（proposal、specs、design、tasks）是否正常生成了，如果检测发现没有则不会进入下一阶段。

> 通过脚本硬性检测，保证 AI 不会漏掉任何一个阶段。

#### 阶段二：Design

检测通过后自动进入第二阶段，Superpowers brainstorming：

```text
# 进入第二阶段 desgin
Open 阶段完成，自动流转到 design 阶段。继续 /comet-design。

⏺ 交接包已生成。现在进入 brainstorming 阶段做深度技术设计。

⏺ Skill(brainstorming)
  ⎿  Successfully loaded skill

⏺ 我先阅读一下交接上下文，并探究当前的代码库结构。

⏺ Explore(Explore kcctl command patterns)
  ⎿  Done (18 tool uses · 57.7k tokens · 1m 43s)
  (ctrl+o to expand)

✽ Offering visual companion… (5m 47s · ↑ 8.4k tokens)
  ⎿  ✔ Explore project context for operation/logs design
     ◼ Offer visual companion for TUI layout questions
     ◻ Spec self-review
     ◻ Write design doc
     ◻ User reviews spec
     
⏺ 好，先启动了可视化服务器。现在进入第一个设计问题。

  TUI 日志查看界面的布局是核心设计决策。spec 里写的是"步骤列表在左，日志内容在右"的分栏布局，但还有别的可能性。让我用浏览器展示几个布局方案给你比较。
  
⏺ 浏览器里展示了 3 种 TUI 布局方案，请打开 http://localhost:59683 查看：

  - A: Split Panel — 左侧步骤列表，右侧日志内容，点步骤切换日志
  - B: Stacked — 顶部步骤横排，下方日志区，纵向日志空间更大
  - C: Tree View — 树形展开折叠，日志内嵌在步骤下方，最简洁

  看看哪个直觉上最好用？

✻ Sautéed for 1m 19s

❯ 方案 A 

⏺ 设计方案已基本成型，让我整理一下完整设计然后给你确认。


⏺ 好，现在写 Design Doc。
⏺ Design Doc 已写入 docs/superpowers/specs/2026-05-27-kcctl-operation-logs-design.md。请审阅一下，有要改的告诉我，没问题的话我们进入实施计划。

❯ 继续吧
```

这个就是 Superpowers 头脑风暴的优点，可以确认很多细节上的需求，避免后续做出来不是自己想要的。

#### 阶段三：Build

然后进入第三阶段：build，使用 Superpowers 的 subagent-driven-development 开始实现：

```text
⏺ Design 阶段通过，自动流转到 build。现在调用 comet-build。

⏺ Skill(comet-build)
  ⎿  Successfully loaded skill
  
⏺ Step 1: 制定实施计划。
⏺ Step 3: 工作区隔离。这个变更涉及 ~15 个文件（新增 pkg/cli/operation/ 整个目录 + 修改 api.go/root.go/logs.go），推荐创建分支。

⏺ Step 4: 选择执行方式。计划有 20 个任务，跨 5 个 phase，推荐 subagent-driven-development。
执行方式？计划有 20 个任务，跨 5 个 phase，推荐 subagent 模式。

❯ 1. Subagent-driven (Recommended)
     任务独立、复杂度高，子 agent 并行执行 + 双阶段审查。适合 20 个任务的规模
  2. Executing-plans
     任务简单、轻量快速，顺序执行。适合小规模
  3. Type something.
  

⏺ 好的，我现在已经掌握了所有上下文。让我创建任务追踪并开始分派子代理。任务1.1-1.4是小型API客户端的修改，可以作为一个批次处理；2.1-2.5是操作子命令；3.1-3.4是纯文本日志；4.1-4.6是TUI；5.1-5.4是测试
  。

⏺ 开始第一阶段。正在派遣实现者子代理执行 API 客户端扩展。

✢ Implementing API client extensions… (2m 9s · ↓ 3.9k tokens · almost done thinking)
  ⎿  ◼ Phase 1: API Client Extensions (1.1-1.4)
     ◻ Phase 2: Operation Subcommand Framework (2.1-2.5)
     ◻ Phase 3: Operation Logs Plain-Text Mode (3.1-3.4)
     ◻ Phase 4: TUI Log Viewer (4.1-4.6)
     ◻ Phase 5: Tests (5.1-5.4)
....
✽ Pontificating… (42m 30s · ↓ 68.8k tokens · almost done thinking)
  ⎿  Tip: Use /clear to start fresh when switching topics and free up context
  
  
- 所有 5 个阶段都已完成。让我进行最终的构建+测试验证，然后运行构建守卫。
```

这一阶段耗时会比较长，AI 会根据前面的计划挨个实现，用上 Superpowers 之后，代码质量比直接 opsx:apply 会好不少。

#### 阶段四：Verify

Build 完成后会自动进入 Verify 阶段，对照 Spec 以及代码，确认所有功能都已经实现完成。

```text
⏺ Build 阶段全部通过，自动流转到 verify。进入 comet-verify。
⏺ 已评估为完整验证模式。让我再用 base-ref 复核提交区间。

⏺ 所有制品都已完成。现在让我根据完整的验证检查清单手动执行完整的验证。

⏺ 验证发现了 1 个 FAIL 和 2 个 minor 问题。主要问题是 kcctl operation list 缺少 sponsor 列。让我修复。


⏺ 所有验证问题已修复。现在运行收尾流程。

⏺ Skill(finishing-a-development-branch)
  ⎿  Successfully loaded skill
```

发现问题也会自动进行修复。

#### 阶段五：Archive

最后就是归档了，Verify 之后自动流转到 Archive：

```text
⏺ Verify 阶段通过，自动流转到 archive。进入最后阶段。

⏺ Skill(comet-archive)
  ⎿  Successfully loaded skill
  
⏺ 归档完成，8/8 步骤全部成功。

  brainstorming → delta spec → 实施 → 验证 → 主 spec 覆盖 → design doc 标注 → 归档 ✓

  Comet 流程全部完成。
```

至此，整个流程就完成了。

## 小结

OpenSpec + Superpowers 组合的核心思想是：**用 OpenSpec 生成和管理 Spec，然后用 Superpowers 这个"资深工程师"来执行 Spec。**

单独使用各有短板，二者结合刚好形成**“规格驱动开发(SDD) + 测试驱动开发(TDD)”**的完整工作流。

- **OpenSpec (SDD)：对齐设计需求**，在编码前生成结构化变更提案(proposal)、需求规范(specs)、技术设计(design)和任务拆解(tasks)
- **Superpowers (TDD)：保证代码质量**，强制 AI 遵循 TDD、YAGNI、DRY 等工程原则

![combined-workflow](https://alphahinex.github.io/contents/openspec-superpowers/combined-workflow.jpg)

如果觉得手动切换两个工具比较繁琐，可以尝试 Comet 将整个流程自动化。
