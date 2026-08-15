---
id: illustrated-word2vec
title: "【译】图解 Word2vec"
description: "基于原文和引用译文，优化补遗，尽力保留原汁原味"
date: 2026.08.16 10:34
categories:
    - AI
tags: [AI, Embedding Model]
keywords: Word2vec, embedding, vector, cosine similarity, dimension, trait, skipgram, sliding window
cover: /contents/illustrated-word2vec/word2vec.png
---

- 原文地址：https://jalammar.github.io/illustrated-word2vec/
- 原文作者：[Jay Alammar](https://jalammar.github.io/)
- 引用译文：[图解Word2vec，读这一篇就够了](https://mp.weixin.qq.com/s?__biz=MjM5MTQzNzU2NA==&mid=2651669277&idx=2&sn=bc8f0590f9e340c1f1359982726c5a30&chksm=bd4c648e8a3bed9817f30c5a512e79fe0cc6fbc58544f97c857c30b120e76508fef37cae49bc&scene=0&xtrack=1#rd)

---

<div class="img-div-any-width" markdown="0" style="text-align: center;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/word2vec.png"/>
  <br />
</div>

<blockquote class='subtle'>
  “<strong>在万物之中，都存在着一种模式，它本是我们宇宙的一部分。它拥有对称、优雅与优美</strong> —— 这些特质，你总能在真正的艺术家所捕捉之物中寻见。你可以在四季更迭中看见它，在沙脊蜿蜒的纹路中看见它，在三齿拉雷亚灌木的枝杈簇生或叶脉排列中看见它。<br /><br />

  我们试图在生活与社会中模仿这些模式，
  追寻那些令人安适的节奏、舞蹈与形态。
  然而，在追寻终极完美的过程中，或许也能窥见危险。
  显然，终极模式内含着自身的固滞。
  在那种完美之中，万物皆走向死亡。”

  —— 《沙丘》（1965年）
</blockquote>

嵌入（embedding）是机器学习中最迷人的想法之一。 如果你曾经使用 Siri、Google Assistant、Alexa、Google 翻译，甚至智能手机键盘进行下一词预测，那么你很有可能从这个已经成为自然语言处理模型核心的想法中受益。在过去的几十年中，嵌入技术用于神经网络模型已有相当大的发展（尤其是最近，其发展包括导致 [BERT](https://jalammar.github.io/illustrated-bert/) 和 GPT2 等尖端模型的语境化嵌入）。

<iframe width="560" height="315" src="https://alphahinex.github.io/contents/illustrated-word2vec/The%20Illustrated%20Word2vec%20-%20A%20Gentle%20Intro%20to%20Word%20Embeddings%20in%20Machine%20Learning.mp4" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"  style="
width: 100%;
max-width: 560px;" allowfullscreen></iframe>

Word2vec 是一种有效创建词嵌入的方法，它自2013年以来就一直存在。但除了作为词嵌入的方法之外，它的一些概念已经被证明可以有效地创建推荐引擎和理解时序数据，甚至可应用于商业性的非语言任务。像 [Airbnb](https://www.kdd.org/kdd2018/accepted-papers/view/real-time-personalization-using-embeddings-for-search-ranking-at-airbnb)、[阿里巴巴](https://www.kdd.org/kdd2018/accepted-papers/view/billion-scale-commodity-embedding-for-e-commerce-recommendation-in-alibaba)、[Spotify](https://www.slideshare.net/AndySloane/machine-learning-spotify-madison-big-data-meetup)、[Anghami](https://towardsdatascience.com/using-word2vec-for-music-recommendations-bb9649ac2484) 这样的公司都从 NLP 领域中提取灵感并用于产品中，从而为新型推荐引擎提供支持。

在这篇文章中，我们将讨论嵌入的概念，以及使用 word2vec 生成嵌入的机制。让我们从一个例子开始，熟悉使用向量来表示事物。你是否知道你的个性可以仅被五个数字的列表（向量）表示？

# 个性嵌入：你是什么样的人？

<blockquote class='subtle'>
“我将沙漠变色龙呈于你们眼前。它那与周遭融为一体的能力，已然昭示了生态学之根源与个体身份之基石的全部奥秘。”

——《沙丘之子》
</blockquote>

如何用 0 到 100 的范围来表示你是多么内向/外向（其中 0 是最内向的，100 是最外向的）？ 
你有没有做过像 MBTI 那样的人格测试，或者 [五大人格特质](https://en.wikipedia.org/wiki/Big_Five_personality_traits) 测试？如果你还没有，这些测试会问你一系列的问题，然后在很多维度给你打分，内向/外向就是其中之一。

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/big-five-personality-traits-score.png"/>
  <br />
  五大人格特质测试结果示例。它可以真正告诉你很多关于你自己的事情，并且在 <a href="http://psychology.okstate.edu/faculty/jgrice/psyc4333/FiveFactor_GPAPaper.pdf">学术</a>、<a href="https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1744-6570.1999.tb00174.x">人格</a> 和 <a href="https://www.massgeneral.org/psychiatry/assets/published_papers/soldz-1999.pdf">职业成功</a> 方面都具有预测能力。<a href="https://projects.fivethirtyeight.com/personality-quiz/">此处</a> 可以找到测试结果。
</div>

假设我的内向/外向得分为 38/100。我们可以用这种方式绘图：

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/introversion-extraversion-100.png"/>
</div>

让我们把范围收缩到 -1 到 1 :

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/introversion-extraversion-1.png"/>
</div>

当你只知道这一条信息的时候，你觉得你有多了解这个人？了解不多。人很复杂，让我们添加另一个维度 —— 测试中另一个特性的的得分。

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/two-traits-vector.png"/>
  <br />
  我们可以将两个维度表示为图形上的一个点，或者作为从原点到该点的向量。我们拥有很棒的工具来处理即将上场的向量们。
</div>

我已经隐藏了我们正在绘制的人格特征，这样你会渐渐习惯于在不知道每个维度代表什么的情况下，从一个人格的向量表示中获得价值信息。

我们现在可以说这个向量部分地代表了我的人格。当你想要将另外两个人与我进行比较时，这种表示法就有用了。假设我被 ```公共汽车``` 撞了，我需要被性格相似的人替换，那在下图中，两个人中哪一个更像我？

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/personality-two-persons.png"/>
</div>

处理向量时，计算相似度得分的常用方法是 [余弦相似度](https://en.wikipedia.org/wiki/Cosine_similarity)：

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/cosine-similarity.png"/>
  <br />
  <span class="encoder" style="color: #70BF41">Person #1</span> 在性格上与我更相似。指向相同方向的向量（长度也起作用）具有更高的余弦相似度。
</div>

再一次，两个维度还不足以捕获有关不同人群的足够信息。心理学已经研究出了五个主要人格特征（以及大量的子特征），所以让我们使用所有五个维度进行比较：

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/big-five-vectors.png"/>
  <br />
</div>

使用五个维度的问题是我们不能在二维平面绘制整齐小箭头了。这是机器学习中的常见挑战，我们经常需要在更高维度的空间中思考。但好在余弦相似度仍然有效，它适用于任意维度：

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/embeddings-cosine-personality.png"/>
  <br />
  余弦相似度适用于任意数量的维度。这些得分比上次的得分要更好，因为它们是根据被比较事物的更高维度算出的。
</div>

在本节的末尾，我希望我们能得出两个核心思想：

1. 我们可以将人（和事物）表示为数值向量（这对机器来说很棒！）。
2. 我们可以很容易地计算出向量之间有多相似。

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/section-1-takeaway-vectors-cosine.png"/>
  <br />
</div>

# 词嵌入

<blockquote class='subtle'>
“词语所赐予的，不过是欺瞒与幻象之能。”

——《沙丘之子》
</blockquote>

通过上文的理解，我们继续看看训练好的词向量实例（也被称为词嵌入）并探索它们的一些有趣属性。

这是一个单词 “king” 的词嵌入（在维基百科上训练的 GloVe 向量）：

<span class="small_code" style="color: #c7254e">
[ 0.50451 ,  0.68607 , -0.59517 , -0.022801,  0.60046 , -0.13498 ,
 -0.08813 ,  0.47377 , -0.61798 , -0.31012 , -0.076666,  1.493   ,
 -0.034189, -0.98173 ,  0.68229 ,  0.81722 , -0.51874 , -0.31503 ,
 -0.55809 ,  0.66421 ,  0.1961  , -0.13495 , -0.11476 , -0.30344 ,
  0.41177 , -2.223   , -1.0756  , -1.0783  , -0.34354 ,  0.33505 ,
  1.9927  , -0.04234 , -0.64319 ,  0.71125 ,  0.49159 ,  0.16754 ,
  0.34344 , -0.25663 , -0.8523  ,  0.1661  ,  0.40102 ,  1.1685  ,
 -1.0137  , -0.21585 , -0.15155 ,  0.78321 , -0.91241 , -1.6106  ,
 -0.64426 , -0.51042 ]
 </span>

这是一个包含 50 个数字的列表。通过观察数值我们看不出什么。但是让我们稍微给它可视化，以便与其它词向量比较。我们把所有这些数字放在一行：

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/king-white-embedding.png"/>
  <br />
</div>

让我们根据它们的值对单元格进行颜色编码（如果它们接近 2 则为红色，接近 0 则为白色，接近 -2 则为蓝色）：

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/king-colored-embedding.png"/>
  <br />
</div>

我们将忽略数字并仅查看颜色以指示单元格的值。现在让我们将 “king” 与其它单词进行比较：

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/king-man-woman-embedding.png"/>
  <br />
</div>

看看 “Man” 和 “Woman” 彼此之间是如何比它们任一一个单词与 “King” 相比更相似的？这暗示你一些事情。这些向量图示很好的展现了这些单词的信息/含义/关联。

这是另一个示例列表（通过垂直扫描列来查找具有相似颜色的列）：

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/queen-woman-girl-embeddings.png"/>
  <br />
</div>

有几个要点需要指出：

1. 所有这些不同的单词都有一条直的红色列。 它们在这个维度上是相似的（虽然我们不知道每个维度是什么）
2. 你可以看到 “woman” 和 “girl” 在很多地方是相似的，“man” 和 “boy” 也是一样
3. “boy” 和 “girl” 也有彼此相似的地方，但这些地方却与 “woman” 或 “man” 不同。这些是否可以总结出一个模糊的 “youth” 概念？可能吧。
4. 除了最后一个单词，所有单词都是代表人。我添加了一个对象（“water”）来显示类别之间的差异。你可以看到蓝色列一直向下并在 “water” 的词嵌入之前停下了。
5. “king” 和 “queen” 彼此之间相似，但它们与其它单词都不同。这些是否可以总结出一个模糊的 “royalty” 概念？

## 类比

<blockquote class='subtle'>
“文字能承载我们所愿的任何重负。所需要的不过是共识，以及一套可赖以构建的传统。”

——《沙丘神帝》
</blockquote>

展现嵌入奇妙属性的著名例子是类比。我们可以添加、减去词嵌入并得到有趣的结果。一个著名例子是公式：“king” - “man” + “woman”：

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/king-man+woman-gensim.png"/>
  <br />
  在 python 中使用 <a href="https://radimrehurek.com/gensim/">Gensim</a> 库，我们可以添加和减去词向量，它会找到与结果向量最相似的单词。该图像显示了最相似的单词列表，每个单词都具有余弦相似性。
</div>

我们可以像之前一样可视化这个类比：

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/king-analogy-viz.png"/>
  <br />
  由 “king-man+woman” 生成的向量并不完全等同于 “queen”，但 “queen” 是我们在此集合中包含的 400,000 个字嵌入中最接近它的单词。
</div>

现在我们已经看过训练好的词嵌入，接下来让我们更多地了解训练过程。但在我们开始使用 word2vec 之前，我们需要看一下词嵌入的父概念：神经语言模型。

# 语言模型

<blockquote class='subtle'>
  “过去、现在、未来之幻象，皆不能惑先知。<strong>语言之固着性，正为此类线性分判之根源。</strong>先知执钥，以启语言之锁。<br /> <br />

  此非机械之宇。事件之线性递进，乃观察者所强加。因果乎？绝非如此。<strong>先知吐露命运之言</strong>，汝则得窥‘必成’之事。然预言之刹那，放出无限兆示与威能之物。宇宙遂生幽灵之移变。”

  ——《沙丘神帝》
</blockquote>

如果要举自然语言处理最典型的例子，那应该就是智能手机输入法中的下一单词预测功能。这是个被数十亿人每天使用上百次的功能。

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/swiftkey-keyboard.png"/>
  <br />
</div>

下一单词预测是一个可以通过 *语言模型* 实现的任务。语言模型会通过单词列表（比如说两个词）去尝试预测可能紧随其后的单词。

在上面这个手机截屏中，我们可以认为该模型接收到两个绿色单词（<span class="plain_code mdc-text-green-600" style="color: #43a047">thou shalt</span>）并推荐了一组单词(“not” 就是其中最有可能被选用的一个)：

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/thou-shalt-_.png"/>
  <br />
</div>

<br />

我们可以把这个模型想象为这个黑盒:

<br />

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/language_model_blackbox.png"/>
  <br />
</div>

<br />

但事实上，该模型不会只输出一个单词。实际上，它对所有它知道的单词（模型的词库，可能有几千到几百万个单词）按可能性打分。输入法程序会选出其中分数最高的推荐给用户。

<br />

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/language_model_blackbox_output_vector.png"/>
  <br />
  自然语言模型的输出就是模型所知单词的概率评分，我们通常把概率按百分比表示，但是实际上，40% 这样的分数在输出向量组是表示为 0.4。
</div>

<br />

自然语言模型（请参考 [Bengio 2003](http://www.jmlr.org/papers/volume3/bengio03a/bengio03a.pdf)）在完成训练后，会按如下所示完成三步预测：

<br />

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/neural-language-model-prediction.png"/>
  <br />
</div>

<br />

第一步与我们最相关，因为我们讨论的就是 Embedding。模型在经过训练之后会生成一个映射单词表所有单词的矩阵。在进行预测的时候，我们的算法就是在这个映射矩阵中查询输入的单词，然后计算出预测值:

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/neural-language-model-embedding.png"/>
  <br />
</div>

现在让我们将重点放到模型训练上，来学习一下如何构建这个映射矩阵。

# 语言模型训练

<blockquote class='subtle'>
“若欲理解一个过程，便不可令其停滞。理解须顺应过程之流，须融入其中，与之同流共行。”

——《沙丘》
</blockquote>

相较于大多数其他机器学习模型，语言模型有一个很大有优势，那就是我们有丰富的文本来训练语言模型。所有我们的书籍、文章、维基百科、及各种类型的文本内容都可用。相比之下，许多其他机器学习的模型开发就需要手工设计数据或者专门采集数据。

> "You shall know a word by the company it keeps" J.R. Firth

我们通过找常出现在每个单词附近的词，就能获得它们的嵌入。机制如下：

1. 我们获取大量文本数据（例如所有维基百科内容）。然后
2. 我们建立一个可以沿文本滑动的窗口（例如一个窗口里包含三个单词）。
3. 利用这样的滑动窗口就能为训练模型生成大量样本数据。

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/wikipedia-sliding-window.png"/>
  <br />
</div>

当这个窗口沿着文本滑动时，我们就能（真实地）生成一套用于模型训练的数据集。为了明确理解这个过程，我们看下滑动窗是如何处理这个短语的:

> “Thou shalt not make a machine in the likeness of a human mind” ~Dune

在一开始的时候，窗口锁定在句子的前三个单词上:

<br />  

<div class="img-div" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/lm-sliding-window.png"/>
  <br />
</div>

<br />  

我们把前两个单词单做特征，第三个单词单做标签:

<br />  

<div class="img-div" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/lm-sliding-window-2.png"/>
  <br />
  这时我们就生产了数据集中的第一个样本，它会被用在我们后续的语言模型训练中。
</div>

<br />  

接着，我们将窗口滑动到下一个位置并生产第二个样本:

<br />  

<div class="img-div" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/lm-sliding-window-3.png"/>
  <br />
  这时第二个样本也生成了。
</div>

<br />  

不用多久，我们就能得到一个较大的数据集，从数据集中我们能看到在不同的单词组后面会出现的单词：

<br />  

<div class="img-div" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/lm-sliding-window-4.png"/>
  <br />  
</div>

<br />  

在实际应用中，模型往往是在我们滑动窗口的同时就被训练的。但是我觉得将“生成数据集”和训练模型分为两个阶段会显得更清晰易懂一些。除了使用神经网络建模之外，大家还常用一项名为 N-grams 的技术进行模型训练（参考：[Speech and Language Processing](http://web.stanford.edu/~jurafsky/slp3/) 第三章）。如果想了解现实产品从使用 N-grams 模型到使用神经模型的转变，可以看一下 [Swiftkey 在 2015 年的发表一篇博客](https://blog.swiftkey.com/neural-networks-a-meaningful-leap-for-mobile-typing/)，我最喜欢的安卓输入法，文中介绍了他们的自然语言模型及该模型与早期 N-gram 模型的对比。我很喜这个例子，因为它能告诉你如何在营销宣讲中把 Embedding 的算法属性解释清楚。

## 顾及两头

<blockquote class='subtle'>
“悖论如指路之标，引你超越其表。若悖论令你不安，正暴露了你对确定性的执念。而相对主义者，不过视悖论为一种兴味，或可一笑，或至惊惧，但终究是一场启迪。”

——《沙丘神帝》
</blockquote>

根据本文前面的信息进行填空:

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/jay_was_hit_by_a_.png"/>
  <br />  
</div>

在空白前面，我提供的上下文是五个单词（以及事先提到的 "bus"）。可以肯定，大多数人都会把 ```bus``` 填入空白中。但是如果我再给你一条信息 —— 比如空白后的一个单词，那答案会有变吗？

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/jay_was_hit_by_a_bus.png"/>
  <br />  
</div>

这下空白处改填的内容完全变了。这时 ```red``` 这个词最有可能适合这个位置。从这个例子中我们能学到，一个单词的前后词语都带信息价值。事实证明，我们需要考虑两个方向的单词（预测单词的左侧单词与右侧单词）以获得更好的词向量。那我们该如何调整训练方式以满足这个要求呢，继续往下看。

# Skipgram 模型

<blockquote class='subtle'>
  “智能行事，常以有限之据涉险，其所处之域，错误非但可能，实属必需。”

  ——《圣殿沙丘》
</blockquote>

我们不仅要考虑目标单词的前两个单词，还要考虑其后两个单词。

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/continuous-bag-of-words-example.png"/>
  <br />  
</div>

如果这么做，我们实际上构建并训练模型所用的数据集就如下所示：

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/continuous-bag-of-words-dataset.png"/>
  <br />  
</div>

上述的这种架构被称为 **连续词袋（Continuous Bag of Words）**，在 [一篇关于 word2vec 的论文](https://arxiv.org/pdf/1301.3781.pdf) [pdf] 中有阐述。还有一种架构，它也常常表现优异，但在具体做法上略有差异。

它不根据上下文（一个单词前后的单词）来猜测目标单词，而是根据当前单词推测可能的前后单词。我们设想一下滑动窗口在训练数据时如下图所示：

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/skipgram-sliding-window.png"/>
  <br />  
  绿框中的词语是输入词，粉框则是可能的输出结果。
</div>

这里粉框颜色深度呈现不同，是因为滑动窗口给训练集产生了4个独立的样本:

<br />  

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/skipgram-sliding-window-samples.png"/>
  <br />  
</div>

<br />  

这种方式称为 **skipgram** 架构。我们可以像下图这样展示滑动窗口的内容：

<br />  

<div class="img-div" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/skipgram-sliding-window-1.png"/>
  <br />  
</div>

<br />  

这样就为数据集提供了 4 个样本:

<br />  

<div class="img-div" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/skipgram-sliding-window-2.png"/>
  <br />  
</div>

然后我们移动滑窗到下一个位置:

<br />  

<div class="img-div" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/skipgram-sliding-window-3.png"/>
  <br />  
</div>
<br />  

这样我们又产生了接下来 4 个样本:

<br />  

<div class="img-div" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/skipgram-sliding-window-4.png"/>
  <br />  
</div>

在移动几组位置之后，我们就能得到一批样本：

<br />  

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/skipgram-sliding-window-5.png"/>
  <br />  
</div>

## 重新审视训练过程

<blockquote class="subtle">
  “穆阿迪布之所以学速惊人，盖因他最初的训练便是‘学之方’。而一切学问之始，便是对自身可学之力的根本信赖。令人骇然的是，世上有多少人竟不信己身有学之能，更有甚者，视学道为畏途。”

  ——《沙丘》
</blockquote>

现在我们已经从现有的文本中获得了 Skipgram 模型的训练数据集，接下来让我们看看如何使用它来训练一个能预测相邻词汇的自然语言模型。

<br />  

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/skipgram-language-model-training.png"/>
  <br />  
</div>

从数据集中的第一个样本开始。我们将特征输入到未经训练的模型，让它预测一个可能的相邻单词。

<br />  

<div class="img-div" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/skipgram-language-model-training-2.png"/>
  <br />  
</div>

该模型会执行三个步骤并输出预测向量（对应于单词表中每个单词的概率）。因为模型未经训练，该阶段的预测肯定是错误的。但是没关系，我们知道应该猜出的是哪个单词 —— 这个词就在我训练集数据中当前数据行的 标签/输出 单元格里：

<br />  

<div class="img-div" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/skipgram-language-model-training-3.png"/>
  <br />  
  目标单词概率为 1，其他所有单词概率为 0，这样数值组成的向量就是“目标向量”。
</div>

<br />  

模型的偏差有多少？将两个向量相减，就能得到偏差向量：

<br />  

<div class="img-div" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/skipgram-language-model-training-4.png"/>
  <br />  
</div>

<br />  

现在这一误差向量可以被用于更新模型了，所以在下一轮预测中，如果用 <span class="plain_code mdc-text-green-500" style="color: #4caf50">not</span> 作为输入，我们更有可能得到 <span class="plain_code mdc-text-pink-500" style="color: #e91e63">thou</span> 作为输出了。

<br />  

<div class="img-div" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/skipgram-language-model-training-5.png"/>
  <br />  
</div>

<br />  

这其实就是训练的第一步了。我们接下来继续对数据集内下一份样本进行同样的操作，直到我们遍历所有的样本。这就是 *一轮（epoch）* 训练了。我们再多做几轮，得到训练过的模型，于是就可以从中提取嵌入矩阵来用于其他应用了。

以上确实有助于我们理解整个流程，但这依然不是 word2vec 真正训练的方法。我们错过了一些关键的想法。

# 负例采样

<blockquote class='subtle'>
“欲解穆阿迪布，而不识其死敌哈克南人，犹欲见真理而不辨谬误，欲睹光明而不识黑暗。此不可得也。”

——《沙丘》
</blockquote>

回想一下这个神经语言模型计算预测值的三个步骤： 
<br />  

<div class="img-div" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/language-model-expensive.png"/>
  <br />  
</div>

<br />  

从计算的角度来看，第三步非常昂贵 —— 尤其是当我们将需要在数据集中为每个训练样本都做一遍（很容易就多达数千万次）。我们需要寻找一些提高表现的方法。

一种方法是将目标分为两个步骤：

1. 生成高质量的词嵌入（不要担心下一个单词预测）。
2. 使用这些高质量的嵌入来训练语言模型（进行下一个单词预测）。

在本文中我们将专注于第 1 步，因为这篇文章专注于嵌入。要使用高性能模型生成高质量嵌入，我们可以改变一下预测相邻单词这一任务：

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/predict-neighboring-word.png "/>
  <br />  
</div>

将其切换到一个同时摄取输入与输出单词的模型，并输出一个表明它们是否是邻居的分数（0 表示“不是邻居”，1 表示“邻居”）。

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/are-the-words-neighbors.png "/>
  <br />  
</div>

这个简单的变换将我们需要的模型从神经网络改为逻辑回归模型 —— 因此它变得更简单，计算速度更快。

这个变换要求我们转换数据集的结构 —— 标签值现在是一个值为 0 或 1 的新列。它们将全部为 1，因为我们添加的所有单词都是邻居。

<br />  

<div class="img-div" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/word2vec-training-dataset.png "/>
  <br />  
</div>

<br />  

现在的计算速度可谓是神速啦 —— 在几分钟内就能处理数百万个例子。但是我们还需要解决一个漏洞。如果所有的例子都是邻居（目标：1），我们这个”天才模型“可能会被训练得永远返回 1 —— 准确性是百分百了，但它什么东西都学不到，只会产生垃圾嵌入结果。

<div class="img-div" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/word2vec-smartass-model.png "/>
  <br />  
</div>

为了解决这个问题，我们需要在数据集中引入 *负样本（negative samples）* —— 不是邻居的单词样本。我们的模型需要为这些样本返回 0。模型必须努力解决这个挑战 —— 而且依然必须保持高速。

<br />  

<div class="img-div" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/word2vec-negative-sampling.png "/>
  <br />  
  对于我们数据集中的每个样本，我们添加了<strong>负面示例</strong>。它们具有相同的输入字词，标签为 0。
</div>

但是我们应该在输出词处填写什么呢？我们从词汇表中随机抽取单词

<br />  

<div class="img-div" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/word2vec-negative-sampling-2.png "/>
  <br />  
</div>

这个想法的灵感来自 [噪声对比评估](http://proceedings.mlr.press/v9/gutmann10a/gutmann10a.pdf) [pdf]。我们将实际信号（相邻单词的正例）与噪声（随机选择的不是邻居的单词）进行对比。这导致了计算效率和统计效率之间的巨大权衡。

# 带负例采样的 Skipgram（SGNS）

我们现在已经介绍了 word2vec 中的两个核心思想：作为一对时，我们称其为带负例采样的 skipgram 。

<div class="img-div" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/skipgram-with-negative-sampling.png "/>
  <br />  
</div>

# Word2vec 训练流程

<blockquote class="subtle">
“机器无法预见所有对人类至关重要的问题。这便是离散的片段与绵延不断的连续体之间的分野。我们属于后者，而机器只能止步于前者。”

——《沙丘神帝》
</blockquote>

现在我们已经了解了 skipgram 和负例采样的两个中心思想，可以继续仔细研究实际的 word2vec 训练过程了。

在训练过程开始之前，我们预先处理我们正在训练模型的文本。在这一步中，我们确定一下词典的大小（我们称之为 <span class="plain_code mdc-text-amber-700" style="color: #ffa000">vocab_size</span>，比如说 10,000）以及哪些词被它包含在内。

在训练阶段的开始，我们创建两个矩阵 —— <span class="plain_code mdc-text-green-500" style="color: #4caf50">Embedding</span> 矩阵和 <span class="plain_code mdc-text-purple-500" style="color: #9c27b0">Context</span> 矩阵。这两个矩阵嵌入了我们词汇表中的每个单词（所以 <span class="plain_code mdc-text-amber-700" style="color: #ffa000">vocab_size</span> 是他们的维度之一）。第二个维度是我们希望每个嵌入的长度（<span class="plain_code mdc-text-amber-900" style="color: #ff6f00">embedding_size</span> —— 300 是一个常见值，但我们在前文也看过 50 的例子）。

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/word2vec-embedding-context-matrix.png "/>
  <br />  
</div>

在训练过程开始时，我们用随机值初始化这些矩阵。然后我们开始训练过程。在每个训练步骤中，我们采取一个相邻的例子及其相关的非相邻例子。我们来看看我们的第一组：

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/word2vec-training-example.png"/>
  <br />  
</div>

现在我们有四个单词：输入单词 <span class="plain_code mdc-text-green-500" style="color: #4caf50">not</span> 和输出/上下文单词: <span class="plain_code mdc-text-purple-500" style="color: #9c27b0">thou</span>（实际邻居词），<span class="plain_code mdc-text-purple-500" style="color: #9c27b0">aaron</span> 和 <span class="plain_code mdc-text-purple-500" style="color: #9c27b0">taco</span>（负面例子）。我们继续查找它们的嵌入 —— 对于输入词，我们查看 <span class="plain_code mdc-text-green-500" style="color: #4caf50">Embedding</span> 矩阵。对于上下文单词，我们查看 <span class="plain_code mdc-text-purple-500" style="color: #9c27b0">Context</span> 矩阵（即使两个矩阵都嵌入了我们词汇表中的每个单词）。

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/word2vec-lookup-embeddings.png "/>
  <br />  
</div>

然后，我们计算输入嵌入与每个上下文嵌入的点积。在每种情况下，结果都将是表示输入和上下文嵌入相似性的数字。

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/word2vec-training-dot-product.png "/>
  <br />  
</div>

现在我们需要一种方法将这些分数转化为看起来像概率的东西 —— 我们需要它们都是正值，并且 处于 0 到 1 之间。[sigmoid](https://jalammar.github.io/feedforward-neural-networks-visual-interactive/#sigmoid-visualization) 这一 [逻辑操作](https://en.wikipedia.org/wiki/Logistic_function) 正适合用来做这样的事情啦。

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/word2vec-training-dot-product-sigmoid.png "/>
  <br />  
</div>

现在我们可以将 sigmoid 操作的输出视为这些示例的模型输出。您可以看到 <span class="plain_code mdc-text-purple-500" style="color: #9c27b0">taco</span> 得分最高，<span class="plain_code mdc-text-purple-500" style="color: #9c27b0">aaron</span> 最低，无论是 sigmoid 操作之前还是之后。

既然未经训练的模型已做出预测，而且我们确实拥有真实目标标签来作对比，那么让我们计算模型预测中的误差吧。为此我们只需从目标标签中减去 sigmoid 分数。

<div class="img-div-any-width" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/word2vec-training-error.png"/>
  <br />  
  <span class="plain_code mdc-text-yellow-800" style="color: #f9a825">error</span> = <span class="plain_code mdc-text-pink-400" style="color: #ec407a">target</span> - <span class="plain_code mdc-text-grey-900">sigmoid_scores</span>
</div>

<br />

这是“机器学习”的“学习”部分。现在，我们可以利用这个错误分数来调整 <span class="plain_code mdc-text-green-500" style="color: #4caf50">not</span>、<span class="plain_code mdc-text-purple-500" style="color: #9c27b0">thou</span>、<span class="plain_code mdc-text-purple-500" style="color: #9c27b0">aaron</span> 和 <span class="plain_code mdc-text-purple-500" style="color: #9c27b0">taco</span> 的嵌入，使我们下一次做出这一计算时，结果会更接近目标分数。

<div class="img-div" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/word2vec-training-update.png "/>
  <br />  
</div>

训练步骤到此结束。我们从中得到该步骤中涉及词汇的微弱改进的嵌入结果（<span class="plain_code mdc-text-green-500" style="color: #4caf50">not</span>，<span class="plain_code mdc-text-purple-500" style="color: #9c27b0">thou</span>，<span class="plain_code mdc-text-purple-500" style="color: #9c27b0">aaron</span> 和 <span class="plain_code mdc-text-purple-500" style="color: #9c27b0">taco</span>）。我们现在进行下一步（下一个相邻样本及其相关的非相邻样本），并再次执行相同的过程。

<div class="img-div" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/word2vec-training-example-2.png "/>
  <br />  
</div>

当我们循环遍历整个数据集多次时，嵌入会继续得到改进。然后我们就可以停止训练过程，丢弃 <span class="plain_code mdc-text-purple-500" style="color: #9c27b0">Context</span> 矩阵，并使用 <span class="plain_code mdc-text-green-500" style="color: #4caf50">Embeddings</span> 矩阵作为下一项任务的已被训练好的嵌入。

# 窗口大小和负样本数量

word2vec 训练过程中的两个关键超参数是窗口大小和负样本的数量。

<div class="img-div" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/word2vec-window-size.png"/>
  <br />  
</div>

不同的任务适合不同的窗口大小。一种 [启发式方法](https://youtu.be/tAxrlAVw-Tk?t=648) 是，使用较小的窗口大小（2-15）会得到这样的嵌入：两个嵌入之间的高相似性得分表明这些单词是 *可互换的*（注意，如果我们只查看附近距离很近的单词，反义词通常可以互换 —— 例如，*好的* 和 *坏的* 经常出现在类似的语境中）。使用较大的窗口大小（15-50，甚至更多）会得到相似性更能指示单词 *相关性* 的嵌入。在实际操作中，你通常需要对嵌入过程提供 [标注](https://youtu.be/ao52o9l6KGw?t=287)，使其学到符合任务需求的相似度衡量。Gensim 默认窗口大小为 5（除了输入字本身以外还包括输入字之前与之后的五个字）。

<div class="img-div" markdown="0" style="text-align: center; color: #999;justify-items: center;">
  <image src="https://alphahinex.github.io/contents/illustrated-word2vec/word2vec-negative-samples.png "/>
  <br />  
</div>

负样本的数量是训练训练过程的另一个因素。原始论文认为 5-20 个负样本是比较理想的数量。它还指出，当你拥有足够大的数据集时，2-5 个似乎就已经足够了。Gensim 默认为 5 个负样本。

# 结论

<blockquote class="subtle">
“如果它超出了你的衡量标准，那么你面对的是智能，而非自动化。”

——《沙丘神帝》
</blockquote>

我希望您现在对词嵌入和 word2vec 算法已有所了解。我也希望现在当你读到一篇提到“带有负例采样的 skip gram”（SGNS）的论文（如顶部的推荐系统论文）时，你已经对这些概念有了更好的认识。一如既往，欢迎任何反馈 <a href="https://twitter.com/JayAlammar">@JayAlammar</a>。

# 参考资料 & 延展阅读

* [Distributed Representations of Words and Phrases and their Compositionality](https://papers.nips.cc/paper/5021-distributed-representations-of-words-and-phrases-and-their-compositionality.pdf) [pdf]
* [Efficient Estimation of Word Representations in Vector Space](https://arxiv.org/pdf/1301.3781.pdf) [pdf]
* [A Neural Probabilistic Language Model](http://www.jmlr.org/papers/volume3/bengio03a/bengio03a.pdf) [pdf]
* [Speech and Language Processing](https://web.stanford.edu/~jurafsky/slp3/) by Dan Jurafsky and James H. Martin is a leading resource for NLP. Word2vec is tackled in Chapter 6.
* [Neural Network Methods in Natural Language Processing](https://www.amazon.com/Language-Processing-Synthesis-Lectures-Technologies/dp/1627052984) by [Yoav Goldberg](https://twitter.com/yoavgo) is a great read for neural NLP topics.
* [Chris McCormick](http://mccormickml.com/) has written some great blog posts about Word2vec. He also just released [The Inner Workings of word2vec](https://www.preview.nearist.ai/paid-ebook-and-tutorial), an E-book focused on the internals of word2vec.
* Want to read the code? Here are two options:
  * Gensim's [python implementation](https://github.com/RaRe-Technologies/gensim/blob/develop/gensim/models/word2vec.py) of word2vec
  * Mikolov's original [implementation in C](https://github.com/tmikolov/word2vec/blob/master/word2vec.c) -- better yet, this [version with detailed comments](https://github.com/chrisjmccormick/word2vec_commented/blob/master/word2vec.c) from Chris McCormick.
* [Evaluating distributional models of compositional semantics](http://sro.sussex.ac.uk/id/eprint/61062/1/Batchkarov,%20Miroslav%20Manov.pdf)
* [On word embeddings](http://ruder.io/word-embeddings-1/index.html), [part 2](http://ruder.io/word-embeddings-softmax/)
* [Dune](https://www.amazon.com/Dune-Frank-Herbert/dp/0441172717/)

<br />
<br />
<br />
<br />