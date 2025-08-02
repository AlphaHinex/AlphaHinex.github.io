---
id: double-pointers
title: "【转】【算法专题突破】双指针 - 有效三角形的个数（5）"
description: "排序后，倒序遍历最大值配合双指针，降低整体算法时间复杂度"
date: 2025.08.03 10:34
categories:
    - algorithm
tags: [algorithm]
keywords: 算法双指针, 算法指针, 指针三角形, 算法三角形, 算法双指针三角形
cover: /contents/double-pointers/problem.png
---

- 原文地址：https://developer.aliyun.com/article/1363712
- 原文作者：[戊子仲秋](https://developer.aliyun.com/profile/w73sboktmi6qk/article_1?spm=a2c6h.12873639.article_author.d_article_author_article.62cd99e0oLRoNX)

## 1. 题目解析

题目链接：[611. 有效三角形的个数 - 力扣（Leetcode）](https://leetcode.cn/problems/valid-triangle-number/?spm=a2c6h.12873639.article-detail.4.62cd99e0oLRoNX)

![problem](https://alphahinex.github.io/contents/double-pointers/problem.png)

我们可以根据示例1来理解这一道题目，<br>
他说数组里面的数可以组成三角形三条边的个数，<br>
那我们先自己枚举一下所有情况看看：<br>
 【2， 2， 3】<br>
 【2， 2， 4】<br>
 【2， 3， 4】<br>
 【2， 3， 4】<br>
总共是四种情况，<br>
而第二种情况是不成立的，看看示例，我们可以知道，虽然都是2，<br>
但是不同位置可以看成不同的元素。

## 2. 算法原理

一开始我们看到这样的题目，实际上第一个想到的解法就是暴力枚举，<br>
把所有情况枚举一遍然后判断，但是这是一个O(N3)的解法，<br>
我们可以通过单调性和双指针的方式来优化我们的时间复杂度，<br>
具体思路如下：
1. 通过sort 找到最大值
2. 使用双指针快速求出符合题目要求的数

具体操作如下：<br>
以这个排好序的数组为例：

![array](https://alphahinex.github.io/contents/double-pointers/array.png)

左指针指向最小的元素，右指针指向最大元素的左边元素，<br>
跟据三角形两边之和需要大于第三边的性质，

![first position](https://alphahinex.github.io/contents/double-pointers/first_position.png)

如果 2 + 9 > 10，就证明 3 + 9，4 + 9 等等情况都会大于10，<br>
这样我们就直接计算出 right - left 种适合的情况，<br>
这样就能让所有的数都跟 9 结合过了，就让 right--。

![second position](https://alphahinex.github.io/contents/double-pointers/second_position.png)

如果 2 + 5 <= 10，就证明无论是 2 + 4 还是 2 + 3 等等情况，都会<=10，<br>
所以我们就能直接让 left++，去找更大的数。<br>
最后等left 和 right 相撞，就能求出所有适合的情况了。 

## 3. 代码编写

```c++
class Solution {
public:
    int triangleNumber(vector<int>& nums) {
        int ans = 0;
        sort(nums.begin(), nums.end());
        for(int i = nums.size() - 1; i > 1; i--) {
            int left = 0, right = i - 1;
            while(left < right) {
                if(nums[left] + nums[right] > nums[i]) {
                    ans += (right - left);
                    right--;
                }
                else left++;
            }
        }
        return ans;
    }
};
```

## 写在最后：

以上就是本篇文章的内容了，感谢你的阅读。<br>
如果感到有所收获的话可以给博主点一个**赞**哦。<br>
如果文章内容有遗漏或者错误的地方欢迎私信博主或者在评论区指出~