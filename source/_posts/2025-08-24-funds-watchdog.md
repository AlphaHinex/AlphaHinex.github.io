---
id: funds-watchdog
title: "基金实时估值监控命令行工具"
description: "可配合系统计划任务定时执行"
date: 2025.08.24 10:26
categories:
    - Go
tags: [Go, Golang, Dingtalk]
keywords: go-toolkit, funds, watchdog, cli, crontab, lark, dingtalk, console, monitoring, realtime
cover: /contents/covers/funds-watchdog.jpeg
---

[watchdog](https://github.com/AlphaHinex/go-toolkit/tree/main/watchdog) 是一个监控基金实时估值的命令行工具，可配合系统计划任务定时执行。

功能
----

- 内置监控时间点，每 15 分钟查询一次基金实时估值（14:46 后每两分钟一次），计划任务可配置为每分钟执行一次
- 自动过滤估值小于 0 的基金，每小时展示一次所有监控基金估值情况
- 按估值涨幅降序排序
- 对波动幅度超过阈值的基金给出历史净值信息
- 监控结果信息支持控制台输出和飞书、钉钉机器人通知
- 每日净值更新后自动输出结果或发送通知

用法
----

```bash
./watchdog -c test.yaml [--verbose] [--watch-now]
```

```bash
$ crontab -l
* * * * * /path/to/watchdog -c /path/to/test.yaml >> /path/to/test.log 2>&1
```

配置文件样例：

```yaml
funds:
  008099: # 基金代码
    cost: 1.6078 # 基金成本价
  000083: 
    cost: 5.1727

token:
  lark: xxxxxx # 飞书机器人 Webhook token，可选
  dingtalk: xxxxxx # 钉钉机器人 Webhook token，可选
```

输出内容样例：

```text
2025-08-22 21:48:03
上证指数：3825.76 54.66 🔺1.45%
沪深300：4378.00 89.93 🔺2.10%
深证成指：12166.06 246.30 🔺2.07%
创业板指：2682.55 87.08 🔺3.36%

000083|汇添富消费行业混合
成本：5.1727
估值：5.1458 🔺0.70% -0.52% 15:00
净值：5.1480 🔺0.74% -0.48% 2025-08-22

008099|广发价值领先混合A
成本：1.6078
估值：1.5244 ▼ -1.01% -5.19% 15:00
净值：1.5222 ▼ -1.16% -5.32% 2025-08-22
```

接口参考
------

- https://github.com/kouchao/TiantianFundApi
- https://github.com/x2rr/funds/

下载地址
------

- [watchdog_darwin_amd64](https://github.com/AlphaHinex/go-toolkit/releases/download/v2.6.0/watchdog_darwin_amd64)
- [watchdog_darwin_arm64](https://github.com/AlphaHinex/go-toolkit/releases/download/v2.6.0/watchdog_darwin_arm64)
- [watchdog_linux_amd64](https://github.com/AlphaHinex/go-toolkit/releases/download/v2.6.0/watchdog_linux_amd64)
- [watchdog_linux_arm64](https://github.com/AlphaHinex/go-toolkit/releases/download/v2.6.0/watchdog_linux_arm64)
- [watchdog_win_amd64.exe](https://github.com/AlphaHinex/go-toolkit/releases/download/v2.6.0/watchdog_win_amd64.exe)
