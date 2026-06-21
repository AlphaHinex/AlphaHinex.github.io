---
id: balanced-trees
title: "【译】平衡树"
description: "介绍了三种类型的平衡树，并证明它们操作的时间复杂度都能保持在 O(log n)。"
date: 2026.06.21 10:34
categories:
    - algorithm
tags: [Data Structures, algorithm]
keywords: AVL, RBT, WBT, balanced trees, binary search trees, logarithmic complexity, self-balancing, tree structures, search, insert, delete, time complexity, black height, tree operations, tree rebalancing
cover: /contents/balanced-trees/binary-tree-768x435.jpg
---

- 原文地址：https://www.baeldung.com/cs/balanced-trees
- 原文作者：[Milos Simic](https://www.baeldung.com/cs/author/milossimic)

---

## 1. 简介

**在本教程中，我们将学习平衡二叉树。** 

特别地，我们将了解这类 [树](https://www.baeldung.com/cs/tree-structures-differences) 为何如此有用，并探索其中的三种类型。我们将讨论 AVL 树、红黑树和权重平衡树。每种类型的树都有其自身对“平衡”的定义。

## 2. 二叉树和二叉搜索树

**如果树中的每个节点最多拥有两个子节点，我们称这棵树为 [二叉树](https://www.baeldung.com/cs/binary-tree-intro)。** 一个节点的左子节点及其后代构成该节点的左子树。右子树的定义类似。

虽然适合存储层次化数据，**但这种一般形式的二叉树并不能保证快速查找**。以在下图中搜索数字 9 为例：

![Example binary tree for search illustration](https://alphahinex.github.io/contents/balanced-trees/binary-tree-768x435.jpg)

无论我们访问哪个节点，我们都不知道接下来应该遍历左子树还是右子树。这是因为这个树的层次结构并不遵循 $\le$ 的关系。

因此，**在最坏的情况下，搜索的时间复杂度为 $O(n)$，其中 $n$ 是树中的节点数。**

### 2.1. 二叉搜索树

我们通过转向一种特殊类型的二叉树来解决这个问题，称为二叉搜索树（binary search tree, BST）。**对于 BST 中的每个节点 $x$，$x$ 左子树中的所有节点的值都严格小于 $x$。进一步地，$x$ 右子树中的所有节点的值都 $\ge x$。** 例如：

![Example BST](https://alphahinex.github.io/contents/balanced-trees/binary-search-tree-768x435.jpg)

**二叉搜索树维护的这种顺序允许我们在查找过程中进行“剪枝”。** 假设我们在搜索目标值 $y$ 时访问了节点 $x < y$。我们可以忽略 $x$ 的左子树，只关注右子树，从而加快搜索速度。下图演示了如何在上述搜索树中找到 $9$：

![Search in BST](https://alphahinex.github.io/contents/balanced-trees/binary-search-tree-example-1-768x435.jpg)

然而，**在最坏的情况下，搜索的时间复杂度仍然是 $O(n)$。** 它发生在当我们从一个有序数组构建树时，此时树的高度为 $n$，并退化为链表。由于插入和删除操作都包含搜索，**在最坏情况下，BST 上的所有常见操作的时间复杂度都是 $O(n)$。** 因此，树的高度决定了复杂度。这正是平衡树发挥作用的地方。它们是一种特殊类型的二叉搜索树。

## 3. 平衡树

**平衡树是一种不仅只维护节点之间顺序的搜索树。它还控制其 [高度](https://www.baeldung.com/cs/height-balanced-tree)，确保在插入或删除后保持 $O(\log n)$ 的复杂度。**

**为此，平衡树必须在添加或删除节点后重新平衡自己。** 这会带来计算开销，并使插入和删除算法复杂化。然而，为获得具有快速搜索、插入和删除操作的对数高度的搜索树，这是我们愿意付出的代价。我们不会在本文中介绍重新平衡算法。

**此类树有几种类型。它们要求所有节点都保持平衡，但平衡的概念因类型而异。**

## 4. AVL 树

**在 [AVL 树](https://www.baeldung.com/java-avl-trees) 中，如果一个节点的左子树和右子树的高度之差最多为 1，我们称该节点是平衡的。** 因此，如果一个根节点为 $x$ 的搜索树的所有节点在 AVL 意义下都是平衡的，那么它就是一棵 AVL 树（空的搜索树，高度为 0，显然是平衡的）：

$$AVL(x) \iff |height(x.left) - height(x.right)| \leq 1 \text{ and } AVL(x.left) \text{ and } AVL(x.right) \tag{1}$$

例如：

![AVL tree example](https://alphahinex.github.io/contents/balanced-trees/A-Balanced-AVL-Tree-768x435.jpg)

这种平衡定义的一个直接结果是，AVL 树的高度在最坏情况下为 $O(\log n)$。

### 4.1. 证明高度为对数的

**当所有兄弟子树的高度都相差 1 时，AVL 树的平衡性最差。** 例如：

![Worst-case AVL tree](https://alphahinex.github.io/contents/balanced-trees/A-Minimal-AVL-tree-768x536.jpg)

这就是 AVL 树的最坏情况结构。向平衡性最差的 AVL 树中添加一个节点，我们要么得到一个非 AVL 树，要么平衡其中的一个节点。删除节点也是如此。因此，这样的 AVL 树是最小的：不存在比它节点更少但高度相同的 AVL 树。

即使我们交换节点的左右子树，树仍然保持平衡。因此，我们假设左子树的节点更多。然后，如果 $N(h)$ 是高度为 $h$ 的最小 AVL 树的节点数，我们有：

$$ N(h) = 1 + \underbrace{N(h-1)}_{\text{left sub-tree}} + \underbrace{N(h-2)}_{\text{right sub-tree}} $$

根据我们的假设，我们有 $N(h-1) \gt N(h-2)$，因此：

$$N(h) \gt 1 + 2N(h-2) \gt 2N(h-2) \gt 4N(h-4) \gt 8N(h-6) \gt ... \gt 2^{\frac{h}{2}}N(0)$$

高度为 $0$ 的 AVL 结构只有一个节点，所以 $N(0) = 1$，并且：

$$ \begin{align\*}
n &= N(h) > 2^{\frac{h}{2}} \\\\
\log_2 n &> \frac{h}{2} \\\\
h &< 2 \log_2 n \in O(\log n)
\end{align\*} $$

**因此，在最不平衡的情况下，AVL 树的高度为 $O(\log n)$。所以，搜索、插入和删除等操作的时间复杂度为对数级。**

## 5. 红黑树


[红黑树](https://www.baeldung.com/cs/red-black-trees)（Red-Black Trees, RBTs） 也平衡了兄弟子树的高度。 但是，**红黑树区分两种类型的节点：红色节点和黑色节点**。红黑树确保从一个节点到其子孙叶子的所有路径都经过相同数量的黑色节点。此外，**从一个节点到其叶子的黑色节点数量（不包括该节点）称为该节点的黑色高度**。整个红黑树的黑色高度是其根节点的黑色高度。例如（为了节省空间，将 NULL 叶子合并为一个节点）：

![Red-black tree example](https://alphahinex.github.io/contents/balanced-trees/Red-Black-Tree-768x536.jpg)

**根据定义，红黑树满足以下条件：**

- 每个节点要么是黑色，要么是红色。
- 根节点是黑色。
- 每个空节点（NULL 或 NIL）是黑色。
- 如果一个节点是红色的，那么它的两个子节点都是黑色的。
- 对于每个节点 $x$，从 $x$（不包括它自己）到其子孙叶子的路径包含相同数量的黑色节点。

有些作者不要求根节点是黑色的，因为我们可以在任何情况下重新涂色一棵树。

红黑树的性质确保：

- 从根节点到任意叶子节点的路径长度，不会超过到另一个叶子节点路径长度的两倍。
- 并且树的高度是 $O(\log n)$。

### 5.1. 证明红黑树高度是 $O(\log n)$

设 $bh(x)$ 是 $x$ 的黑色高度。我们首先通过归纳法证明，**以 $x$ 为根的子树至少包含 $2^{bh(x)} - 1$ 个内部节点**。

基本情况是 $bh(x) = 0$，这意味着 $x$ 是一个空节点，即一个叶子节点：

$$ 2^{bh(NULL)} - 1 = 2^0 - 1 = 0 $$

所以基本情况成立。在归纳步骤中，我们关注 $x$ 及其子节点。它们的黑色高度等于 $bh(x)$ 或 $bh(x) - 1$，取决于它们的颜色。根据归纳假设，它们每个至少包含 $2^{bh(x)-1} - 1$ 个节点。因此，以 $x$ 为根的整个子树至少包含这些节点：

$$ 2 \cdot (2^{bh(x)-1} - 1) + 1 = 2^{bh(x)-1+1} - 2 + 1 = 2^{bh(x)} - 1 $$

现在，设 $h$ 是根节点 $x$ 的高度。**由于红色节点只能有黑色子节点，从根到任意叶子的路径中至少有一半的节点必须是黑色的。** 因此，根的黑色高度 $\geq h/2$。

利用关于内部节点的结果，我们得到：

$$ \begin{align\*}
n & \geq 2^{\frac{h}{2}} - 1 \\\\
n + 1 & \geq 2^{\frac{h}{2}} \\\\
2^{\frac{h}{2}} & \leq n + 1 \\\\
h & \leq 2 \log_2 n + 1 \in O(\log n)
\end{align\*} $$

**同样，我们得出树的高度随着节点数量的对数增长。**

## 6. 权重平衡树

**[权重平衡树](https://www.cambridge.org/core/books/advanced-data-structures/D56E2269D7CEE969A3B8105AD5B9254C)（Weight-Balanced Trees, WBTs）不平衡兄弟子树的高度，而是平衡它们的叶子数量。** 因此，设 $x'$ 和 $x''$ 为 $x$ 的子树，并设 $leaves(x') \geq leaves(x'')$。我们说 $x$ 是平衡的，如果：

$$ \frac{leaves(x'')}{leaves(x')} \leq \beta \in (0,1) $$

我们还要求 $x$ 的所有后代节点满足相同的条件。**这等价于说明存在一个 $\alpha \in (0,1)$，使得对于树中的每个节点 $x$，以下条件成立：**

$$ \begin{align\*}
leaves(x.left) &\geq \alpha \cdot leaves(x) \\\\
leaves(x.right) &\geq \alpha \cdot leaves(x)
\end{align\*} $$

为了理解原因，让我们回忆一下 $leaves(x') > leaves(x'')$ 并跟随推导过程：

$$ \begin{align\*}
leaves(x) &= leaves(x') + leaves(x'') \\\\
&\leq 2 \beta \cdot leaves(x'') \\\\
&\implies \\\\
leaves(x'') &\geq \frac{1}{2 \beta} \cdot leaves(x)
\end{align\*} $$

所以，这就是权重平衡树 $x$ 的递归定义：

$$WBT(x) \iff leaves(x.left) \geq leaves(x) \text{ and } leaves(x.right) \geq leaves(x) \text{ and } WBT(x.left) \text{ and } WBT(x.right) \tag{2}$$

这是一个 $\alpha = 0.29$ 的 WBT 的示例（每个节点内写着叶子数量）：

![Weight-balanced tree example](https://alphahinex.github.io/contents/balanced-trees/Weight-Balanced-Tree-768x435.jpg)

树中叶子节点的总数即为其权重，这也是“权重平衡树”名称的由来。我们将证明，权重平衡树的高度同样被限制在 $\log n$。

### 6.1. 证明权重平衡树的高度是 $O(\log n)$

假设 $x$ 是一棵高度为 $h$ 的最小权重平衡树，并设 $L(h)$ 为其叶子节点的数量。根据权重平衡树的定义，我们知道 $x$ 的子树包含的叶子节点数量最多为父节点的 $1 - \alpha$ 。此外，子树的高度最多为 $h-1$。因此，我们有：

$$ \begin{align\*}
L(h - 1) &\leq (1 - \alpha) L(h) \\\\
L(h - 2) &\leq (1 - \alpha)^2 L(h) \\\\
&... \\\\
L(0) &= 1 \leq (1 - \alpha)^h L(h)
\end{align\*} $$

由于 $L(h) \leq n$，$n$ 是树中的节点数，我们有：

$$ \begin{align\*}
(1 - \alpha)^h n &\geq 1 \\\\
n &\geq (1 - \alpha)^{-h} \\\\
(1 - \alpha)^{-h} &\leq n \\\\
(\frac{1}{1-\alpha})^h &\leq n \\\\
h &\leq \log_\frac{1}{1 - \alpha} n \in O(\log n)
\end{align\*} $$

**所以，权重平衡树的高度也是节点数量的对数级别。**

### 6.2. $\alpha$ 的取值

如果我们使用过大的 $\alpha$，重新平衡可能会变得不可完成。它的值应该 $< 1 - \frac{1}{\sqrt{2}}$。

如果我们准备使用复杂的自定义重新平衡算法，我们可以使用任意小的 $\alpha$。然而，推荐使用 $\alpha \in (\frac{2}{11},1 - \frac{1}{\sqrt{2}})$。

## 7. 结论

**在本文中，我们介绍了三种类型的平衡树。** 分别是：AVL 树、红黑树和权重平衡树。**通过使用不同的平衡概念，它们都能保证查找、插入和删除操作的 [时间复杂度](https://www.baeldung.com/cs/time-vs-space-complexity) 为 $O(\log n)$。**

然而，这些树在发生更改时必须进行自我重新平衡，以使其高度保持在节点数量的对数级别。额外的工作会增加插入和删除算法的复杂度和耗时。但这种开销是值得的，因为它确保了操作的复杂度保持在 $O(\log n)$。