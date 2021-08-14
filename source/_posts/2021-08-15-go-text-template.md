---
id: go-text-template
title: "Go text tempate"
description: "铁打的格式，流水的内容"
date: 2021.08.15 10:34
categories:
    - Go
tags: [Go]
keywords: Go, template, action, function, pipeline, run, build
cover: /contents/covers/go-text-template.jpeg
---

`text/template` 是 Go 的标准库，提供数据驱动的文本模板生成功能。

Quick start
===========

先来快速感受一下，将下面代码保存为 `template.go`：

```go
package main

import (
	"os"
	"text/template"
)

func main() {
	text := `START
[Actions]
    {{/* abdef */}}
    {{- "action" }}
    {{- range . }}
    {{ . }}
    {{- end }}
[Text and spaces]
    math expr: {{ 23 }} < {{- 45 }}
[Arguments]
    {{ . }}
[Pipelines]
    {{ . | len | eq 2 | and 1 }}
[Variables]
    {{ $m := . }}
    {{- $m }}
[Functions]
    {{ index . "author" }} {{ $m.url }}
    {{ urlquery .url }}
[Associated templates]
    {{- define "A1" }}Content in associated template created by {{ . }}{{ end }}
    {{ template "A1" "hinex" }}
[Nested template definitions]
    {{- define "T1" }}ONE{{ end }}
    {{- define "T2" }}TWO{{ end }}
    {{- define "T3" }}{{ template "T1" }} {{ template "T2" }}{{ end }}
    {{ template "T3"}}
END`
	tpl, err := template.New("test").Parse(text)
	if err != nil { panic(err) }
	err = tpl.Execute(os.Stdout, map[string]string{
		"author": "AlphaHinex",
		"url": "https://alphahinex.github.io/2021/08/15/go-text-template/"})
	if err != nil { panic(err) }
}
```

运行得到如下输出结果：

```bash
$ go run template.go
START
[Actions]
    action
    AlphaHinex
    https://alphahinex.github.io/2021/08/15/go-text-template/
[Text and spaces]
    math expr: 23 <45
[Arguments]
    map[author:AlphaHinex url:https://alphahinex.github.io/2021/08/15/go-text-template/]
[Pipelines]
    true
[Variables]
    map[author:AlphaHinex url:https://alphahinex.github.io/2021/08/15/go-text-template/]
[Functions]
    AlphaHinex https://alphahinex.github.io/2021/08/15/go-text-template/
    https%3A%2F%2Falphahinex.github.io%2F2021%2F08%2F15%2Fgo-text-template%2F
[Associated templates]
    Content in associated template created by hinex
[Nested template definitions]
    ONE TWO
END
```

也可编译为可执行文件（不需要 Go 运行环境），如：

```bash
# 编译为可在当前环境运行的可执行文件
$ go build template.go
# 编译为可在其他环境运行的可执行文件
$ GOOS=windows GOARCH=amd64 go build template.go
```

> 可用的 GOOS 和 GOARCH 可参照 https://golang.google.cn/doc/install/source#environment 。


概念
===

[Actions][sec1]
---------------

模板，顾名思义，就是铁打的格式，流水的内容。在 Go 的 template 里，通过 `Actions` 来设定模板中变化的部分，使用双大括号来表示，如 `{{ "action" }}`。

Actions 中，通过对传入模板中的数据进行加工，将数据转换为最终需要的形式。

在 Go 的 template 中，通过 `.` 获得绑定的数据，称为 `dot`。通常情况下，`dot` 绑定的是传入模板的数据。但在上面 `range` 的例子中，`dot` 在 `range` 作用域范围内，被设定为了通过 range 获得的具体元素。

类似的，能够改变 `dot` 内容的 action，除了 `range`，还有 `template` 和 `with`。

Actions 中还支持条件判断，用以在不同数据状态下，输出不同的结果，支持三种条件判断语法：

```text
{{if pipeline}} T1 {{end}}
{{if pipeline}} T1 {{else}} T0 {{end}}
{{if pipeline}} T1 {{else if pipeline}} T0 {{end}}
```

[Text and spaces][sec2]
-----------------------

Actions 之外的内容，会原封不动的输出到最终的结果中；Actions 之中的内容，会输出动作执行结果。

但有些情况下可能会产生一些不必要的空格，比如模板内容本身的格式化。对比如下模板输出结果：

模板1：
```text
Comment in action
{{/* May contain newlines*/}}
END
```

结果1：
```text
Comment in action

END
```

模板2：
```text
Comment in action
{{/* May contain newlines*/}}END
```

结果2：
```text
Comment in action
END
```

出于模板文件本身可阅读性及可维护性的考虑，建议在模板中应该添加必要的空格及换行，但又不想影响最终输出的结果，此时可以通过 `-` 来移除不需要的空格。使用方式为：
1. `{‎{- `：`{‎{` 后紧跟一个 `-` 和一个空格 ` `，会移除 Actions 之前的所有空格，包括换行
2. ` -}}`：`}}` 前是一个空格 ` ` 和一个 `-`，会移除 Actions 之后的所有空格，包括换行

[Arguments][sec3]
-----------------

指参数，运算获得的值，如 `dot` 以及访问到的 `dot` 内部结构的值。

[Pipelines][sec4]
-----------------

与 Linux 中 pipeline 类似，用 `|` 来表示，可以将前一个命令的结果，作为最后一个参数，传递给后面的命令，如：

```text
{{ . | len | eq 2 | and 1 }}
```

意为 `1 && (2 == len(.))`。

[Variables][sec5]
-----------------

可在 action 中进行变量的定义，如：

```text
{{ $m := . }}
```

也可以在定义之后再赋值，如：

```text
{{ $m = . }}
```

[Functions][sec6]
-----------------

可利用内置的函数，在模板中操作数据，如 `print`、`len` 等。

除了内置的函数外，还可以引入三方的模板函数库，如 [sprig](https://masterminds.github.io/sprig/) 以完成更加复杂的模板操作。

[Associated templates][sec7]
----------------------------

每个模板创建时，都需要有个名字。每个模板可以和其他模板通过名称进行关联，即在一个模板中，通过名称，引入另一个模板中的内容，并可以通过 pipeline，为引入的模板绑定数据，如上面例子中的：

```text
{{ template "A1" "hinex" }}
```

> 例子中为了方便，将关联的模板也定义到了这个模板中。实际场景可能是将模板定义在多个模板文件中，通过 template 的 API 方法，将多个模板进行解析及关联。

[Nested tempate definitions][sec8]
----------------------------------

模板中除了可以引入外部模板外，还可以通过 `define` 和 `end` 进行内嵌模板的定义。

[sec1]:https://pkg.go.dev/text/template#hdr-Actions
[sec2]:https://pkg.go.dev/text/template#hdr-Text_and_spaces
[sec3]:https://pkg.go.dev/text/template#hdr-Arguments
[sec4]:https://pkg.go.dev/text/template#hdr-Pipelines
[sec5]:https://pkg.go.dev/text/template#hdr-Variables
[sec6]:https://pkg.go.dev/text/template#hdr-Functions
[sec7]:https://pkg.go.dev/text/template#hdr-Associated_templates
[sec8]:https://pkg.go.dev/text/template#hdr-Nested_template_definitions