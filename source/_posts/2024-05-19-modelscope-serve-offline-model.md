---
id: modelscope-serve-offline-model
title: "使用 modelscope 在离线环境部署模型服务关键点"
description: "五个点很关键"
date: 2024.05.19 10:34
categories:
    - Python
tags: [Python]
keywords: modelscope, offline, model, server
cover: /contents/modelscope-serve-offline-model/03-swagger.png
---

在 ModelScope 的 [本地启动服务](https://modelscope.cn/docs/本地启动服务) 文档中，介绍了使用 `modelscope server` 发布模型服务的方法。
简单来说，就是执行如下命令：

```bash
modelscope server --model_id=qwen/Qwen-7B-Chat --revision=v1.0.5
```

但在离线环境中使用上述命令时，可能会遇到各种问题。本文以使用 `modelscope` 最近的（2024-04-27）发布版本 [v1.14.0](https://github.com/modelscope/modelscope/releases/tag/v1.14.0) 为例，介绍在离线环境中部署模型服务的关键点。

TL;DR
======

共有如下五个关键点需要注意：

1. 模型文件的路径中必须包含 `.mdl`、`.msc` 和 `.mv` 三个文件；
1. 需修改 [modelscope/hub
/file_download.py](https://github.com/modelscope/modelscope/blob/v1.14.0/modelscope/hub/file_download.py#L39)，将 `local_files_only: Optional[bool] = False,` 改为 `local_files_only: Optional[bool] = True,`；
1. 需修改 [modelscope/utils/input_output.py](https://github.com/modelscope/modelscope/blob/v1.14.0/modelscope/utils/input_output.py#L81)，将 `model=model_id,` 修改为 `model=cfg.filename.replace('/configuration.json', ''),`；
1. 需修改 [modelscope/utils/pipeline_schema.json](https://github.com/modelscope/modelscope/blob/v1.14.0/modelscope/utils/pipeline_schema.json#L3835)，将 [倒数第二行](https://github.com/modelscope/modelscope/pull/859) 的 `},` 改为 `}`；
1. 启动命令中必须指定 `--revision` 参数，如无值可设置为 `--revision=`。

> 下载模型文件若直接通过 `git clone` 克隆模型仓库地址，则不包含必须的三个 `.m*` 文件；需使用 `modelscope` 提供的 `snapshot_download` 方法下载：
> ```bash
> python -c "from modelscope import snapshot_download; snapshot_download('qwen/Qwen1.5-7B-Chat', cache_dir='qwen1.5-7b-chat')"
> ```

> **注意：以上代码修改内容在 v1.14.0 版本 modelscope 库中验证有效，版本不同时可能需要根据实际情况做出调整。**

在线 Notebook 环境模拟验证
========================

接下来使用魔搭社区提供的在线 CPU [Notebook 环境](https://modelscope.cn/my/mynotebook/preset) 对离线环境部署模型服务进行模拟验证。

![notebook](/contents/modelscope-serve-offline-model/01-notebook.png)

启动 Notebook 后在 Launcher 中打开一个 Terminal：

![terminal](/contents/modelscope-serve-offline-model/02-terminal.png)

检查 modelscope 版本
--------------------

```bash
$ pip show modelscope
Name: modelscope
Version: 1.14.0
Summary: ModelScope: bring the notion of Model-as-a-Service to life.
Home-page: https://github.com/modelscope/modelscope
Author: ModelScope team
Author-email: contact@modelscope.cn
License: Apache License 2.0
Location: /opt/conda/lib/python3.10/site-packages
Requires: addict, attrs, datasets, einops, filelock, gast, huggingface-hub, numpy, oss2, pandas, Pillow, pyarrow, python-dateutil, pyyaml, requests, scipy, setuptools, simplejson, sortedcontainers, tqdm, urllib3, yapf
Required-by: adaseq, ms-swift
```

下载模型文件
----------

为方便演示，下载一个小模型：

```bash
python -c "from modelscope import snapshot_download; snapshot_download('damo/nlp_structbert_word-segmentation_chinese-base', cache_dir='cache')"
```

因未指定下载版本，下载时会有类似如下提示：

```bash
WARNING - Model revision not specified, use revision: v1.0.3
```

记住这个版本号以备后续使用。

确认 `.m*` 文件存在：

```bash
$ ls -al cache/damo/nlp_structbert_word-segmentation_chinese-base/.m*
-rw-r--r-- 1 root root  73  5月 18 21:58 cache/damo/nlp_structbert_word-segmentation_chinese-base/.mdl
-rw------- 1 root root 596  5月 18 21:58 cache/damo/nlp_structbert_word-segmentation_chinese-base/.msc
-rw-r--r-- 1 root root  36  5月 18 21:58 cache/damo/nlp_structbert_word-segmentation_chinese-base/.mv
```

设置 host 模拟离线环境
----------------------

```bash
echo '0.0.0.0 www.modelscope.cn' >> /etc/hosts
```

验证默认情况下无法启动服务
------------------------

```bash
MODELSCOPE_CACHE=/mnt/workspace/cache modelscope server --model_id=damo/nlp_structbert_word-segmentation_chinese-base --revision=v1.0.3
```

会有如下报错信息：

```bash
requests.exceptions.ConnectionError: HTTPSConnectionPool(host='www.modelscope.cn', port=443): Max retries exceeded with url: /api/v1/models/damo/nlp_structbert_word-segmentation_chinese-base/revisions (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x7fefa2dfc2e0>: Failed to establish a new connection: [Errno 111] Connection refused'))
```

修改 file_download.py
--------------------

```bash
$ cat /opt/conda/lib/python3.10/site-packages/modelscope/hub/file_download.py|grep "local_files_only: Optional\[bool\]"
    local_files_only: Optional[bool] = False,
```

```bash
$ sed -i 's/local_files_only: Optional\[bool\] = False,/local_files_only: Optional\[bool\] = True,/' /opt/conda/lib/python3.10/site-packages/modelscope/hub/file_download.py
```

```bash
$ cat /opt/conda/lib/python3.10/site-packages/modelscope/hub/file_download.py|grep "local_files_only: Optional\[bool\]"
    local_files_only: Optional[bool] = True,
```

修改 input_output.py
--------------------

```bash
$ cat /opt/conda/lib/python3.10/site-packages/modelscope/utils/input_output.py|grep "model=model_id,"
    model=model_id,
```

```bash
$ sed -i "s#model=model_id,#model=cfg.filename.replace('/configuration.json', ''),#" /opt/conda/lib/python3.10/site-packages/modelscope/utils/input_output.py
```

```bash
$ cat /opt/conda/lib/python3.10/site-packages/modelscope/utils/input_output.py|grep "model="
    model=cfg.filename.replace('/configuration.json', ''),
```

修改 pipeline_schema.json
------------------------

```bash
$ cat /opt/conda/lib/python3.10/site-packages/modelscope/utils/pipeline_schema.json|tail -n 2
    },
}
```

```bash
$ line_num=$(($(wc -l < /opt/conda/lib/python3.10/site-packages/modelscope/utils/pipeline_schema.json) - 1))
$ sed -i "${line_num}s/},/}/" /opt/conda/lib/python3.10/site-packages/modelscope/utils/pipeline_schema.json
```

```bash
$ cat /opt/conda/lib/python3.10/site-packages/modelscope/utils/pipeline_schema.json|tail -n 2
    }
}
```

启动服务
--------

```bash
$ MODELSCOPE_CACHE=/mnt/workspace/cache modelscope server --model_id=damo/nlp_structbert_word-segmentation_chinese-base --revision=v1.0.3
...
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

点击终端中的 `http://0.0.0.0:8000`，会在浏览器中打开一个使用了代理域名地址的新 tab 页，后面加上 `docs` 即可打开 Swagger 页面：

![swagger](/contents/modelscope-serve-offline-model/03-swagger.png)
