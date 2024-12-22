---
id: vllm-multi-node-inference
title: "用 vLLM 在多节点多卡上部署 Qwen2.5 以及进行推理"
description: "本文记录了在两台机器，每台机器一块 Tesla T4 显卡的环境下，使用 vLLM 部署 Qwen2.5-32B-Instruct-GPTQ-Int4 模型的过程及遇到的问题，供类似环境使用 vLLM 进行多节点多卡推理参考。"
date: 2024.12.22 10:26
categories:
    - AI
tags: [AI, Python, vLLM]
keywords: vllm, gptq, gptq_marlin, tensor-parallel-size, Qwen2.5-32B-Instruct-GPTQ-Int4, multi-node inference, docker, nvidia container toolkit, max-model-len, gpu-memory-utilization, tesla t4
cover: /contents/covers/vllm-multi-node-inference.png
---

本文记录了在两台机器，每台机器一块 Tesla T4 显卡的环境下，使用 vLLM 部署 Qwen2.5-32B-Instruct-GPTQ-Int4 模型的过程及遇到的问题，供类似环境使用 vLLM 进行多节点多卡推理参考。

# 部署清单

1. [Qwen2.5-32B-Instruct-GPTQ-Int4](https://modelscope.cn/models/Qwen/Qwen2.5-32B-Instruct-GPTQ-Int4/files)、[vLLM](https://docs.vllm.ai/en/latest/serving/deploying_with_docker.html)
1. [docker v27.4.0](https://download.docker.com/linux/static/stable/x86_64/docker-27.4.0.tgz)、[nvidia-container-toolkit v1.17.3](https://github.com/NVIDIA/nvidia-container-toolkit/releases/tag/v1.17.3)
1. Tesla T4 显卡驱动 [v550.127.08 CUDA12.4](https://cn.download.nvidia.com/tesla/550.127.08/NVIDIA-Linux-x86_64-550.127.08.run)

## 部署包准备

```bash
# qwen
$ git clone https://www.modelscope.cn/Qwen/Qwen2.5-32B-Instruct-GPTQ-Int4.git

# vllm image
$ docker pull vllm/vllm-openai:v0.6.4.post1

# export
$ docker save vllm/vllm-openai:v0.6.4.post1 | gzip > images.tar.gz
```

# 更新显卡驱动

需要更新至 cuda>=12.4，以运行 vLLM 容器。

```bash
# 先卸载之前安装的驱动 
$ sh ./NVIDIA-Linux-x86_64-550.127.08.run --uninstall 
# 再安装驱动 
$ sh ./NVIDIA-Linux-x86_64-550.127.08.run 
# 检测驱动 
$ nvidia-smi
```

# Docker

## Docker Engine

```bash
$ tar -xzf docker-27.4.0.tgz
$ cp docker/* /usr/local/bin/
$ docker -v
```

将 https://github.com/containerd/containerd/blob/main/containerd.service 内容保存至 `/usr/lib/systemd/system/containerd.service`：

```service
# Copyright The containerd Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

[Unit]
Description=containerd container runtime
Documentation=https://containerd.io
After=network.target local-fs.target dbus.service

[Service]
ExecStartPre=-/sbin/modprobe overlay
ExecStart=/usr/local/bin/containerd

Type=notify
Delegate=yes
KillMode=process
Restart=always
RestartSec=5

# Having non-zero Limit*s causes performance problems due to accounting overhead
# in the kernel. We recommend using cgroups to do container-local accounting.
LimitNPROC=infinity
LimitCORE=infinity

# Comment TasksMax if your systemd version does not supports it.
# Only systemd 226 and above support this version.
TasksMax=infinity
OOMScoreAdjust=-999

[Install]
WantedBy=multi-user.target
```

```bash
$ systemctl enable --now containerd
$ systemctl status containerd
```

将下面内容保存至 `/usr/lib/systemd/system/docker.service`：

```service
[Unit]
Description=Docker Application Container Engine
Documentation=https://docs.docker.com
After=network-online.target firewalld.service
Wants=network-online.target

[Service]
Type=notify
ExecStart=/usr/local/bin/dockerd
ExecReload=/bin/kill -s HUP $MAINPID
TimeoutStartSec=0
RestartSec=2
Restart=always
StartLimitBurst=3
StartLimitInterval=60s
LimitNOFILE=infinity
LimitNPROC=infinity
LimitCORE=infinity
TasksMax=infinity
Delegate=yes
KillMode=process
OOMScoreAdjust=-500

[Install]
WantedBy=multi-user.target
```

```bash
$ systemctl enable --now docker
$ systemctl status docker
```

## Nvidia Container Toolkit

```bash
$ tar -xzf nvidia-container-toolkit_1.17.3_rpm_x86_64.tar.gz
$ cd release-v1.17.3-stable/packages/centos7/x86_64
$ rpm -i libnvidia-container1-1.17.3-1.x86_64.rpm
$ rpm -i libnvidia-container-tools-1.17.3-1.x86_64.rpm
$ rpm -i nvidia-container-toolkit-base-1.17.3-1.x86_64.rpm
$ rpm -i nvidia-container-toolkit-1.17.3-1.x86_64.rpm 
# 检查安装情况
$ nvidia-ctk -h
# 配置 Nvidia Container Runtime
$ nvidia-ctk runtime configure --runtime=docker
# 检查配置
$ cat /etc/docker/daemon.json
# 重启 docker
$ systemctl restart docker
# 重启服务后执行如下命令查看效果：
$ docker info | grep Runtimes
 Runtimes: io.containerd.runc.v2 nvidia runc
```

# Qwen

## 1. 校验模型文件

```text
942d93a82fb6d0cb27c940329db971c1e55da78aed959b7a9ac23944363e8f47  model-00001-of-00005.safetensors
19139f34508cb30b78868db0f19ed23dbc9f248f1c5688e29000ed19b29a7eef  model-00002-of-00005.safetensors
d0f829efe1693dddaa4c6e42e867603f19d9cc71806df6e12b56cc3567927169  model-00003-of-00005.safetensors
3a5a428f449bc9eaf210f8c250bc48f3edeae027c4ef8ae48dd4f80e744dd19e  model-00004-of-00005.safetensors
c22a1d1079136e40e1d445dda1de9e3fe5bd5d3b08357c2eb052c5b71bf871fe  model-00005-of-00005.safetensors
```

```bash
$ cd /root/model/Qwen2.5-32B-Instruct-GPTQ-Int4
$ sha256sum *.safetensors > sum.txt
```

## 2. 配置集群

在两台机器分别准备好 `vllm/vllm-openai:v0.6.4.post1` 镜像后，将 https://github.com/vllm-project/vllm/blob/main/examples/run_cluster.sh 存放至 `/root/model/`：

```sh
#!/bin/bash

# Check for minimum number of required arguments
if [ $# -lt 4 ]; then
    echo "Usage: $0 docker_image head_node_address --head|--worker path_to_hf_home [additional_args...]"
    exit 1
fi

# Assign the first three arguments and shift them away
DOCKER_IMAGE="$1"
HEAD_NODE_ADDRESS="$2"
NODE_TYPE="$3"  # Should be --head or --worker
PATH_TO_HF_HOME="$4"
shift 4

# Additional arguments are passed directly to the Docker command
ADDITIONAL_ARGS=("$@")

# Validate node type
if [ "${NODE_TYPE}" != "--head" ] && [ "${NODE_TYPE}" != "--worker" ]; then
    echo "Error: Node type must be --head or --worker"
    exit 1
fi

# Define a function to cleanup on EXIT signal
cleanup() {
    docker stop node
    docker rm node
}
trap cleanup EXIT

# Command setup for head or worker node
RAY_START_CMD="ray start --block"
if [ "${NODE_TYPE}" == "--head" ]; then
    RAY_START_CMD+=" --head --port=6379"
else
    RAY_START_CMD+=" --address=${HEAD_NODE_ADDRESS}:6379"
fi

# Run the docker command with the user specified parameters and additional arguments
docker run \
    --entrypoint /bin/bash \
    --network host \
    --name node \
    --shm-size 10.24g \
    --gpus all \
    -v "${PATH_TO_HF_HOME}:/root/.cache/huggingface" \
    "${ADDITIONAL_ARGS[@]}" \
    "${DOCKER_IMAGE}" -c "${RAY_START_CMD}"
```

选择 节点1 作为 head node，节点2 作为 worker node。

在 节点1 执行：

```bash
nohup bash run_cluster.sh \
    vllm/vllm-openai:v0.6.4.post1 \
    IP_OF_HEAD_NODE \
    --head \
    /root/model > nohup.log 2>&1 &
```

在 节点2 执行：

```bash
nohup bash run_cluster.sh \
    vllm/vllm-openai:v0.6.4.post1 \
    IP_OF_HEAD_NODE \
    --worker \
    /root/model > nohup.log 2>&1 &
```

> 注意：两个节点执行脚本指定的都是 head 节点的 IP。

在任意节点通过 `docker exec -ti node bash` 进入容器：

```bash
# 查看集群状态
$ ray status
```

## 3. 启动 vLLM 服务

在 节点1 的容器中启动服务（按当前显卡配置，GPU 利用率 90% 的前提下，只能将原始模型 32k 的上下文长度缩减到 4k）：

```bash
# 根据 2 个节点和每个节点 1 个 GPU 设置总的 tensor-parallel-size
$ nohup vllm serve /root/.cache/huggingface/Qwen2.5-32B-Instruct-GPTQ-Int4 \
    --served-model-name Qwen2.5-32B-Instruct-GPTQ-Int4 \
    --tensor-parallel-size 2 --max-model-len 4096 \
    > vllm_serve_qwen_nohup.log 2>&1 &
```

### 参数调整过程

默认 `gpu-memory-utilization`（`0.9`）时，日志中输出的 `# GPU blocks` 为 `0`。

> No available memory for the cache blocks. Try increasing gpu_memory_utilization when initializing the engine. —— --gpu-memory-utilization 0.95

调整 `gpu-memory-utilization` 为 `0.95` 后，`# GPU blocks: 271`，`271 * 16 = 4336`，即下面报错中的 KV cache token 数。

> The model's max seq len (32768) is larger than the maximum number of tokens that can be stored in KV cache (4336). Try increasing gpu_memory_utilization or decreasing max_model_len when initializing the engine. —— --max_model_len 4096

添加 `--max-model-len 4096` 后，`# GPU blocks: 1548`

## 4. 验证对话接口

```bash
curl --request POST \
  -H "Content-Type: application/json" \
  --url http://IP_OF_HEAD_NODE:8000/v1/chat/completions \
  --data '{"messages":[{"role":"user","content":"我希望你充当 IT 专家。我会向您提供有关我的技术问题所需的所有信息，而您的职责是解决我的问题。你应该使用你的计算机科学、网络基础设施和 IT 安全知识来解决我的问题。在您的回答中使用适合所有级别的人的智能、简单和易于理解的语言将很有帮助。用要点逐步解释您的解决方案很有帮助。尽量避免过多的技术细节，但在必要时使用它们。我希望您回复解决方案，而不是写任何解释。我的第一个问题是“我的笔记本电脑出现蓝屏错误”。"}],"stream":true,"model":"Qwen2.5-32B-Instruct-GPTQ-Int4"}'
```

> 必须设置 `Content-Type` 请求头，否则会报 500 的错误：[[Bug]: Missing Content Type returns 500 Internal Server Error instead of 415 Unsupported Media Type](https://github.com/vllm-project/vllm/issues/11171)

### 回复都是 ！

> we currently find two workarounds
> - use gptq_marlin, which is available for Ampere and later cards.
> - change the number on this line from 50 to 0 and install from the modified source code. it may affect speed on short sequences though.
> —— https://github.com/QwenLM/Qwen2.5/issues/1103#issuecomment-2507022590

目前 Qwen 和 vLLM 社区均向项目开发者报告了类似问题，[jklj077](https://github.com/jklj077) 暂时给出了两个绕过方案：

1. 需要修改模型文件中的 `config.json`，将其中的 `"quant_method": "gptq",` 修改为 `"quant_method": "gptq_marlin",`，但 [需要显卡算力在 8.0 以上](https://github.com/vllm-project/vllm/blob/main/vllm/model_executor/layers/quantization/utils/marlin_utils.py#L36)；
2. 需要修改 vLLM 源码，之后使用修改后源码安装。

## 5. 验证补全接口

```bash
curl --request POST \
  -H "Content-Type: application/json" \
  --url http://IP_OF_HEAD_NODE:8000/v1/completions \
  --data '{"prompt":"who r u?","model":"Qwen2.5-32B-Instruct-GPTQ-Int4"}'
```

# 参考资料

- [nvidia显卡驱动安装](https://zhuanlan.zhihu.com/p/12913261423)
- [Centos7.9离线安装Docker24(无坑版)_centos7.9 离线安装docker-CSDN博客](https://blog.csdn.net/jianghuchuang/article/details/141220379)
- [用 PaddleNLP 结合 CodeGen 实现离线 GitHub Copilot - Alpha Hinex's Blog](https://alphahinex.github.io/2023/06/11/paddlenlp-codegen-copilot/)
- [[Usage]: vllm infer with 2 * Nvidia-L20, output repeat !!!!](https://github.com/vllm-project/vllm/issues/10713)
- [[Bug]: Qwen2.5-32B-GPTQ-Int4 inference !!!!!](https://github.com/vllm-project/vllm/issues/10656)
- [Distributed Inference and Serving](https://docs.vllm.ai/en/stable/serving/distributed_serving.html)
- [vLLM - Multi-Node Inference and Serving](https://docs.vllm.ai/en/stable/serving/distributed_serving.html#multi-node-inference-and-serving)
- [大模型推理:vllm多机多卡分布式本地部署_vllm 多卡部署-CSDN博客](https://blog.csdn.net/sunny0121/article/details/139331035)
- [vLLM分布式多GPU Docker部署踩坑记 | LittleFish’Blog](https://www.xiaoiluo.com/article/vllm-gpu-ray-multigpu#google_vignette)
