---
id: noc-online-quiz
title: "全国中小学信息技术创新与实践大赛（NOC）Python 在线练习"
description: "收集到的一些全国中小学信息技术创新与实践大赛（NOC）Python 真题和模拟题在线练习"
date: 2024.03.10 10:26
categories:
    - Python
tags: [Python, NOC]
keywords: NOC, Python, Online, Quiz, 全国中小学信息技术创新与实践大赛
cover: /contents/covers/noc-online-quiz.png
---

收集到的一些 [NOC](http://s.noc.net.cn/Home/Index) Python 真题和模拟题

在线练习地址：https://alphahinex.github.io/NOC

欢迎纠错和补充习题

题库文件 `noc.js`，题目格式：

```json
{
    "question":"[多选]下面哪些代码可以往列表 ls 中添加元素?",
    "image":"noc/mock27.png",
    "choices":["A.ls.append()","B.ls.clear()","C.ls.pop()","D.ls.insert()"],
    "correct":["A.ls.append()","D.ls.insert()"],
    "explanation":"在 Python 中，append() 和 insert()都可以往列表中增加元素，只是 append 是在最后增加，insert 可以自由的插入列表中。clear() 函数是用来清空列表的。pop()函数是删除最后一项，并且作为返回值。"
},
```

`image` 和 `explanation` 可为空，`correct` 为正确选项，可多个，需包含 `choices` 中正确选项的完整内容。

基于 https://github.com/AlphaHinex/ACP 。