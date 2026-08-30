---
id: skills-lock
title: "【转】skills-lock.json：给 Agent Skills 上一把锁"
description: "Agent Skill 的版本控制和可复现性"
date: 2026.08.30 10:34
categories:
    - AI
tags: [AI]
keywords: Skills, skill, skills.sh, agent skill, skills-lock.json, skills-lock, lock, reproducibility
cover: /contents/skills-lock/lock-entry.svg
---

- 原文地址：https://meiki.dev/blog/skills-lock/
- 原文作者：[meiki的胡思乱想](https://meiki.dev/)

---

[上一篇](https://meiki.dev/blog/agent-skills/) 我把博客里那套「怎么加一个工具」的规矩做成了一个 Skill，省下了反复交代的口舌。那篇讲的是「自己写一个 skill」。可我电脑里现在装着的 skill，绝大多数不是我自己写的——是从别人仓库、从飞书的 well-known 端点拉来的一大票（光飞书那套 lark-* 就几十个）。

事情一到这一步，性质就变了。自己写的那个，坏了我自己修；可这些拉来的，背后是别人的仓库，别人随时在改。于是我开始好奇一个很实际的问题：**我今天装的这一批 skill，明天换台机器、或者让 CI 跑、或者哪个朋友 clone 我的仓库，他们装到的还是同一批、同一个版本吗？** 翻了一圈，我在自己机器上 `~/.agents/` 目录下发现了一个我没主动建过的文件：`.skill-lock.json`。顺着它查下去，才搞明白这就是答案——它和项目里那个 `skills-lock.json` 是一回事的两个落点。

## skills-lock.json 是什么

一句话：它是 **Agent Skills 的 `package-lock.json`** 。

你大概熟悉 npm 那套——`package.json` 写你「想要哪些依赖」，`package-lock.json` 锁死「实际装了哪些、精确到哪个版本」，后者提交进 git，保证别人 `npm ci` 装出来的和你一模一样。skill 现在也有了同一套东西。管它的命令行工具叫 `skills`（[vercel-labs/skills](https://github.com/vercel-labs/skills)，平时 `npx skills` 调用），你用它装第一个 skill 的时候，它就顺手把这个 lock 文件生成出来了。

它记的不是 skill 的内容，而是 skill 的**出身和指纹**。我把自己机器上那条真实记录拆开看了看，长这样：

![lock entry](https://alphahinex.github.io/contents/skills-lock/lock-entry.svg)

```json
{
  "version": 3,
  "skills": {
    "lark-im": {
      "source": "open.feishu.cn",
      "sourceType": "well-known",
      "sourceUrl": "https://open.feishu.cn/.well-known/skills/lark-im/SKILL.md",
      "skillFolderHash": "",
      "installedAt": "2026-05-22T01:54:05.059Z",
      "updatedAt": "2026-05-22T01:54:05.059Z"
    }
  }
}
```

上面这段是我直接从机器上 `~/.agents/.skill-lock.json` 抠出来的真东西（`version: 3`），不是我编的示例。每个字段在说什么：

- **`source` / `sourceType` / `sourceUrl`** ：这条 skill 从哪来。`sourceType` 可能是 `github`（GitHub 仓库）、本地路径，或者我这台机器上看到的 `well-known`（飞书把 skill 挂在 `.well-known/` 端点上分发）。后面的 url 是拉取它的确切地址。
- **`skillFolderHash`** ：内容指纹，对 GitHub 来源来说就是那个 skill 文件夹的 **tree SHA**。这是整套「能不能查更新」机制的命根子，下面 How 部分细说。
- **`installedAt` / `updatedAt`** ：装上、以及最近一次更新的时间戳。

这里有个我亲眼看到、值得记一笔的细节：**我那些飞书 skill 的 `skillFolderHash` 全是空字符串**。因为它们是 `well-known` 来源，不是 GitHub 仓库，没有 tree SHA 可记。也就是说「靠 hash 比对来发现更新」这套玩法，只对 GitHub 来源的 skill 真正生效——这点官方文档我没找到明说，是我对着自己的文件推出来的，姑且当个观察。

还有个容易绊一下的点，关于这文件到底叫什么、放哪：

| | 全局锁 | 项目锁 |
|---|---|---|
| 路径 | `~/.agents/.skill-lock.json` | `skills-lock.json`（仓库根目录） |
| 管的是 | 你这台机器上全局装的 skill | 当前这个项目的 skill |
| 进 git 吗 | 不进（在你 home 目录） | 进，跟代码一起提交 |

注意这俩文件名其实对不齐：全局那个是单数加点的 `.skill-lock.json`，项目那个是复数的 `skills-lock.json`。用户真正会提交、会分享、这篇标题写的，是项目级那个。两者是同一套 v3 格式，区别只在放哪、给谁用。（我机器上现成的是全局那份；项目级的我还没在真项目里生成过，格式一致这点是按文档推的，自己打个折扣。）

## 它怎么工作、怎么用

`skills` 这个 CLI 的命令，几乎是照着 npm 的肌肉记忆设计的。常用的就这几个：

```bash
npx skills add owner/repo          # 装一个 skill（顺手写进 lock）
npx skills add -g owner/repo       # 装到全局
npx skills list                    # 看装了哪些（别名 ls）
npx skills check                   # 查上游有没有更新
npx skills update                  # 把更新应用上
npx skills remove                  # 删掉（别名 rm）
npx skills experimental_install    # 按 lock 还原（还挂着 experimental 前缀）
```

把它们串成一条线，就是这个文件的完整生命周期：

![reproducibility](https://alphahinex.github.io/contents/skills-lock/reproducibility.svg)

**第一步，装与记。** `skills add owner/repo` 把 skill 拉下来装好，同时在 lock 文件里写下那条记录——来源、那一刻的 `skillFolderHash`、时间。你不用手写这个文件，它和 `package-lock.json` 一样是工具维护的产物，**别去手改**。

**第二步，提交。** 把 `skills-lock.json` 加进版本库，跟你的代码一起走。这一步是整件事的支点：没提交，下面两步全免谈。

**第三步，还原。** 别人 clone 下来、或 CI 起一个干净环境，跑 `skills install`（npm 那边对应 `npm ci`），它就照着 lock 把同一批 skill、同一个指纹版本装出来。这样大家的 agent 读到的是同一套指令，行为才对得齐。

把 lock 提交、靠它还原，这是官方明确推荐的用法。但要说句实在的： **`install` / `sync` 这几个还原命令目前都还挂着 `experimental` 字样** ，官方仓库里「从 lock 一键还原」（`npm ci` 那种体验）甚至还是[挂着的 feature request](https://github.com/vercel-labs/skills/issues/549)。所以这第三步今天能用，但还嫩，别当成 npm 那么成熟的东西。

至于「查更新」是怎么做到的，机关全在那个 hash 上：`skills check` 拿你 lock 里记的 `skillFolderHash`，去和上游那个 skill 文件夹当前的 tree SHA 比一下——**对不上，就说明上游改过了**，它提示你有更新；`skills update` 帮你拉新版、并把 lock 里的 hash 改写成最新的。就这么个朴素的比对。Thilo Maier 在[他那篇讲这个 lock 文件的笔记](https://maier.tech/notes/a-lockfile-for-agent-skills)里点出了关键：**在有这套之前，你根本没法知道一个 skill 有没有更新**——只能手动重装一遍，再靠 git diff 看看变了没。lock + hash 把这件事从「手动考古」变成了「一条命令」。

## 为什么 skill 需要一把锁

前面都是机制。但我真正想清楚的是这一层：**为什么这东西值得存在**。

答案就一句：**一旦你用上了别人写的 skill，你就背上了一个依赖**。而且是个挺特殊的依赖——它不是一段会被编译执行的代码，它是一段「agent 会照着做的指令」。你那句「这个仓库该怎么改」的规矩，有一部分现在住在别人的仓库里，由别人维护、别人随时能改。没有 lock 的依赖，就是经典的「在我机器上是好的」——只不过这次飘忽不定的不是代码行为，是 **agent 的行为**。

把锁加上，换来三件具体的好处，刚好对上前面那两张图：

1. **可复现。** 队友、CI、外包、还有半年后忘了一切的我自己，照着同一个 lock 装出同一批 skill，agent 读到的指令就是同一套。不会出现「你那儿 Claude 一句话就把活干对了，我这儿它压根不知道规矩」。
2. **更新可见。** 上游把某个 skill 改了，hash 就对不上，`skills check` 让你**看见**这次变更，然后由你决定跟不跟。这比两个极端都强：要么你从来不更新、慢慢和上游飘移；要么你盲目跟最新、哪天它悄悄改坏了你都不知道。
3. **供应链卫生。** 这点是我作为一个「自己东西自己扛」的人最在意的。skill 是 agent 会拿着我的工具、我的凭据去执行的指令。把 hash 钉死，意味着上游的改动没法悄悄改变我 agent 的行为——它一变，hash 就报警，我可以像 review 一次依赖升级那样，先看清 diff 再决定要不要收。

说到底，这和我[用 workflow 搭 MVP](https://meiki.dev/blog/claude-code-dynamic-workflows/)、[给博客写 skill](https://meiki.dev/blog/agent-skills/) 时反复念叨的是同一件事：**工具能把活儿做快，但给成品兜底的永远是人**。lock 文件不替我做判断，它只是把「我的 agent 接下来会照着哪版指令干活」这件事，变成可钉死、可 review 的——而钉的是哪一版、要不要升，决定权还在我手里。

## 碎碎念

**工具还年轻，别当成熟品用。** `install` / `sync` 还是 `experimental`；Maier 还提到 `remove` 删 skill 时[并不会同步更新 lock 文件](https://maier.tech/notes/a-lockfile-for-agent-skills)——也就是说 lock 有可能和你实际装的东西对不上。这套东西方向对，但细节还在长，踩到不一致别太意外。

**别和「声明清单」搞混。** 我看到有[第三方文章](https://dev.to/toyama0919/managing-ai-agent-skills-with-npx-skills-a-practical-guide-2an8)提到还有个 `.skills.json` 充当「你想要哪些 skill」的声明清单（类比 `package.json`），和锁定实际版本的 lock 文件分工。这个我没在自己机器上确认过，先记一笔：真要类比 npm，就是「声明」和「锁定」两份文件，这篇讲的是后者。

**锁定 ≠ 审过。** 钉死 hash 能挡住「上游悄悄改」，但**第一次**把一个 skill 装进来的时候，你信的是它当下那段指令本身。lock 只保证「以后不偷偷变」，它不替你判断「这段指令值不值得信」。该读的还是要读——尤其是带 `allowed-tools`、能动你文件和凭据的那种。

**它不是 Claude 专属的。** 管 lock 的 `skills` CLI 来自 Vercel，配合的是[跨工具的 Agent Skills 标准](https://agentskills.io)。所以这套「锁定 + 还原」不绑死在某一个 agent 上——这点我觉得是好事，但具体到每个工具认不认 lock，我没逐一验证。

## 小结

`skills-lock.json` 就是 Agent Skills 的 `package-lock.json`：记下你装了哪些 skill、从哪来、指纹是什么，好让这批 skill 能被精确复现，也让上游的更新变得**看得见**。机制朴素——出身 + 一个 hash + 几个时间戳；命令也照着 npm 的肌肉记忆来。工具本身还嫩（还原命令挂着 `experimental`、`remove` 不同步 lock），但它背后的判断我完全同意：**一旦 skill 成了从别处拉来的依赖，它就该有一把锁**。

想看一手的，CLI 在这儿：[vercel-labs/skills](https://github.com/vercel-labs/skills)；把 lock 文件的来龙去脉讲得最清楚的是 Thilo Maier 的[这篇笔记](https://maier.tech/notes/a-lockfile-for-agent-skills)；想先搞懂 skill 本身是怎么回事，可以回看我[上一篇](https://meiki.dev/blog/agent-skills/)。等我在真项目里把它用起来、踩过更多坑，再回来更新这篇。