---
id: short-free-llm-api
title: "一些短期免费调用 DeepSeek-V3-0324 等模型 API 的方法"
description: "可供临时、验证等场景使用"
date: 2025.05.11 10:26
categories:
    - AI
tags: [AI, LLM]
keywords: DeepSeek, DeepSeek-V3, DeepSeek-V3-0324, API, curl, RESTful, free
cover: /contents/short-free-llm-api/github.png
---

有哪些可以短期免费调用 DeepSeek-V3-0324 等模型 API 的方法？

# HuggingFace

## 获取调用方式

https://huggingface.co/deepseek-ai/DeepSeek-V3-0324?inference_api=true&inference_provider=sambanova&language=sh

## API Key

https://huggingface.co/settings/tokens

## 调用示例

```bash
curl https://router.huggingface.co/sambanova/v1/chat/completions \
    -H 'Authorization: Bearer hf_xxxxxxxxxxxxxxxxxxxxxxxx' \
    -H 'Content-Type: application/json' \
    -d '{
        "messages": [
            {
                "role": "user",
                "content": "What is the capital of France?"
            }
        ],
        "model": "DeepSeek-V3-0324",
        "stream": false
    }'
```

```json
{"choices":[{"finish_reason":"stop","index":0,"logprobs":null,"message":{"content":"The capital of France is **Paris**. It is known for its iconic landmarks such as the Eiffel Tower, the Louvre Museum, and the Arc de Triomphe.  \n\nWould you like information on anything else related to Paris or France? 😊","role":"assistant"}}],"created":1746852567.742961,"id":"003de5ed-2a5e-4cc8-a1dc-a83f2339d994","model":"DeepSeek-V3-0324","object":"chat.completion","system_fingerprint":"fastcoe","usage":{"completion_tokens":51,"completion_tokens_after_first_per_sec":203.1970451845694,"completion_tokens_after_first_per_sec_first_ten":204.03983207094663,"completion_tokens_per_sec":135.12995588730448,"end_time":1746852567.7429223,"is_last_response":true,"prompt_tokens":10,"start_time":1746852567.3655078,"stop_reason":"stop","time_to_first_token":0.1313478946685791,"total_latency":0.3774144649505615,"total_tokens":61,"total_tokens_per_sec":161.6260256691289}}
```

## 限额

每月 `$0.1` 免费额度，上面示例调用大概消耗 `$0.01`。

---

# GitHub

## 获取调用方式

https://github.com/marketplace/models/azureml-deepseek/DeepSeek-V3-0324

