---
id: rotate-captcha
title: "识别旋转验证码图片角度"
description: "Windows CPU 可用"
date: 2024.05.12 10:26
categories:
    - Python
tags: [Python, CNN]
keywords: rotate captcha, windows, cpu, RotNet, PyTorch
cover: /contents/covers/rotate-captcha.png
---

代码库
=====

[简单聊聊旋转验证码攻防](https://www.52pojie.cn/thread-1754224-1-1.html) 中介绍了一些旋转验证码的攻防思路，并提供了 [rotate-captcha-crack](https://github.com/Starry-OvO/rotate-captcha-crack) 实现。

README 文档的 [Prepare](https://github.com/Starry-OvO/rotate-captcha-crack?tab=readme-ov-file#prepare) 部分提到需要支持 `CUDA10+` 的设备（GPU），经实测，在 Windows CPU 环境下也可使用，且性能基本满足需求。

调整为 CPU 版本
--------------

为在 Windows CPU 环境执行 `test_captcha.py` 脚本验证旋转角度预测效果，以及通过 `server.py` 发布 HTTP 服务，需对仓库中代码进行以下 [调整](https://github.com/Starry-OvO/rotate-captcha-crack/compare/master...AlphaHinex:rotate-captcha-crack:cpu)：

```diff
diff --git a/rotate_captcha_crack/common.py b/rotate_captcha_crack/common.py
index 00d3a3a..683f217 100644
--- a/rotate_captcha_crack/common.py
+++ b/rotate_captcha_crack/common.py
@@ -7,5 +7,6 @@ if sys.version_info >= (3, 11):
 else:
     import tomli as tomllib  # noqa: F401
 
-device = torch.device('cuda')
+# device = torch.device('cuda')
+device = torch.device('cpu')
 torch.backends.cudnn.benchmark = True
diff --git a/server.py b/server.py
index 36266cf..5620bcf 100644
--- a/server.py
+++ b/server.py
@@ -8,6 +8,7 @@ from aiohttp import web
 from PIL import Image
 
 from rotate_captcha_crack.common import device
+from rotate_captcha_crack.const import DEFAULT_CLS_NUM
 from rotate_captcha_crack.logging import RCCLogger
 from rotate_captcha_crack.model import RotNetR, WhereIsMyModel
 from rotate_captcha_crack.utils import process_captcha
@@ -21,9 +22,9 @@ parser = argparse.ArgumentParser()
 parser.add_argument("--index", "-i", type=int, default=-1, help="Use which index")
 opts = parser.parse_args()
 
-model = RotNetR(cls_num=180, train=False)
+model = RotNetR(cls_num=DEFAULT_CLS_NUM, train=False)
 model_path = WhereIsMyModel(model).with_index(opts.index).model_dir / "best.pth"
-model.load_state_dict(torch.load(str(model_path)))
+model.load_state_dict(torch.load(str(model_path), map_location=torch.device('cpu')))
 model = model.to(device=device)
 model.eval()
 
diff --git a/test_captcha.py b/test_captcha.py
index 9d2453b..459a977 100644
--- a/test_captcha.py
+++ b/test_captcha.py
@@ -19,11 +19,11 @@ if __name__ == "__main__":
         model = RotNetR(cls_num=cls_num, train=False)
         model_path = WhereIsMyModel(model).with_index(opts.index).model_dir / "best.pth"
         print(f"Use model: {model_path}")
-        model.load_state_dict(torch.load(str(model_path)))
+        model.load_state_dict(torch.load(str(model_path), map_location=torch.device('cpu')))
         model = model.to(device=device)
         model.eval()
 
-        img = Image.open("datasets/tieba/1615096444.jpg")
+        img = Image.open("datasets/download.png")
         img_ts = process_captcha(img)
         img_ts = img_ts.to(device=device)
```

或直接使用已修改好的 [fork 版本](https://github.com/AlphaHinex/rotate-captcha-crack)。

Windows 环境搭建
---------------

下载 Windows 环境下的 [miniconda 安装包](https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-py39_23.11.0-2-Windows-x86_64.exe) 并做好 [镜像源配置](https://mirrors.tuna.tsinghua.edu.cn/help/anaconda/)。

在 `Anaconda Prompt(MiniConda3)` 应用中执行如下命令。

创建并激活虚拟环境：

```cmd
> conda create -n rotate python=3.10
> conda activate rotate
```

Clone CPU 版代码：

```cmd
> git clone https://github.com/AlphaHinex/rotate-captcha-crack
> cd rotate-captcha-crack
```

安装依赖：

```cmd
> pip install torch torchvision
> pip install -e .[server]
```

下载模型文件 [RotNetR.7z](https://github.com/Starry-OvO/rotate-captcha-crack/releases/download/v0.5.0/RotNetR.7z)，将解压后内容放置到代码仓库根路径的 `models` 路径下：

```cmd
> tree
...
├─rotate-captcha-crack
...
│  ├─datasets
...
│  ├─models
│  │  └─RotNetR
│  │      └─240319_11_33_53_000
│  │          └─log
...
```


测试数据集
=========

可从 https://github.com/chencchen/RotateCaptchaBreak/tree/master/data/baiduCaptcha 选择一些图片进行测试。测试图片可以放置到代码仓库根路径的 `datasets/download.png`


调用方式
=======

本地调用
-------

在 conda 环境下执行 `python test_captcha.py`，或无需激活 conda 环境，通过全路径方式调用：

```cmd
> /d/miniconda3/envs/rotate/python test_captcha.py
Use model: models/RotNetR/240319_11_33_53_000/best.pth
Predict degree: 61.8750°
```

可以验证效果：

![predict](/contents/covers/rotate-captcha.png)

RESTful API
------------

执行 `python server.py` 启动 HTTP Server 后，可以调用 RESTful API 预测旋转角度：

```cmd
> curl --request POST --url http://localhost:4396/ --form img=@datasets\download.png
{"err":{"code":0,"msg":"success"},"pred":61.875}
```

```bash
$ curl --request POST \
  --url http://localhost:4396/ \
  --header 'content-type: multipart/form-data' \
  --form img=@/Users/alphahinex/Desktop/rotate-captcha/download.png
{"err":{"code":0,"msg":"success"},"pred":61.875}
```
