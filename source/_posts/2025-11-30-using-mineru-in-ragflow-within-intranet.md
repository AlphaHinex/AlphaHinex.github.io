---
id: using-mineru-in-ragflow-within-intranet
title: "内网环境在 RAGFlow 中使用 MinerU"
description: "CPU 环境默认使用 MinerU 的 pipeline backend"
date: 2025.11.30 10:34
categories:
    - AI
tags: [RAG]
keywords: RAGFlow, MinerU, mineru-api, mineru-models-download, intranet, offline, python, uv, modelscope
cover: /contents/using-mineru-in-ragflow-within-intranet/cover.png
---

本文可作为 [使用教程：如何在 RAGFlow 中使用 MinerU](https://opendatalab.github.io/MinerU/zh/usage/plugin/RagFlow/) 的补充，介绍如何在内网环境下配置 MinerU 解析器以供 RAGFlow 使用。

# 前提假设

1. 已通过 docker 的形式在内网环境部署 RagFlow
1. RAGFlow 版本 >= `v0.21.1`
1. 有内网环境 pip 源

# 安装 MinerU

## 更新 .env 文件

在 [.env](https://github.com/infiniflow/ragflow/blob/main/docker/.env) 文件中添加如下内容：

```.env
MINERU_EXECUTABLE=/ragflow/uv_tools/.venv/bin/mineru
MINERU_MODEL_SOURCE=local
```

其中 `MINERU_MODEL_SOURCE=local` 表示 MinerU 使用 [本地模型](https://opendatalab.github.io/MinerU/zh/usage/model_source/#1)。

> 注意需保持 `USER_MINERU=false`，若设为 true，启动容器时会自动执行 MinerU 的安装，在内网环境不适用。

## 创建 mineru.json

根据 [MinerU 配置模板](https://gcore.jsdelivr.net/gh/opendatalab/MinerU@master/mineru.template.json) 或下面内容，创建 `mineru.json` 配置文件，放在 `volume` 路径下供后面 `docker-compose.yml` 中使用：

```json
{
    "bucket_info":{
        "bucket-name-1":["ak", "sk", "endpoint"],
        "bucket-name-2":["ak", "sk", "endpoint"]
    },
    "latex-delimiter-config": {
        "display": {
            "left": "$$",
            "right": "$$"
        },
        "inline": {
            "left": "$",
            "right": "$"
        }
    },
    "llm-aided-config": {
        "title_aided": {
            "api_key": "your_api_key",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "model": "qwen3-next-80b-a3b-instruct",
            "enable_thinking": false,
            "enable": false
        }
    },
    "models-dir": {
        "pipeline": "",
        "vlm": ""
    },
    "config_version": "1.3.1"
}
```

## 更新 docker-compose.yml 文件

更新 [docker-compose.yml](https://github.com/infiniflow/ragflow/blob/main/docker/docker-compose.yml) 文件，为 `ragflow-cpu` 服务挂载本地路径，以免重建容器时需重新安装：

```diff
diff --git a/docker/docker-compose.yml b/docker/docker-compose.yml
index ce9823a..8416cce 100644
--- a/docker/docker-compose.yml
+++ b/docker/docker-compose.yml
@@ -42,6 +42,9 @@ services:
       - ../history_data_agent:/ragflow/history_data_agent
       - ./service_conf.yaml.template:/ragflow/conf/service_conf.yaml.template
       - ./entrypoint.sh:/ragflow/entrypoint.sh
+      - ./volume/mineru.json:/root/mineru.json
+      - ./volume/.cache/modelscope:/root/.cache/modelscope
+      - ./volume/.venv:/ragflow/uv_tools/.venv
     env_file: .env
     networks:
       - ragflow
```

## 重建 ragflow-cpu 容器

在 [ragflow/docker](https://github.com/infiniflow/ragflow/tree/main/docker) 路径下执行：

```bash
$ docker compose down ragflow-cpu
$ docker compose up -d ragflow-cpu
```

## 安装 MinerU

通过 `docker exec -ti docker-ragflow-cpu-1 bash` 进入容器执行安装：

```bash
$ pwd
/ragflow
$ cd uv_tools
$ uv venv .venv
$ source .venv/bin/activate
# 创建配置文件，使用内网 pip 源
$ cat > /ragflow/uv_tools/pyproject.toml << EOF
[[tool.uv.index]]
name = "nexus"
url = "http://192.168.1.16:8080/pypi/web/simple"
EOF
$ uv pip install -U "mineru[core]"
...
$ uv pip list | grep mineru
mineru                   2.6.4
mineru-vl-utils          0.1.16
```

## 下载模型文件

MinerU 使用的模型文件可提前下载至 `ragflow/docker/volume/.cache/modelscope/hub/models/OpenDataLab` 路径下。

例如 pipeline 模型可从 https://www.modelscope.cn/OpenDataLab/PDF-Extract-Kit-1.0 下载，放到 `ragflow/docker/volume/.cache/modelscope/hub/models/OpenDataLab/PDF-Extract-Kit-1___0` 目录下：

> vlm 模型可从 https://www.modelscope.cn/models/OpenDataLab/MinerU2.5-2509-1.2B 下载。

```bash
$ tree -L 3
.
├── PDF-Extract-Kit-1___0
│   └── models
│       ├── Layout
│       ├── MFD
│       ├── MFR
│       ├── OCR
│       ├── OriCls
│       ├── ReadingOrder
│       ├── TabCls
│       └── TabRec
└── PDF-Extract-Kit-1.0 -> /root/.cache/modelscope/hub/models/OpenDataLab/PDF-Extract-Kit-1___0

10 directories, 1 file
```

如果内网有 [ModelScope](https://www.modelscope.cn/) 的镜像地址，也可通过修改 [modelscope](https://github.com/modelscope/modelscope) SDK 的方式从内网地址下载模型。

修改 [/ragflow/uv_tools/.venv/lib/python3.10/site-packages/modelscope/hub/constants.py](https://github.com/modelscope/modelscope/blob/master/modelscope/hub/constants.py#L6) 文件中的 `MODELSCOPE_URL_SCHEME = 'http://'` 和 `DEFAULT_MODELSCOPE_DOMAIN = 'www.modelscope.cn'` 为内网地址，例如：

```bash
$ cat /ragflow/uv_tools/.venv/lib/python3.10/site-packages/modelscope/hub/constants.py |grep -B 1 "DEFAULT_MODELSCOPE_DOMAIN ="
MODELSCOPE_URL_SCHEME = 'http://'
DEFAULT_MODELSCOPE_DOMAIN = '192.168.1.16:8093'
```

之后通过 `mineru-models-download` 命令下载模型（以下载 pipeline 模型为例）：

```bash
# 临时关闭本地模式，以能够下载模型
$ unset MINERU_MODEL_SOURCE
$ mineru-models-download -s modelscope -m pipeline
# 下载后恢复本地模式
$ export MINERU_MODEL_SOURCE=local
```

模型下载后会自动更新 `/root/mineru.json` 文件中的 `models-dir` 路径，手动下载模型后，也可根据实际路径参照下面内容进行修改：

```bash
$ cat ~/mineru.json
{
    "bucket_info": {
        "bucket-name-1": [
            "ak",
            "sk",
            "endpoint"
        ],
        "bucket-name-2": [
            "ak",
            "sk",
            "endpoint"
        ]
    },
    "latex-delimiter-config": {
        "display": {
            "left": "$$",
            "right": "$$"
        },
        "inline": {
            "left": "$",
            "right": "$"
        }
    },
    "llm-aided-config": {
        "title_aided": {
            "api_key": "your_api_key",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "model": "qwen3-next-80b-a3b-instruct",
            "enable_thinking": false,
            "enable": false
        }
    },
    "models-dir": {
        "pipeline": "/root/.cache/modelscope/hub/models/OpenDataLab/PDF-Extract-Kit-1___0",
        "vlm": "/root/.cache/modelscope/hub/models/OpenDataLab/MinerU2___5-2509-1___2B"
    },
    "config_version": "1.3.1"
}
```

## 验证功能

完成安装后通过命令行验证 MinerU 功能：

```bash
$ mineru -p test.pdf -o ./
```

## 发布 MinerU API 服务

```bash
$ mineru-api --host 0.0.0.0 --port 9382
```

之后可通过宿主机 IP 和端口 `9382` 访问 MinerU API：

![API](https://alphahinex.github.io/contents/using-mineru-in-ragflow-within-intranet/api.png)

# 在 RAGFlow 中使用

RAGFlow 知识库配置中，选择 MinerU 作为 PDF 解析器后，上传文档执行解析任务，可在容器中看到 MinerU 进程在运行：

```bash
$ ps -ef|grep mineru|grep -v grep
root      1863    25 99 22:04 ?        00:00:39 /ragflow/uv_tools/.venv/bin/python3 /ragflow/uv_tools/.venv/bin/mineru -p /tmp/mineru_bin_pdf_vqf00tlw/20251126-090158.pdf -o /tmp/mineru_pdf_k3y3cwp7 -m auto -b pipeline
```

执行效果：

![RAGFlow](https://alphahinex.github.io/contents/using-mineru-in-ragflow-within-intranet/cover.png)
