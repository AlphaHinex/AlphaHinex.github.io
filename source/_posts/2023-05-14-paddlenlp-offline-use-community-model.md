---
id: paddlenlp-offline-use-community-model
title: "PaddleNLP 离线使用已下载好的社区模型"
description: "修改源码，或者修改模型名称为全路径"
date: 2023.05.14 10:26
categories:
    - AI
tags: [AI, PaddleNLP]
keywords: PaddlePaddle, PaddleNLP, NVIDIA, Salesforce CodeGen, GPU, offline
cover: /contents/covers/paddlenlp-offline-use-community-model.png
---

# TL;DR

使用 PaddleNLP 加载社区模型时，因为社区模型需联网下载，可先从在线环境进行模型下载，再将下载好的模型传输到离线环境中。此时在离线环境下可能会遇到 https://github.com/PaddlePaddle/PaddleNLP/pull/5817 中描述的问题，可参照该 PR [files](https://github.com/PaddlePaddle/PaddleNLP/pull/5817/files) 中内容修改，以支持离线环境的正常使用。

# PaddleNLP

> PaddleNLP是一款简单易用且功能强大的自然语言处理开发库。聚合业界优质预训练模型并提供开箱即用的开发体验，覆盖NLP多场景的模型库搭配产业实践范例可满足开发者灵活定制的需求。 —— https://github.com/PaddlePaddle/PaddleNLP

PaddleNLP 文档地址：https://paddlenlp.readthedocs.io/zh/latest/index.html# 

不过从实际使用下来的体验来看，文档内容对刚接触 PaddleNLP 的人并不友好，需要自行摸索和补充了解的内容较多。

