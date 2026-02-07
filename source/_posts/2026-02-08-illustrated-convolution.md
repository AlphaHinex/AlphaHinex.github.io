---
id: illustrated-convolution
title: "【转】【图解AI：动图】各种类型的卷积，你认全了吗？"
description: "直观理解各类卷积的计算过程及其区别"
date: 2026.02.08 10:26
categories:
    - AI
tags: [AI, CNN]
keywords: 卷积, Convolution, 反卷积, 可分离卷积, 分组卷积, 空洞卷积, 深度可分离卷积, 扁平卷积, 混洗分组卷积, 二维卷积, 三维卷积, 1x1卷积, 转置卷积
cover: /contents/illustrated-convolution/00-cover.jpg
---

- 原文地址：https://my.oschina.net/u/876354/blog/3064227
- 原文作者：[雪饼](https://my.oschina.net/u/876354)

![](https://alphahinex.github.io/contents/illustrated-convolution/00-cover.jpg)

<span style="color:red">卷积（convolution）</span>是深度学习中非常有用的计算操作，主要用于提取图像的特征。在近几年来深度学习快速发展的过程中，卷积从标准卷积演变出了反卷积、可分离卷积、分组卷积等各种类型，以适应于不同的场景，接下来一起来认识它们吧。

# <span style="color:red">一、卷积的基本属性</span>

**卷积核（Kernel）**：卷积操作的感受野，直观理解就是一个滤波矩阵，普遍使用的卷积核大小为3×3、5×5等；

**步长（Stride）**：卷积核遍历特征图时每步移动的像素，如步长为1则每次移动1个像素，步长为2则每次移动2个像素（即跳过1个像素），以此类推；

**填充（Padding）**：处理特征图边界的方式，一般有两种，一种是对边界外完全不填充，只对输入像素执行卷积操作，这样会使输出特征图的尺寸小于输入特征图尺寸；另一种是对边界外进行填充（一般填充为0），再执行卷积操作，这样可使输出特征图的尺寸与输入特征图的尺寸一致；

**通道（Channel）**：卷积层的通道数（层数）。

如下图是一个卷积核（kernel）为3×3、步长（stride）为1、填充（padding）为1的二维卷积：

![kernel](https://alphahinex.github.io/contents/illustrated-convolution/01-kernel.gif)

# <span style="color:red">二、卷积的计算过程</span>

卷积的计算过程非常简单，当卷积核在输入图像上扫描时，将卷积核与输入图像中对应位置的数值逐个相乘，最后汇总求和，就得到该位置的卷积结果。不断移动卷积核，就可算出各个位置的卷积结果。如下图：

![compute](https://alphahinex.github.io/contents/illustrated-convolution/02-compute.jpg)

# <span style="color:red">三、卷积的各种类型</span>

卷积现在已衍生出了各种类型，包括标准卷积、反卷积、可分离卷积、分组卷积等等，下面逐一进行介绍。

## <span style="color:red">1、标准卷积</span>

### （1）二维卷积（单通道卷积版本）（2D Convolution: the single channel version）

只有一个通道的卷积。

如下图是一个卷积核（kernel）为3×3、步长（stride）为1、填充（padding）为0的卷积：

![2d-conv](https://alphahinex.github.io/contents/illustrated-convolution/03-2d-conv.gif)

### （2）二维卷积（多通道卷积版本）（2D Convolution: the multi-channel version）

拥有多个通道的卷积，例如处理彩色图像时，分别对R, G, B这3个层处理的3通道卷积，如下图：

![2d-conv-multi-01](https://alphahinex.github.io/contents/illustrated-convolution/04-2d-conv-multi-01.gif)

再将三个通道的卷积结果进行合并（一般采用元素相加），得到卷积后的结果，如下图：

![2d-conv-multi-02](https://alphahinex.github.io/contents/illustrated-convolution/05-2d-conv-multi-02.gif)

### （3）三维卷积（3D Convolution）

卷积有三个维度（高度、宽度、通道），沿着输入图像的3个方向进行滑动，最后输出三维的结果，如下图：

![3d-conv](https://alphahinex.github.io/contents/illustrated-convolution/06-3d-conv.jpg)

### （4）1x1卷积（1 x 1 Convolution）

当卷积核尺寸为1x1时的卷积，也即卷积核变成只有一个数字。如下图：

![1x1-conv](https://alphahinex.github.io/contents/illustrated-convolution/07-1x1-conv.jpg)

从上图可以看出，1x1卷积的作用在于能有效地减少维度，降低计算的复杂度。1x1卷积在GoogLeNet网络结构中广泛使用。

## <span style="color:red">2、反卷积（转置卷积）（Deconvolution / Transposed Convolution）</span>

卷积是对输入图像提取出特征（可能尺寸会变小），而所谓的“反卷积”便是进行相反的操作。但这里说是“反卷积”并不严谨，因为并不会完全还原到跟输入图像一样，一般是还原后的尺寸与输入图像一致，主要用于向上采样。从数学计算上看，“反卷积”相当于是将卷积核转换为稀疏矩阵后进行转置计算，因此，也被称为“转置卷积”

如下图，在2x2的输入图像上应用步长为1、边界全0填充的3x3卷积核，进行转置卷积（反卷积）计算，向上采样后输出的图像大小为4x4

![deconv](https://alphahinex.github.io/contents/illustrated-convolution/08-deconv.gif)

## <span style="color:red">3、空洞卷积（膨胀卷积）（Dilated Convolution / Atrous Convolution）</span>

为扩大感受野，在卷积核里面的元素之间插入空格来“膨胀”内核，形成“空洞卷积”（或称膨胀卷积），并用膨胀率参数L表示要扩大内核的范围，即在内核元素之间插入L-1个空格。当L=1时，则内核元素之间没有插入空格，变为标准卷积。

如下图为膨胀率L=2的空洞卷积：

![dilated-conv](https://alphahinex.github.io/contents/illustrated-convolution/09-dilated-conv.gif)

## <span style="color:red">4、可分离卷积（Separable Convolutions）</span>

### （1）空间可分离卷积（Spatially Separable Convolutions）

空间可分离卷积是将卷积核分解为两项独立的核分别进行操作。一个3x3的卷积核分解如下图：

![spatial-separable-conv](https://alphahinex.github.io/contents/illustrated-convolution/10-spatial-separable-conv.jpg)

分解后的卷积计算过程如下图，先用3x1的卷积核作横向扫描计算，再用1x3的卷积核作纵向扫描计算，最后得到结果。采用可分离卷积的计算量比标准卷积要少。

![spatial-separable-conv-compute](https://alphahinex.github.io/contents/illustrated-convolution/11-spatial-separable-conv-compute.jpg)

### （2）深度可分离卷积（Depthwise Separable Convolutions）

深度可分离卷积由两步组成：深度卷积和1x1卷积。

首先，在输入层上应用深度卷积。如下图，使用3个卷积核分别对输入层的3个通道作卷积计算，再堆叠在一起。

![depthwise-separable-conv-01](https://alphahinex.github.io/contents/illustrated-convolution/12-depthwise-separable-conv-01.jpg)

再使用1x1的卷积（3个通道）进行计算，得到只有1个通道的结果

![depthwise-separable-conv-02](https://alphahinex.github.io/contents/illustrated-convolution/13-pointwise-separable-conv-02.jpg)

重复多次1x1的卷积操作（如下图为128次），则最后便会得到一个深度的卷积结果。

![depthwise-separable-conv-03](https://alphahinex.github.io/contents/illustrated-convolution/14-depthwise-separable-conv-03.jpg)

完整的过程如下：

![depthwise-separable-conv](https://alphahinex.github.io/contents/illustrated-convolution/15-depthwise-separable-conv.jpg)

## <span style="color:red">5、扁平卷积（Flattened convolutions）</span>

扁平卷积是将标准卷积核拆分为3个1x1的卷积核，然后再分别对输入层进行卷积计算。这种方式，跟前面的“空间可分离卷积”类似，如下图：

![flattened-conv](https://alphahinex.github.io/contents/illustrated-convolution/16-flattened-conv.jpg)

## <span style="color:red">6、分组卷积（Grouped Convolution）</span>

2012年，AlexNet论文中最先提出来的概念，当时主要为了解决GPU显存不足问题，将卷积分组后放到两个GPU并行执行。

在分组卷积中，卷积核被分成不同的组，每组负责对相应的输入层进行卷积计算，最后再进行合并。如下图，卷积核被分成前后两个组，前半部分的卷积组负责处理前半部分的输入层，后半部分的卷积组负责处理后半部分的输入层，最后将结果合并组合。

![grouped-conv](https://alphahinex.github.io/contents/illustrated-convolution/17-grouped-conv.jpg)

## <span style="color:red">7、混洗分组卷积（Shuffled Grouped Convolution）</span>

在分组卷积中，卷积核被分成多个组后，输入层卷积计算的结果仍按照原先的顺序进行合并组合，这就阻碍了模型在训练期间特征信息在通道组之间流动，同时还削弱了特征表示。而混洗分组卷积，便是将分组卷积后的计算结果混合交叉在一起输出。

如下图，在第一层分组卷积（GConv1）计算后，得到的特征图先进行拆组，再混合交叉，形成新的结果输入到第二层分组卷积（GConv2）中：

![shuffled-grouped-conv](https://alphahinex.github.io/contents/illustrated-convolution/18-shuffled-grouped-conv.jpg)

欢迎关注本人的微信公众号“大数据与人工智能Lab”（BigdataAILab），获取更多信息

![qrcode](https://alphahinex.github.io/contents/illustrated-convolution/19-qrcode.jpg)
