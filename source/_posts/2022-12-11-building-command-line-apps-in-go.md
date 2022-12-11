---
id: building-command-line-apps-in-go
title: "用 Go 构建全平台命令行工具"
description: "无其他依赖的 write once, run anywhere"
date: 2022.12.11 10:26
categories:
    - Go
tags: [Go, Golang]
keywords: golang, cli, urfave/cli, exe, postman, mdnice, gitlab
cover: /contents/building-command-line-apps-in-go/cover.png
---

[Write once, run anywhere](https://en.wikipedia.org/wiki/Write_once,_run_anywhere) 是 Sun 1995 年为宣传 Java 语言的跨平台特性而提出的口号。

然而了解 Java 的人都知道，这个 run anywhere 是以目标环境存在 JVM 为前提的。当我们希望构建一个可以 run anywhere 的命令行工具时，Java 显然不是最好的选择。

Golang
======

作为一个更加简洁、现代的编程语言，[Golang](https://golang.google.cn/) 可以通过指定 `GOOS` 和 `GOARCH` 两个环境变量，将 Go 代码编译为目标环境的可执行文件（无需 Go 运行环境等其他任何依赖），真正做到 Write Once, (Build multi-times), Run Anywhere。

```bash
# 编译本地环境可执行文件
$ go build
# 编译 Windows 环境 64 位 x86 架构可执行文件
$ GOOS=windows GOARCH=amd64 go build
```

> 更多可用的 `GOOS` 和 `GOARCH` 组合可参照 https://golang.google.cn/doc/install/source#environment 。

在 Golang 的官网上，也有一个专门的页面 —— [Command-line Interfaces (CLIs)](https://golang.google.cn/solutions/clis) —— 介绍使用 Go 开发命令行工具的好处，并给出了一些流行的开源项目，以便开发者能够更快速的使用 Go 构建命令行应用：

* [spf13/cobra](https://github.com/spf13/cobra)
* [spf13/viper](https://github.com/spf13/viper)
* [urfave/cli](https://github.com/urfave/cli)
* [delve](https://github.com/go-delve/delve)
* [chzyer/readline](https://github.com/chzyer/readline)

接下来以 `urfave/cli` 为例，构建一些命令行应用。

urfave/cli
==========

按照 https://cli.urfave.org/v2/getting-started/ 中的例子，让我们创建一个 `boom.go` 文件

```go
package main

import (
    "fmt"
    "log"
    "os"

    "github.com/urfave/cli/v2"
)

func main() {
    app := &cli.App{
        Name:  "boom",
        Usage: "make an explosive entrance",
        Action: func(*cli.Context) error {
            fmt.Println("boom! I say!")
            return nil
        },
    }

    if err := app.Run(os.Args); err != nil {
        log.Fatal(err)
    }
}
```

因为需要将 `urfave/cli` v2 的包引入进来，所以我们需要 [使用 Go Modules](https://go.dev/blog/using-go-modules) 。在 `boom.go` 所在路径中，执行：

```bash
$ go mod init example.com/boom
```

之后按照 [安装文档](https://cli.urfave.org/#installation) ，添加 `urfave/cli` v2 模块：

```bash
$ go get github.com/urfave/cli/v2
```

此时即可编译 `boom.go` 获得您使用 `urfave/cli` 构建的第一个命令行应用了：

```bash
$ go build
$ ./boom
boom! I say!
$ ./boom --help
NAME:
   boom - make an explosive entrance

USAGE:
   boom [global options] command [command options] [arguments...]

COMMANDS:
   help, h  Shows a list of commands or help for one command

GLOBAL OPTIONS:
   --help, -h  show help (default: false)
```

更多用法可参考 [v2 Manual](https://cli.urfave.org/v2/getting-started/) 中的 Examples。

> 在执行 `go get github.com/urfave/cli/v2` 时如果遇到连接超时问题，可以按照 https://goproxy.cn/ 中的说明，使用七牛提供的 Go 模块代理。

Postman
=======

还不怎么会写 Go 代码？如果你想构建的命令行应用是一个调用三方 RESTful API 实现一些功能的工具（如下面的 `mdnice` 样例），可以先使用 [Postman](https://www.postman.com/) 进行接口的调用和调试，之后直接生成 go 代码：

![](/contents/building-command-line-apps-in-go/postman.png)

关于 Postman 的更多用法，可参考 [使用 Postman 进行系统可接受性测试](https://alphahinex.github.io/2022/05/22/use-postman-to-do-system-acceptance-test/) 。

Sample
======

提供几个样例，源码地址：https://github.com/AlphaHinex/go-toolkit

random-pick
-----------

https://github.com/AlphaHinex/go-toolkit/tree/main/random-pick

随机选择指定类型文件，复制或移动到指定路径。

```bash
$ ./random-pick -h
NAME:
   random-pick - Random pick files in some path

USAGE:
   random-pick [global options] command [command options] [arguments...]

COMMANDS:
   help, h  Shows a list of commands or help for one command

GLOBAL OPTIONS:
   -n value    Pick n files (default: 10)
   -t value    File type(s) to pick, * means all types, comma separated for multi values: 'jpg,png', case insensitive (default: "*")
   -i value    Path to pick files (default: ".")
   -o value    Output picked files (default: ".")
   -k          Keep picked files in path (default: false)
   --help, -h  show help (default: false)
```

从 `./foo` 路径选择 5 个 jpg 或 png 类型的文件，复制到 `./bar` 路径：

```bash
$ ./random-pick -i ./foo -n 5 -t jpg,png -o ./bar -k
./random-pick -i ./foo -n 5 -t jpg,png -o ./bar -k
Copy ./foo/21670642460.JPG to ./bar/01670679254.JPG
Copy ./foo/31670642460.JPG to ./bar/11670679254.JPG
Copy ./foo/51670642460.JPG to ./bar/21670679254.JPG
Copy ./foo/11670642460.JPG to ./bar/31670679254.JPG
Copy ./foo/71670642460.PNG to ./bar/41670679254.PNG
```

mdnice
------

https://github.com/AlphaHinex/go-toolkit/tree/main/mdnice

将指定路径下的所有图片文件，上传至 [mdnice](https://editor.mdnice.com/) 的图床，需要 mdnice 的 JWT token。图片在图床的链接以 markdown 格式输出到图片来源路径的 README.md 文件中，上传失败的也会将失败原因记录至 md 文件。

```bash
$ ./mdnice -h
NAME:
   mdnice - Upload pictures to mdnice

USAGE:
   mdnice [global options] command [command options] [arguments...]

COMMANDS:
   help, h  Shows a list of commands or help for one command

GLOBAL OPTIONS:
   -i value            Path to be uploaded (default: ".")
   --token value       Bearer token of mdnice
   --token-file value  Bearer token file of mdnice
   --help, -h          show help (default: false)
```

使用 token 文件中的 JWT Token，将 `./foo` 路径下的所有（图片）文件上传：

```bash
$ ./mdnice -i ./foo --token-file token
Failed to upload 01670642460.GIF
Upload 01670642460.JPG done
Upload 11670642460.JPG done
Upload 21670642460.JPG done
Upload 31670642460.JPG done
Upload 41670642460.JPG done
Upload 51670642460.JPG done
Upload 61670642460.JPG done
Failed to upload 71670642460.PNG
Upload 81670642460.JPG done
Failed to upload README.md
$ cat ./foo/README.md
![](https://files.mdnice.com/user/30377/89e8cb29-4f58-4afc-a9cd-37018de437e3.JPG)
![](https://files.mdnice.com/user/30377/263b7008-eb99-4a0a-b502-2b3b1ceb6e3c.JPG)
![](https://files.mdnice.com/user/30377/4df30bf5-b763-4c94-801b-a7f52573e5c1.JPG)
![](https://files.mdnice.com/user/30377/bf4099ce-b81e-4320-aed7-7501bf06a22f.JPG)
![](https://files.mdnice.com/user/30377/f6183597-1929-42c9-bfa8-962b9521b0c7.JPG)
![](https://files.mdnice.com/user/30377/6f204840-cedd-4d67-909f-ef373bdf5443.JPG)
![](https://files.mdnice.com/user/30377/d42fa98a-0f30-4a87-8a26-32add001aa8d.JPG)
![](https://files.mdnice.com/user/30377/1a5152b1-a665-461e-8324-b58e3209a13a.JPG)

---
Upload ./foo/01670642460.GIF failed: 50005:文件过大
Upload ./foo/71670642460.PNG failed: 50005:文件过大
Upload ./foo/README.md failed: 50005:文件类型错误，仅支持jpg、jpeg、png、gif、svg类型
```

gitlab
------

https://github.com/AlphaHinex/go-toolkit/tree/main/gitlab

调用 GitLab RESTful API，分析指定项目和分支在某时间范围内的 Commit 情况，对每个 commit 中修改的文件进行逐个分析，统计新增代码行数、减少代码行数，以及忽略空格和换行改动的新增代码行数、减少代码行数（相当于 `git diff -w`），将分析结果生成 csv 文件，并按提交人邮箱进行汇总排名，输出至 console，并可通过飞书机器人发送统计结果。支持过滤初始 Commit 及 Merge Request Commit。

主要使用了以下两个 API：

1. [/help/api/projects.md](https://docs.gitlab.com/ee/api/projects.html)
1. [/help/api/commits.md](https://docs.gitlab.com/ee/api/commits.html)

```bash
$ ./gitlab -h
NAME:
   gitlab - Use GitLab API to do some analysis works

USAGE:
   gitlab [global options] command [command options] [arguments...]

COMMANDS:
   help, h  Shows a list of commands or help for one command

GLOBAL OPTIONS:
   --url value, -u value            GitLab host url
   --access-token value, -t value   Access token to use GitLab API
   --project-id value, -p value     Project ID in GitLab
   --branch value, -b value         Branch of project
   --since value                    Date of since, from 00:00:00 (default: "2022-01-01")
   --until value                    Date of until, to 23:59:59 (default: "2022-12-31")
   --parallel value                 Number of commit parsers (default: 16)
   --lark value                     Lark webhook url
   --commit-parents commit-parents  Only count the commit has commit-parents number parent(s),
                                        -1 means counting all commits,
                                        0 means only counting the initial commit,
                                        2 means only counting merge request commit,
                                        1 means exclude initial commit and merge request commit (default: -1)
   --help, -h                       show help (default: false)
```

统计 https://gitlab.com/gnachman/iterm2 项目 2022 年 11 月代码提交情况：

```bash
$ ./gitlab -u https://gitlab.com/ -t XXXXXX -p 252461 -b master --commit-parents 1 --since 2022-11-01 --until 2022-11-30
2022/12/10 22:47:19 Start to analyse iterm2 ...
2022/12/10 22:47:22 Load all commits
2022/12/10 22:47:31 Generate 252461_iterm2_master_2022-11-01~2022-11-30.csv use 24.443924546s.

iterm2 项目 master  分支代码分析结果（2022-11-01~2022-11-30)

No. author                    effLines(ratio)	effAdds(ratio)	commits	files
 1. gnachman@gmail.com        2366(90.31%)	1538(90.26%)	23	64
 2. brewingcode@users.noreply.github.com 2(50.00%)	2(50.00%)	1	2

以上结果统计了除初始 Commit 和 Merge Request 外的所有 Commit（时间范围内）
* effLines（有效代码行数）= 有效增加代码行数 + 有效减少代码行数
* effLines ratio（有效代码率）= 有效代码行数 / 总代码行数 * 100%
* effAdds（有效增加行数）= 有效增加代码行数
* effAdds ratio（有效增加率）= 有效增加代码行数 / 总增加代码行数 * 100%
* commits：Commit 总数
* files：文件总数（不去重）
* 有效代码：忽略仅有空格或换行的代码改动，diff -w
```