---
id: zero-width-space
title: "【转】你看到的事实，不一定是事实"
description: "零宽字符"
date: 2021.03.07 10:34
categories:
    - Others
tags: [Others]
keywords: 零宽字符, 零宽空格, zero width, zero width space
# cover: /contents/covers/invisible.png
---

原文地址：https://wyiyi.github.io/amber/2021/03/06/zero-width-space/

大家都熟悉的 Unicode（万国码）几乎包含 [所有符号](https://unicode-table.com/)：

* 常用的 Emoji： 😂 😸 ✌
* 颜文字：  (๑•̀ㅂ•́)  ٩(͡๏̯͡๏)۶ $_$
* 表意文字：𠁀 𡮘 𠆳 
* 国际象棋图案：♕ ♛ ♙
* 扑克牌： 🂡 🃁 🂳 
* 麻将牌： 🀄 🀝 🀇 

还有很多种玩法，比如在朋友圈火热的花式飞机坦克等。

![飞机](https://wyiyi.github.io/amber/contents/noseeunicode/huiji.jpg)

![坦克](https://wyiyi.github.io/amber/contents/noseeunicode/tanke.jpg)

一些特殊符号对应的 Unicode 编码及 HTML 代码如下：

| 图形                        |  Unicode 编码 |  HTML 代码  |
|  :-------                   |  :--------  |:---------- |
|    ◙                        |    U+25D9   |  `&#9689;` |
|    ▬                        |    U+25AC   |  `&#9644;` |
|    ▦                       |    U+25A6   |  `&#9638;` |
|    ▲                        |    U+25B2   |  `&#9650;` |
|    ●                        |    U+25CF   |  `&#9679;` |
|    ◥                       |    U+25E5   |  `&#9701;` |
|  ...                        |    ...      |   ...      |

在这些 Unicode 中，有一类特殊的字符，它们虚无缥缈，摸得着，看不见，它们就是：`零宽字符`。

## 什么是零宽字符

顾名思义，就是字节宽度为 `0` 的特殊字符。比如 [Byte-Order Mark](https://wyiyi.github.io/amber/2021/01/13/unicode/) 就是零宽字符的一种。

零宽度字符是一些不可见的，不可打印的字符。它们存在于页面中主要用于调整字符的显示格式，下面就是一些常见的零宽度字符及它们的 Unicode 码和原本用途：

- zero-width space（ZWSP）用于较长单词的换行分隔。Unicode: `U+200B`，HTML: `&#8203;`
- zero-width non-joiner（ZWNJ）放在两个字符之间，用于阻止这两个字符发生连字效果。Unicode: `U+200C`，HTML: `&#8204;`
- zero-width joiner（ZWJ）是一个控制字符，放在某些需要复杂排版语言（如阿拉伯语、印地语）的两个字符之间，使得这两个本不会发生连字的字符产生了连字效果。Unicode: `U+200D`，HTML: `&#8205;`
- Left-to-right mark（LRM）是一种控制字符，用于在混合文字方向的多种语言文本中（例：混合左至右书写的英语与右至左书写的希伯来语），规定排版文字书写方向为左至右。Unicode: `U+200E`，HTML: `&lrm;`、`&#x200E;` 或 `&#8206;`
- Right-to-left mark（RLM）是右至左控制字符，用于在混合文字方向的多种语言文本中，规定排版文字书写方向为右至左。Unicode: `U+200F`，HTML: `&rlm;`、`&#x200F;` 或 `&#8207;`
- Word joiner（WJ），自 Unicode 3.2 版本（2002 年发布）之后，替代了之前的 zero width no-break space(ZWNBSP)，用来表示不应该在此处进行单词的换行分割。Unicode: `U+2060`，HTML: `&#8288;`、`&NoBreak;`
- Byte Order Mark（BOM），表示字节顺序标识。Unicode 3.2 之后，使用 `U+FEFF` 来代表 BOM。而在 3.2 版本之前，`U+FEFF` 是用来表示 zero width no-break space（ZWNBSP）的，即不进行换行。

## 怎么输入零宽字符

可以使用 js，在浏览器 console 中解码 Unicode 编码，实现零宽字符的输入，如：

```js
> unescape('%u200e')
< "‎"
> unescape('%u2060')
< "⁠"
```

## 零宽字符应用

### 传递隐秘信息

利用零宽度字符不可见的特性，我们可以用零宽度字符在任何未对零宽度字符做过滤的网页内插入不可见的隐形文本。

安利一个[小工具](http://www.atoolbox.net/Tool.php?Id=829)。

### 隐形水印

通过零宽度字符我们可以对内部文件添加隐形水印。

在浏览者登录页面对内部文件进行浏览时，我们可以在文件的各处插入使用零宽度字符加密的浏览者信息，如果浏览者又恰好使用复制粘贴的方式在公共媒体上匿名分享了这个文件，我们就能通过嵌入在文件中的隐形水印轻松找到分享者了。

完整源码可见[仓库](https://github.com/wyiyi/bronze)。

```java
@SpringBootTest
class ZeroWidthUnicodeTest {
    private WaterMark waterMark = new WaterMark();
    private DeEncode deEncode = new DeEncode();

    @Test
    void testWaterMark() {
        String input = "测试添加水印";
        String string = "原文本：\"" + input + "\"，文本长度：" + input.length();
        String output = "原文本：\"测试添加水印\"，文本长度：6";
        assert string.equals(output);

        String watermarkInput = "抓鸭子，抓几只？";
        String string1 = "水印文本：\"" + watermarkInput + "\"，文本长度：" + watermarkInput.length();
        String watermarkOutput = "水印文本：\"抓鸭子，抓几只？\"，文本长度：8";
        assert string1.equals(watermarkOutput);

        String encode = deEncode.encode(watermarkInput);
        String waterCode = "水印编码：\"" + encode + "\"，编码长度：" + encode.length();
        String waterTextOutput = "水印编码：\"\u200C\uFEFF\u200B\uFEFF\u200B\uFEFF\u200C\uFEFF\u200C\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200C\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200C\uFEFF\u200C\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200C\uFEFF\u200C\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200B\uFEFF\u200B\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200B\uFEFF\u200B\uFEFF\u200C\uFEFF\u200B\uFEFF\u200B\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200C\uFEFF\u200C\uFEFF\u200C\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200C\uFEFF\u200C\uFEFF\u200C\uFEFF\u200C\uFEFF\u200B\uFEFF\u200B\uFEFF\u200C\uFEFF\u200C\uFEFF\u200C\uFEFF\u200B\uFEFF\u200B\uFEFF\u200C\uFEFF\u200C\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200C\uFEFF\u200B\uFEFF\u200B\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200C\uFEFF\u200C\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200C\uFEFF\u200C\uFEFF\u200C\uFEFF\u200C\uFEFF\u200C\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200C\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200C\uFEFF\u200C\uFEFF\u200C\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\"，编码长度：256";
        assert waterCode.equals(waterTextOutput);


        String result = waterMark.addWatermark(input, encode, CodeUtil.WATERMARK_POS_HEAD);
        String resultOutput = "输出：\"" + result + "\"，文本长度：" + result.length();
        String resultTrue = "输出：\"\u200C\uFEFF\u200B\uFEFF\u200B\uFEFF\u200C\uFEFF\u200C\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200C\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200C\uFEFF\u200C\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200C\uFEFF\u200C\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200B\uFEFF\u200B\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200B\uFEFF\u200B\uFEFF\u200C\uFEFF\u200B\uFEFF\u200B\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200C\uFEFF\u200C\uFEFF\u200C\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200C\uFEFF\u200C\uFEFF\u200C\uFEFF\u200C\uFEFF\u200B\uFEFF\u200B\uFEFF\u200C\uFEFF\u200C\uFEFF\u200C\uFEFF\u200B\uFEFF\u200B\uFEFF\u200C\uFEFF\u200C\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200C\uFEFF\u200B\uFEFF\u200B\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200C\uFEFF\u200C\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200C\uFEFF\u200C\uFEFF\u200C\uFEFF\u200C\uFEFF\u200C\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200C\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200B\uFEFF\u200C\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200C\uFEFF\u200C\uFEFF\u200C\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF\u200B\uFEFF测试添加水印\"，文本长度：262";
        assert resultOutput.equals(resultTrue);

        result = waterMark.extractWatermark(result, CodeUtil.WATERMARK_POS_HEAD);
        String watermark = deEncode.decode(result);
        assert watermarkInput.equals(watermark);
    }
}
```

### 逃脱关键字过滤

通过零宽度字符我们可以轻松逃脱关键字过滤。关键字自动过滤是维持互联网社区秩序的一项重要工具，只需导入关键字库和匹配相应关键字，即可将大量的预设关键字拒之门外。使用谐音与拼音来逃脱关键字过滤会让语言传递信息的效率降低，而使用零宽度字符可以在逃脱关键字过滤的同时将词义原封不动地传达给接受者，大大提高信息传播者与接受者之间交流的效率。

```js
const sensitive = '关键字'
// 利用零宽度字符 zero-width joiner U+200D 来分隔关键字 
sensitive.replace(/关键字/g, '‍')
// 使用零宽度空格 zero-width space U+200B对字符串进行分隔
Array.from(sensitive).join('​').replace(/关键字/g, '')
```

**小心零宽字符带来的困扰，同时也可以很好的利用零宽字符！**

## 参考资料

* [零宽度字符：和谐？屏蔽？不存在的](https://juejin.cn/post/6844903669192720391)
* [Zero width space](https://en.wikipedia.org/wiki/Zero-width_space)
* [Zero with non joiner](https://en.wikipedia.org/wiki/Zero-width_non-joiner)
* [Zero width joiner](https://en.wikipedia.org/wiki/Zero-width_joiner)
* [Word joiner](https://en.wikipedia.org/wiki/Word_joiner)
* [Byte order mark](https://en.wikipedia.org/wiki/Byte_order_mark)