![github](https://alphahinex.github.io/contents/short-free-llm-api/github.png)

## API Key

https://github.com/settings/tokens

## 调用示例

```bash
curl -X POST "https://models.github.ai/inference/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $GITHUB_TOKEN" \
    -d '{
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "What is the capital of France?"
            }
        ],
        "temperature": 1.0,
        "top_p": 1.0,
        "max_tokens": 1000,
        "model": "deepseek/DeepSeek-V3-0324"
    }'
```

```json
{"choices":[{"finish_reason":"stop","index":0,"message":{"content":"The capital of France is **Paris**. It is known for its iconic landmarks such as the Eiffel Tower, the Louvre Museum, and Notre-Dame Cathedral. Let me know if you'd like more details!","role":"assistant","tool_calls":null}}],"created":1746858750,"id":"a16d9594455d49b2b6f30590ed7451d0","model":"DeepSeek-V3-0324","object":"chat.completion","usage":{"completion_tokens":44,"prompt_tokens":16,"prompt_tokens_details":null,"total_tokens":60}}
```

## 限额

https://docs.github.com/en/github-models/prototyping-with-ai-models#rate-limits

每分钟允许请求 10 次，每天 50 次。

---

# Gitee

## 获取调用方式

https://ai.gitee.com/serverless-api?model=DeepSeek-V3&tab=info

## API Key

点击 `添加令牌` 获得：

![gitee](https://alphahinex.github.io/contents/short-free-llm-api/gitee.png)

## 调用示例

```bash
curl https://ai.gitee.com/v1/chat/completions \
	-X POST \
	-H "Authorization: Bearer XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" \
	-H "Content-Type: application/json" \
	-H "X-Failover-Enabled: true" \
	-d '{"model":"DeepSeek-V3","stream":false,"max_tokens":1024,"temperature":0.6,"top_p":0.8,"top_k":20,"frequency_penalty":1.1,"messages":[{"role":"system","content":"You are a helpful and harmless assistant. You should think step-by-step."},{"role":"user","content":"Can you please let us know more details about your "}]}'
```

```json
{"id":"chatcmpl-d9bf82216e91467793a8653cd30ca265","object":"chat.completion","created":1746859390,"model":"DeepSeek-V3","choices":[{"index":0,"message":{"role":"assistant","reasoning_content":null,"content":"Certainly! Could you clarify what specific details you'd like to know? For example, are you asking about:  \n\n1. **My Capabilities** – What I can help with (e.g., answering questions, generating text, assisting with coding, etc.).  \n2. **How I Work** – My underlying technology (e.g., AI model, training data, limitations).  \n3. **Usage Guidelines** – How to interact with me effectively or any policies around my use.  \n4. **Something Else?**  \n\nLet me know so I can provide the most relevant information!","tool_calls":[]},"logprobs":null,"finish_reason":"stop","stop_reason":null}],"usage":{"prompt_tokens":29,"total_tokens":148,"completion_tokens":119,"prompt_tokens_details":null},"prompt_logprobs":null}
```

## 限额

每日免费调用 100 次。

---

# 硅基流动

## 获取调用方式

https://cloud.siliconflow.cn/models

https://docs.siliconflow.cn/cn/api-reference/chat-completions/chat-completions?playground=open#llm

## API Key

https://cloud.siliconflow.cn/account/ak

## 调用示例

```bash
curl --request POST \
  --url https://api.siliconflow.cn/v1/chat/completions \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
  "model": "deepseek-ai/DeepSeek-V3",
  "stream": false,
  "max_tokens": 512,
  "enable_thinking": true,
  "thinking_budget": 4096,
  "min_p": 0.05,
  "temperature": 0.7,
  "top_p": 0.7,
  "top_k": 50,
  "frequency_penalty": 0.5,
  "n": 1,
  "stop": [],
  "messages": [
    {
      "role": "user",
      "content": "你是谁"
    }
  ]
}'
```

```json
{"id":"0196b8f8b9334d6d0f9f6367b4d86cf6","object":"chat.completion","created":1746860030,"model":"deepseek-ai/DeepSeek-V3","choices":[{"index":0,"message":{"role":"assistant","content":"我是DeepSeek Chat，由深度求索公司创造的智能AI助手！✨ 我可以帮你解答问题、提供建议、陪你聊天，甚至帮你处理各种文本和文件。如果有任何问题或需要帮助，尽管问我吧！😊"},"finish_reason":"stop"}],"usage":{"prompt_tokens":4,"completion_tokens":50,"total_tokens":54},"system_fingerprint":""}
```

## 限额

https://cloud.siliconflow.cn/expensebill

注册赠送 `14` 元，上面示例调用大概消耗 `0.0005` 元。每成功邀请一位新用户通过手机号码注册，可获得 `14` 元奖励。

---

# 七牛云

## 获取调用方式

https://portal.qiniu.com/ai-inference/model

## API Key

https://portal.qiniu.com/ai-inference/api-key

## 调用示例

```bash
curl https://api.qnaigc.com/v1/chat/completions \
  --request POST \
  --header 'Authorization: Bearer <API_KEY>' \
  --header 'Content-Type: application/json' \
  --data '{
  "stream": false,
  "model": "deepseek-v3-0324",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    },
    {
      "role": "user",
      "content": "Hello!"
    }
  ]
}'
```

```json
{"id":"chatcmpl-d2e38cb15db906e53b0f689673e9d7e7","object":"chat.completion","created":1746860956,"model":"deepseek-v3-0324","choices":[{"index":0,"message":{"role":"assistant","content":"Hello! 😊 How can I assist you today?","content_any":null},"finish_reason":"stop"}],"usage":{"prompt_tokens":11,"completion_tokens":11,"total_tokens":22}}
```

## 限额

https://portal.qiniu.com/ai-inference/usage

新用户 100 万免费 Token。

---

# DeepSeek 官方

## 获取调用方式

https://api-docs.deepseek.com/zh-cn/#%E8%B0%83%E7%94%A8%E5%AF%B9%E8%AF%9D-api

## API Key

https://platform.deepseek.com/api_keys

## 调用示例

```bash
curl https://api.deepseek.com/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <DeepSeek API Key>" \
  -d '{
        "model": "deepseek-chat",
        "messages": [
          {"role": "system", "content": "You are a helpful assistant."},
          {"role": "user", "content": "Hello!"}
        ],
        "stream": false
      }'
```

## 限额

https://api-docs.deepseek.com/zh-cn/quick_start/pricing

已无赠送的免费额度，按量付费。

---

# FOFA

## 获取调用方式

https://fofa.info

搜索 `port="11434" && status_code="200"`，搜索结果添加 `/v1/models` 获得 Ollama 服务可用模型列表

## 调用示例

```bash
curl --request POST \
  --url http://xxx.xxx.xxx.xxx:11434/v1/chat/completions \
  --data '{
    "model": "deepseek-r1:32b",
    "messages": [
    {
        "role": "user",
        "content": "What is the capital of France?"
    }
],
    "stream": false,
    "temperature": 0
}'
```

```json
{
  "id": "chatcmpl-311",
  "object": "chat.completion",
  "created": 1746862661,
  "model": "deepseek-r1:32b",
  "system_fingerprint": "fp_ollama",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "<think>\nOkay, so I need to figure out what the capital of France is. Hmm, I think it's Paris, but let me make sure. I remember learning in school that Paris is a major city in France and it's known for landmarks like the Eiffel Tower and the Louvre Museum. But wait, could there be another city that might also be considered? Maybe Lyon or Marseille? No, those are big cities too, but they're not capitals. The capital should be where the government is located, right? So Paris has the presidential palace, the Élysée Palace, and other important government buildings. Also, when I think of France's history, Paris was always at the center, like during the French Revolution and other significant events. Plus, in movies and books, Paris is often portrayed as the heart of France. Yeah, I'm pretty confident now that Paris is indeed the capital.\n</think>\n\nThe capital of France is Paris. It is the political, cultural, and economic heart of the country, home to government institutions such as the Élysée Palace and renowned landmarks like the Eiffel Tower and the Louvre Museum."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 234,
    "total_tokens": 244
  }
}
```
