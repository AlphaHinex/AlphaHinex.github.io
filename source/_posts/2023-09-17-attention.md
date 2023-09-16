---
id: attention
title: "【译】可视化神经机器翻译模型（Seq2seq 模型的注意力机制）"
description: "Visualizing A Neural Machine Translation Model (Mechanics of Seq2seq Models With Attention)"
date: 2023.09.17 10:34
categories:
    - AI
tags: [AI]
keywords: Attention, Sequence-to-sequence, deep learning, machine translation, RNN, encoder, decoder, context, hidden state, vector, embedding, feedforward neural network
cover: /contents/attention/attention.png
---

- 原文地址：https://jalammar.github.io/visualizing-neural-machine-translation-mechanics-of-seq2seq-models-with-attention/
- 作者：[Jay Alammar](https://jalammar.github.io/)

<style>
.encoder{
  color:#70BF41
}

.decoder{
  color:#B36AE2
}

.context{
  color:#F39019
}

.embedding{
  color:#00882B
}


.step_no{
  color:#5CBCE9
}

.ffnn{
  color:#EC5D57
}

.logits_output{
  color:#DF5F91
}

.img-div {
  max-width: 600px;
  margin: auto;
  font-size: 85%;
  color: #999;
}

.img-div img {
  border: 1px solid #eee;
}
</style>

**注意：** 下面的动画是视频。轻触或（使用鼠标）悬停在它们上，可获得播放控件，以便在需要时暂停。

序列到序列（Sequence-to-sequence）模型是一种深度学习模型，在诸如机器翻译、文本摘要和图像标题生成等任务中取得了许多成功。Google Translate 在 2016 年底开始在生产环境中 [使用](https://blog.google/products/translate/found-translation-more-accurate-fluent-sentences-google-translate/) 这种模型。这些模型在两篇开创性论文（[Sutskever et al., 2014](https://papers.nips.cc/paper/5346-sequence-to-sequence-learning-with-neural-networks.pdf), [Cho et al., 2014](http://emnlp2014.org/papers/pdf/EMNLP2014179.pdf)）中进行了说明。

然而我发现，充分理解并实现模型需要逐步揭示一系列相互依存的概念。我认为这些概念以视觉方式表达会更加易于理解。这就是我在本文试图做的。阅读本文需要对深度学习有一定的了解。我希望本文可以成为您阅读上面提到的论文（和本文之后引用的注意力论文）的得力助手。

序列到序列模型是一种将一系列项目（如单词、字母、图像的特征等）输入并输出一系列其他项目的模型。一个训练过的模型将以如下方式工作：

<video width="100%" height="auto" loop autoplay controls>
  <source src="/contents/attention/seq2seq_1.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

在神经机器翻译中，序列是一系列单词，逐个处理后，输出也是一系列单词：

<video width="100%" height="auto" loop autoplay controls>
  <source src="/contents/attention/seq2seq_2.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

## 深入了解

在内部，该模型由一个 编码器 <span class="encoder">encoder</span> 和一个 解码器 <span class="decoder">decoder</span> 组成。

编码器 <span class="encoder">encoder</span> 处理输入序列中的每个项目，并将其捕获的信息编译成一个向量（称为 上下文 <span class="context">context</span>）。在处理完整个输入序列之后，编码器 <span class="encoder">encoder</span> 将上下文 <span class="context">context</span> 发送给解码器 <span class="decoder">decoder</span>，解码器开始逐个生成输出序列的项目。

<video width="100%" height="auto" loop autoplay  controls>
  <source src="/contents/attention/seq2seq_3.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

机器翻译也是相同的情况。

<video width="100%" height="auto" loop autoplay controls>
  <source src="/contents/attention/seq2seq_4.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

在机器翻译中，<span class="context">context</span> 是一个向量（基本上是由数字组成的数组）。编码器 <span class="encoder">encoder</span> 和解码器 <span class="decoder">decoder</span> 通常都是循环神经网络（recurrent neural networks，RNN）。请务必查看 Luis Serrano 的 [A friendly introduction to Recurrent Neural Networks](https://www.youtube.com/watch?v=UNmqTiOnRfg) 以了解 RNN 的基础知识。

<div class="img-div" markdown="0">
    <img src="/contents/attention/context.png" />
    上下文 <span class="context">context</span> 是浮点数组成的向量。稍后我们在本文中将以颜色可视化向量，将更高值的单元格分配更亮的颜色。
</div>

在设置您的模型时，您可以设置上下文 <span class="context">context</span> 向量的大小。基本上，这是在 RNN 编码器 <span class="encoder">encoder</span> 中的隐藏单元数量。这些可视化展示了一个大小为 4 的向量，但在现实应用中，上下文 <span class="context">context</span> 向量大小可能会是 256、512 或 1024 等。

按设计，RNN 在每个时间步骤中接受两个输入：一个输入（在编码器的情况下，是输入句子中的一个单词）和一个隐藏状态。并且，单词需要用向量来表示。为了将单词转化为向量，我们使用被称为 “词嵌入 [word embedding](https://machinelearningmastery.com/what-are-word-embeddings/)” 算法的方法类。这些算法将单词转化为向量空间，其中包含单词的许多含义/语义信息（例如：[king - man + woman = queen](http://p.migdal.pl/2017/01/06/king-man-woman-queen-why.html)）。

<div class="img-div" markdown="0">
    <img src="/contents/attention/embedding.png" />
    在处理输入之前，我们需要将输入单词转换为向量。这个过程使用 <a href="https://en.wikipedia.org/wiki/Word_embedding">word embedding</a> 算法完成。我们可以使用预训练的嵌入 <a href="http://ahogrammer.com/2017/01/20/the-list-of-pretrained-word-embeddings/">pre-trained embeddings</a> 或在我们自己的数据集上训练自己的嵌入。典型的嵌入向量边长为 200 或 300，为了简单起见，我们在这里展示了一个大小为 4 的向量。
</div>

现在我们已经介绍了我们的主要向量/张量，让我们回顾一下 RNN 的机制并建立一个可视化的语言来描述这些模型：

<video width="100%" height="auto" loop autoplay controls>
  <source src="/contents/attention/RNN_1.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

RNN 下一步会使用第二个输入向量和第一步的隐藏状态，创建第二个时间步骤的输出。

下一步是使用第二个输入向量和一个隐藏状态#1来创建该时间的输出。后文中，我们会使用类似这样的动画来描述神经机器翻译模型内部的向量。

在接下来的可视化中，每个编码器 <span class="encoder">encoder</span> 或解码器 <span class="decoder">decoder</span> 的脉冲都是 RNN 处理其输入并生成该时间步的输出。由于编码器 <span class="encoder">encoder</span> 和解码器 <span class="decoder">decoder</span> 都是 RNN，每个时间步骤中一个 RNN 进行一些处理，它根据它的输入和之前步骤中它能看到的输入来更新其隐藏状态 <span class="context">hidden state</span>。

让我们观察编码器 <span class="encoder">encoder</span> 的隐藏状态 <span class="context">hidden states</span>。请注意，实际上最后一个隐藏状态 <span class="context">hidden state</span> 我们作为上下文 <span class="context">context</span>传递给了解码器 <span class="decoder">decoder</span>。

<video width="100%" height="auto" loop autoplay controls>
  <source src="/contents/attention/seq2seq_5.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

在解码器 <span class="decoder">decoder</span> 中，也会维护一个从一个时间步骤传递到下一个时间步骤的隐藏状态 <span class="decoder">hidden state</span>。但我们目前关注的是模型的主要部分，所以没有在可视化中展示它。

现在让我们来看看另一种可视化序列到序列模型的方式。这个动画将更容易理解描述这些模型的静态图形。这被称为“展开”视图，在这个视图中，我们不只显示一个解码器 <span class="decoder">decoder</span>，而是为每个时间步骤显示一个副本。这样我们就可以查看每个时间步骤的输入和输出。

<video width="100%" height="auto" loop autoplay controls>
  <source src="/contents/attention/seq2seq_6.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

## 让我们集中注意力

对于这类模型来说，上下文 <span class="context">context</span> 向量成为了一个瓶颈。它使得模型难以处理较长的句子。[Bahdanau et al., 2014](https://arxiv.org/abs/1409.0473) 和 [Luong et al., 2015](https://arxiv.org/abs/1508.04025) 提出了一个解决方案。这些论文引入并改进了一种被称为“注意力”的技术，极大地提高了机器翻译系统的质量。注意力允许模型根据需要专注于输入序列的相关部分。

<img src="/contents/attention/attention.png" />

<div class="img-div" markdown="0">
    在时间步骤 7 中，注意力机制使解码器 <span class="decoder">decoder</span> 能够在生成英语翻译之前关注输入序列中的 “étudiant”（法语中的 “student”）。这种在输入序列相关部分放大信号的能力使得注意力模型产生的结果优于没有注意力的模型。
</div>

让我们继续在这个高层抽象层面上查看注意力模型。注意力模型与经典的序列到序列模型有两个主要区别：

首先，编码器 <span class="encoder">encoder</span> 将更多的数据传递给解码器 <span class="decoder">decoder</span>。编码器 <span class="encoder">encoder</span> 不再只传递编码阶段的最后隐藏状态，而是将 *所有* 隐藏状态 <span class="context">hidden states</span> 都传递给解码器 <span class="decoder">decoder</span>：

<video width="100%" height="auto" loop autoplay controls>
  <source src="/contents/attention/seq2seq_7.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

其次，在生成输出之前，有注意力机制的解码器 <span class="decoder">decoder</span> 会执行一个额外的步骤。为了聚焦于与当前解码时间步骤相关的输入部分，解码器 <span class="decoder">decoder</span> 会执行以下操作：

1. 浏览它收到的编码器隐藏状态 <span class="context">hidden states</span> 集合 - 每个编码器隐藏状态 <span class="context">encoder hidden state</span> 与输入句子中最相关的某个单词关联
1. 给每个隐藏状态 <span class="context">hidden state</span> 赋予一个分数（我们先不考虑分数的计算方式）
1. 将每个隐藏状态 <span class="context">hidden state</span> 乘以其经过 softmax 处理后的分数，从而放大具有高分数的隐藏状态 <span class="context">hidden states</span>，并淹没具有低分数的隐藏状态 <span class="context">hidden states</span>

<video width="100%" height="auto" loop autoplay controls>
   <source src="/contents/attention/attention_process.mp4" type="video/mp4">
   Your browser does not support the video tag.
</video>

这个评分过程在解码器 <span class="decoder">decoder</span> 端的每个时间步骤中进行。

现在让我们将所有内容整合到以下可视化中，看看注意力过程是如何工作的：

1. 注意力解码器 RNN 接收 <span class="embedding">\<END\></span> 符号的嵌入向量，和一个初始解码器隐藏状态 <span class="decoder">initial decoder hidden state</span>。
1. RNN 处理输入，生成一个输出和一个新的隐藏状态 <span class="decoder">new hidden state</span> 向量（<span class="decoder">h</span><span class="step_no">4</span>）。输出被丢弃。
1. 注意力步骤：我们使用编码器隐藏状态 <span class="context">encoder hidden states</span> 和 <span class="decoder">h</span><span class="step_no">4</span> 向量来计算该时间步骤的上下文向量（<span class="step_no">C</span><span class="decoder">4</span>）。
1. 我们将 <span class="decoder">h</span><span class="step_no">4</span> 和 <span class="step_no">C</span><span class="decoder">4</span> 连接成一个向量。
1. 我们通过一个前馈神经网络 <span class="ffnn">feedforward neural network</span>（与模型一起训练的网络）传递这个向量。
1. 前馈神经网络的输出 <span class="logits_output">output</span> 指示了该时间步骤的输出单词。
1. 下一个时间步骤重复以上步骤。

<video width="100%" height="auto" loop autoplay controls>
   <source src="/contents/attention/attention_tensor_dance.mp4" type="video/mp4">
   Your browser does not support the video tag.
</video>

这是另一种观察我们在每个解码步骤上关注输入句子的哪个部分的方式：

<video width="100%" height="auto" loop autoplay controls>
  <source src="/contents/attention/seq2seq_9.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

请注意，模型并不是简单地将输出的第一个单词与输入的第一个单词对齐。它实际上是在训练阶段学习了如何对齐该语言对（例如上例中的法语和英语）。可以从上面列出的注意力论文中看到这种机制有多么精确的例子：

<div class="img-div" markdown="0">
<img src="/contents/attention/attention_sentence.png" />
    您可以看到，当输出“European Economic Area”时，模型正确地进行了注意力对齐。在法语中，这些单词的顺序与英语相反（“européenne économique zone”）。句子中的其他单词也以类似的顺序排列。
</div>

如果您觉得已经准备好学习实现的内容，请务必查看 TensorFlow 的 [Neural Machine Translation (seq2seq) Tutorial](https://github.com/tensorflow/nmt)。