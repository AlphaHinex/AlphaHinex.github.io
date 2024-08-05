---
id: postfile-for-ab
title: "构造 ApacheBench 可用的 postfile"
description: "本文描述了如何使用 ApacheBench 测试文件上传接口"
date: 2024.08.04 10:34
categories:
    - Test
tags: [HTTP, Java]
keywords: Apache Bench, ab, test, postfile, putfile, media-type, multipart/form-data, RFC 7578, RFC 2046, CRLF, boundary, Content-Disposition, form-data, filename
cover: /contents/covers/postfile-for-ab.png
---


## 摘要

在 `Web` 开发过程中，文件上传功能是常见的需求。对于开发者而言，确保上传功能的稳定性和性能至关重要。

本文将带你了解如何使用`ApacheBench`性能测试工具对文件上传功能进行性能测试，特别是如何按照规范构造上传文件的请求体，以便评估和提高服务器在高并发情况下的处理能力。

## ApacheBench 简介

`ApacheBench`（简称`ab`）是 `Apache` 服务器自带的一个性能测试工具，它能够模拟多用户并发请求，从而评估服务器在高负载下的性能表现。若系统中未安装 `Apache` 服务器，可前往 [Apache 官网](https://httpd.apache.org/)下载和安装。更多关于 ApacheBench 的信息，请参考：[ApacheBench 简介](https://mp.weixin.qq.com/s/5lqaOphTwsWhGHT-VSH0Tg)。

## 前置条件
假设有一个文件上传 `POST` 接口 `http://localhost:8080/upload` ，在请求体中接受 `key` 为 `file` 的文件，并返回上传的文件名和文件大小：

![](/contents/covers/postfile-for-ab.png)

通过 `Postman` 等工具，我们可以直观地看到上传文件的请求内容：

```text
POST /upload HTTP/1.1
Host: localhost:8080
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Length: 204

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="/C:/Users/admin/Desktop/test.jpg"
Content-Type: image/jpeg

(data)
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

## 问题

当需要使用 `ApacheBench` 测试上传文件的 `POST` 接口时，`ab -h` 中只写到了通过 `-p` 参数指定 `postfile`：

> -p postfile     File containing data to POST. Remember also to set -T

那么这个 `postfile` 中包含哪些内容呢？应该如何构造一个 `ApacheBench` 可用的 `postfile` 呢？

## 有关 `multipart/form-data` 的规范

[RFC 7578 第4节](https://www.rfc-editor.org/rfc/rfc7578#section-4) 中关于 `multipart/form-data` 的定义提到：`multipart/form-data` 遵循 [RFC 2046 第 5.1 节](https://www.rfc-editor.org/rfc/rfc2046#section-5.1) 中定义的多部分 `MIME` 数据流结构，并有一些变化，大致的结构要求如下：

1. 请求头必须包含 `Content-Type: multipart/form-data; boundary=边界分隔符`；
2. 多部分文件需要组合成一个单个的请求体，`边界分隔符` 字符串需保证在整个请求体内唯一，不会出现在分割行以外的其他部分；
3. 请求体必须包含一个或多个部分，每部分一个实体（如：文件）；
4. 各部分使用 [CRLF](https://developer.mozilla.org/zh-CN/docs/Glossary/CRLF) +`--` +`边界分隔符`作为一个`边界分割行`进行分隔，最后一部分后面使用 `边界分隔行` +`--`表示结束；换行符均需使用 CRLF（即 `\r\n`，即使在非 Windows 环境中）；
5. 每部分在边界分隔行之间，又由三部分组成：头区域、空白行、内容区域；
6. 每部分头区域必须包含 `Content-Disposition`  头字段，类型为 `form-data`；同时必须包含 `name` 参数，值为 `form` 中的原始字段名；当内容区域表示的是文件时，还应该提供 `filename` 参数。

更详细的内容可参考上面引用的 `RFC` 规范文档。

## 构造 postfile

下面依照规范中格式要求，构造一个只发送一个文件的 `postfile`。

### 1. 准备 postfile 文件

- 准备要上传的文件：如：`test.jpg`；
- 新建一个文本文件，命名为`postfile.txt`。

### 2. 确定边界分隔符

选择一个不会在文件内容中出现的字符串作为边界分隔符，例如：`----WebKitFormBoundary7MA4YWxkTrZu0gW`。

### 3. 编写 postfile 头区域及空白行

在 `postfile.txt` 中写入以下内容，这些内容构成了请求体的头部信息，其中 `name` 应该与服务器端接收的字段名一致，`filename` 是要上传的文件的名称。

```text
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="test.jpg"
Content-Type: image/jpeg

```

> 依据规范描述，Content-Type 头字段非必要。

**此处需注意：**

因为规范要求使用`CRLF`作为换行符，在`非 Windows` 环境中，不能直接使用文本编辑器输入上面内容，可以按如下方式通过命令构造此部分内容：

```Bash
$ echo -e '------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="file"; filename="test.jpg"\r\nContent-Type: image/jpeg\r\n\r' > postfile.txt
```
> 通过 `>`、`>>`向文件中添加内容时，会自动在最后追加一个 LR（`\n`），所以省略最后一个 `\n`。

使用 `cat -e` 可验证换行符，每行结尾是 `^M$` 代表 `CRLF`换行符：

```Bash
$ cat -e postfile.txt
------WebKitFormBoundary7MA4YWxkTrZu0gW^M$
Content-Disposition: form-data; name="file"; filename="test.jpg"^M$
Content-Type: image/jpeg^M$
^M$
```

### 4. 添加文件内容至 postfile 内容区域

由于文件内容通常是二进制数据，不能直接在文本编辑器中粘贴，可使用 `cat` 命令将文件内容追加至 `postfile` 中：

```Bash
# 将 test.jpg 文件内容追加到 postfile.txt
$ cat test.jpg >> postfile.txt
```

> Windows 系统中可在 `git bash` 中使用 `cat` 命令。

> [Benchmarking file uploads](https://gist.github.com/chiller/dec373004894e9c9bb38ac647c7ccfa8) 中以 base64 值作为文件数据内容进行传输的方式能够正常调用接口，但实测服务端接收到的数据内容依旧是 base64 的内容，并不是文件原始内容。故此处直接使用 `cat` 将文件原始数据内容直接追加到 `postfile` 中。

### 5. 添加结束标记

最后以 [CRLF](https://developer.mozilla.org/zh-CN/docs/Glossary/CRLF)+`--` +`边界分隔符`+`--` 标记结束：

```bash
# 将结束标记添加到 postfile.txt
$ echo -e "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--" >> postfile.txt
```

> 因为在将文件流内容追加至 `postfile.txt` 文件后，已无法使用文本编辑器直接打开此文件，故继续使用命令追加文件内容，同样在 Windows 环境中可以通过 `git bash` 使用 `echo` 命令。

## 执行 ab 命令

使用以下命令执行文件上传测试：

```bash
$ ab -n 1 -c 1 -p postfile.txt -v 2 \
-T "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW" \
http://localhost:8080/upload \
-v 2
```

- `-n 1` 表示总共发送 1 个请求（根据实际测试需求进行调整）。
- `-c 1` 表示同时并发 1 个请求（根据实际测试需求进行调整）。
- `-p postfile.txt` 指定包含`POST`数据的文件。
- `-T "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW"` 指定请求的内容类型，包括之前定义的边界分隔符。
- `-v verbosity`用于设置 `ApacheBench` 的详细输出级别。在详细输出级别 `2` 下，`ApacheBench`会打印出警告信息和信息信息，如：请求和响应的头部信息。

执行命令后，在控制台中，可以在 `LOG: header received:` 消息之后找到响应状态码和响应内容。如果状态码为 `200`且和预期值一致，表示服务器成功处理了请求。

在控制台中还会提供一系列关键指标，如每秒请求数、请求平均响应时间等关键指标。这些数据可以帮助分析文件上传的性能表现，并为优化提供依据。

```text
This is ApacheBench, Version 2.3 <$Revision: 1901567 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking localhost (be patient)...INFO: POST header ==
---
POST /upload HTTP/1.0
Content-length: 24223
Content-type: multipart/form-data; boundary=---WebKitFormBoundary7MA4YWxkTrZu0gW
secret-id: 3e6bec50-3bbd-4443-b141-82aaee645cc7
secret-key: f1596671ce4d30a7847a91b8c674f43c
Host: localhost:8080
User-Agent: ApacheBench/2.3
Accept: */*


---
LOG: header received:
HTTP/1.1 200
Content-Type: text/plain;charset=UTF-8
Content-Length: 113
Date: Wed, 31 Jul 2024 13:37:18 GMT
Connection: close

File uploaded successfully: postfile.txt with size: 24072 bytes
..done


Server Software:
Server Hostname:        localhost
Server Port:            8080

Document Path:          /upload
Document Length:        113 bytes

Concurrency Level:      1
Time taken for tests:   0.056 seconds
Complete requests:      1
Failed requests:        0
Total transferred:      247 bytes
Total body sent:        24512
HTML transferred:       113 bytes
Requests per second:    17.73 [#/sec] (mean)
Time per request:       56.388 [ms] (mean)
Time per request:       56.388 [ms] (mean, across all concurrent requests)
Transfer rate:          4.28 [Kbytes/sec] received
                        424.51 kb/s sent
                        428.79 kb/s total

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.0      0       0
Processing:    56   56   0.0     56      56
Waiting:       53   53   0.0     53      53
Total:         56   56   0.0     56      56
```

## 扩展 putfile

`ApacheBench (ab)` 同样适用于测试 `PUT`接口。构造`putfile`的方法与`POST`接口类似，只需确保请求体的内容和头部信息符合`PUT`请求的要求。

> -u putfile File containing data to PUT. Remember also to set -T

## 附录

### 单个文件

构造命令：

```Bash
echo -e '------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="file"; filename="file1.jpg"\r\n\r' > postfile.txt
cat 1.jpg >> postfile.txt
echo -e "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--" >> postfile.txt
```

发送请求：

```Bash
ab -n 1 -c 1 -p postfile.txt -v 2 \
-T "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW" \
http://localhost:8080/upload
```

### 多个文件

构造命令：

```Bash
echo -e '------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="file1"; filename="file1.jpg"\r\n\r' > postfile.txt
cat 1.jpg >> postfile.txt
echo -e "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r" >> postfile.txt
echo -e 'Content-Disposition: form-data; name="file2"; filename="file2.zip"\r\n\r' >> postfile.txt
cat demo.zip >> postfile.txt
echo -e "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--" >> postfile.txt
```

发送请求：

```Bash
ab -n 1 -c 1 -p postfile.txt -v 2 \
-T "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW" \
http://localhost:8080/upload2
```
