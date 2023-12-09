---
id: sonar-exporter
title: "SonarQube 项目总览状态导出工具"
description: "SonarQube 上项目越来越多，筛选困难时，可以试试将项目信息导出再筛选"
date: 2023.12.10 10:26
categories:
    - DevOps
tags: [DevOps, Sonar]
keywords: Sonar, SonarQube, export
cover: /contents/covers/sonar-exporter.png
---

随着 [SonarQube](https://www.sonarsource.com/products/sonarqube) 上的项目越来越多，我们希望能够对这些项目按照一定的指标进行筛选，比如：

- `Size` 为 `L` 且 `Duplications` 在 `5% - 10%` 之间的项目
- `Coverage` 在 `60%` 以上的项目

Sonar 界面中提供的筛选功能，只能按照指定的范围进行筛选，并且每个指标除了第一个和最后一个范围，中间的范围都是包含下面范围的。例如 `Coverage` 指标提供的范围是：

- ≥ 80%
- 70% - 80%
- 50% - 70%
- 30% - 50%
- < 30%

选择 `50% - 70%` 这个范围时，是包含下面 `30% - 50%` 和 `< 30%` 两个范围的，即只能过滤覆盖率在 70% 以下的项目，无法更加精细的进行过滤。

Sonar 中也没找到能够将项目总览信息导出的方式，所以就有了这样一个小工具：

sonar-exp
=========

- 源码：https://github.com/AlphaHinex/go-toolkit/tree/main/sonar-exp
- Release 页面：https://github.com/AlphaHinex/go-toolkit/releases/tag/v2.3.0
- 预编译二进制包括：

```list
sonar-exp_darwin_amd64
sonar-exp_darwin_arm64
sonar-exp_linux_amd64
sonar-exp_linux_arm64
sonar-exp_win_amd64.exe
```

导出工具使用了 Sonar [Web API](http://localhost:9000/web_api?deprecated=true&internal=true) 中的两个内部接口：

1. [GET api/components/search_projects
INTERNAL
SINCE 6.2](http://localhost:9000/web_api/api/components/search_projects?internal=true)
1. [GET api/measures/search
INTERNAL
SINCE 6.2](http://localhost:9000/web_api/api/measures/search?internal=true)

并支持按项目名称或 key 进行过滤，项目数据已 csv 格式输出，可以重定向至文件，如：

```bash
$ ./sonar-exp -host http://localhost:9000 -t xxxxx -q ds-3 > ds3.csv
$ cat ds3.csv
Project,Bugs,Vulnerabilities,Hotspots Reviewed,Code Smells,Coverage,Duplications,Lines,NCLOC Language Distribution,Size,Duplications*Lines,Bug/Lines*1k%,Code Smells/Lines*1k%
ds-305-master,10,4,0.0,3396,0.0,20.0,60080,java=59046;xml=1034,M,12016.000000,0.166445,56.524635
ds-317-dev,78,11,0.0,4256,0.0,35.7,98510,java=97850;xml=660,M,35168.070312,0.791798,43.203735
```

| Project       | Bugs | Vulnerabilities | Hotspots Reviewed | Code Smells | Coverage | Duplications | Lines | NCLOC Language Distribution | Size | Duplications*Lines | Bug/Lines*1k% | Code Smells/Lines*1k% |
|:--------------|:-----|:----------------|:------------------|:------------|:---------|:-------------|:------|:----------------------------|:-----|:-------------------|:--------------|:----------------------|
| ds-305-master | 10   | 4               | 0.0               | 3396        | 0.0      | 20.0         | 60080 | java=59046;xml=1034         | M    | 12016.000000       | 0.166445      | 56.524635             |
| ds-317-dev    | 78   | 11              | 0.0               | 4256        | 0.0      | 35.7         | 98510 | java=97850;xml=660          | M    | 35168.070312       | 0.791798      | 43.203735             |

![screenshot](/contents/covers/sonar-exporter.png)

拿到 csv 格式数据后，即可自由进行过滤条件设置了。