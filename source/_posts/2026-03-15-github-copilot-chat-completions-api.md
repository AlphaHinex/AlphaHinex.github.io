---
id: github-copilot-chat-completions-api
title: "【转】如何调用Github Copilot订阅的Chat Completions API"
description: "或许你会需要免费的4o"
date: 2026.03.15 10:34
categories:
    - AI
tags: [AI, GitHub Copilot, LLM, OpenAI]
keywords: GitHub Copilot, OpenAI, Chat Completions API, Device Flow, access_token, Copilot token
cover: /contents/covers/github-copilot-chat-completions-api.png
---

- 原文地址：https://skae.top/p/copilot-api/
- 原文作者：[^薄荷布丁^](https://skae.top/)

---

这篇文章教你怎么自己编写代码，把你的Github Copilot订阅的API接出来用。

大致流程是：

1. 发起 Device Flow 请求，获取`device_code`和`user_code`（`XXXX-XXXX`）。
2. 在浏览器访问 https://github.com/login/device，输入`user_code`。
3. 轮询换取`access_token`（`ghu_`开头的 token）。
4. 用`access_token`获取短效`Copilot token`。
5. 用`Copilot token`调用 Chat Completions API。

# 1. 发起 Device Flow 请求

```bash
curl -X POST https://github.com/login/device/code \
  -H "Accept: application/json" \
  -d "client_id=<CLIENT_ID>&scope=read:user"
```

返回：

```json
{
  "device_code": "...",
  "user_code": "XXXX-XXXX",
  "verification_uri": "https://github.com/login/device",
  "expires_in": 900,
  "interval": 5
}
```

> client_id 可以是自己注册的 GitHub OAuth App 的 ID，或者也可以直接用已知的 Copilot 客户端 ID（见下）。
> 
> | 应用 | client_id |
> | --- | --- |
> | VS Code Copilot | Iv1.b507a08c87ecfe98 |
> | GitHub CLI | 178c6fc778ccc68e1d6a |

# 2. 打开浏览器

访问 `https://github.com/login/device`，输入上一步得到的`user_code`，完成登录。

# 3. 轮询换取 access_token

```bash
curl -X POST https://github.com/login/oauth/access_token \
  -H "Accept: application/json" \
  -d "client_id=<CLIENT_ID>&device_code=<DEVICE_CODE>&grant_type=urn:ietf:params:oauth:grant-type:device_code"
```

返回：

```json
{
  "access_token": "gh_xxx",
  "token_type": "bearer",
  "scope": "read:user"
  //（以及一些其它字段，这里不列出）
}
```

# 4. 获取 Copilot token

```bash
curl https://api.github.com/copilot_internal/v2/token \
  -H "Authorization: token ghu_xxx" \
  -H "Editor-Version: vscode/1.85.0" \
  -H "Editor-Plugin-Version: copilot/1.155.0" \
  -H "User-Agent: GitHubCopilotChat/0.12.0"
```

返回：

```json
{
  "agent_mode_auto_approval": true,
  "annotations_enabled": true,
  "azure_only": false,
  "blackbird_clientside_indexing": false,
  "chat_enabled": true,
  "chat_jetbrains_enabled": true,
  "code_quote_enabled": true,
  "code_review_enabled": true,
  "codesearch": true,
  "copilotignore_enabled": false,
  "endpoints": {
    "api": "https://api.business.githubcopilot.com",
    "origin-tracker": "https://origin-tracker.business.githubcopilot.com",
    "proxy": "https://proxy.business.githubcopilot.com",
    "telemetry": "https://telemetry.business.githubcopilot.com"
  },
  "expires_at": 1773238125,
  "individual": false,
  "limited_user_quotas": null,
  "limited_user_reset_date": null,
  "organization_list": [
    "xxx"
  ],
  "prompt_8k": true,
  "public_suggestions": "disabled",
  "refresh_in": 1500,
  "sku": "copilot_for_business_seat_quota",
  "snippy_load_test_enabled": false,
  "telemetry": "disabled",
  "token": "tid=xx;ol=xx;exp=1773238125;sku=copilot_for_business_seat_quota;proxy-ep=proxy.business.githubcopilot.com;st=dotcom;ssc=1;chat=1;cit=1;malfil=1;editor_preview_features=1;agent_mode=1;agent_mode_auto_approval=1;mcp=1;ccr=1;8kp=1;ip=44.243.00.00;asn=AS16509:xxx",
  "tracking_id": "xxx",
  "vsc_electron_fetcher_v2": false,
  "xcode": true,
  "xcode_chat": false
}
```

此处只需保存`token`字段的值即可

> 另外注意到（虽然没什么好注意的）：
> 
> - 个人Pro版，学生包，企业版等copilot在sku字段会不同
> - endpoints字段有API的地址，稍后会用到，但是其亦可以从proxy-ep解析出来
> - token在半小时后过期

# 5. 调用 Chat Completions API

```bash
curl https://api.business.githubcopilot.com/chat/completions \
  -H "Authorization: Bearer <copilot_token>" \
  -H "Content-Type: application/json" \
  -H "Copilot-Integration-Id: vscode-chat" \
  -H "Editor-Version: vscode/1.85.0" \
  -H "Editor-Plugin-Version: copilot/1.155.0" \
  -H "User-Agent: GitHubCopilotChat/0.12.0" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "hello"}]
  }'
```

此处的`copilot_token`即上一步得到的`token`字段的值。

注意api地址根据不同订阅有两种：

- `https://api.business.githubcopilot.com/chat/completions`（企业版）
- `https://api.individual.githubcopilot.com/chat/completions`（个人版）

可以通过上一步返回的`endpoints.api`字段或者`proxy-ep`字段解析得到。
