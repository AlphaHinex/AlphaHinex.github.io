---
id: model-memory-usage
title: "可本地部署使用的大模型显存资源估算工具"
description: "解决线上版本当前无法正常使用以及无法访问的问题"
date: 2025.02.16 10:34
categories:
    - AI
    - Python
tags: [AI, Python, HuggingFace, LLM]
keywords: Hugging Face, Model Memory Calculator, Accelerate, Model was not found on the Hub
cover: /contents/model-memory-usage/cover.png
---

[🤗 Model Memory Calculator](https://huggingface.co/spaces/hf-accelerate/model-memory-usage) 是 [🤗 Accelerate](https://github.com/huggingface/accelerate) 库提供的一个模型显存计算工具，可估算模型训练或推理时所需的显存大小。

但目前该在线工具无法正常使用，即使使用默认的模型名称，也会报在 Hub 中无法找到该模型：

![not found](/contents/model-memory-usage/not-found.png)

在该 space 的 [discussions](https://huggingface.co/spaces/hf-accelerate/model-memory-usage/discussions) 中也有不少人遇到了此问题。

本文提供一种本地化部署运行此工具的方法，还可通过指定 `HF_ENDPOINT` 避免无法访问 Hugging Face 的问题。

本地部署
=======

hotfix 版本
-----------

直接部署 https://huggingface.co/spaces/hf-accelerate/model-memory-usage/tree/main 中的内容会遇到一些问题，可使用 [hotfix](https://github.com/AlphaHinex/model-memory-usage) 分支的版本，主要改动内容如下：

1. `requirements.txt` 中增加 `gradio==4.43.0` 依赖。使用 [README.md](https://huggingface.co/spaces/hf-accelerate/model-memory-usage/blob/main/README.md) 中设定的 Gradio SDK 版本 `4.36.0` 可能会遇到 [与 pydantic 版本不匹配导致的报错](https://blog.csdn.net/qq_38463737/article/details/142825145)，故升级至 `4.43.0` 版本。
1. 修改 `src/app.py` 中 `get_results` 方法，修复官方应用中无法在 Hub 中找到模型的问题。

```diff
diff --git a/src/app.py b/src/app.py
index 7a5e23e..500023a 100644
--- a/src/app.py
+++ b/src/app.py
@@ -7,6 +7,8 @@ from model_utils import calculate_memory, get_model


 def get_results(model_name: str, library: str, options: list, access_token: str):
+    if access_token == "":
+        access_token = None
     model = get_model(model_name, library, access_token)
     # try:
     #     has_discussion = check_for_discussion(model_name)
```

> 与原始版本具体区别可见 [diff](https://github.com/AlphaHinex/model-memory-usage/compare/main...hotfix)。

Python 3.8
----------

```bash
# conda create -n mmu-env python=3.8 -c https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
$ conda create -n mmu-env python=3.8
$ conda activate mmu-env
```

> conda 环境安装可参照 [miniconda](https://alphahinex.github.io/2024/01/14/jupyter-lab-in-action/)。

部署
----

```bash
$ git clone https://github.com/AlphaHinex/model-memory-usage.git
$ cd model-memory-usage

# pip install -r requirements.txt -i http://192.168.1.200/local/proxy/pypi/web/simple --trusted-host 192.168.1.200
# pip install -r requirements.txt
$ pip install -r requirements.txt -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple

# python src/app.py
$ HF_ENDPOINT=https://hf-mirror.com python src/app.py
```

`Model Name or URL` 处输入 `deepseek-ai/DeepSeek-R1-Distill-Qwen-32B`，在 `Model Precision` 选择要估算的精度，点击 `Calculate Memory Usage`：

![](/contents/model-memory-usage/cover.png)
