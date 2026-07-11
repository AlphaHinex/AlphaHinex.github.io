---
id: user-free-models-with-copilot
title: "一些免费AI模型，及在 VS Code 中使用"
description: ""
date: 2026.07.12 10:26
categories:
    - AI
tags: [AI, AI Agent]
keywords: AI, OpenSpec, Superpowers, SDD, TDD, Vibe Coding, AI Agent
cover: /contents/user-free-models-with-copilot/add-models.png
---

## VS Code 中添加 AI 模型

Visual Studio Code（简称 VS Code）官方文档 [Bring your own language model key](https://code.visualstudio.com/docs/agent-customization/language-models#_bring-your-own-language-model-key) 中介绍了在 VS Code 中添加更多语言模型的方法，包括 [内置提供商（Built-in providers）](https://code.visualstudio.com/docs/agent-customization/language-models#_add-a-model-from-a-built-in-provider)、[扩展（Extensions）](https://code.visualstudio.com/docs/agent-customization/language-models#_add-a-model-provider-extension)、[自定义端点（Custom endpoint）](https://code.visualstudio.com/docs/agent-customization/language-models#_add-a-custom-endpoint-model) 三种方式。

自定义端点支持三种 API 类型：[Chat Completions](https://developers.openai.com/api/reference/chat-completions/overview)、[Responses](https://developers.openai.com/api/reference/responses/overview) 和 [Messages](https://platform.claude.com/docs/en/api/messages)。

添加模型步骤如下：

1. 切换模型处选择其他模型后的配置图标：
  ![models](https://alphahinex.github.io/contents/user-free-models-with-copilot/other-models.png)
2. 选择添加模型，然后选择自定义端点（Custom Endpoint）：
  ![add-models](https://alphahinex.github.io/contents/user-free-models-with-copilot/add-models.png)
3. 为模型输入组名，这是在模型选择器和语言模型编辑器中显示的分组标签。组名后续可修改。
4. 输入端点的 API 密钥，秘钥会以密文形式存储。
5. 选择 API 类型：
  ![api-type](https://alphahinex.github.io/contents/user-free-models-with-copilot/api-type.png)
6. 之后 VS Code 会打开一个 `chatLanguageModels.json` 文件，调用模型具体的模型名称（`id`）和完整 `url` 需在此文件中填写。有关配置属性的详细信息，请参阅 [Model configuration reference](https://code.visualstudio.com/docs/agent-customization/language-models#_model-configuration-reference)。

下面是调用 Anthropic Messages API 的配置示例：

```json
[
  {
    "name": "Anthropic",
    "vendor": "customendpoint",
    "apiKey": "YOUR_API_KEY",
    "apiType": "messages",
    "models": [
      {
        "id": "claude-sonnet-4-6",
        "name": "Claude Sonnet 4.6",
        "url": "https://api.anthropic.com/v1/messages",
        "toolCalling": true,
        "vision": true,
        "maxInputTokens": 200000,
        "maxOutputTokens": 64000
      }
    ]
  }
]
```

下面是调用 OpenAI Chat Completions API 的配置示例：

```json
[
  {
    "name": "LocalHost",
    "vendor": "customendpoint",
    "apiKey": "${input:chat.lm.secret.xxxxxx}",
    "apiType": "chat-completions",
    "models": [
      {
        "id": "model1",
        "name": "Local Model 1",
        "url": "http://localhost:8000/v1/chat/completions",
        "toolCalling": true,
        "vision": true,
        "maxInputTokens": 128000,
        "maxOutputTokens": 16000
      },
      {
        "id": "model2",
        "name": "Local Model 2",
        "url": "http://localhost:8000/v1/chat/completions",
        "toolCalling": true,
        "vision": true,
        "maxInputTokens": 128000,
        "maxOutputTokens": 16000
      }
    ]
  }
]
```

### Debug

在 VS Code GitHub Copilot Chat 中使用自定义模型可能会遇到请求失败的报错，如：

```error
Sorry, your request failed. Please try again.
Client Request Id: 95903bd3-e7d5-435f-a842-45bcf985940b
Reason: token expired or invalid: 403: Error: token expired or invalid: 403 at qG._provideLanguageModelResponse (/Applications/Visual Studio Code.app/Contents/Resources/app/extensions/copilot/dist/extension.js:1690:14362) at process.processTicksAndRejections (node:internal/process/task_queues:104:5) at async qG.provideLanguageModelResponse (/Applications/Visual Studio Code.app/Contents/Resources/app/extensions/copilot/dist/extension.js:1690:15327)
```

[Meta: Sorry, your request failed. Please try again. #253136](https://github.com/microsoft/vscode/issues/253136) 给出了一些解决方案，如重试请求、更换模型、检查日志（`CTRL + SHIFT + U` 打开输出面板，选择 `GitHub Copilot Chat` 查看日志）等。

![output](https://alphahinex.github.io/contents/user-free-models-with-copilot/output.png)

## Free Models

<style>
  .model-table {
    border-collapse: separate;
    border-spacing: 0;
    width: 100%;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    font-size: 0.9rem;
    background: #ffffff;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0, 20, 40, 0.08);
  }
  .model-table thead th {
    background: #0b1e33;
    color: rgba(255,255,255,0.9);
    font-weight: 600;
    font-size: 0.8rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    padding: 14px 18px;
    text-align: left;
    border-bottom: 2px solid #1e3a5f;
  }
  .model-table thead th:first-child { border-top-left-radius: 16px; }
  .model-table thead th:last-child { border-top-right-radius: 16px; }
  .model-table tbody td {
    padding: 12px 18px;
    border-bottom: 1px solid #e6edf4;
    vertical-align: middle;
    color: #1a2a3a;
  }
  .model-table tbody tr:last-child td:first-child { border-bottom-left-radius: 16px; }
  .model-table tbody tr:last-child td:last-child { border-bottom-right-radius: 16px; }
  .model-table tbody tr:hover {
    background: #f0f6fe;
    transition: background 0.15s;
  }
  .model-table tbody tr:nth-child(even) {
    background: #f8faff;
  }
  .model-table tbody tr:nth-child(even):hover {
    background: #eaf1fb;
  }
  .model-table a {
    color: #0a5c9e;
    text-decoration: none;
    font-weight: 500;
    border-bottom: 1px solid transparent;
    transition: border-color 0.15s;
  }
  .model-table a:hover {
    border-bottom-color: #0a5c9e;
    color: #003d73;
  }
  .model-table td:nth-child(3),
  .model-table td:nth-child(4) {
    font-family: "SF Mono", "Fira Code", "Cascadia Code", monospace;
    font-size: 0.8rem;
    word-break: break-word;
  }
  .model-table td:last-child a {
    display: inline-block;
    background: #eef3fa;
    padding: 3px 14px;
    border-radius: 40px;
    font-size: 0.75rem;
    font-weight: 600;
    color: #0b2b4a;
    border: 1px solid #d3dce8;
    transition: all 0.15s;
    border-bottom: none;
  }
  .model-table td:last-child a:hover {
    background: #d5e1f0;
    border-color: #8aa9c9;
    transform: translateY(-1px);
  }
  .model-table td:last-child:not(:has(a)) {
    color: #8a9caa;
  }
  .model-table td[rowspan] {
    background: #f0f5fc;
    font-weight: 600;
    color: #0b2e4a;
    border-right: 1px solid #e0e8f2;
  }
  .model-table td[rowspan] a {
    border-bottom: none;
    font-weight: 600;
  }
</style>

<table class="model-table">
  <thead>
    <tr>
      <th>模型</th>
      <th>平台</th>
      <th>URL</th>
      <th>模型 ID</th>
      <th>API Key</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><a href="https://www.modelscope.cn/models/deepseek-ai/DeepSeek-V4-Flash">DeepSeek-V4-Flash</a></td>
      <td rowspan="3"><a href="https://opencode.ai/docs/zh-cn/zen/">OpenCode Zen</a></td>
      <td rowspan="3">https://opencode.ai/zen/v1/chat/completions</td>
      <td>deepseek-v4-flash-free</td>
      <td rowspan="3">-</td>
    </tr>
    <tr><td><a href="https://www.modelscope.cn/models/XiaomiMiMo/MiMo-V2.5">MiMo-V2.5</a></td><td>mimo-v2.5-free</td></tr>
    <tr><td><a href="https://www.modelscope.cn/models/Tencent-Hunyuan/Hy3">Hy3</a></td><td>hy3-free</td></tr>
    <tr>
      <td><a href="https://build.nvidia.com/deepseek-ai/deepseek-v4-flash/modelcard">DeepSeek-V4-Flash</a></td>
      <td rowspan="8"><a href="https://build.nvidia.com/models?filters=nimType%3Anim_type_preview">Nvidia</a></td>
      <td rowspan="8">https://integrate.api.nvidia.com/v1/chat/completions</td>
      <td>deepseek-ai/deepseek-v4-flash</td>
      <td rowspan="8"><a href="https://build.nvidia.com/settings/api-keys">API Keys</a></td>
    </tr>
    <tr><td><a href="https://build.nvidia.com/deepseek-ai/deepseek-v4-pro/modelcard">DeepSeek-V4-Pro</a></td><td>deepseek-ai/deepseek-v4-pro</td></tr>
    <tr><td><a href="https://build.nvidia.com/z-ai/glm-5.2/modelcard">GLM-5.2</a></td><td>z-ai/glm-5.2</td></tr>
    <tr><td><a href="https://build.nvidia.com/qwen/qwen3.5-122b-a10b/modelcard">Qwen3.5-122B-A10B</a></td><td>qwen/qwen3.5-122b-a10b</td></tr>
    <tr><td><a href="https://build.nvidia.com/qwen/qwen3.5-397b-a17b/modelcard">Qwen3.5-397B-A17B</a></td><td>qwen/qwen3.5-397b-a17b</td></tr>
    <tr><td><a href="https://build.nvidia.com/qwen/qwen3-next-80b-a3b-instruct/modelcard">Qwen3-Next-80B-A3B-Instruct</a></td><td>qwen/qwen3-next-80b-a3b-instruct</td></tr>
    <tr><td><a href="https://build.nvidia.com/minimaxai/minimax-m3/modelcard">MiniMax-M3</a></td><td>minimaxai/minimax-m3</td></tr>
    <tr><td><a href="https://build.nvidia.com/stepfun-ai/step-3.7-flash/modelcard">Step 3.7 Flash</a></td><td>stepfun-ai/step-3.7-flash</td></tr>
    <tr>
      <td><a href="https://docs.mistral.ai/models/model-cards/mistral-medium-3-5-26-04">Mistral Medium 3.5</a></td>
      <td><a href="https://docs.mistral.ai/getting-started/models">Mistral</a></td>
      <td>https://api.mistral.ai/v1/chat/completions</td>
      <td>mistral-medium-3-5</td>
      <td><a href="https://admin.mistral.ai/organization/api-keys">API Keys</a></td>
    </tr>
  </tbody>
</table>