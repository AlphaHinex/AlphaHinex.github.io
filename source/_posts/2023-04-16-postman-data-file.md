---
id: postman-data-file
title: "借助 Data File 实现请求数据与 Postman 脚本的分离"
description: "本文给出一种将请求数据与 Postman JSON 脚本分离的方法，避免 JSON 中嵌套 JSON 带来的可读性和可维护性的下降"
date: 2023.04.16 10:34
categories:
    - Test
tags: [Automation test, Integration test, JavaScript]
keywords: Postman, 测试, Newman, Automation test, Integration test, data file, loops through
cover: /contents/postman-data-file/cover.png
---

# Why：问题背景

在 [使用 Postman 进行系统可接受性测试](https://alphahinex.github.io/2022/05/22/use-postman-to-do-system-acceptance-test/) 中，我们介绍了使用 Postman 进行持续测试的方法。实际使用中，我们遇到了这样一个问题：

某个请求的请求体（Request Body）异常的大，JSON 格式，80KB+，占整个 Postman 脚本的近 40% ，格式如下：

```json
{
  "roleId": "{{role_id}}",
  "resources": [
    {
      "id": "0",
       "name": "root",
       "parentId": "-1"
     },
     {
       "id": "1",
       "name": "child",
       "parentId": "0"
     },
     ……
  ]
}
```

Postman 脚本的导出文件格式也为 JSON，这个超大的 JSON 请求体进行转义之后，嵌入到 Postman 脚本的 JSON 文件中，类似下面代码片段（`request.body.raw`）的模样：

```JSON
"request": {
    "method": "POST",
    "body": {
        "mode": "raw",
        "raw": "{\r\n    \"roleId\":\"{{role_id}}\",\r\n   …………………… }",
        "options": {
            "raw": {
                "language": "json"
            }
        }
    },
    …………
}
```

这直接导致 Gitlab 的 MergeRequest 无法对涉及此请求体改动的 Postman 脚本文件调整进行 diff，不能进行 code review，想在 Postman 的 JSON 脚本文件中对此请求体的内容进行微调也变得异常困难。

虽然可以将请求体设置成 `form-data` 或 `binary` 类型再选择文件（类似文件上传），但这种方式需要调整接口的实现方式，在请求体中有变量（如：`"firstName": "{‎{firstName}}"`）需要替换时，也无法处理。

![from-data](/contents/postman-data-file/form-data-file.png)

如果在 `Pre-request Script` 或 `Tests` 里能使用 JS 从外部文件读取数据并使用就好了。在官方 [Postman App Support](https://github.com/postmanlabs/postman-app-support) 仓库中，我们也可以看到有类似需求的讨论：

- [read local file in tests in postman #798](https://github.com/postmanlabs/postman-app-support/issues/798)
- [Read external files in pre-tests and tests requests #7210](https://github.com/postmanlabs/postman-app-support/issues/7210)
- [Variable substitution in binary/external files #11708](https://github.com/postmanlabs/postman-app-support/issues/11708)

尽管有官方成员一直在关注相关讨论，并 [提到](https://github.com/postmanlabs/postman-app-support/issues/7210#issuecomment-526458551) 有考虑实现一个接口以允许从工作目录读取文件至请求体，不过至今 [仍未有实质性的进展](https://github.com/postmanlabs/postman-app-support/issues/7210#issuecomment-800262955) 。

讨论中，也有人给出了一些替代方案，如：架设一个 HTTP 服务，用以通过 REST 接口获得数据文件中的内容；或者 [Looping through a Data File in the Postman Collection Runner](https://blog.postman.com/looping-through-a-data-file-in-the-postman-collection-runner/)

# What：Postman Data File

Pstman 的 Data File 是什么呢？简单来说，就是可以用来给一组相同的测试用例喂以多组不同的数据，实现所谓参数化测试或数据驱动测试的效果，存放这多组测试数据的文件，就是 Data File —— 数据文件。

数据文件以相同的变量名存放一组值，可以是包含标题行的 `csv` 格式的：

![ramen.csv](/contents/postman-data-file/ramen-csv-screenshot.png)

也可以是 `json` 格式的：

![ramen.json](/contents/postman-data-file/ramen-json-screenshot.png)

准备好数据文件之后，可以在请求中直接通过 `{‎{variable-name}}` 直接引用：

![parameters](/contents/postman-data-file/ramen-parameters.png)

也可以在脚本中使用 `pm.iterationData.get("variable-name")` 方法获得：

![script](/contents/postman-data-file/ramen-script.png)

在 Postman App 中，需要以请求集合（Collection）的 Runner 批量运行一批请求时，才可以为该请求集合选择一个数据文件：

![runner](/contents/use-postman-to-do-system-acceptance-test/runner.png)

如果是以命令行工具 `newman` 运行 Postman 的 JSON 脚本，则需在命令行中通过 `-d` 或 `--iteration-data` 参数指定数据文件路径，如：

```bash
$ newman run demo.postman_collection.json -d resources.json
```

更详细的使用方法及样例可见 [Looping through a Data File in the Postman Collection Runner](https://blog.postman.com/looping-through-a-data-file-in-the-postman-collection-runner/)。

# How：解决方案

那么使用 Postman 的 Data File 能否解决上面提到的问题呢？

Data File 的主要作用是用来提供一组测试数据给测试用例，我们也可以只放入一个值，即把大请求体的数据作为有且仅有的一个值，放到数据文件的一个变量中，如：

```json
[
  {
    "resources": [
      {
        "id": "0",
        "name": "root",
        "parentId": "-1"
      },
      {
        "id": "1",
        "name": "child",
        "parentId": "0"
      },
      ……
    ]
  }
]
```

之所以只放入请求体中的 `resources` 属性，是因为请求体中还包括需要替换的变量（`roleId`），此时 Postman 请求中的 `Body` 是这样的：

![body](/contents/postman-data-file/body.png)

发送请求后，会遇到这样的问题 —— 发送的请求体中，`resources` 属性并不是 JSON 数组内容，而是一个个 `[object Object]` 对象：

![object](/contents/postman-data-file/object.png)

当数据文件的变量值为对象时，不能简单的直接使用数据变量进行引用，可以在 `Pre-request Script` 中，通过脚本组装请求体，再放入 `Body` 中，如：

![pre-request](/contents/postman-data-file/pre-request.png)

![new-body](/contents/postman-data-file/new-body.png)

## 约束

按照在 `Pre-request Script` 中通过 `pm.iterationData.get("variable-name")` 方法获得 JSON 数据，再存储为字符串型变量，在 `Body` 中通过数据变量引入的方式，能够解决本文最初提到的问题，但也有一些约束，如：

1. 只能通过 Runner 执行请求，不能再直接点击请求的发送按钮执行此请求，因为只能在 Runner 中选择数据文件；
1. 每个 collection 只能指定一个数据文件：当有多个类似请求时，需要在数据文件中设置多个变量，不能每个大请求体存放在一个独立的文件中，除非使用不同的请求集合。