`PaddleNLP` 依赖 [PaddlePaddle](https://github.com/paddlepaddle/paddle)，`PaddlePaddle` 分为 `paddlepaddle` 和 `paddlepaddle-gpu` 两个版本，想使用 GPU 进行计算，需要安装 `paddlepaddle-gpu`。使用 GPU 版本，还涉及到 [显卡驱动](https://www.nvidia.cn/Download/index.aspx?lang=cn)、[CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)、[cuDNN](https://developer.nvidia.cn/zh-cn/cudnn)、[cuBLAS](https://developer.nvidia.com/zh-cn/cublas) 等，各个组件之间版本繁杂，兼容性问题较多，想构建起一个可用的环境不是一件容易的事情。

推荐使用 Docker 环境上手体验，安装 [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-docker) 之后，根据 CUDA 和 cuDNN 选择对应的镜像版本，如：

```bash
docker run --name dev --runtime=nvidia -v $PWD:/mnt -p 8888:8888 -it paddlecloud/paddlenlp:develop-gpu-cuda11.2-cudnn8-e72fb9 /bin/bash
```

即便是官方提供的镜像，里面的组件版本也可能存在兼容性问题。上面 `paddlecloud/paddlenlp:develop-gpu-cuda11.2-cudnn8-e72fb9` 这个镜像，在引入 `paddlenlp` 中的 `Taskflow` 时，会[抛出异常](https://github.com/PaddlePaddle/PaddleNLP/issues/5495#issuecomment-1517138237)，需要在容器里把 `paddlepaddle-gpu` 从 `2.3.0` 升级到 `2.4.2`。

# Salesforce CodeGen

[Salesforce CodeGen](https://github.com/salesforce/CodeGen) 是一组开放的、支持多回合交谈式 AI 编程的大语言模型，包含多种尺寸和数据集，模型命名方式为：

`codegen-{model-size}-{data}`

`model-size` 有四个选项：`350M`、`2B`、`6B`,`16B`，代表每个模型的参数数量；`data` 有三个选项：`nl`、`multi`、`mono`。

- `nl` 模型基于 [The Pile](https://github.com/EleutherAI/the-pile) —— 一个 825.18 GB 的英文语料库初始化和训练而来
- `multi` 模型基于 `nl` 模型初始化，再使用由多种编程语言组成的代码语料库训练
- `mono` 模型基于 `multi` 模型初始化，再使用 Python 代码语料库训练

关于各数据集的详细信息，可见 [CodeGen: An Open Large Language Model for Code with Multi-Turn Program Synthesis](https://arxiv.org/pdf/2203.13474.pdf) 。

# PaddleNLP 加载 CodeGen 模型

## Online

在线环境下，加载内置的模型时，会从预设的网址下载对应文件到本地。忽略了加载模型相关日志输出的，使用 CodeGen 模型通过提示词补全后续代码的示例代码如下：

```bash
$ python3
>>> from paddlenlp import Taskflow
>>> codegen = Taskflow("code_generation", model="Salesforce/codegen-350M-mono",decode_strategy="greedy_search", repetition_penalty=1.0)
>>> print(codegen("def lengthOfLongestSubstring(self, s: str) -> int:"))
['\n        if not s:\n            return 0\n        \n        dic = {}\n        max_len = 0\n        \n        for i in range(len(s)):\n         if s[i] in dic:\n                dic[s[i]] += 1\n                if dic[s[i]] > max_len:\n                    max_len = dic[s[i]]\n            else:\n                dic[s[i]] = 1\n        \n        return max_len']
```

此时在本地 `~/.paddlenlp` 路径下，会下载好模型相关文件：

```bash
$ pwd
/root/.paddlenlp
$ tree
.
├── datasets
├── models
│   ├── Salesforce
│   │   └── codegen-350M-mono
│   │       ├── added_tokens.json
│   │       ├── config.json
│   │       ├── merges.txt
│   │       ├── model_config.json
│   │       ├── model_state.pdparams
│   │       ├── special_tokens_map.json
│   │       ├── tokenizer_config.json
│   │       └── vocab.json
│   └── embeddings
└── packages
```

## Offline

然而遗憾的是，上面的代码在离线环境无法直接使用，即使将模型相关文件全部传输到离线环境相同路径内，使用 `Taskflow("code_generation", model="Salesforce/codegen-350M-mono")` 时也会得到无法连接 `bj.bcebos.com` 域名的报错：

```log
HTTPSConnectionPool(host='bj.bcebos.com', port=443): Max retries exceeded with url: /paddlenlp/models/community/Salesforce/codegen-350M-mono/config.json (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x140053a90>: Failed to establish a new connection: [Errno 8] nodename nor servname provided, or not known'))
```

完整的报错信息可见 https://github.com/PaddlePaddle/PaddleNLP/pull/5817 。

### 报错原因

报相关错误的原因是，PaddleNLP 在加载社区模型（`community/model-name`）时，会先去判断对应模型文件在社区网站（ 默认为：https://bj.bcebos.com/paddlenlp/models/community ）是否存在，不论本地是否已经下载过了该模型。

### 解决思路

解决的思路很简单，在下载社区模型相关文件时，首先检查缓存路径中是否已经存在对应文件，如存在则直接使用，不存在再通过网络请求进行获取。

### 修改文件

可在错误堆栈中获取报错环境中需要修改的具体文件路径，如：

```path
/Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages/paddlenlp/transformers/model_utils.py
```

需要修改的文件如下，或参考 https://github.com/PaddlePaddle/PaddleNLP/pull/5817/files 。

- `paddlenlp/transformers/configuration_utils.py`

`_get_config_dict` 方法 `elif from_hf_hub:` 后面再添加一个 `elif`：

```python
elif os.path.isfile(os.path.join(cache_dir, CONFIG_NAME)):
    resolved_config_file = os.path.join(cache_dir, CONFIG_NAME)
```

- `paddlenlp/transformers/model_utils.py`

`_resolve_model_file_path` 方法 `0. when it is local file` 后面增加一个 `elif` 条件：

```python
elif os.path.isfile(os.path.join(cache_dir, cls.resource_files_names["model_state"])):
    return os.path.join(cache_dir, cls.resource_files_names["model_state"])
```

- `paddlenlp/transformers/auto/modeling.py`

`_from_pretrained` 方法 `# Assuming from community-contributed pretrained models` 部分调整：

```diff
         # Assuming from community-contributed pretrained models
         else:
+            cached_standard_config = os.path.join(cache_dir, cls.model_config_file)
+            cached_legacy_config = os.path.join(cache_dir, cls.legacy_model_config_file)
             standard_community_url = "/".join(
                 [COMMUNITY_MODEL_PREFIX, pretrained_model_name_or_path, cls.model_config_file]
             )
             legacy_community_url = "/".join(
                 [COMMUNITY_MODEL_PREFIX, pretrained_model_name_or_path, cls.legacy_model_config_file]
             )
             try:
-                if url_file_exists(standard_community_url):
+                if os.path.isfile(cached_standard_config):
+                    resolved_vocab_file = cached_standard_config
+                elif os.path.isfile(cached_legacy_config):
+                    resolved_vocab_file = cached_legacy_config
+                elif url_file_exists(standard_community_url):
                     resolved_vocab_file = get_path_from_url_with_filelock(standard_community_url, cache_dir)
                 elif url_file_exists(legacy_community_url):
```

### 效果验证

离线环境下可通过下列方式，验证加载已下载好的社区模型是否会报错：

```python
from paddlenlp import Taskflow
codegen = Taskflow("code_generation", model="Salesforce/codegen-350M-mono",decode_strategy="greedy_search", repetition_penalty=1.0)
```

```python
from paddlenlp.transformers import CodeGenForCausalLM, CodeGenTokenizer
CodeGenTokenizer.from_pretrained("Salesforce/codegen-350M-mono")
CodeGenForCausalLM.from_pretrained("Salesforce/codegen-350M-mono", load_state_as_np=True)
```

```python
from paddlenlp.transformers import AutoModel
AutoModel.from_pretrained("Salesforce/codegen-350M-mono")
```

### 全路径加载离线模型

在不修改代码的情况下，也可通过模型文件全路径在离线环境加载模型，但涉及到在线环境和离线环境的代码不一致，可自行取舍：

```python
from paddlenlp.transformers import AutoModel
AutoModel.from_pretrained("~/.paddlenlp/models/Salesforce/codegen-350M-mono")
```