---
id: json-lines
title: "处理大数据集的灵活格式 —— JSON Lines"
description: "格式及相关小工具介绍"
date: 2023.07.16 10:34
categories:
    - Others
tags: [Go, JSON Lines, AI]
keywords: JSON, JSON Lines, go-toolkit, files2jsonl
cover: /contents/covers/json-lines.png
---

[JSON Lines](https://jsonlines.org/)，顾名思义，就是每行都是一个 JSON，是一种文本格式。

在处理和分析大型数据集时，JSON Lines 格式成为了一种受欢迎的选择。JSON Lines 通过将每个 JSON 对象放在独立的一行中，使得逐行读取和处理数据变得简单，易于处理大型数据集、容易与现有工具集成，具有灵活性和可扩展性、易于阅读和维护等特点。

与传统的 JSON 格式相比，JSON Lines 不需要一次性加载整个文件，而是可以逐行读取和处理数据。这种特性使得 JSON Lines 非常适用于处理大型数据集，无需担心内存限制或性能问题。

## JSON Lines 特点

1. 采用 UTF-8 编码；
2. 每行必须是一个有效的 JSON 对象；
3. 在每个 JSON 对象，采用 \n 或 \r\n 作为行分隔符；
4. 建议约定：
   - JSON Lines文件通常使用文件扩展名 `.jsonl` 保存
   - 建议使用像 `gzip` 或 `bzip2` 这样的流压缩器以节省空间，生成 `.jsonl.gz` 或 `.jsonl.bz2` 文件
   - MIME 类型可以是 `application/jsonl`，但这 [还没有被标准化](https://github.com/wardi/jsonlines/issues/19)
   - 文本编辑程序将文本文件的第一行称为“第1行”。JSON Lines文件中的第一个值也应称为“第1个值”

## 举个栗子

一个大小为 1GB 的 JSON 文件，当我们需要读取/写入内容时，需要读取整个文件、存储至内存并将其解析、操作，这是不可取的。

若采用 JSON Lines 保存该文件，则操作数据时，我们无需读取整个文件后再解析、操作，而可以根据 JSON Lines 文件中每一行便为一个 JSON 值的特性，边读取边解析、操作。例如：在插入 JSON 值时，我们只需要 append 值到文件中即可。因此，操作 JSON Lines 文件时，只需要：

1. 读取一行值；
2. 将值解析为 JSON；
3. 重复 1、2 步骤。

JSON Lines 格式非常适合处理日志文件等大型数据集。它通过逐行读取和处理数据，方便了大数据场景下的分析和处理。同时，它的灵活性和可扩展性使得我们可以根据需要定义自己的数据结构。

```json lines
{"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]}
{"name": "Alexa", "wins": [["two pair", "4♠"], ["two pair", "9♠"]]}
{"name": "May", "wins": []}
{"name": "Deloise", "wins": [["three of a kind", "5♣"]]}
```

JSON Lines 在处理大量类似的嵌套数据结构方面的优势最大。
与一个满是XML文件的目录相比，使用一个 `.jsonl` 文件更容易操作。

那么如何将 JSON Lines 转换为 JSON 格式呢？下方代码为 JavaScript 示例：

```js
const jsonLinesString = `{"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]}
{"name": "Alexa", "wins": [["two pair", "4♠"], ["two pair", "9♠"]]}
{"name": "May", "wins": []}
{"name": "Deloise", "wins": [["three of a kind", "5♣"]]}`;

const jsonLines = jsonLinesString.split(/\n/);

const jsonString = "[" + jsonLines.join(",") + "]";

const jsonValue = JSON.parse(jsonString);

console.log(jsonValue);
```

### 注意

如果您有大型的嵌套结构，那么不建议直接阅读 JSON Lines 文本。使用 `jq` 工具可以更轻松地查看大型结构：

```bash
$ grep pair winning_hands.jsonl | jq .
{
  "name": "Gilbert", 
  "wins": [
    [
      "straight", 
      "7♣"
    ], 
    [
      "one pair", 
      "10♥"
    ]
  ]
}
{
  "name": "Alexa", 
  "wins": [
    [
      "two pair", 
      "4♠"
    ], 
    [
      "two pair", 
      "9♠"
    ]
  ]
}
```

## 格式校验

https://jsonlines.org/validator/ 提供一个在线的格式校验工具，可校验内容是否是合法的 JSON Lines 格式。

## files2jsonl

[files2jsonl](https://github.com/AlphaHinex/go-toolkit/tree/main/files2jsonl) 可以将一个路径下的多个文本文件（可按文件类型过滤）内容，输出成一个 JSON Lines 格式文件。输出的文件中，每行表示一个输入文件的 JSON 字符串。

具体格式如下：

```json lines
{"text": "content_of_source_file_1", "url": "absolute_path_to_source_file_1"}
{"text": "content_of_source_file_2", "url": "absolute_path_to_source_file_2"}
{"text": "content_of_source_file_3", "url": "absolute_path_to_source_file_3"}
...
```

### 用法示例

```bash
./files2jsonl -d /path/to/src \
-i xml,pom,java,groovy,yml,yaml,properties,json,sql,htm,vue,json,html,js,md,sh \
-o /path/to/target
```

- `-d` 指定源文件路径
- `-i` 指定需要包含的文件类型，不区分大小写，可省略，表示包含全部文件
- `-o` 指定输出文件路径，默认输出到当前路径

在 [Releases](https://github.com/AlphaHinex/go-toolkit/releases) 页面可以下载到此工具的预编译版本，如 Windows x86_64 位环境下可用的 `files2jsonl_win_amd64.exe`

通过如下命令可将 `C:/Users/Administrator/Desktop` 路径下的所有文件内容输出至一个 JSON Lines 文件内：

```cmd
files2jsonl_win_amd64.exe -d C:/Users/Administrator/Desktop
```

不使用 `-o` 参数指定输出文件时，默认在当前路径生成一个 `data.jsonl` 文件和 `data.jsonl.gz` 文件：

```data.jsonl
{"text":"#!/bin/bash\nnohup ... \n","url":"C:\\Users\\Administrator\\Desktop\\start.sh"}
{"text":"package com.xxx.entity;\r\n","url":"C:\\Users\\Administrator\\Desktop\\Test.java"}
...
```