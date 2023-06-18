---
id: fauxpilot
title: "GitHub Copilot 开源替代品 —— FauxPilot"
description: "可私有化部署，可使用多 GPU 加载大模型"
date: 2023.06.18 10:34
categories:
    - AI
tags: [AI, VS Code]
keywords: GitHub Copilot, Copilot, NVIDIA, nvidia-docker, NVIDIA Container Toolkit, FauxPilot, VS Code, CodeGen, Triton Inference Server, GPU
cover: /contents/fauxpilot/cover.png
---

[用 PaddleNLP 结合 CodeGen 实现离线 GitHub Copilot][paddlenlp] 介绍了使用 PaddleNLP + CodeGen 实现类似 GitHub Copilot 服务端的方式，客户端在 VSCode 中使用了 FauxPilot 插件。

FauxPilot 插件原本是对接 [FauxPilot](https://github.com/fauxpilot/fauxpilot) Server 的，通过 FauxPilot Server 也可以实现 GitHub Copilot 服务的功能，并支持多显卡加载 CodeGen 模型，可解决单卡显存不足又想加载大模型的问题。

> 例如 FauxPilot 提供的 codegen-16B-multi-gptj 模型需要 32G 显存，你有两张 24G 显存的显卡，可以使用每张显卡 16G 左右的显存，成功加载 16B 模型。

# 最终效果

还是先展示一下最终的效果：

<video autoplay loop muted src="/contents/fauxpilot/demo.mov" controls style width=100%></video>

# Prerequisite

FauxPilot 的环境需求可见 [Prerequisites](https://github.com/fauxpilot/fauxpilot#prerequisites)，包括：

- Docker
- `docker compose` >= [1.28](https://github.com/docker/compose/issues/8142#issuecomment-783115801)
- NVIDIA GPU 算力 >= 6.0 和足够模型使用的显存
- [nvidia-docker](https://github.com/NVIDIA/nvidia-docker)
- `curl` 和 `zstd` 命令行工具用来下载和解压模型文件

Nvidia container toolkit 的离线安装方式可参考 [用 PaddleNLP 结合 CodeGen 实现离线 GitHub Copilot][paddlenlp] 一文的前置条件中相关内容。

# FauxPilot Server 部署

如果是联网环境，可参照 [How to set-up a FauxPilot server](https://github.com/fauxpilot/fauxpilot/blob/main/documentation/server.md) 通过 `setup.sh` 下载模型并直接启动服务，或在完成配置后，使用 `launch.sh` 脚本启动服务。

> FasterTransformer backend 和 Python backend 中推荐选择 FasterTransformer backend。

服务启动时，会通过 Docker Compose，按照 [docker-compose.yaml](https://github.com/fauxpilot/fauxpilot/blob/main/docker-compose.yaml) 的配置，以及 [proxy.Dockerfile](https://github.com/fauxpilot/fauxpilot/blob/main/proxy.Dockerfile)、[triton.Dockerfile](https://github.com/fauxpilot/fauxpilot/blob/main/triton.Dockerfile) 构建两个镜像：

- `fauxpilot-main-copilot_proxy:latest`
- `fauxpilot-main-triton:latest`

故在离线环境部署时，只需将在线环境构建好的上面两个镜像导出：

```bash
$ docker save > fauxpilot-triton.tar fauxpilot-main-triton
$ docker save > fauxpilot-proxy.tar fauxpilot-main-copilot_proxy
```

再在离线环境导入：

```bash
$ docker load < fauxpilot-triton.tar
$ docker load < fauxpilot-proxy.tar
```

然后将下载好的模型文件目录、`docker-compose.yaml` 和执行 `setup.sh` 后生成的 `.env` 文件传入离线环境：

```bash
$ tree -a
├── .env
├── docker-compose.yaml
└── models
    └── codegen-16B-multi-2gpu
        └── fastertransformer
            ├── 1
            │   └── 2-gpu
            │       ├── config.ini
            │       ├── model.final_layernorm.bias.bin
            |       ├── ...
            │       └── model.wte.bin
            └── config.pbtxt
```

根据实际情况调整 `.env` 文件中的 `MODEL_DIR` 和 `HF_CACHE_DIR` 为离线环境路径，并将 `docker-compose.yaml` 中 `build` 部分改为直接使用镜像：

```yaml
version: '3.3'
services:
  triton:
    image: fauxpilot-main-triton:latest
    command: bash -c "CUDA_VISIBLE_DEVICES=${GPUS} mpirun -n 1 --allow-run-as-root /opt/tritonserver/bin/tritonserver --model-repository=/model"
    shm_size: '2gb'
    volumes:
      - ${MODEL_DIR}:/model
      - ${HF_CACHE_DIR}:/root/.cache/huggingface
    ports:
      - "8000:8000"
      - "${TRITON_PORT}:8001"
      - "8002:8002"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
  copilot_proxy:
    # For dockerhub version
    image: fauxpilot-main-copilot_proxy:latest
    command: uvicorn app:app --host 0.0.0.0 --port 5000
    env_file:
      # Automatically created via ./setup.sh
      - .env
    ports:
      - "${API_EXTERNAL_PORT}:5000"
```

之后直接通过 Docker Compose 启动即可：

```bash
$ docker compose up
```

# 客户端

FauxPilot Server 启动成功后，可按 [用 PaddleNLP 结合 CodeGen 实现离线 GitHub Copilot][paddlenlp] 中 `Fauxpilot VSCode Plugin` 部分配置 VSCode 插件使用，也可直接通过 RESTful API 试用：

```bash
$ curl -s -H "Accept: application/json" -H "Content-type: application/json" -X POST -d '{"prompt":"def hello","max_tokens":100,"temperature":0.1,"stop":["\n\n"]}' http://localhost:5000/v1/engines/codegen/completions
{"id": "cmpl-R6DqtyLigNJVJzt4F617KoM3EjB9M", "model": "codegen", "object": "text_completion", "created": 1686646299, "choices": [{"text": "(self):\n        return \"Hello World\"", "index": 0, "finish_reason": "stop", "logprobs": null}], "usage": {"completion_tokens": 11, "prompt_tokens": 2, "total_tokens": 13}}
```

接口结构参照 https://platform.openai.com/docs/api-reference/completions/create 。

请求体结构：

```json
{
  "model": "text-davinci-003",
  "prompt": "Say this is a test",
  "max_tokens": 7,
  "temperature": 0,
  "top_p": 1,
  "n": 1,
  "stream": false,
  "logprobs": null,
  "stop": "\n"
}
```

响应体结构：

```json
{
  "id": "cmpl-uqkvlQyYK7bGYrRHQ0eXlWi7",
  "object": "text_completion",
  "created": 1589478378,
  "model": "text-davinci-003",
  "choices": [
    {
      "text": "\n\nThis is indeed a test",
      "index": 0,
      "logprobs": null,
      "finish_reason": "length"
    }
  ],
  "usage": {
    "prompt_tokens": 5,
    "completion_tokens": 7,
    "total_tokens": 12
  }
}
```

[paddlenlp]:https://alphahinex.github.io/2023/06/11/paddlenlp-codegen-copilot/