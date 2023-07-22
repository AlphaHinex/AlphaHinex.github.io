---
id: deepspeed-finetune-codegen
title: "让 AI 辅助编写内部代码"
description: "使用 DeepSpeed 微调 CodeGen 模型并可在 FauxPiolot 中使用"
date: 2023.07.23 10:26
categories:
    - AI
tags: [AI, VS Code]
keywords: GitHub Copilot, Copilot, FauxPilot, VS Code, CodeGen, Triton Inference Server, GPU, FasterTransformer
cover: /contents/fauxpilot/cover.png
---

在 [用 PaddleNLP 结合 CodeGen 实现离线 GitHub Copilot](https://alphahinex.github.io/2023/06/11/paddlenlp-codegen-copilot/) 和 [GitHub Copilot 开源替代品 —— FauxPilot](https://alphahinex.github.io/2023/06/18/fauxpilot/) 中，我们分别使用 PaddleNLP 和 FauxPilot 将 CodeGen 模型代理为可通过 HTTP 请求访问的接口，并通过 VS Code 插件在 IDE 中获得与 GitHub Copilot 类似的 AI 辅助编码能力。

但不论是这种方式也好，或者是 GitHub Copilot，能够辅助编写的都是通用代码，无法辅助编写内部框架或私有类库的相关代码。

这个场景可以通过对 CodeGen 模型进行微调来实现。

本文介绍了基于 [CodeGen-350M-multi](https://huggingface.co/Salesforce/codegen-350M-multi) 模型，使用 [DeepSpeed](https://www.deepspeed.ai/) 对模型进行微调，并使用 [FauxPilot](https://github.com/fauxpilot/fauxpilot) 项目中提供的脚本，对模型进行转换，以使用 [FasterTransformer](https://github.com/NVIDIA/FasterTransformer) 进行加速，最终在 VS Code 的 [FauxPilot](https://github.com/Venthe/vscode-fauxpilot) 插件中，实现让 AI 辅助编写内部代码的效果。

# 模型微调

## DeepSpeed 微调环境

DeepSpeed 依赖 [PyTorch](https://pytorch.org/)，完整的环境需求可见官方文档 [Requirements](https://github.com/microsoft/DeepSpeed#requirements)，本文在 Docker 镜像中执行微调，使用 [deepspeed/deepspeed:latest_torch111](https://hub.docker.com/layers/deepspeed/deepspeed/latest_torch111/images/sha256-7e594486a330c7c53be12fdc3c1b426f853a3dd1dc43d9ea1dcdf5cbc19150c4?context=explore) 作为基础镜像，[🤗 Transformers](https://github.com/huggingface/transformers) `v4.21.1` 版本中的 [run_clm.py](https://github.com/huggingface/transformers/blob/v4.21.1/examples/pytorch/language-modeling/run_clm.py) 脚本作为微调脚本，需在微调环境中安装微调脚本所需依赖 [requirements.txt](https://github.com/huggingface/transformers/blob/v4.21.1/examples/pytorch/language-modeling/requirements.txt) 及 `aiohttp` 和 `transformers`。

这里需注意 `run_clm.py` 和 `requirements.txt` 要使用与安装的 Transformers 版本一致的源码 tag 中的文件，如上面链接均为 `v4.21.1` 版本的。

可参照如下 `Dockerfile` 构建微调环境所使用的镜像：

```Dockerfile
FROM deepspeed/deepspeed:latest_torch111

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt
RUN pip install aiohttp==3.6
RUN pip install transformers==4.21.1
```

构建镜像：

```bash
docker build -t deepspeed:codegen .
```

使用镜像启动并进入容器：

```bash
$ docker run --name dstest --runtime=nvidia -v $PWD:/mnt -it deepspeed:codegen /bin/bash

=============
== PyTorch ==
=============

NVIDIA Release 21.12 (build 29870972)
PyTorch Version 1.11.0a0+b6df043

Container image Copyright (c) 2021, NVIDIA CORPORATION & AFFILIATES. All rights reserved.

Copyright (c) 2014-2021 Facebook Inc.
Copyright (c) 2011-2014 Idiap Research Institute (Ronan Collobert)
Copyright (c) 2012-2014 Deepmind Technologies    (Koray Kavukcuoglu)
Copyright (c) 2011-2012 NEC Laboratories America (Koray Kavukcuoglu)
Copyright (c) 2011-2013 NYU                      (Clement Farabet)
Copyright (c) 2006-2010 NEC Laboratories America (Ronan Collobert, Leon Bottou, Iain Melvin, Jason Weston)
Copyright (c) 2006      Idiap Research Institute (Samy Bengio)
Copyright (c) 2001-2004 Idiap Research Institute (Ronan Collobert, Samy Bengio, Johnny Mariethoz)
Copyright (c) 2015      Google Inc.
Copyright (c) 2015      Yangqing Jia
Copyright (c) 2013-2016 The Caffe contributors
All rights reserved.

NVIDIA Deep Learning Profiler (dlprof) Copyright (c) 2021, NVIDIA CORPORATION & AFFILIATES.  All rights reserved.

Various files include modifications (c) NVIDIA CORPORATION & AFFILIATES.  All rights reserved.

This container image and its contents are governed by the NVIDIA Deep Learning Container License.
By pulling and using the container, you accept the terms and conditions of this license:
https://developer.nvidia.com/ngc/nvidia-deep-learning-container-license

NOTE: MOFED driver for multi-node communication was not detected.
      Multi-node communication performance may be reduced.

NOTE: The SHMEM allocation limit is set to the default of 64MB.  This may be
   insufficient for PyTorch.  NVIDIA recommends the use of the following flags:
   docker run --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 ...
root@f8338550c41f:/workspace#
```

容器中使用 `ds_report` 验证 DeepSpeed 状态：

```bash
root@f8338550c41f:/workspace# ds_report
--------------------------------------------------
DeepSpeed C++/CUDA extension op report
--------------------------------------------------
NOTE: Ops not installed will be just-in-time (JIT) compiled at
      runtime if needed. Op compatibility means that your system
      meet the required dependencies to JIT install the op.
--------------------------------------------------
JIT compiled ops requires ninja
ninja .................. [OKAY]
--------------------------------------------------
op name ................ installed .. compatible
--------------------------------------------------
cpu_adam ............... [NO] ....... [OKAY]
cpu_adagrad ............ [NO] ....... [OKAY]
fused_adam ............. [NO] ....... [OKAY]
fused_lamb ............. [NO] ....... [OKAY]
 [WARNING]  please install triton==1.0.0 if you want to use sparse attention
sparse_attn ............ [NO] ....... [NO]
transformer ............ [NO] ....... [OKAY]
stochastic_transformer . [NO] ....... [OKAY]
 [WARNING]  async_io requires the dev libaio .so object and headers but these were not found.
 [WARNING]  async_io: please install the libaio-dev package with apt
 [WARNING]  If libaio is already installed (perhaps from source), try setting the CFLAGS and LDFLAGS environment variables to where it can be found.
async_io ............... [NO] ....... [NO]
utils .................. [NO] ....... [OKAY]
quantizer .............. [NO] ....... [OKAY]
transformer_inference .. [NO] ....... [OKAY]
--------------------------------------------------
DeepSpeed general environment info:
torch install path ............... ['/opt/conda/lib/python3.8/site-packages/torch']
torch version .................... 1.11.0a0+b6df043
torch cuda version ............... 11.5
torch hip version ................ None
nvcc version ..................... 11.5
deepspeed install path ........... ['/opt/conda/lib/python3.8/site-packages/deepspeed']
deepspeed info ................... 0.6.5, unknown, unknown
deepspeed wheel compiled w. ...... torch 1.11, cuda 11.5
```

容器中验证 CUDA 状态：

```bash
root@f8338550c41f:/workspace# python
Python 3.8.12 | packaged by conda-forge | (default, Oct 12 2021, 21:59:51)
[GCC 9.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import torch
>>> torch.cuda.is_available()
True
```

## 数据集

微调数据集若使用 Hugging Face 上的，可直接在微调命令中传入数据集名称，如 [moyjx/debian_csrc](https://huggingface.co/datasets/moyix/debian_csrc)。如需使用本地数据集，仅支持 `csv/json/txt` 格式，这里的 `json` 格式，是指 [处理大数据集的灵活格式 —— JSON Lines](https://alphahinex.github.io/2023/07/16/json-lines/) 中提到的 JSON Lines 格式，例如：

```jsonl
{"text": "content_of_source_file_1", "url": "path_to_source_file_1"}
{"text": "content_of_source_file_2", "url": "path_to_source_file_2"}
...
```

其中：

- `text` 属性为必需属性，保存训练数据，即源码文件内容，该属性名可在 `run_clm.py` 脚本中修改。
- 其他属性可自愿添加，如上面的 `url` 属性可以标识文件来源。

可使用 [files2jsonl](https://github.com/AlphaHinex/go-toolkit/tree/main/files2jsonl) 工具将源码文件夹转换为可直接使用的本地数据集。

## 微调命令

```bash
deepspeed --num_gpus 4 --num_nodes 1 \
./run_clm.py \
--model_name_or_path=./codegen-350M-multi \
--per_device_train_batch_size=1 \
--learning_rate 2e-5 \
--num_train_epochs 1 \
--output_dir=./codegen-350M-multi-finetune \
--train_file ./test_dataset.json \
--tokenizer_name ./codegen-350M-multi \
--block_size 2048 \
--gradient_accumulation_steps 32 \
--do_train \
--fp16 \
--overwrite_output_dir \
--deepspeed ./ds_config.json
```

`train_file` 参数指定本地文件。若要使用 Hugging Face 上数据集微调，可使用 `dataset_name` 参数指定数据集名称。

`ds_config.json` 可使用 [这里的示例](https://github.com/fauxpilot/fauxpilot/issues/62#issuecomment-1304681430):

```json
{
    "zero_optimization": {
        "stage": 2,
        "offload_optimizer": {
            "device": "cpu",
            "pin_memory": true
        },
        "allgather_partitions": true,
        "allgather_bucket_size": 2e8,
        "overlap_comm": true,
        "reduce_scatter": true,
        "reduce_bucket_size": 2e8,
        "contiguous_gradients": true
    },
    "gradient_accumulation_steps": "auto",
    "gradient_clipping": "auto",
    "steps_per_print": 2000,
    "train_batch_size": "auto",
    "train_micro_batch_size_per_gpu": "auto",
    "wall_clock_breakdown": false
}
```

### 使用多卡微调

`num_gpus` 参数可以指定使用的 GPU 数量。

如使用多个 GPU 时遇以下报错：

```text
Pytorch "NCCL error": unhandled system error, NCCL version 2.4.8"
```

可参照 [这里](https://stackoverflow.com/questions/61075390/pytorch-nccl-error-unhandled-system-error-nccl-version-2-4-8#) 在 `run_clm.py` 中加入 `INFO` 级别调试信息，如：

```diff
 from transformers.utils import check_min_version, send_example_telemetry
 from transformers.utils.versions import require_version

+os.environ["NCCL_DEBUG"] = "INFO"

 # Will error if the minimal version of Transformers is not installed. Remove at your own risks.
 check_min_version("4.21.0")
```

查看详细报错信息。

如看到具体 [报错](https://github.com/NVIDIA/nccl/issues/290) 为：

```text
NCCL WARN Call to posix_fallocate failed : No space left on device
```

可参照 PaddlePaddle 的 [解决方式](https://github.com/PaddlePaddle/Paddle/pull/28484/files)，在 `run_clm.py` 中加入：

```diff
 from transformers.utils import check_min_version, send_example_telemetry
 from transformers.utils.versions import require_version

 os.environ["NCCL_DEBUG"] = "INFO"
+os.environ['NCCL_SHM_DISABLE'] = str(1)

 # Will error if the minimal version of Transformers is not installed. Remove at your own risks.
 check_min_version("4.21.0")
```

### 指定 GPU

要指定 GPU 时，可参照 [deepspeed多机多卡训练踏过的坑](https://zhuanlan.zhihu.com/p/624223085) 中内容，去掉 `num_gpus` 和 `num_nodes` 参数，使用 `--include localhost:1,2` 形式配置单机多卡。

## 微调耗时评估

使用一个 Tesla P40（24G VRAM）微调 CodeGen-350M-multi 模型，显存使用 23G 左右，微调时间：

1. 40w 行邮箱数据，24M 训练数据集，大约耗时 10 分钟
2. 300 个 java 文件，75M 训练数据集，大约耗时 1 小时 20 分钟

在 https://github.com/fauxpilot/fauxpilot/discussions/74#discussioncomment-3798458 中，FauxPilot 作者也给出了他们微调 16B 模型的资源需求情况：

> As a warning, fine-tuning or training large models (like CodeGen 16B) takes a lot of GPU resources – we fine-tuned a 16B model on Verilog code, and it took 3xA100 GPUs with 80GB of VRAM each running for six days to do one pass over the 400MB dataset.

## 微调后验证

模型微调之后，可通过如下 Python 代码进行验证：

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
tokenizer = AutoTokenizer.from_pretrained("/path/to/codegen-350M-multi-finetune")
model = AutoModelForCausalLM.from_pretrained("/path/to/codegen-350M-multi-finetune")

text = "def qucik_sort"
input_ids = tokenizer(text, return_tensors="pt").input_ids

generated_ids = model.generate(input_ids, max_length=128)
print(tokenizer.decode(generated_ids[0], skip_special_tokens=True))
```

在 `text` 中放入提示词，观察 `print` 输出的结果，是否学习到了训练数据中的内容。

# 模型转换

在通过上面的 Python 代码验证微调后的模型能力时，可以感受到需要的时间还是很长的，这个时间长到无法满足在 IDE 中即时补全代码的需求。

为了解决这个问题，FauxPilot 的作者使用了 [线性代数的方法](https://gist.github.com/moyix/7896575befbe1b99162ccfec8d135566)，通过 [gist 上的 codegen_gptj_convert.py](https://gist.github.com/moyix/0f37da9c21c4ddfa0ab39ddad1639db4) 或 [仓库中的 codegen_gptj_convert.py](https://github.com/fauxpilot/fauxpilot/blob/main/converter/codegen_gptj_convert.py) 转换脚本，将 CodeGen 模型转换为了 [GPT-J](https://github.com/kingoflolz/mesh-transformer-jax#gpt-j-6b) 模型。

之所以转换成 GPT-J 模型，是因为这两个模型在架构上有 99.9% 的相似，并且 GPT-J 在推理加速引擎 [FasterTransformer](https://github.com/NVIDIA/FasterTransformer/) 的 [支持列表](https://github.com/NVIDIA/FasterTransformer/#support-matrix) 中。这也是我们会发现在使用 FauxPilot 时，是去作者自己的 Hugging Face 模型仓库中下载转换后的模型（如 https://huggingface.co/moyix/codegen-350M-multi-gptj ），而不是直接使用 Salesforce 发布的原始模型的原因。

原始的 CodeGen 模型需要 12 秒生成 128 个 token，经过推理加速后，在一个 A6000 GPU 上可以将耗时缩短到 5.7 秒，并且使用多 GPU 还有进一步加速的可能。

可通过如下步骤，将我们微调好的 CodeGen 模型，转换为可在 FauxPilot Server 中使用的形式。

## codegen_gptj_convert.py

先使用 [codegen_gptj_convert.py](https://github.com/fauxpilot/fauxpilot/blob/main/converter/codegen_gptj_convert.py) 脚本，将 Salesforce CodeGen 模型转换为 GPT-J 模型。

转换本地微调后的模型时，需修改脚本内容，去掉 `choices=CODEGEN_PRETRAINED_MODEL_ARCHIVE_LIST, default='Salesforce/codegen-350M-multi',` 行：

```diff
 parser.add_argument('--code_model',
-                    choices=CODEGEN_PRETRAINED_MODEL_ARCHIVE_LIST, default='Salesforce/codegen-350M-multi',
                     help='which SalesForce model to convert'
                     )
```

使用下面命令执行转换：

```bash
python /path/to/codegen_gptj_convert.py \
--code_model /path/to/codegen-350M-multi-finetune \
/path/to/codegen-350M-multi-finetune-gptj
```

转换时需要 `code_model` 路径内的 `pytorch_model.bin` 和 `config.json` 文件，转换后模型仍为一个 `pytorch_model.bin` 文件，但内容发生了变化，配套的 `config.json` 文件也不一样了。

> 脚本用法可参照 [download_and_convert_model.sh](https://github.com/fauxpilot/fauxpilot/blob/main/converter/download_and_convert_model.sh)。

## triton_config_gen.py

转换后的 GPT-J 模型在经过 FasterTransformer 加速后，最终会部署到 [Triton Inference Server](https://github.com/triton-inference-server/backend) 中。需先使用 [triton_config_gen.py](https://github.com/fauxpilot/fauxpilot/blob/main/converter/triton_config_gen.py) 脚本来生成 Triton 需使用的配置文件。

但在使用 FauxPilot 仓库中的这个脚本生成 CodeGen-350M-multi 微调后模型的配置时，`vocab_size` 的算法需要进行调整，否则使用转换后的模型时会出现补全的都是混乱内容的情况：

```diff
 # Vocab size *sometimes* gets rounded up to a multiple of 1024
-params['vocab_size'] = tokenizer.vocab_size+len(tokenizer.get_added_vocab())  # round_up(tokenizer.vocab_size, 1024)
+params['vocab_size'] = round_up(tokenizer.vocab_size, 1024)
 params['start_id'] = tokenizer.eos_token_id
```

调整脚本后执行如下命令生成配置：

```bash
python /path/to/triton_config_gen.py -n 2 \
--tokenizer /path/to/codegen-350M-multi-finetune \
--hf_model_dir /path/to/codegen-350M-multi-finetune-gptj \
--model_store /path/to/fauxpilot/models \
--rebase /model
```

> `triton_config_gen.py` 脚本需与 [config_template.pbtxt](https://github.com/fauxpilot/fauxpilot/blob/main/converter/config_template.pbtxt) 模板文件放在相同路径下共同使用。

其中：

- `-n` 为最终运行时需要使用的 GPU 数量
- `--tokenizer` 指定微调后的 CodeGen 模型路径（因为使用 `codegen_gptj_convert.py` 脚本转换得到的 GPT-J 模型路径中只有 `pytorch_model.bin` 和 `config.json` 两个文件）
- `--hf_model_dir` 指定转换后的 GPT-J 模型路径
- `--model_store` 指定配置文件的生成路径
- `--rebase` 用来指定将 FasterTransformer 加速后的模型文件挂载到容器里时，容器内所使用的模型文件路径。如使用 FauxPilot 提供的 Docker Compose 方式启动 FauxPilot Server 服务，可保持使用 `/model` 路径不变

以上面的命令为例，执行成功后会在 `/path/to/fauxpilot/models/codegen-350M-multi-finetune-gptj-2gpu/fastertransformer` 路径下生成一个 `config.pbtxt` 文件。

## huggingface_gptj_convert.py

使用 [huggingface_gptj_convert.py](https://github.com/fauxpilot/fauxpilot/blob/main/converter/huggingface_gptj_convert.py) 脚本将 GPT-J 模型转换成 FasterTransformer 格式：

```bash
python /path/to/huggingface_gptj_convert.py \
-in_file /path/to/codegen-350M-multi-finetune-gptj \
-saved_dir /path/to/fauxpilot/models/codegen-350M-multi-finetune-gptj-2gpu/fastertransformer/1 \
-infer_gpu_num 2
```

其中：

- `in_file` 为转换成 GPT-J 格式的微调后模型文件路径
- `saved_dir` 为上面 `triton_config_gen.py` 脚本生成配置文件的路径加一层 `/1`
- `infer_gpu_num` 为推理所使用的 GPU 数量，注意需与 `triton_config_gen.py` 脚本的 `-n` 参数值一致

## All in one 脚本

可使用 [convert_model.sh](https://github.com/AlphaHinex/fauxpilot/blob/350m/converter/convert_model.sh) 脚本完成上述所有转换工作，用法为：

```bash
./convert_model.sh codegen-350M-multi-finetune 2
```

将微调后的模型文件路径放至该脚本路径内，并将该脚本与其他转换所需脚本和模板文件放置在相同路径下。第一个参数为微调后的模型文件路径，第二个参数为推理时需使用的 GPU 数量。

该脚本内容如下：

```bash
#!/bin/bash

MODEL=${1}
NUM_GPUS=${2}

echo "Converting model ${MODEL} with ${NUM_GPUS} GPUs"

python3 codegen_gptj_convert.py --code_model ./${MODEL} ${MODEL}-gptj

rm -rf ./models/${MODEL}-${NUM_GPUS}gpu

python3 triton_config_gen.py -n ${NUM_GPUS} --tokenizer ./${MODEL} --hf_model_dir ${MODEL}-gptj --model_store ./models --rebase /model

python3 huggingface_gptj_convert.py -in_file ${MODEL}-gptj -saved_dir ./models/${MODEL}-gptj-${NUM_GPUS}gpu/fastertransformer/1 -infer_gpu_num ${NUM_GPUS}

rm -rf ${MODEL}-gptj
```

执行成功后，会在脚本所在位置的 `models/codegen-350M-multi-finetune-gptj-2gpu` 下获得转换好的模型文件。

## 替换部分文件

实际使用时发现，经过上述过程转换后的模型在 FauxPilot Server 中使用时，会出现补全的代码内容都是混乱的无法辨识内容，经试验发现需要使用 FauxPilot 使用的原始模型中的部分文件替换通过上述方式转换之后的 FasterTransformer 模型文件。以 `CodeGen-350M-multi` 为例，需替换的文件为：

```text
model.lm_head.bias.bin
model.lm_head.weight.bin
model.wte.bin
```

可在 https://huggingface.co/moyix/codegen-350M-multi-gptj/tree/main 对应 GPU 数量的 `zst` 压缩文件中，提取上述文件（或使用 Salesforce 原始模型通过上述过程转换得到，不微调直接转换时这三个文件内容应该是正确的，可以在 FauxPilot Server 中正常使用），并覆盖自行转换出的文件，如：


```bash
cp /path/to/origin/codegen-350M-multi-2gpu/fastertransformer/1/2-gpu/model.lm_head.bias.bin /path/to/fauxpilot/models/codegen-350M-multi-finetune-gptj-2gpu/fastertransformer/1/2-gpu/model.lm_head.bias.bin
cp /path/to/origin/codegen-350M-multi-2gpu/fastertransformer/1/2-gpu/model.lm_head.weight.bin /path/to/fauxpilot/models/codegen-350M-multi-finetune-gptj-2gpu/fastertransformer/1/2-gpu/model.lm_head.weight.bin
cp /path/to/origin/codegen-350M-multi-2gpu/fastertransformer/1/2-gpu/model.wte.bin /path/to/fauxpilot/models/codegen-350M-multi-finetune-gptj-2gpu/fastertransformer/1/2-gpu/model.wte.bin
```

## 模型转换过程最终输出文件树

```bash
$ pwd
/path/to/fauxpilot/models/codegen-350M-multi-finetune-gptj-2gpu
$ tree -L 4
.
└── fastertransformer
    ├── 1
    │   └── 2-gpu
    │       ├── config.ini
    │       ├── model.final_layernorm.bias.bin
    │       ├── model.final_layernorm.weight.bin
    │       ├── model.layers.0.attention.dense.weight.0.bin
    │       ├── model.layers.0.attention.query_key_value.weight.0.bin
    │       ├── model.layers.0.input_layernorm.bias.bin
    │       ├── model.layers.0.input_layernorm.weight.bin
    │       ├── model.layers.0.mlp.dense_4h_to_h.bias.bin
    │       ├── model.layers.0.mlp.dense_4h_to_h.weight.0.bin
    │       ├── model.layers.0.mlp.dense_h_to_4h.bias.0.bin
    │       ├── model.layers.0.mlp.dense_h_to_4h.weight.0.bin
...
    │       ├── model.layers.9.attention.dense.weight.0.bin
    │       ├── model.layers.9.attention.query_key_value.weight.0.bin
    │       ├── model.layers.9.input_layernorm.bias.bin
    │       ├── model.layers.9.input_layernorm.weight.bin
    │       ├── model.layers.9.mlp.dense_4h_to_h.bias.bin
    │       ├── model.layers.9.mlp.dense_4h_to_h.weight.0.bin
    │       ├── model.layers.9.mlp.dense_h_to_4h.bias.0.bin
    │       ├── model.layers.9.mlp.dense_h_to_4h.weight.0.bin
    │       ├── model.lm_head.bias.bin
    │       ├── model.lm_head.weight.bin
    │       └── model.wte.bin
    └── config.pbtxt
```

# 新模型使用

在 FauxPilot 中使用微调并转换后的新模型就比较简单了，按照 [GitHub Copilot 开源替代品 —— FauxPilot](https://alphahinex.github.io/2023/06/18/fauxpilot/) 中方式准备好运行环境，修改 `.env` 文件中的 `MODEL_DIR` 为新模型路径即可，如 `/path/to/fauxpilot/models/codegen-350M-multi-finetune-gptj-2gpu`。如本文中的示例可使用的 `.env` 文件内容如下：

```.env
NUM_GPUS=2
GPUS=0,1
API_EXTERNAL_PORT=5000
TRITON_HOST=triton
TRITON_PORT=8001
MODEL=codegen-350M-multi
MODEL_DIR=/path/to/fauxpilot/models/codegen-350M-multi-finetune-gptj-2gpu
HF_CACHE_DIR=/path/to/fauxpilot/.hf_cache
```

# 附录

本文中所使用的修改后的脚本，及 All in one 转换脚本，可在 https://github.com/AlphaHinex/fauxpilot 中获取。

# 参考资料

- [How to optimize CodeGen for my code before launching FauxPilot](https://github.com/fauxpilot/fauxpilot/issues/62)
- [Guide on how to train new models on an existing codebase?](https://github.com/fauxpilot/fauxpilot/discussions/74)
- [How to convert the SalesForce CodeGen models to GPT-J](https://gist.github.com/moyix/7896575befbe1b99162ccfec8d135566)
- [Convert a SalesForce CodeGen model’s weights to plain GPT-J](https://gist.github.com/moyix/0f37da9c21c4ddfa0ab39ddad1639db4)
- [大模型的好伙伴，浅析推理加速引擎FasterTransformer](https://zhuanlan.zhihu.com/p/626008090)