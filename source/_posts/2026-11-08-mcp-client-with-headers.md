---
id: mcp-client-with-headers
title: "MCP 透传请求头配置"
description: "访问真实业务 API"
date: 2026.11.08 10:26
categories:
    - AI
tags: [AI, AI Agent, VS Code, DeepSeek]
keywords: VS Code, MCP, dsh, Nacos, Higress, DeepSeek, Harness, AI, API, DeepSeek Harness, MCP Server, swagger2openapi
cover: /contents/mcp-client-with-headers/clear.png
---

# API => MCP Server

API 转 MCP Server 过程可参考：[Harness 低成本调用存量 API](https://alphahinex.github.io/2026/11/01/api-to-mcp/) 。

假设 API 访问权限需通过请求头传递：

```JSON
curl -i -X POST 'http://host:port/api/idx' \ 
  -H 'Content-Type: application/json' \ 
  -b 'XSRF-TOKEN=xxxxx;SESSION=xxxxx' \ 
  -H 'X-XSRF-TOKEN: xxxxx' \ 
  -d '{"idxName":"MCP测试指标","idxDesc":""}' 
```

Nacos v3.2.2 中，[不支持](https://github.com/alibaba/nacos/issues/15494) 在新版控制台配置 [argsPosition 参数](https://nacos.io/docs/latest/manual/user/ai/mcp-template/#%E5%8F%82%E6%95%B0%E4%BD%8D%E7%BD%AE%E4%BF%A1%E6%81%AFargsposition)，可选择升级到 v3.3.0，但实测不为每个工具配置这个参数也能透传请求头。

**即，只需在 Harness 中配置 MCP Server 时，添加请求头即可，Nacos 和 Higress 中无需额外配置。**

## swagger2openapi 

可使用 [swagger2openapi](https://github.com/Mermade/oas-kit/blob/main/packages/swagger2openapi/README.md) 工具，将 Swagger 2.0 JSON 文档转换为 OpenAPI 3.0 格式：

```Bash
# Install(node 12.x)
$ npm install -g swagger2openapi
# Convert
$ swagger2openapi api-docs.json -o openapi.json
```

如遇 `S2OError: Could not resolve reference #/definitions/xxx` 报错，可添加 `--warnOnly` 参数。

如遇 `S2OError: (Patchable) parameter.type is mandatory for non-body parameters` 报错，可添加 `--patch` 参数。

```Bash
swagger2openapi --warnOnly --patch api-docs.json -o openapi.json
```

得到的 `openapi.json` 在 Nacos 中导入时可能会报错：

```error
Tool `pageUsingGET_9` has invalid JSON parameters:
        - Value is not accepted. Valid values: "array", "boolean", "integer", "null", "number", "object", "string".
```

原因是转换后的 JSON 中，对于对象类型的参数，`type` 填写的是 `ref`，需要调整成 `object`：

```JSON
"queryConditions": {
  "description": "查询条件",
  "type": "ref"
}
```

=>

```JSON
"queryConditions": {
  "description": "查询条件",
  "type": "object"
}
```

另外，如果 `openapi.json` 中包含的接口数量过多，可能会导致在 Nacos 中导入后保存时报 `413 Content Too Large` 错误，进而无法保存 MCP Server。可选择要使用的接口精简工具数量之后再导入 MCP Server 中。

# Harness 中配置 MCP

## VS Code

[Add MCP servers in VS Code](https://code.visualstudio.com/docs/agent-customization/mcp-servers) 提到 MCP 的配置文件可以放置在不同位置，以作用于不同的范围。以放在 `./.vscode/mcp.json` 为例：

```JSON
{
    "servers": {
        "xxx/idx-mcp": {
            "url": "http://127.0.0.1:8082/mcp/idx-mcp",
            "type": "http",
            "headers": {
                "Cookie": "XSRF-TOKEN=${input:xsrfToken};SESSION=${input:idxSession}",
                "X-XSRF-TOKEN": "${input:xsrfToken}"
            }
        }
    },
    "inputs": [
        {
            "type": "promptString",
            "id": "xsrfToken",
            "description": "idx-mcp 的 xsrfToken 值",
            "password": true
        },
        {
            "type": "promptString",
            "id": "idxSession",
            "description": "idx-mcp 的 SESSION 值",
            "password": true
        }
    ]
}
```

直接用 VS Code 打开 `mcp.json` 文件，点击 `Start` 启动 MCP 服务后会弹出输入框，要求输入 `inputs` 中定义的参数：

![start](https://alphahinex.github.io/contents/mcp-client-with-headers/start.png)

![fill](https://alphahinex.github.io/contents/mcp-client-with-headers/fill.png)

过期之后可以在密文上点击浮动按钮清理后重新输入：

![clear](https://alphahinex.github.io/contents/mcp-client-with-headers/clear.png)

## DeepSeek Harness

`~/.dsh/profiles/web/cordis.patch.yml`：

```YAML
- insert:
    - id: streamable-http-mcp-test
      name: '@deepseek-ai/dsh-mcp-client'
      config:
        serverName: test
        transport: streamable-http
        url: http://127.0.0.1:8082/mcp/idx-mcp
        headers:
          Cookie: "XSRF-TOKEN=xxxxx;SESSION=xxxxx"
          X-XSRF-TOKEN: "xxxxx"
```

过期之后可直接修改配置文件中密文内容，无需重启 dsh，稍后即可生效。
