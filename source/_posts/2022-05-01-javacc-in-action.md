---
id: javacc-in-action
title: "JavaCC 实战"
description: "JavaCC 介绍、用法及实例"
date: 2022.05.01 10:34
categories:
    - Others
tags: [JavaCC]
keywords: JavaCC, compiler, parser, BNF, EBNF
cover: /contents/covers/javacc-in-action.png
---

JavaCC
======

Java Compiler Compiler (JavaCC) 是一个语法解释器生成工具，可以读取语法规则，并将其转换为能够识别这些语法的 Java 程序。

比如通过 Java 程序解析 Structured Query Language (SQL)。

语法规则使用类似 [如何描述一种语言？](https://alphahinex.github.io/2022/04/24/bnf-ebnf/) 中介绍的 EBNF 规范进行描述，组织为 `.jj` 格式的文件。

JavaCC 发布包是 JAR 格式，可以通过 Java 命令直接执行，读取 `.jj` 文件，并根据其生成可运行的 Java 代码，实现对符合语法规则的内容的解析。

生成的 Java 代码只需要 JRE 运行环境，没有额外依赖。

语法文件格式
----------

一个 `.jj` 语法文件格式如下：

```bnf
javacc_input ::= javacc_options
                 "PARSER_BEGIN" "(" identifier ")"
                 CompilationUnit
                 "PARSER_END" "(" identifier ")"
                 ( production )+
                 <EOF>
```

分为三部分：

### `javacc_options`

```bnf
javacc_options ::= [ "options" "{" ( option-binding )*; "}" ]
```

JavaCC 的配置选项，整个部分为可选的，可以在 `.jj` 文件中指定，也可以在生成 Java 代码时通过命令行参数指定。

可以指定生成 DEBUG 信息、生成非静态类等，完整的可用参数可以通过命令行获得，如：

```bash
$ java -classpath javacc-7.0.11.jar javacc
```

或者查看 [JavaCC Grammar](https://javacc.github.io/javacc/documentation/grammar.html) 语法文档。

### `PARSER_BEGIN` ~ `PARSER_END`

```bnf
identifier ::= <IDENTIFIER>

CompilationUnit ::= ( PackageDeclaration )?
                    ( ImportDeclaration )*
                    ( TypeDeclaration )*
```

解析器类定义，`identifier` 需与 `CompilationUnit` 中类名一致，如：

```java
PARSER_BEGIN(Example)

/** Simple brace matcher. */
public class Example {

  /** Main entry point. */
  public static void main(String args[]) throws ParseException {
    Example parser = new Example(System.in);
    parser.Input();
  }

}

PARSER_END(Example)
```

### `production`

```bnf
production ::= javacode_production
             | cppcode_production
             | regular_expr_production
             | token_manager_decls
             | bnf_production
```

`production` 部分即为最重要的词法和语法规则描述。

JavaCC 将词法规则（如保留字、表达式）和语法规则（BNF）都统一写在一个文件中，并支持使用正则表达式，使语法描述文件易读且易于维护。

词法规则一般通过 `regular_expr_production` 部分进行描述，
常用 `SKIP` 定义需要忽略的内容（如空格、换行等），`TOKEN` 定义语法中的保留字等，
每个部分都可以出现多次，便于将内容分类放置，如：

```jj
SKIP :
{
  " "
| "\t"
| "\n"
| "\r"
}

TOKEN:
{
    <TODO: "TODO">
|   <USE: "USE">
|   <CREATE: "CREATE">
}

TOKEN:
{
    <S_BIT_FORMAT1: "b" "'" (["0", "1"])+ "'">
|   <S_BIT_FORMAT2: "0" "b" (["0", "1"])+>
}
```

语法规则一般通过 `bnf_production` 部分描述，`bnf_production` 的 BNF 如下：

```bnf
bnf_production ::= AccessModifier
                   ResultType
                   identifier
                   FormalParameters ( "throws" Name ( "," Name )* )?
                   ":"
                   Block
                   "{" expansion_choices "}"
```

能够支持复杂的语法描述，简单的实例如下：

```jj
void Input() :
{}
{
  MatchedBraces() ("\n"|"\r")* <EOF>
}
```

```jj
SqlStatement SetVariableStatement():
{
    Assignment assignment;
}
{
    (
        <SET> assignment = Assignment()
    )
    {
        return new SetVariableStatement(assignment);
    }
}
```

上面两个实例中的第一行可以理解为 Java 中的方法签名，会对应到生成的 Parser 类中的方法。
下面的 `{}` 中可以定义一些变量，供最后一组 `{}` 中的内容使用。
最后一组 `{}` 中定义该规则会匹配的内容，以及方法的返回值（可选）。

完整的 JavaCC BNF 描述可见 [官方文档](https://javacc.github.io/javacc/documentation/bnf.html) 。

一个简单的，可以解析成对的大括号以及内嵌的成对大括号的 `Example.jj` 语法文件完整实例如下：

```jj
PARSER_BEGIN(Example)

/** Simple brace matcher. */
public class Example {

  /** Main entry point. */
  public static void main(String args[]) throws ParseException {
    Example parser = new Example(System.in);
    parser.Input();
  }

}

PARSER_END(Example)

/** Root production. */
void Input() :
{}
{
  MatchedBraces() ("\n"|"\r")* <EOF>
}

/** Brace matching production. */
void MatchedBraces() :
{}
{
  "{" [ MatchedBraces() ] "}"
}
```

用法
---

有了 `.jj` 文件，接下来让我们看看如何使用其生成解析器的代码。

以上面的 `Example.jj` 为例，我们可以按如下方式生成解析器：

```bash
$ java -classpath /path/to/javacc-7.0.11.jar javacc Example.jj
Java Compiler Compiler Version 7.0.11 (Parser Generator)
(type "javacc" with no arguments for help)
Reading from file Example.jj . . .
File "TokenMgrError.java" does not exist.  Will create one.
File "ParseException.java" does not exist.  Will create one.
File "Token.java" does not exist.  Will create one.
File "SimpleCharStream.java" does not exist.  Will create one.
Parser generated successfully.
$ tree
.
├── Example.java
├── Example.jj
├── ExampleConstants.java
├── ExampleTokenManager.java
├── ParseException.java
├── SimpleCharStream.java
├── Token.java
└── TokenMgrError.java

0 directories, 8 files
```

可以看到根据 `Example.jj` 文件生成了七个 Java 文件，可以直接编译运行：

```bash
$ javac Example.java
$ java Example
{}}
Exception in thread "main" ParseException: Encountered " "}" "} "" at line 1, column 3.
Was expecting one of:
    <EOF>
    "\n" ...
    "\r" ...

	at Example.generateParseException(Example.java:247)
	at Example.jj_consume_token(Example.java:185)
	at Example.Input(Example.java:42)
	at Example.main(Example.java:9)
```

输入数量不匹配的大括号时，会抛出 `ParseException` 异常。

为了观察语法规则匹配情况，可以在使用 JavaCC 生成解析器时，添加 `-debug_parser` 参数，之后编译运行，可以看到输入 `{}` 的匹配日志：

```bash
$ java -classpath /Users/alphahinex/github/origin/javacc-demo/lib/javacc-7.0.11.jar javacc -debug_parser Example.jj
Java Compiler Compiler Version 7.0.11 (Parser Generator)
(type "javacc" with no arguments for help)
Reading from file Example.jj . . .
File "TokenMgrError.java" is being rebuilt.
File "ParseException.java" is being rebuilt.
File "Token.java" is being rebuilt.
File "SimpleCharStream.java" is being rebuilt.
Parser generated successfully.
$ javac Example.java
$ java Example
Call:	Input
  Call:	MatchedBraces
{}
    Consumed token: <"{" at line 1 column 1>
    Consumed token: <"}" at line 1 column 2>
  Return: MatchedBraces
  Consumed token: <"\n": "\n" at line 1 column 3>
  Consumed token: <<EOF> at line 1 column 3>
Return: Input
```

> 注意：`<EOF>` 可通过 `Control`+`D` 输入，表示到达了文件或输入的结尾。


基本概念
-------

为了能够更好的理解或编写 `.jj` 文件，我们需要了解一些基本的概念。

### TokenManager

JavaCC 的词法规则是由一组词法状态（Lexical State）组成的，每个词法状态有一个唯一的标识，可以将词法状态理解为语法中所需要识别的最小单位。Token Manager 按照语法规则描述，以词法状态为单位进行状态的变迁，所以在任意时刻 Token Manager 都是处在这些词法状态的某一个状态中。Token Manager 类在初始化时，默认是从一个标准的 `DEFAULT` 词法状态开始，也可以通过构造参数指定其他词法状态。

在进行 Token 的匹配时，Token Manager 会尽可能的寻找最长的匹配内容。如果存在相同长度的最长匹配内容，会按照在语法描述文件中出现的先后顺序，选择先出现的内容作为最佳匹配结果。

在完成一个词法状态的匹配后，可以指定一个词法动作（Lexical Action），也可以迁移到一个新的词法状态中，如果没有指定新的词法状态，Token Manager 会继续留在之前的状态中。

更多说明请见官方文档：https://javacc.github.io/javacc/tutorials/token-manager.html

### LOOKAHEAD

以下面的语法描述为例：

```jj
void Input() :
{}
{
  "a" BC() "c"
}

void BC() :
{}
{
  "b" [ "c" ]
}
```

按照语法描述，这个解析器应该会识别 `abc` 和 `abcc` 两个输入内容。当我们使用 `abc` 作为输入进行语法解析时，一般的解析过程大致如下：

Step：
1. 第一个字符为 `a`，与 `Input` 中的 `a` 匹配
2. 接下来会进入到 `BC` 中，第二个字符 `b` 与 `BC` 中的 `b` 匹配
3. 此时，我们来到了语法中的一个选择点：`BC` 中的 `["c"]` 为可选内容，所以既可以选择继续在 `BC` 中尝试匹配，也可以跳出 `BC` 回到 `Input` 中尝试继续匹配。我们选择继续留在 `BC` 中，此时需要一个 `c`，输入中的第三个字符 `c` 可以匹配
4. 现在我们完成了非终止符 `BC` 的匹配，继续回到 `Input` 中尝试匹配。语法中要求此时还应该有一个 `c`，但我们已经没有输入的字符了
5. 当我们遇到类似这样的场景时，意味着我们在之前的选择点中做出了错误的选择。我们回到做出这个错误选择的第三步，并尝试做出不同的选择，这个过程称为回溯（backtracking）
6. 我们现在回到了步骤三的状态，并做出不同的选择，即不继续留在 `BC` 中，而是返回到 `Input` 中继续进行匹配。此时语法要求一个 `c`，而我们输入的第三个字符恰好是 `c`
7. 我们成功抵达了 `Input` 的最后状态，这意味着输入的字符串 `abc` 成功匹配了 `Input` 语法

我们按照上面描述的一般解析过程可以看到，一个输入的解析可能会导致大量的回溯操作，这会消耗很多时间，对于解析器而言，这样的回溯耗时是不能接受的，所以大部分解析器不会按照上面描述的方式进行回溯，甚至选择根本不回溯，它们会根据在选择点时能够得到的有限信息直接进行决策。

JavaCC 处理这类问题的方式，是向前多看一些 Token，以便做出更好的决定，在 JavaCC 中，称为 `LOOKAHEAD`，默认的行为是向前多看一个 Token，即 `LOOKAHEAD(1)`。这种从左向右扫描输入，分析过程使用最左推导的方式统称为 [LL 语法](https://en.wikipedia.org/wiki/LL_grammar)，JavaCC 的 `LOOKAHEAD(1)` 即为 `LL(1)`。

通过 `javacc_options` 部分或命令行参数，可以调整全局的 `LOOKAHEAD` 为更大的值，也可以针对某个语法指定局部的 `LOOKAHEAD` 值。

更多说明请见官方文档：https://javacc.github.io/javacc/tutorials/lookahead.html


实例
====

求和(100,23)
-----------

一个简单的整数求和中文公式解析器实例，语法文件 [SumParser.jj](https://github.com/AlphaHinex/javacc-demo/blob/main/src/main/javacc/SumParser.jj)：

```jj
options {
    DEBUG_PARSER = true;
    UNICODE_INPUT = true;
    STATIC = false;
}

PARSER_BEGIN(SumParser)
package io.github.alphahinex.javacc.demo.sum;

/** Simple brace matcher. */
public class SumParser {

  /** Main entry point. */
  public static void main(String args[]) throws ParseException {
    SumParser parser = new SumParser(System.in);
    System.out.println(parser.Sum());
  }

}
PARSER_END(SumParser)

SKIP : {
      " "
    | "\t"
    | "\n"
    | "\r"
}

TOKEN : {
      <SUM: "求和">
    | <INTEGER: (["+","-"])? ["1"-"9"] (["0"-"9"])*>
}

/** Root production. */
int Sum() :
{
    int left;
    int right;
}
{
  <SUM> "(" left=Integer() "," right=Integer() ")" { return left + right; }
}

int Integer() :
{
    Token tk;
}
{
    tk = <INTEGER> { return Integer.parseInt(tk.image); }
}
```

[单元测试](https://github.com/AlphaHinex/javacc-demo/blob/main/src/test/groovy/org/javacc/tutorials/example/SumParserSpec.groovy)：

```groovy
class SumParserSpec extends Specification {

    @Unroll
    def '#formula = #result'() {
        expect:
        new SumParser(new ByteArrayInputStream(formula.getBytes())).Sum() == result

        where:
        formula         | result
        '求和(100,23)'   | 123
        '求和(-100, 23)'  | -77
    }

}
```

AbccParser
----------

在官方文档中，介绍了一种 [Semantic LOOKAHEAD](https://javacc.github.io/javacc/tutorials/lookahead.html#semantic) 的方式解决 [Example1](https://javacc.github.io/javacc/tutorials/lookahead.html#example1) 只能匹配 `abcc` 而不能匹配 `abc` 的问题。

但从 [单元测试](https://github.com/AlphaHinex/javacc-demo/blob/main/src/test/groovy/org/javacc/tutorials/example/TutorialSpec.groovy#L19-L27) 的实际执行结果来看，在解析 `abc` 时，依然会抛出解析异常。

```groovy
def 'Semantic.jj still only match `abcc`, could not match `abc`'() {
    expect:
    new Semantic(new ByteArrayInputStream('abcc'.getBytes())).Input()

    when:
    new Semantic(new ByteArrayInputStream('abc'.getBytes())).Input()
    then:
    thrown(org.javacc.tutorials.semantic.ParseException)
}
```

[这里](https://github.com/AlphaHinex/javacc-demo/blob/main/src/main/javacc/AbccParser.jj) 给出了一个能够同时解析 `abc` 和 `abcc` 的语法描述，修改了官方文档例子中的 `getToken(2).kind != C` 为 `getToken(2).kind == C`：

```jj
void BC() :
{}
{
  "b"
  [
    LOOKAHEAD( "c", { getToken(2).kind == C } )
    <C:"c">
  ]
}
```

[测试用例](https://github.com/AlphaHinex/javacc-demo/blob/main/src/test/groovy/org/javacc/tutorials/example/TutorialSpec.groovy#L29-L33) 如下：

```groovy
def 'AbccParser.jj could match both `abcc` and `abc`'() {
    expect:
    new AbccParser(new ByteArrayInputStream('abcc'.getBytes())).Input()
    new AbccParser(new ByteArrayInputStream('abc'.getBytes())).Input()
}
```

MySQL Parser
------------

[AlphaHinex/mysql2h2-converter](https://github.com/AlphaHinex/mysql2h2-converter) 是从 [andrewparmet/mysql2h2-converter](https://github.com/andrewparmet/mysql2h2-converter) fork 的一个仓库，在 [sqlgrammar.jj](https://github.com/AlphaHinex/mysql2h2-converter/blob/enhance/parser/src/main/javacc/sqlgrammar.jj) 文件中补充了对 MySQL 语法的一些支持，使该库可以适应更多的 SQL 转换场景。

可从下面单元测试中新增加的用例，了解增加的语法支持：

```diff
 package com.granveaud.mysql2h2converter.parser;

 import org.junit.Test;

 import com.granveaud.mysql2h2converter.SQLParserManager;
@@ -61,18 +62,39 @@ public class BasicTest {
                 "t1 int(10) NOT NULL AUTO_INCREMENT," +
                 "t2 int(10) NOT NULL," +
                 "t3 varchar(55) DEFAULT ''," +
-                "PRIMARY KEY (t1)," +
+                "t4 datetime DEFAULT ''," +
+                "t5 datetime(0) DEFAULT ''," +
+                "PRIMARY KEY (t1) USING BTREE," +
                 "UNIQUE KEY u1 (t1,t2)," +
                 "KEY k1 (t2)," +
-                "CONSTRAINT c1 FOREIGN KEY (t2) REFERENCES test2 (t2) ON DELETE CASCADE" +
-                ") ENGINE=InnoDB DEFAULT CHARSET=utf8";
+                "CONSTRAINT c1 FOREIGN KEY (t2) REFERENCES test2 (t2) ON DELETE CASCADE," +
+                "UNIQUE INDEX `UNIQUE_NAME_NAMESPACES` (`NAME`,`NAMESPACE`) USING BTREE" +
+                ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci";
         assertStatementEquals(str);
+
+        str = "CREATE TABLE test (t1 int(10)) ENGINE=InnoDB CHARACTER SET=utf8mb4";
+        assertStatementEquals(str, "CREATE TABLE test (t1 int(10)) ENGINE=InnoDB CHARACTER=utf8mb4");
     }

     @Test
     public void testAlterTable() throws Exception {
         String str = "ALTER TABLE test ADD CONSTRAINT c1 FOREIGN KEY (f1) REFERENCES test2 (t2)";
         assertStatementEquals(str);
+
+        str = "ALTER TABLE test MODIFY c1 VARCHAR(255) NULL";
+        assertStatementEquals(str);
+
+        str = "ALTER TABLE test MODIFY COLUMN c1 VARCHAR(255) NULL";
+        assertStatementEquals(str);
+
+        str = "ALTER TABLE test MODIFY c1 VARCHAR(255) NULL FIRST";
+        assertStatementEquals(str);
+
+        str = "ALTER TABLE test MODIFY COLUMN c1 VARCHAR(255) NULL AFTER c0";
+        assertStatementEquals(str);
+
+        str = "ALTER TABLE test MODIFY c1 VARCHAR(256) AFTER c0,MODIFY c2 VARCHAR(256)";
+        assertStatementEquals(str);
     }

     @Test
@@ -101,4 +123,44 @@ public class BasicTest {
         str = "INSERT INTO t1 VALUES (\"this is a test test2 \\\" \\t\\n \\\" test3 \\'\",\"test4\",\"this is a test '' test5 \\' '' \\' test6 \\\\\",\"test7\")";
         assertStatementEquals(str);
     }
+
+    @Test
+    public void testSetNames() throws ParseException {
+        String str = "SET NAMES utf8mb4";
+        assertStatementEquals(str, "SET NAMES=utf8mb4");
+    }
+
+    @Test
+    public void testDelete() throws Exception {
+        String str = "DELETE FROM test";
+        assertStatementEquals(str);
+
+        str = "DELETE FROM test WHERE t1=1";
+        assertStatementEquals(str);
+
+        str = "DELETE FROM test WHERE t1='abc' AND t2=1";
+        assertStatementEquals(str);
+
+        str = "DELETE FROM test WHERE t1=\"2\" OR t2=1";
+        assertStatementEquals(str);
+    }
+
+    @Test
+    public void testUpdate() throws ParseException {
+        String str = "UPDATE test SET t1=1,t2='test',t3=5.0 WHERE t4=1";
+        assertStatementEquals(str);
+
+        str = "UPDATE test SET t1=CONCAT(t1,'-\")-', \"'\",'-',t2) WHERE t4=1";
+        assertStatementEquals(str);
+    }
+
+    @Test
+    public void testWhereClause() throws ParseException {
+        String str = "DELETE FROM test WHERE t1 IN ('1','2','3')";
+        assertStatementEquals(str);
+
+        str = "DELETE FROM test WHERE t1<>'' && t2 IS NOT NULL";
+        assertStatementEquals(str);
+    }
+
 }
```

参考资料
=======

* [JavaCC 详解](https://blog.csdn.net/newpidian/article/details/52964017)
* [小型桌面计算器的实现](https://www.iteye.com/topic/359454?spm=a2c6h.12873639.article-detail.5.29097943B68VnB)
* [JavaCC 的学习](https://developer.aliyun.com/article/14660)
* [JavaCC 从入门到出门](https://www.cnblogs.com/orlion/p/7096645.html)
* [javacc](https://blog.csdn.net/liu_jin_hui/article/details/121266235)