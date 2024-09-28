---
id: compare-pdfs
title: "比较两个相似 PDF 文件的内容差异"
description: "本文给出两个比较相似 PDF 文件内容差异的方法"
date: 2024.09.28 10:34
categories:
    - Others
tags: [Python, PDF]
keywords: pdf, diff, compare, PyMuPDF, difflib, DiffPDF
cover: /contents/compare-pdfs/diffpdf.png
---

本文给出两个比较相似 PDF 文件内容差异的方法，
以 [《Understanding DeepLearning (5 August 2024)》](https://github.com/udlbook/udlbook/releases/download/4.0.4/UnderstandingDeepLearning_08_05_24_C.pdf) 
和 [《Understanding DeepLearning (28 August 2024)》](https://github.com/udlbook/udlbook/releases/download/v.4.0.4/UnderstandingDeepLearning_08_28_24_C.pdf) 
为例进行对比。


## PyMuPDF + difflib

此方法引自 [Python对比PDF文件并生成对比文件](https://www.jianshu.com/p/f0a02743e580)。

先用 [PyMuPDF](https://github.com/pymupdf/PyMuPDF) 提取 PDF 文件中的文字内容，再通过 [difflib](https://github.com/python/cpython/blob/main/Lib/difflib.py) 模块输出差异内容。

安装依赖：

```bash
pip install PyMuPDF
```

将以下代码保存至 `compare_diff.py`：

``` python
import os

file1 = input("请输入第一个pdf文件路径：")
file2 = input("请输入第二个pdf文件路径：")

# 使用PyMuPDF库打开pdf文件
import pymupdf

doc1 = pymupdf.open(file1)
doc2 = pymupdf.open(file2)

# 获取pdf文件中的文本内容
text1 = ""
text2 = ""

for page in doc1:
    text1 += page.get_text()

for page in doc2:
    text2 += page.get_text()

# 对比文本内容
if text1 == text2:
    print("两个pdf文件内容相同")
else:
    print("两个pdf文件内容不同")

# 生成对比文件
import difflib

# 将文本内容转换为列表
text1_lines = text1.splitlines()
text2_lines = text2.splitlines()

# 对比文本内容
d = difflib.Differ()
diff = d.compare(text1_lines, text2_lines)

# 生成有标注的对比文件
diff_html = difflib.HtmlDiff().make_file(text1_lines, text2_lines)
file1_path = os.path.dirname(file1)
with open(os.path.join(file1_path, "diff.html"), "w", encoding='utf-8') as f:
    f.write(diff_html)

print("对比文件已生成")
```

```bash
$ python3 compare_diff.py
请输入第一个pdf文件路径：/Users/alphahinex/Desktop/compare_pdf/UnderstandingDeepLearning_08_05_24_C.pdf
请输入第二个pdf文件路径：/Users/alphahinex/Desktop/compare_pdf/UnderstandingDeepLearning_08_28_24_C.pdf
两个pdf文件内容不同
对比文件已生成
```

打开生成的 `diff.html` 文件，可以看到两个 PDF 文件的内容差异：

![difflib](/contents/compare-pdfs/difflib.png)


## DiffPDF

[DiffPDF](http://www.qtrac.eu/diffpdf.html) 老版本是 [开源软件](http://www.qtrac.eu/diffpdf-foss.html)，目前为商用版，有 20 天试用期，提供了更多功能以及对多核处理器更好的支持。

> 老版本目前官网不再提供，可以从 [这里](https://soft.rubypdf.com/software/diffpdf) 找到一些老版本的源码和 Windows 版本可执行文件。

> 参照源码包中 README 内容，可以编译其他系统版本。

![diffpdf](/contents/compare-pdfs/diffpdf.png)


## 相关链接

- https://pymupdf.readthedocs.io/en/latest/
- https://docs.python.org/3/library/difflib.html
- https://github.com/vslavik/diff-pdf
