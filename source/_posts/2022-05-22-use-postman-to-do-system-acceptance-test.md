---
id: use-postman-to-do-system-acceptance-test
title: "使用 Postman 进行系统可接受性测试"
description: "Postman 发请求及测试基本用法介绍"
date: 2022.05.22 10:26
categories:
    - Test
tags: [Automation test, Integration test, JavaScript]
keywords: Postman, 测试, Newman, Automation test, Integration test
cover: /contents/use-postman-to-do-system-acceptance-test/cover.png
---

在微服务架构盛行的今天，一套系统涉及到的组件数量是非常庞大的，这不仅增大了系统部署的难度，也提出了一个在系统部署完成后如何进行基本的可用性检查这样一个问题。

有人可能会说我们有完善的测试用例，有专门的测试团队，这完全不是问题，那么问题来了：

1. 人工执行的测试用例，通常需要执行人具备一定的专业测试技能及责任心；自动化测试用例则不仅有更高的技能要求，对测试工具及环境也有依赖；
1. 测试团队的资源是有限的，通常申请测试资源时都需要进行排队等待。

可以用检车来类比一下：检车的流程是固定的，检测的项目就好比测试用例。然而作为车主，在需要检车时，仍然需要将车开到检车线，由专业的人员使用专业设备进行检测，通常还需要排队等待，并支付必需的费用。

在系统进行全新部署、更新升级后，用户会希望能够像检车或保养一样，对系统的主要功能进行一个基本的可用性检测，以避免在需要使用系统某些功能时才发现功能无法正常使用。

这个过程如果能够由用户自己完成，并且不需要付出额外的代价（排队等待、测试资源、技能门槛等），岂不美哉？

如果你也觉得真香，不妨看看下面的方案。


Postman
=======

