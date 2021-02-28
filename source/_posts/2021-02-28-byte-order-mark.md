---
id: byte-order-mark
title: "【转】都是 “编码格式” 惹得祸"
description: "很多事来不及思考，就这样自然发生了"
date: 2021.02.28 10:26
categories:
    - Others
tags: [Others]
keywords: BOM, UTF8 with BOM, byte order mark
cover: /contents/covers/bom.png
---

原文地址：https://wyiyi.github.io/amber/2021/01/13/unicode/

遇到的问题：在单元测试中执行sql文件，sql的内容是正确的，但是执行报错。扎心。

重现该场景，关键代码如下：完整实例可见[仓库](https://github.com/wyiyi/bronze) 

```java
@SpringBootTest
class DemoTest {

    @BeforeEach
    @Sql("/com/amber/demo/init.sql")
    // 建表语句： drop table if exists USER; create table USER(ID int(11) NOT NULL AUTO_INCREMENT, NAME VARCHAR, SEX  VARCHAR,ADDR VARCHAR);
    void test(){
       assert true;
    }

    @Test
    @Sql("/com/amber/demo/insert.sql")
    // insert语句：INSERT INTO USER(ID, NAME, SEX, ADDR) VALUES (1, 'liming', 'men', 'jinzhou')
    void insert(){
        assert true;
    }

    @Ignore
    @Sql("/com/amber/demo/utf8bom.sql")
    // insert语句：INSERT INTO USER(ID, NAME, SEX, ADDR) VALUES (2, 'anc', 'man', 'shanghai')，保存为 UTF-8 with BOM 的编码格式，失败
    void testBom(){
        Exception exception = assertThrows(RuntimeException.class, () -> {
            Integer.parseInt("1a");
        });

        String expectedMessage = "Failed to execute SQL script statement";
        String actualMessage = exception.getMessage();

        assertTrue(actualMessage.contains(expectedMessage));

    }
}
```

在执行`testBom()`的过程中报错如下：
```text
org.springframework.jdbc.datasource.init.ScriptStatementFailedException: Failed to execute SQL script statement #1 of class path resource [com/amber/demo/utf8bom.sql]: 锘縄NSERT INTO USER(ID, NAME, SEX, ADDR) VALUES (2, 'anc', 'man', 'shanghai'); nested exception is org.h2.jdbc.JdbcSQLSyntaxErrorException: Syntax error in SQL statement "锘縄NSERT[*] INTO USER(ID, NAME, SEX, ADDR) VALUES (2, 'anc', 'man', 'shanghai')";
```

根据日志发现多了一些乱码的字符，将sql的文件以十六进制打开后，发现在开头处有多余的字符 `EF BB BF`（文件编码格式显示为 `UTF-8 with BOM`），将文件重新保存成UTF-8的编码格式，执行成功。

原来是 BOM 在作祟。 

### 什么是 BOM 

`BOM(Byte-Order Mark)`即字节顺序标记，出现在文本文件头部， Unicode编码标准中用于标识文件是采用哪种格式的编码，但它对于文件的读者来说是不可见字符。

摘自[Wikipedia](https://en.wikipedia.org/wiki/Byte_order_mark)： 

> The byte order mark (BOM) is a particular usage of the special Unicode character, U+FEFF BYTE ORDER MARK, whose appearance as a magic number at the start of a text stream can signal several things to a program reading the text:[1]
> - The byte order, or endianness, of the text stream in the cases of 16-bit and 32-bit encodings;
> - The fact that the text stream's encoding is Unicode, to a high level of confidence;
> - Which Unicode character encoding is used.
BOM use is optional. Its presence interferes with the use of UTF-8 by software that does not expect non-ASCII bytes at the start of a file but that could otherwise handle the text stream.

摘自[Unicode](http://www.unicode.org/faq/utf_bom.html#bom1)： 

> A: A byte order mark (BOM) consists of the character code U+FEFF at the beginning of a data stream, where it can be used as a signature defining the byte order and encoding form, primarily of unmarked plaintext files. Under some higher level protocols, use of a BOM may be mandatory (or prohibited) in the Unicode data stream defined in that protocol. [AF]


### 为什么会存在 BOM
- UTF-16、UTF-32是以2个字节和4个字节为单位进行处理的， 即1次读取2个字节或4个字节， 这样一来， 在存储和网络传输时就要考虑1个单位内2个字节或4个字节之间顺序的问题。
- UTF-8编码是以1个字节为单位进行处理的，不会受CPU大小端的影响。UTF-8 不需要 BOM 来表明字节顺序， 但可以用 BOM 来表明编码方式。 字符 “Zero Width No-Break Space” 的 UTF-8 编码是 EF BB BF。 
所以如果接收者收到以 EF BB BF 开头的字节流， 就知道这是 UTF-8编码了。 Windows 就是使用 BOM 来标记文本文件的编码方式的。 


### UTF-8 BOM 长什么样
- 无论 Unicode 文本如何转换， BOM都可以用作签名： UTF-8， UTF-16， 或UTF-32等。包含BOM的字节将是由该转换格式转换为Unicode字符 `U + FEFF` 的任何字节。 
在下列表格中， 表示BOM 的 Unicode 以及它的十六进制。

| 编码        |  表示（十六进制）|
|  :--------  |  :----------    |
| UTF-8       |   EF BB BF      |
| UTF-16 (BE) |   FE FF         |
| UTF-16 (LE) |   FF FE         |
| UTF-32 (BE) |   00 00 FE FF   |
| UTF-32 (LE) |   FF FE 00 00   | 
| UTF-7       |   2B 2F 76      | 
| UTF-1       |   F7 64 4C      | 
| UTF-EBCDIC  |   DD 73 66 73   | 
| SCSU        |   0E FE FF      | 
| ...         |   ...           |

### 怎么查看 BOM

1. BOM 头在记事本中是看不到的，可以使用以下工具查看，文本中字符内容均为 abc ：

- 使用十六进制编辑工具进行查看
- 亦可使用Total Commander 文件管理工具， 查看文件， 选择options， 即可查看各种Unicode格式
   - 以 UTF-8 BOM [bom.txt](https://github.com/wyiyi/amber/blob/master/contents/unicode/bom.txt) 的文件为例，通过Total Commander 的 options， 则可以看到字符头：
    `EF BB BF 61 62 63 ...`。
   - 以 UTF-16 或者 UTF-32 big-endian [16be.txt](https://github.com/wyiyi/amber/blob/master/contents/unicode/16be.txt) 的文件为例，看到的字符头显示为：
    `FE FF 00 61 00 62 00 63 ...`。
   - 以 UTF-16 或者 UTF-32 little-endian [16le.txt](https://github.com/wyiyi/amber/blob/master/contents/unicode/16le.txt) 的文件为例，看到的字符头显示为：
    `FF FE 61 00 62 00 63 00 ...`。

2.在linux 中查看 BOM
- 找到对应的文件位置
- 查找当前包含 BOM 头的文件： 
```bash
$ grep -r $'^\xEF\xBB\xBF'
bom.txt：abc
```
- 查看文件相关信息

```bash
$ ll bom.txt
-rw-rw-r-- 1 xxx xxx 6 Dec 18 16:22 bom.txt
$ file bom.txt
bom.txt: UTF-8 Unicode text, with no line terminators
$ file 16be.txt
16be.txt: Big-endian UTF-16 Unicode text, with no line terminators
...
```

- 使用 `vi` 打开查看文件内容
- 查看`bom.txt`文件的十六进制`:%!xxd`显示内容：
  `0000000: efbb bf61 6263 0a   ... abc.`
其中包含`EF BB BF` 即为 BOM 标记

### 如何添加或去掉 BOM
1.Windows BOM 操作： 
- 增加 BOM 编码格式：
  新建一个文件，输入 `abc` 保存时选择使用 UTF-8、UTF-8 with BOM、UTF-16 LE 或者 UTF-16 BE 等格式（以 VS Code 为例）
- 去掉 BOM 编码格式：
  可通过程序控制过滤掉BOM：存在 BOM 字符相关则去掉

2.linux BOM  命令操作：

- utf8.txt 加上 BOM 的编码格式

```bash
$ file utf8.txt
utf8.txt: ASCII text, with no line terminators
# 用 vi 打开文件 
# 设置 bom 格式，执行命令 :set bomb
# 保存并退出 vi :wq!
$ file utf8.txt
utf8.txt: UTF-8 Unicode (with BOM) text
```

- bom.txt 去掉 BOM 的编码格式

```bash
$ file bom.txt
bom.txt: UTF-8 Unicode (with BOM) text, with no line terminators
# 用 vi 打开文件
# 设置无 bom 格式， 执行命令 :set nobomb
# 保存并退出 vi，执行命令 :wq!
$ file bom.txt
bom.txt: ASCII text
```

- bom.txt 的 UTF-8 with BOM 编码格式修改为 UTF-16 Little-endian 或者 UTF-16 Big-endian 的编码格式

```bash
$ file bom.txt
bom.txt: UTF-8 Unicode (with BOM) text, with no line terminators
# 用 vi 打开文件 
# 设置 UTF-16 Little-endian 格式，执行命令 :set fileencoding=utf-16le
# 保存并退出 vi :wq!
$ file bom.txt
bom.txt: Little-endian UTF-16 Unicode text, with no line terminators

# 设置 UTF-16 Big-endian 格式，执行命令① :set fileencoding=utf-16 或者② :set fileencoding=utf-16be
# 保存并退出 vi :wq!
$ file bom.txt
bom.txt: Big-endian UTF-16 Unicode text
...
```

### Linux 和 Windows 关于 BOM 的区别

- Linux 默认的编码格式为 [UTF-8](https://unix.stackexchange.com/questions/112216/which-terminal-encodings-are-default-on-linux-and-which-are-most-common#:~:text=The%20default%20encoding%20for%20new%20Debian%20GNU%2FLinux%20installations,and%20many%20other%29%20are%20utf-8%20capable%20by%20default.)。
Linux 保存文件的编码格式为UTF-8，如：[abc.txt](https://github.com/wyiyi/amber/blob/master/contents/unicode/abc.txt) 查看编码格式：
`abc.txt: UTF-8 Unicode text`
- Windows 默认的编码格式为 [GBK](https://stackoverflow.com/questions/16602900/why-is-my-java-charset-defaultcharset-gbk-and-not-unicode)。
Windows 自带的记事本等软件， 在保存一个以UTF-8编码的文件时， 会在文件开始的地方插入三个不可见的字符（0xEF 0xBB 0xBF， 即BOM）。 如： [utf8.txt](https://github.com/wyiyi/amber/blob/master/contents/unicode/utf8.txt)

### BOM  不是明智的选择

UTF-8 BOM  是文本流（0xEF、0xBB、0xBF） 开始时的字节序列，允许读取器更可靠地猜测文件在 UTF-8 中编码。

虽然BOM字符起到了标记文件编码的作用但它并不属于文件的内容部分， 所以会产生一些问题：

1. BOM 用来表示编码的字节序，但是由于字节序对 UTF-8 无效，因此不需要 BOM。
1. BOM 不仅在 JSON 中非法且破坏了JSON 解析器。
1. BOM 会阻断一些脚本： Shell scripts， Perl scripts， Python scripts， Ruby scripts， Node.js。
1. BOM 对 PHP 很不友好： PHP 不能识别 BOM 头，且不会忽略BOM， 所以在读取、包含或者引用这些文件时，会把BOM作为该文件开头正文的一部分。 根据嵌入式语言的特点， 这串字符将被直接执行（显示）出来。 由于页面的 `top padding` 为0， 导致无法让整个网页紧贴浏览器顶部。

#### 2.6 Encoding Schemes

> ... Use of a BOM  is neither required nor recommended for UTF-8, but may be encountered in contexts where UTF-8 data is converted from other encoding forms that use a BOM  or where the BOM  is used as a UTF-8 signature.
> 
> See the "Byte Order Mark" subsection in Section 16.8, Specials, for more information.

根据 [Unicode标准](http://www.unicode.org/versions/Unicode5.0.0/ch02.pdf) 不建议使用 UTF-8 文件的 BOM，所以在将文件保存为 UTF-8 的编码格式时，一定要注意一般不使用 UTF-8 with BOM 的编码格式。