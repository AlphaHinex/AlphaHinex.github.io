---
id: sonar-quality-gates
title: "Sonar Quality Gates"
description: "通过质量门禁为新增代码设定准入条件"
date: 2023.09.24 10:26
categories:
    - DevOps
tags: [DevOps, Sonar]
keywords: Sonar, SonarQube, quality, quality gate, CI, DevOps, pipeline
cover: /contents/sonar-quality-gates/failed.png
---

# Sonar Quality Gates

[SonarQube](https://www.sonarsource.com/products/sonarqube) 简称 Sonar，是一个能够帮助我们编写整洁、安全代码的平台。通过 [SonarScanner](https://docs.sonarsource.com/sonarqube/latest/analyzing-source-code/overview/) 对代码进行扫描，之后将扫描结果展现，如 https://next.sonarqube.com/sonarqube/projects ：

![sonarqube](/contents/sonar-quality-gates/sonarqube.png)

[Quality Gates](https://docs.sonarsource.com/sonarqube/latest/user-guide/quality-gates/) 可译为质量门禁，能够检查新增代码是否满足其中的规则要求，以判断新代码是否达到合并要求。Sonar 中有开箱即用的内置质量门禁规则，也可自定义：

![conditions](/contents/sonar-quality-gates/conditions.png)

在项目总览页中，可以看到质量门禁状态：

![passed](/contents/sonar-quality-gates/passed.png)

![failed](/contents/sonar-quality-gates/failed.png)

通过质量门禁，可以优先保证新增代码的基本质量水准，再逐步解决遗留代码的问题，以提升项目的整体代码质量。


# Quality Gate 状态集成至 DevOps 流程

质量门禁的状态，可以 [报告至合并请求](https://docs.sonarsource.com/sonarqube/10.2/devops-platform-integration/gitlab-integration/#reporting-your-quality-gate-status-in-gitlab)，以便在代码合并之前的审查阶段尽早发现质量问题。但类似的功能，都需要在 SonarQube [Developer 版及以上](https://www.sonarsource.com/products/sonarqube/downloads/) 才可使用：

![editions](/contents/sonar-quality-gates/editions.png)

## `sonar.qualitygate.wait`

Sonar 从 [8.1](https://github.com/SonarSource/sonarqube/blob/8.1.0.31237/sonar-scanner-engine/src/main/java/org/sonar/scanner/scan/ScanProperties.java#L44C33-L44C33) 开始，在 [分析参数](https://docs.sonarsource.com/sonarqube/latest/analyzing-source-code/analysis-parameters/) 中添加了 `sonar.qualitygate.wait`，用来阻塞分析步骤直至查询到（可设置超时）本次分析的质量门禁状态，并可 [根据状态结果使 DevOps 流水线失败](https://docs.sonarsource.com/sonarqube/latest/analyzing-source-code/ci-integration/overview/#quality-gate-fails)：

``` bash
$ mvn sonar:sonar -Dsonar.qualitygate.wait=true
...
[INFO] ------------- Check Quality Gate status
[INFO] Waiting for the analysis report to be processed (max 300s)
[INFO] ------------------------------------------------------------------------
[INFO] Reactor Summary:
[INFO]
[INFO] demo 1.0.0-SNAPSHOT .......................... FAILURE [ 14.169 s]
[INFO] demo-svc ..................................... SUCCESS [  0.000 s]
[INFO] demo-biz 1.0.0 ............................... SUCCESS [ 20.421 s]
[INFO] demo-premise 1.0.0 ........................... SUCCESS [  0.500 s]
[INFO] ------------------------------------------------------------------------
[INFO] BUILD FAILURE
[INFO] ------------------------------------------------------------------------
[INFO] Total time: 38.138 s
[INFO] Finished at: 2023-09-23T13:07:59+08:00
[INFO] ------------------------------------------------------------------------
[ERROR] Failed to execute goal org.sonarsource.scanner.maven:sonar-maven-plugin:3.10.0.2594:sonar (default-cli) on project demo: QUALITY GATE STATUS: FAILED - View details on http://sonarhost/dashboard?id=demo -> [Help 1]
[ERROR]
[ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
[ERROR] Re-run Maven using the -X switch to enable full debug logging.
[ERROR]
[ERROR] For more information about the errors and possible solutions, please read the following articles:
[ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/MojoExecutionException
```

然而如果 Sonar 版本较低，则无法直接使用此参数。此时可尝试通过 Sonar 的 Web API 手动请求获得质量门禁状态。

## Web API

[Web API](https://docs.sonarsource.com/sonarqube/latest/extension-guide/web-api/) 可使用 token 或账号进行认证（需注意不同版本 Sonar 的 Web API 认证方式可能略有差异）。之后可访问 https://next.sonarqube.com/sonarqube/web_api 中列出的 API 接口。

获得项目质量门禁状态的 [接口](https://next.sonarqube.com/sonarqube/web_api/api/qualitygates/project_status) 为：

```API
GET api/qualitygates/project_status
```

![参数列表](/contents/sonar-quality-gates/params.png)

响应结果：

```json
{
  "projectStatus": {
    "status": "ERROR",
    "ignoredConditions": false,
    "caycStatus": "non-compliant",
    "conditions": [
      {
        "status": "ERROR",
        "metricKey": "new_coverage",
        "comparator": "LT",
        "errorThreshold": "85",
        "actualValue": "82.50562381034781"
      },
      {
        "status": "ERROR",
        "metricKey": "new_blocker_violations",
        "comparator": "GT",
        "errorThreshold": "0",
        "actualValue": "14"
      },
      {
        "status": "ERROR",
        "metricKey": "new_critical_violations",
        "comparator": "GT",
        "errorThreshold": "0",
        "actualValue": "1"
      },
      {
        "status": "OK",
        "metricKey": "new_sqale_debt_ratio",
        "comparator": "GT",
        "errorThreshold": "5",
        "actualValue": "0.6562109862671661"
      },
      {
        "status": "OK",
        "metricKey": "reopened_issues",
        "comparator": "GT",
        "actualValue": "0"
      },
      {
        "status": "ERROR",
        "metricKey": "open_issues",
        "comparator": "GT",
        "actualValue": "17"
      },
      {
        "status": "OK",
        "metricKey": "skipped_tests",
        "comparator": "GT",
        "actualValue": "0"
      }
    ],
    "period": {
        "mode": "last_version",
        "date": "2000-04-27T00:45:23+0200",
        "parameter": "2015-12-07"
     }
  }
}
```

响应中包含每个条件的状态和整体状态。

利用 `curl`、`jq` 和退出码检查质量门禁状态：

```bash
#!/bin/bash

token=xxx

st=$(curl -u $token: http://sonar-host/api/qualitygates/project_status?projectKey=demo | jq -r .projectStatus.status)
echo $st

if [ "$st" = "OK" ]; then
    exit 0  # 返回退出码 0 表示成功
else
    exit 1  # 返回退出码 1 表示失败
fi
```