最初对 Postman 的印象，是一个浏览器插件，可以帮助用户通过浏览器发送非 GET 类请求。在可以使用 [curl](https://curl.se/) 及 IDEA 的 [HTTP Client](https://www.jetbrains.com/help/idea/http-client-in-product-code-editor.html) 完成各类请求的发送时，对 Postman 确实没有什么额外的需求。

但当我们从技术视角切换到用户视角时，Postman 就变得非常有用了。[Postman](https://www.postman.com/) 现在不仅仅是一个浏览器插件，引用官网的描述：

> What is Postman?
> 
> Postman is an API platform for building and using APIs. Postman simplifies each step of the API lifecycle and streamlines collaboration so you can create better APIs—faster.

从 [官方下载页面](https://www.postman.com/downloads/) 可以选择一种习惯的使用 Postman 的方式。以桌面客户端为例，安装后可以注册一个账号或跳过登录直接使用，大致界面如下：

![主界面](/contents/use-postman-to-do-system-acceptance-test/app.png)

如果像上图一样，将测试用例都通过 Postman 进行描述和组织，那么用户只需要点击最明显的那个 `Send` 按钮，就可以完成测试请求的发送，甚至得到如下图一样的测试报告：

![测试报告](/contents/use-postman-to-do-system-acceptance-test/result.png)

通过测试报告中的成功和失败数量以及明显的颜色标识（绿色成功、红色失败），可以直观的观测到测试用例的执行通过情况。使用 Postman 进行系统的一个基本的可接受性测试，操作简单，结果直观，可以随时进行，不受任何资源限制。

唯一复杂一些的可能是测试用例的编写，而这是可以由技术人员事先编写好的。下面先来具体说说如何执行这些测试用例，再来介绍一些常见场景的测试用例如何编写。


如何执行测试用例
=============

准备
---

在 Postman 中，请求需要放在一个 `Collection` 下，可以将之理解为一个请求的集合，集合中可以任意创建文件夹及子文件夹，但导入导出是以集合为单位的。每个集合中所配置的文件夹、请求及测试脚本等内容，可以导出为一个 `.json` 文件。例如下图中，`云平台可用性验证` 即为一个 `Collection`，可以在右侧 `。。。` 按钮中找到导出（`Export`）功能，得到一个 `云平台可用性验证.postman_collection.json` 文件；用户拿到 JSON 文件后，通过下图右上角的导入（`Import`）功能导入，即可在 Postman 中看到这个集合了。

![导出导入](/contents/use-postman-to-do-system-acceptance-test/exp-imp.png)

执行
---

执行的粒度则要灵活得多，可以集合或文件夹为单位批量执行，也可以像最开始提到的那样直接点击 `Send` 按钮发送请求进行单一接口的测试。

选择集合或文件夹后，可以在主界面找到 `Run` 按钮，点击后会弹出一个 `Runner` tab 页，可调整一些执行参数，如接口调用顺序、全部或部分执行、循环次数（`Iterations`）、两个接口的调用间隔（`Delay`），及是否保存响应（`Save responses`）。

在进行系统可接受性测试时，可只循环一次，并适当加长调用间隔时间来模拟人工操作，以免接口调用过快造成有前后依赖关系的接口失败。配置完成后，点击页面蓝色主按钮进行执行，并可在执行结束后获得前面提到的测试报告。

![执行配置](/contents/use-postman-to-do-system-acceptance-test/runner.png)

简单总结一下，执行测试用例的过程：
1. 获取并选择要执行的用例集合（或文件夹）；
1. 调整或使用默认的运行参数，运行用例；
1. 得到执行报告，根据是否有失败的用例，判断系统是否可被接受。

系统是否可被接受的标准，可以通过测试用例来描述。接下来让我们来看看如何使用 Postman 来编写一些常见场景的测试用例。


如何编写测试用例
=============

Postman 中可以方便的配置 HTTP 请求信息，如 URL、方法、请求头、请求体等，并且可以在请求发送之前（[Pre-request Script](https://learning.postman.com/docs/writing-scripts/pre-request-scripts/)），以及请求响应之后（[Test Script](https://learning.postman.com/docs/writing-scripts/test-scripts/)），执行一些 JS 脚本。

Postman 可用的 JS 内容可参考 [Postman JavaScript reference](https://learning.postman.com/docs/writing-scripts/script-references/postman-sandbox-api-reference/) 。

如果你想先快速写一些测试脚本体验一下，可以直接使用界面右侧的链接快速获得对应测试脚本片段，如校验响应的状态码为 `200`：

![测试脚本](/contents/use-postman-to-do-system-acceptance-test/snippets.png)

断言
---

Postman 中 [断言](https://learning.postman.com/docs/writing-scripts/script-references/postman-sandbox-api-reference/#writing-test-assertions) 可以这样写：

`pm.test(testName:String, specFunction:Function):Function`

如：

```js
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});
```

此外，目前还是可以使用以前的 [已经弃用](https://learning.postman.com/docs/writing-scripts/script-references/test-examples/#previous-style-of-writing-postman-tests-deprecated) 的语法：

```js
tests["Status code is 200"] = responseCode.code === 200
```

虽然已弃用的语法看着更简洁，但在断言失败时，只会提示出本应为真的 `responseCode.code === 200` 这个表达式得到的是 `false`；而第一种断言写法会在执行结果中，明确的告诉你断言失败的原因是因为期望得到 `200` 响应码，实际得到的却是 `XXX`。

使用变量
-------

通常我们可能需要在请求中使用之前请求得到的响应中的数据。例如先新增了一条数据，之后需要通过新增这条数据的 ID 来进行更新和删除等操作。

在 Postman 中，可以使用 [变量](https://learning.postman.com/docs/sending-requests/variables/)，来完成这类操作。

集合的变量可以在界面中直接进行设定：

![变量](/contents/use-postman-to-do-system-acceptance-test/variables.png)

例如请求的 URL 前缀、Cookie 等内容，可以设定为集合变量，供集合内的所有请求所使用。

设定变量时有两个值：初始值（`INITIAL VALUE`）与当前值（`CURRENT VALUE`）。可以这样理解这两个值：
1. 初始值是会被持久化的值，即导出的 JSON 文件中会包含初始值，但不会包含当前值；
1. 如果未设置当前值，当前值默认取初始值；
1. 获取和更改变量值时，操作的是当前值，而不是初始值。

除预先设置变量外，还可以通过 JS 脚本对变量进行操作，如：

```js
// 设置集合变量
pm.collectionVariables.set("variable_key", "variable_value");
// 获取集合变量
pm.collectionVariables.get("variable_key");
```

在非 JS 脚本环境，变量可以直接通过 `{‎{variable_key}}` 的方式获取。

回到上面新增再删除记录的场景，可以先创建一个新增记录的请求，在其 `Tests` 标签页中解析响应报文中的记录 ID，并将其设置为集合变量：

```js
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
    pm.collectionVariables.set("ID", pm.response.json().data.id);
});
```

在后续的删除请求中，可直接设置 URL 为 `{‎{base_url}}/records/{‎{ID}}`，方法设置为 `DELETE`。

在 test 中发送其他请求
-------------------

比如有一组关联操作，会发送很多请求，每个请求都配置到集合里，显得比较乱且不方便一同操作，创建个文件夹进行归类又不方便设置与前后请求之间的执行顺序。这时可以考虑在请求的 `Tests` 中，通过 JS 发送其他请求，如：

```js
const base_url = pm.collectionVariables.get("base_url");
const cookie = pm.collectionVariables.get("cookie");
const xsrfToken = pm.collectionVariables.get("xsrf_token");

const url = {
    url: base_url + '/records',
    method: 'PUT',
    header: {
        'Cookie': cookie,
        'X-XSRF-TOKEN': xsrfToken,
        'Content-Type': 'application/json;charset=UTF-8'
    },
    body: {
        mode: 'raw',
        raw: JSON.stringify({"description":"postman","updateBy":"postman"})
    }
};
pm.sendRequest(url, function (err, response) {
    pm.test("Successful delete app", function () {
        pm.expect(response.code).to.be.eql(200);
        pm.expect(response.json().message).to.be.eql('success');
    });
});
```

重试请求
-------

加入一个资源的删除操作，依赖与其关联的其他所有资源的释放，而这些关联资源的释放是一个耗时操作，在 `Tests` 中可以根据响应内容等待一段时间后重发请求，如：

```js
tests["Status code is 200"] = responseCode.code === 200;

const base_url = pm.collectionVariables.get("base_url");
const cookie = pm.collectionVariables.get("cookie");
const xsrfToken = pm.collectionVariables.get("xsrf_token");

let waitAndTryAgain = function (code) {
    if (code === 0) {
        pm.test("Delete namespace successfully", {});
    } else {
        setTimeout(() => {
            pm.test("Wait 3 seconds and try again", {});
            const url = {
                url: base_url + '/system/namespace/postman-test-ns',
                method: 'DELETE',
                header: {
                    'Cookie': cookie,
                    'X-XSRF-TOKEN': xsrfToken
                }
            };
            pm.sendRequest(url, function (err, response) {
                waitAndTryAgain(response.json().code);
            });
        }, 1000 * 3);
    }
};

waitAndTryAgain(JSON.parse(responseBody).code);
```

执行效果如图：

![重试](/contents/use-postman-to-do-system-acceptance-test/retry.png)

> 注意，这种场景下，想通过断言输出重试信息，需要使用 `pm.test(testName:String, specFunction:Function):Function` 形式，弃用的断言写法无法正确输出信息。

延迟请求
-------

每个请求间的时间间隔，可以通过上面提到的 Runner 中的 `Delay` 参数来设置。

当需要为单个请求增加延迟时间时，可以在 `Pre-request Script` 中通过如下脚本，实现类似 `sleep` 的效果：

```js
setTimeout(() => {}, 1000 * 5);
```

更多
----

更多测试脚本样例，可参考 [Test script examples](https://learning.postman.com/docs/writing-scripts/script-references/test-examples/) 。


Tips
====

文末附录几个使用 Postman 的小技巧。

发送文件及设置工作目录
------------------

使用 Postman 发送带附件的请求时，可按下图方式设置：

![发送文件](/contents/use-postman-to-do-system-acceptance-test/file.png)

选择文件后，多半会出现未设置工作目录的警告信息。

Postman 中，工作目录（`Working directory`）的含义是：当请求中包含文件时，文件的路径会以相对于工作目录的相对路径形式，记录到集合中。当需要在其他环境使用该集合时，只要该环境基于工作目录的相对路径中也存在这个文件，就可以保证文件被正确的找到。

工作目录可以在下图位置进行设置：

![工作目录](/contents/use-postman-to-do-system-acceptance-test/dir.png)

调试
---

编写测试用例时难免要调试。在 `Console` 中，可以看到发送出去的请求的相关信息，甚至是在 JS 脚本中通过 `console` 打印的信息（`info` 以上级别）。此外，还可以在使用 `Runner` 执行时，勾选 `Save responses` 参数，这样在测试报告中，就可以直接点击请求的名称，查看相关的请求和响应信息了。

![调试](/contents/use-postman-to-do-system-acceptance-test/debug.png)

> 注意：测试报告中，无法看到通过 JS 脚本发送的请求相关信息，只能在 `Console` 中根据请求地址查找具体请求。

命令行运行
--------

除通过 Postman 客户端执行外，还可以通过命令行运行。官方提供了一个命令行工具 [newman](https://github.com/postmanlabs/newman)，可参照如下方式安装及运行：

```bash
$ npm install -g newman
$ newman run 云平台可用性验证.postman_collection.json --folder 创建测试资源
```

> 注意：命令行方式运行时，预置的变量需要设定 `INITIAL VALUE`，因为 `CURRENT VALUE` 不会被持久化到 JSON 文件中。