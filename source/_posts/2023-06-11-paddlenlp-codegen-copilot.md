---
id: paddlenlp-codegen-copilot
title: "用 PaddleNLP 结合 CodeGen 实现离线 GitHub Copilot"
description: "私有化代码辅助生成"
date: 2023.06.11 10:26
categories:
    - AI
tags: [AI, PaddleNLP]
keywords: PaddlePaddle, PaddleNLP, NVIDIA, Salesforce CodeGen, GPU, offline, GitHub Copilot
cover: /contents/paddlenlp-codegen-copilot/cover.png
---

[代码生成：写代码的AI助理](https://github.com/PaddlePaddle/PaddleNLP/tree/develop/examples/code_generation/codegen) 中给出了用 PaddleNLP 结合 CodeGen 实现代码 AI 助理的例子。

文档内容比较简略，实操下来可能会遇到不少问题。本文以离线环境部署为前提，给出一个实际案例。

# 效果展示

先上最终效果：

<video autoplay loop muted src="/contents/paddlenlp-codegen-copilot/demo.mov" controls style width=100%></video>

# Prerequisite

为避免各种组件版本的兼容性问题，本文使用 Docker 方式部署，并需装好显卡驱动等。可按下述方式检查所需组件状态。

## 显卡驱动

```bash
$ nvidia-smi
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 515.43.04    Driver Version: 515.43.04    CUDA Version: 11.7     |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|                               |                      |               MIG M. |
|===============================+======================+======================|
|   0  Tesla P40           Off  | 00000000:3B:00.0 Off |                    0 |
| N/A   24C    P0    49W / 250W |      0MiB / 23040MiB |      0%      Default |
|                               |                      |                  N/A |
+-------------------------------+----------------------+----------------------+
|   1  Tesla P40           Off  | 00000000:D8:00.0 Off |                    0 |
| N/A   26C    P0    48W / 250W |      0MiB / 23040MiB |      1%      Default |
|                               |                      |                  N/A |
+-------------------------------+----------------------+----------------------+

+-----------------------------------------------------------------------------+
| Processes:                                                                  |
|  GPU   GI   CI        PID   Type   Process name                  GPU Memory |
|        ID   ID                                                   Usage      |
|=============================================================================|
|  No running processes found                                                 |
+-----------------------------------------------------------------------------+
```

## Docker

```bash
$ docker version
Client: Docker Engine - Community
 Version:           23.0.4
 API version:       1.42
 Go version:        go1.19.8
 Git commit:        f480fb1
 Built:             Fri Apr 14 10:36:38 2023
 OS/Arch:           linux/amd64
 Context:           default

Server: Docker Engine - Community
 Engine:
  Version:          23.0.4
  API version:      1.42 (minimum version 1.12)
  Go version:       go1.19.8
  Git commit:       cbce331
  Built:            Fri Apr 14 10:34:14 2023
  OS/Arch:          linux/amd64
  Experimental:     false
 containerd:
  Version:          1.6.20
  GitCommit:        2806fc1057397dbaeefbea0e4e17bddfbd388f38
 runc:
  Version:          1.1.5
  GitCommit:        v1.1.5-0-gf19387a
 docker-init:
  Version:          0.19.0
  GitCommit:        de40ad0
```

## Nvidia container toolkit

要在容器环境中使用 GPU，还需安装 [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-docker)，
NVIDIA Container Toolkit [需要满足如下安装前置条件](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#platform-requirements)：

1. GNU/Linux x86_64 内核版本 > 3.10
1. Docker >= 19.03（虽然文档中说最小支持 1.12 版本，但还是推荐使用 19.03 以上）
1. NVIDIA GPU [架构](https://www.nvidia.com/en-us/technologies/) >= Kepler (或 [算力](https://developer.nvidia.com/cuda-gpus#compute) 3.0 以上)
1. NVIDIA Linux 驱动 >= 418.81.07

### 离线安装

满足安装前置条件后，可参照 [Docker离线安装Nvidia-container-toolkit实现容器内GPU调用](https://blog.csdn.net/NekoTom/article/details/127508810) 或如下内容执行离线安装。

#### 1. 下载离线文件并安装

[Components and Packages](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/arch-overview.html#components-and-packages) 中说明了 NVIDIA Container Toolkit 的主要包：

- `nvidia-container-toolkit`
- `nvidia-cotnainer-toolkit-base`
- `libnvidia-container-tools`
- `libnvidia-container1`

以及依赖关系：

```text
├─ nvidia-container-toolkit (version)
│    ├─ libnvidia-container-tools (>= version)
│    └─ nvidia-container-toolkit-base (version)
│
├─ libnvidia-container-tools (version)
│    └─ libnvidia-container1 (>= version)
└─ libnvidia-container1 (version)
```

在 https://github.com/NVIDIA/libnvidia-container/tree/gh-pages/ 下载对应安装文件后（注意目标系统版本），按依赖关系倒序安装，如：

```bash
rpm -i libnvidia-container1-1.13.0-1.x86_64.rpm
rpm -i libnvidia-container-tools-1.13.0-1.x86_64.rpm
rpm -i nvidia-container-toolkit-base-1.13.0-1.x86_64.rpm
rpm -i nvidia-container-toolkit-1.13.0-1.x86_64.rpm
```

安装成功后可检查安装情况：

```bash
$ nvidia-ctk -h
NAME:
   NVIDIA Container Toolkit CLI - Tools to configure the NVIDIA Container Toolkit

USAGE:
   nvidia-ctk [global options] command [command options] [arguments...]

VERSION:
   1.13.0
commit: b7079454b5b8fed1390ce78ca5a3343748f62657

COMMANDS:
   hook     A collection of hooks that may be injected into an OCI spec
   runtime  A collection of runtime-related utilities for the NVIDIA Container Toolkit
   info     Provide information about the system
   cdi      Provide tools for interacting with Container Device Interface specifications
   system   A collection of system-related utilities for the NVIDIA Container Toolkit
   help, h  Shows a list of commands or help for one command

GLOBAL OPTIONS:
   --debug, -d    Enable debug-level logging (default: false) [$NVIDIA_CTK_DEBUG]
   --help, -h     show help (default: false)
   --version, -v  print the version (default: false)
```

#### 2. 配置 NVIDIA Container Runtime

```bash
$ nvidia-ctk runtime configure --runtime=docker
INFO[0000] Loading docker config from /etc/docker/daemon.json
INFO[0000] Successfully loaded config
INFO[0000] Wrote updated config to /etc/docker/daemon.json
INFO[0000] It is recommended that the docker daemon be restarted.
```

上述操作执行成功后会在 `/etc/docker/daemon.json` 中增加如下内容：

```json
"runtimes": {
    "nvidia": {
        "args": [],
        "path": "nvidia-container-runtime"
    }
},
```

之后重启 docker 服务以使配置生效：

```bash
systemctl restart docker
```

重启服务后执行如下命令查看效果：

```bash
$ sudo docker info | grep Runtimes
 Runtimes: io.containerd.runc.v2 nvidia runc
```

# 服务端

## PaddleNLP 镜像

PaddleNLP 的镜像可从 https://hub.docker.com/r/paddlecloud/paddlenlp 查看，根据 CUDA 及 cuDNN 版本，选择对应的 tag 拉取镜像。

CUDA 版本可在 `nvidia-smi` 中查看，cuDNN 版本可在头文件中查看：

```bash
$ cat /usr/local/cuda/include/cudnn_version.h |grep CUDNN_MAJOR -A 2
#define CUDNN_MAJOR 8
#define CUDNN_MINOR 4
#define CUDNN_PATCHLEVEL 1
--
#define CUDNN_VERSION (CUDNN_MAJOR * 1000 + CUDNN_MINOR * 100 + CUDNN_PATCHLEVEL)

#endif /* CUDNN_VERSION_H */
```

镜像 tag 有 `cuda10.2-cudnn7` 和 `cuda11.2-cudnn8` 两类，根据大版本号选择即可，如：

```bash
docker pull paddlecloud/paddlenlp:develop-gpu-cuda11.2-cudnn8-e72fb9
```

## 下载 CodeGen 的模型

[Salesforce CodeGen](https://github.com/salesforce/CodeGen) 是一组开放的、支持多回合交谈式 AI 编程的大语言模型，包含多种尺寸和数据集，模型命名方式为：

`codegen-{model-size}-{data}`

`model-size` 有四个选项：`350M`、`2B`、`6B`,`16B`，代表每个模型的参数数量；`data` 有三个选项：`nl`、`multi`、`mono`。

- `nl` 模型基于 [The Pile](https://github.com/EleutherAI/the-pile) —— 一个 825.18 GB 的英文语料库初始化和训练而来
- `multi` 模型基于 `nl` 模型初始化，再使用由多种编程语言组成的代码语料库训练
- `mono` 模型基于 `multi` 模型初始化，再使用 Python 代码语料库训练

关于各数据集的详细信息，可见 [CodeGen: An Open Large Language Model for Code with Multi-Turn Program Synthesis](https://arxiv.org/pdf/2203.13474.pdf) 。

PaddleNLP 使用的是 `.pdparams` 自有格式的模型，通过 PaddleNLP 下载的模型相关文件会存放在 `~/.paddlenlp` 路径下，如：

```bash
$ tree
.
├── datasets
├── models
│   ├── Salesforce
│   │   └── codegen-16B-multi
│   │       ├── added_tokens.json
│   │       ├── config.json
│   │       ├── merges.txt
│   │       ├── model_config.json
│   │       ├── model_state.pdparams
│   │       ├── special_tokens_map.json
│   │       ├── tokenizer_config.json
│   │       └── vocab.json
│   └── embeddings
└── packages
```

除 `config.json` 外，均可直接通过下方链接进行下载（注意修改 URL 中的模型参数大小）：

- [added_tokens.json](https://bj.bcebos.com/paddlenlp/models/community/Salesforce/codegen-16B-multi/added_tokens.json)
- [merges.txt](https://bj.bcebos.com/paddlenlp/models/community/Salesforce/codegen-16B-multi/merges.txt)
- [model_config.json](https://bj.bcebos.com/paddlenlp/models/community/Salesforce/codegen-16B-multi/model_config.json)
- [model_state.pdparams](https://bj.bcebos.com/paddlenlp/models/community/Salesforce/codegen-16B-multi/model_state.pdparams)
- [special_tokens_map.json](https://bj.bcebos.com/paddlenlp/models/community/Salesforce/codegen-16B-multi/special_tokens_map.json)
- [tokenizer_config.json](https://bj.bcebos.com/paddlenlp/models/community/Salesforce/codegen-16B-multi/tokenizer_config.json)
- [vocab.json](https://bj.bcebos.com/paddlenlp/models/community/Salesforce/codegen-16B-multi/vocab.json)

`config.json` 会根据 `model_config.json` 自动生成，无需提前下载。

## 启动 CodeGen Server

在将模型文件和 docker 镜像传输至离线环境后，可以开始准备启动辅助生成代码的服务端了。

可在保存模型文件的路径执行如下命令，会将模型文件挂载至容器的 `/mnt` 路径下：

```bash
$ docker run --name dev --runtime=nvidia -v $PWD:/mnt -p 8978:8978 -it paddlecloud/paddlenlp:develop-gpu-cuda11.2-cudnn8-e72fb9 /bin/bash
```

假设模型文件挂载路径为：`/mnt/paddlenlp/Salesforce/codegen-16B-multi`

如果使用的是 `paddlecloud/paddlenlp:develop-gpu-cuda11.2-cudnn8-e72fb9` 版本的镜像，进入容器后，需先更新 paddlepaddle（注意 cuda 版本需匹配，不低于容器内 cuda 版本应该就可以），以免遇到 [这个问题](https://github.com/PaddlePaddle/PaddleNLP/issues/5495#issuecomment-1517138237)：

```bash
pip install /mnt/paddlenlp/paddlepaddle_gpu-2.4.2.post117-cp37-cp37m-linux_x86_64.whl
```

之后需要安装依赖：

```bash
pip install -r examples/code_generation/codegen/requirements.txt
```

如有内网源，可使用内网源，或提前准备好 `requirements.txt` 中依赖的离线安装文件。

修改为使用提前下载好的模型地址后，即可启动服务：

```bash
$ cp examples/code_generation/codegen/*.py .
$ sed -i 's#Salesforce/codegen-350M-mono#/mnt/paddlenlp/Salesforce/codegen-16B-multi#g' codegen_server.py
$ python codegen_server.py
```

服务成功启动后，可在 8978 端口访问，如 http://localhost:8978 。


# 客户端

## Fauxpilot VSCode Plugin

Visual Studio Code 中可通过 [vscode-fauxpilot](https://github.com/Venthe/vscode-fauxpilot) 插件，使用代码辅助编写功能。在 VSCode 插件市场搜索 `Fauxpilot` 或在 [releases](https://github.com/Venthe/vscode-fauxpilot/releases) 页面下载 `.vsix` 格式的插件离线安装包，安装后在插件的配置页面，设置 `Fauxpilot: Server` 地址为之前启动的服务端地址，如 `http://localhost:8978/v1/engines`，重启 VSCode 后即可体验类似 GitHub Copilot 的离线环境 AI 辅助代码编写了。