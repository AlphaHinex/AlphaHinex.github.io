---
id: gitbook-export-fine-enough-pdf
title: "GitBook 本地使用排雷，及导出基本可用的 PDF 版本"
description: "总结了离线环境使用 GitBook 以及将 GitBook 编写的文档导出成 PDF 时可能会遇到的问题和解决办法"
date: 2022.09.18 10:34
categories:
    - Book
tags: [GitBook]
keywords: GitBook, PDF, graceful-fs, ebook-convert
cover: /contents/gitbook-export-fine-enough-pdf/cover.jpeg
---

## GitBook 简介

[GitBook](https://www.gitbook.com/) 是一个现代的文档平台，提供了基于 Markdown 等方式的在线协作编辑文档方式，并可以方便的通过浏览器阅读文档内容。

有大量的公司、开源项目等，都在使用，如 [GitBook 自己的文档](https://docs.gitbook.com/)、[Fluent Bit](https://docs.fluentbit.io/manual/) 等。

GitBook 团队曾经还提供过一个离线的命令行工具和 Node.js 类库 - [gitbook](https://github.com/GitbookIO/gitbook)，用来在本地离线环境使用 Markdown 或 AsciiDoc 构建一个电子书，遗憾的是目前这个项目已经被弃用了。

虽然 GitbookIO 的这个 `gitbook` 工具已经不再维护了，但其仍是目前通过 Markdown 编写可导出的电子书的比较好的工具，且简单易用。

本文针对使用 `gitbook` 工具编写、发布 HTML 版本和导出成 PDF 版本所遇到的一些问题进行总结，并给出解决方案，使我们可以利用 `gitbook` 获得一个还算够好的 PDF 版本电子书。


## 本地使用 gitbook

本地使用 GitBook 需要 Node.js 运行环境，可全局安装命令行工具：

```bash
$ npm install gitbook-cli -g
```

`gitbook-cli` 是一个安装和使用多个版本 `GitBook`（Node.js 类库）的工具，会自动安装所需要的 `GitBook` 版本。可通过如下命令查看 `CLI` 版本及自动安装 `GitBook` 最后发布版，一切顺利的话会看到：

```bash
$ gitbook --version
CLI version: 2.3.2
Installing GitBook 3.2.3
...
GitBook version: 3.2.3
```

> 如果不顺利，可以查看下面的 `问题1` ，及解决方案。

常用命令：

```bash
# 初始化一个模板
$ gitbook init
# 本地启动一个 HTTP 服务进行预览
$ gitbook serve
# 编译静态网站，可将生成的 _book 路径中内容发布到 HTTP 服务中
$ gitbook build
```

如果不想全局安装，也可以仅安装至当前路径，并按如下方式使用：

```bash
$ npm i gitbook-cli
$ node node_modules/gitbook-cli/bin/gitbook.js fetch 3.2.3
$ node node_modules/gitbook-cli/bin/gitbook.js --version
CLI version: 2.3.2
GitBook version: 3.2.3
```

### 问题1：gitbook-cli 报错

在使用 `gitbook-cli` 时，可能会遇到如下问题：

```bash
$ gitbook --version
CLI version: 2.3.2
Installing GitBook 3.2.3
/Users/alphahinex/.nvm/versions/node/v12.22.12/lib/node_modules/gitbook-cli/node_modules/npm/node_modules/graceful-fs/polyfills.js:287
      if (cb) cb.apply(this, arguments)
                 ^

TypeError: cb.apply is not a function
    at /Users/alphahinex/.nvm/versions/node/v12.22.12/lib/node_modules/gitbook-cli/node_modules/npm/node_modules/graceful-fs/polyfills.js:287:18
    at FSReqCallback.oncomplete (fs.js:169:5)
```

原因是依赖的 `graceful-fs` 版本有问题，可按照 [Gitbook build stopped to work in node 12.18.3 #110](https://github.com/GitbookIO/gitbook-cli/issues/110#issuecomment-863706455) 中提供的方式，修改 `gitbook-cli` 所依赖的 `graceful-fs` 版本解决。

全局安装的 `CLI` 安装在 npm 配置的全局安装路径，如 `~/.nvm/versions/node/v12.22.12/lib/node_modules/gitbook-cli`。

```bash
$ cd ~/.nvm/versions/node/v12.22.12/lib/node_modules/gitbook-cli
$ npm i graceful-fs@4.1.4 --save
$ cd ~/.nvm/versions/node/v12.22.12/lib/node_modules/gitbook-cli/node_modules/npm
$ npm i graceful-fs@4.1.4 --save
```

> 注意：有两处版本需要修改：
> 1. `gitbook-cli` 自身依赖的 `graceful-fs` 
> 1. `gitbook-cli` 依赖的 `npm` 中依赖的 `graceful-fs`

除上面方法外，也可以直接将报错位置代码注掉，或降低 gitbook-cli 版本解决此问题：

```bash
$ npm install -g gitbook-cli@2.2.0
$ gitbook fetch 3.2.3
```

### 问题2：如何解除对 README.md 文件的依赖

使用 `gitbook init` 生成模板工程后，会自动生成 `SUMMARY.md` 和 `README.md` 两个文件。`SUMMARY.md` 中内容为 GitBook 的目录，`README.md` 会被初始化为 `Introduction` 章节。这两个文件默认是必须存在的，即使在 `SUMMARY.md` 中去掉对 `README.md` 文件的依赖，使用 `gitbook serve` 等命令时也会提示找不到 `README.md` 文件。

可以按照官方文档中关于配置文件的说明，在项目根路径放置一个 `book.json` 文件，通过 [structure.*](https://github.com/GitbookIO/gitbook/blob/master/docs/config.md#structure) 参数调整默认文件，以解除对 `README.md` 文件的依赖。

|Variable|Description|
|:-------|:----------|
|structure.readme|Readme file name (defaults to README.md)|
|structure.summary|Summary file name (defaults to SUMMARY.md)|
|structure.glossary|Glossary file name (defaults to GLOSSARY.md)|
|structure.languages|Languages file name (defaults to LANGS.md)|

`book.json` 示例：

```json
{
  "structure": {
    "readme": "rdm.md"
  }
}
```

### 问题3：如何自动生成 SUMMARY.md 的内容

目录内容及层级较多时，可通过一些工具自动生成 `SUMMARY.md` 文件，如 [gitbook-summary](https://github.com/imfly/gitbook-summary)：

```bash
$ npm install -g gitbook-summary
$ book sm
```

### 问题4：如何添加插件

GitBook 可通过插件对功能进行扩展，如添加页面内导航、目录折叠等。

不过由于项目的弃用，如今已无法方便的搜索可用插件了。

可利用搜索引擎，搜索介绍 GitBook 插件的文章，实现曲线救国，如 [Gitbook常用插件合集](https://www.jianshu.com/p/09bf890ec8f6)、[Gitbook 插件](http://www.zhaowenyu.com/gitbook-doc/plugins/) 等。

设置插件时，同样是在 `book.json` 中配置，如：

```json
{
    "plugins": [
        "-lunr",
        "-search",
        "search-pro"
    ]
}
```

在添加插件后，需通过 `gitbook install` 命令将插件安装（下载）至本地。

> 注意：有些插件（如页面内导航等）会影响导出成 PDF 时生成的目录，建议在导出 PDF 文件时，尽量减少不必要的插件。

### 问题5：gitbook build 报缺少插件中的文件

在 CI/CD 环境执行 `gitbook build` 时，即使已通过 `gitbook install` 完成了插件的安装，也会有较大概率出现随机缺少插件中的某个文件的报错（报错信息如下），导致构建失败。

```text
Error: ENOENT: no such file or directory, stat '/opt/buildagent/work/173f165a668e1392/_book/gitbook/gitbook-plugin-code/plugin.css'
```

遇到这个问题，需要修改 `GitBook` 中的 `copyPluginAssets.js` 文件中的内容。

`GitBook` 被安装在 `~/.gitbook/versions/` 路径的版本号文件夹下，如：`~/.gitbook/versions/3.2.3` 。

`copyPluginAssets.js` 文件的路径则为 `~/.gitbook/versions/3.2.3/lib/output/website/copyPluginAssets.js`，需将此文件中的 `confirm: true` 替换为 `confirm: false`：

```bash
# linux
$ sed -i "s#confirm: true#confirm: false#g" copyPluginAssets.js
# macOS
$ sed -i '' 's/confirm: true/confirm false/g' copyPluginAssets.js
```


## GitBook 导出 PDF

之所以在 `gitbook` 项目被弃用了之后依然使用其编写文档，主要看重的是 GitBook 能够导出成电子书的能力。

GitBook 导出电子书，需要安装 [Calibre 应用](https://calibre-ebook.com/download) ，并使命令行中可以使用 `ebook-convert` 工具。

Mac 上将 `calibre.app` 移至应用文件夹后，还需参照 [官方文档](https://github.com/GitbookIO/gitbook/blob/master/docs/ebook.md#installing-ebook-convert) 或如下内容，创建一个软链接，以便可以在终端中直接使用 `ebook-convert`：

```bash
$ ln -s /Applications/calibre.app/Contents/MacOS/ebook-convert /usr/local/bin/ebook-convert
$ ebook-convert --version
ebook-convert (calibre 6.3.0)
Created by: Kovid Goyal <kovid@kovidgoyal.net>
```

Windows 上安装最新版 `Calibre` 后，可直接使用 `ebook-convert`，如果不行，可以在安装路径找到 `ebook-convert.exe`，并将其路径配置到环境变量的 `Path` 中。

`ebook-convert` 可用后，即可使用如下命令，将使用 GitBook 编写的文档，输出成 PDF 格式了：

```bash
$ gitbook pdf
```

一切看上去都很美，然而打开生成的 PDF 文件之后，会发现理想和现实还是有差距的。

以 [wl-awesome](https://github.com/weiliang-ms/wl-awesome) 仓库中的 GitBook 为例，直接按上述方式生成的 PDF 电子书，打开后会发现存在不少问题：

![](/contents/gitbook-export-fine-enough-pdf/before.png)

* 所有页的页眉都是第一个章节的名称
* 点击目录书签只能跳转到文档中的目录页
* 点击文档中的目录页则是打开浏览器跳转到一个无法访问的链接
* 页边距过大，显得每页内容过少
* 以电子书的角度来看，缺少封面
* 生成的 PDF 文件名为 `book.pdf`
* 字体过小
* ……

这些问题，使得生成的 PDF 文件距离一本基本令人满意的电子书还有一定的距离。接下来让我们看看如何解决或缓解这些问题。

### 问题1：页眉问题

在 GitBook 的 [文档](https://github.com/GitbookIO/gitbook/tree/master/docs) 中，并未找到设置页眉相关的参数。但从依赖关系我们可以知道生成 PDF 使用的是 `ebook-convert`。

通过查看 `gitbook` 的源码，在 `~/.gitbook/versions/3.2.3/lib/output/ebook/onFinish.js` 的 `runEbookConvert` 方法中，可以看到使用 `ebook-convert` 转换成 PDF 时所执行的命令：

```js
var cmd = [
    'ebook-convert',
    path.resolve(outputFolder, SUMMARY_FILE),
    path.resolve(outputFolder, 'index.' + format),
    command.optionsToShellArgs(options)
].join(' ');

return command.exec(cmd)
```

其中的 `options` 是传给 `ebook-convert` 的参数。完整的可用参数列表，可以在 `ebook-convert` 的 [使用手册](https://manual.calibre-ebook.com/generated/en/ebook-convert.html) 中查阅。

继续查看源码，在 [lib/output/ebook/getConvertOptions.js](https://github.com/GitbookIO/gitbook/blob/master/lib/output/ebook/getConvertOptions.js) 中可以找到生成 PDF 文件所使用的参数。

经过试验，去掉如下四行代码的内容，即可使页眉正常显示所属章节的标题：

```js
// '--chapter':                    'descendant-or-self::*[contains(concat(\' \', normalize-space(@class), \' \'), \' book-chapter \')]',
// '--level1-toc':                 'descendant-or-self::*[contains(concat(\' \', normalize-space(@class), \' \'), \' book-chapter-1 \')]',
// '--level2-toc':                 'descendant-or-self::*[contains(concat(\' \', normalize-space(@class), \' \'), \' book-chapter-2 \')]',
// '--level3-toc':                 'descendant-or-self::*[contains(concat(\' \', normalize-space(@class), \' \'), \' book-chapter-3 \')]',
```

### 问题2：目录书签跳转问题

在按照 `问题1` 的解决方式，去掉四个参数后，生成的 PDF 文件目录书签也发生了变化，从折叠的层级关系变成了平铺的，但点击书签跳转到对应页面的功能可以正常使用了，牺牲了一点美观性，换来了实用性，也还勉强可以接受。

### 问题3：目录跳转问题

点击 PDF 内目录页中链接，跳转到的地址（如：https://calibre-pdf-anchor.n/%2309Guan%20Bi%20Tu%20Xing%20Hua.html ）转义后可以发现，跳转地址是由 `https://calibre-pdf-anchor.n/` +  `#09Guan Bi Tu Xing Hua.html` 两部分组成的。其中第二部分 `#` 后的内容，正是我们在 `SUMMARY.md` 关联的 Markdown 文件名（转换为了 `html` 格式）。

而关联的 Markdown 文件名如果是英文的，则可以在 PDF 中正常跳转，如 `1.8网络` 下的 `03-wireshark` 章节。

故要解决目录跳转问题，在 `SUMMARY.md` 中关联的 Markdown 文件，文件名中不能有中文（路径中可以有中文）。

### 问题4：边距太大

关于 PDF 文件的边距，在 [PDF Options](https://github.com/GitbookIO/gitbook/blob/master/docs/config.md#pdf-options) 文档中有说明，即可以通过在 `book.json` 添加配置进行调整。

然而即使将边距都设置为 `0`，依然会感觉页边距有点大。

```json
"pdf": {
  "margin": {
    "left": 0,
    "right": 0,
    "top": 0,
    "bottom": 0
  }
}
```

此时可以继续修改 `getConvertOptions.js` 文件，在 `getConvertOptions` 方法最后返回的 `options` 对象使用的 `extend` 方法的第二个参数中，增加 `ebook-convert` 中所支持的 `--pdf-page-margin-*` 参数。

例如，将 `--pdf-page-margin-left` 和 `--pdf-page-margin-right` 默认的 `72px` 调整为 `50px`：

```js
return options = extend(options, {
    '--chapter-mark':           String(pdfOptions.chapterMark),
    '--page-breaks-before':     String(pdfOptions.pageBreaksBefore),
    '--margin-left':            String(pdfOptions.margin.left),
    '--margin-right':           String(pdfOptions.margin.right),
    '--margin-top':             String(pdfOptions.margin.top),
    '--margin-bottom':          String(pdfOptions.margin.bottom),
    '--pdf-default-font-size':  String(pdfOptions.fontSize),
    '--pdf-mono-font-size':     String(pdfOptions.fontSize),
    '--paper-size':             String(pdfOptions.paperSize),
    '--pdf-page-numbers':       Boolean(pdfOptions.pageNumbers),
    '--pdf-sans-family':        String(pdfOptions.fontFamily),
    '--pdf-header-template':    headerTpl,
    '--pdf-footer-template':    footerTpl,
    '--pdf-page-margin-left':   '50',
    '--pdf-page-margin-right':  '50',
});
```

### 问题5：如何添加封面

为电子书添加封面，只需按照 [Cover](https://github.com/GitbookIO/gitbook/blob/master/docs/ebook.md#cover) 中说明，在根路径放置一个符合要求的 `cover.jpg` 图片即可。

### 问题6：指定 PDF 文件名

在导出 PDF 命令中，可以指定生成 PDF 的文件名，如：

```bash
$ gitbook pdf . 文档集.pdf
```

### 问题7：如何调整字体大小

`book.json` 中可设定字体大小（默认为 `12`）：

```json
  "pdf": {
    "fontSize": 15
  }
```

### 问题8：目录（平铺）内容较多时，有不完整的情况

当按 `问题1` 的方式去掉了识别目录层级的 XPath 表达式后，目录书签不再按照层级的方式展现，而是平铺了出来。此时如果目录内容较多，会出现仅有部分目录显示在书签里的情况。

原因是 `ebook-convert` 的 [--max-toc-links](https://manual.calibre-ebook.com/generated/en/ebook-convert.html#cmdoption-ebook-convert-max-toc-links) 参数默认值是 `50`，意为最多只插入 50 个链接至目录书签中。

同样可以修改 `getConvertOptions.js` 文件，在 `options` 中加入

```js
'--max-toc-links':              '0'
```

以禁用最大数量的限制。

### 最终效果

![](/contents/gitbook-export-fine-enough-pdf/after.png)