---
id: java-regex-catastrophic-backtracking
title: "Java 正则表达式的灾难性回溯"
description: "Java 正则表达式的灾难性回溯问题可能导致应用程序的拒绝服务。本文介绍了如何重现、风险原因、风险评估、如何避免、修复示例等内容。"
date: 2024.10.13 10:26
categories:
    - Java
tags: [Java, Regex]
keywords: regex, backtracking, catastrophic backtracking, java, security, performance, denial of service, DoS, ReDoS, OWASP, CWE, S5852
cover: /contents/covers/java-regex-catastrophic-backtracking.png
---

# 现象重现

新建一个 `Backtracking.java` 文件，内容如下：

```java
public class Backtracking {
    public static void main(String[] args) {
        System.out.println(System.getProperty("java.version"));
        System.out.println("The first regex evaluation will never end in JDK <= 9:");
        System.out.println(java.util.regex.Pattern.compile("(a+)+").matcher(
"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"+
"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"+
"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"+
"aaaaaaaaaaaaaaa!").matches()); // Sensitive
        System.out.println("and the second regex evaluation will never end in any versions of the JDK:");
        System.out.println(java.util.regex.Pattern.compile("(h|h|ih(((i|a|c|c|a|i|i|j|b|a|i|b|a|a|j))+h)ahbfhba|c|i)*").matcher(
"hchcchicihcchciiicichhcichcihcchiihichiciiiihhcchi"+
"cchhcihchcihiihciichhccciccichcichiihcchcihhicchcciicchcccihiiihhihihihi"+
"chicihhcciccchihhhcchichchciihiicihciihcccciciccicciiiiiiiiicihhhiiiihchccch"+
"chhhhiiihchihcccchhhiiiiiiiicicichicihcciciihichhhhchihciiihhiccccccciciihh"+
"ichiccchhicchicihihccichicciihcichccihhiciccccccccichhhhihihhcchchihih"+
"iihhihihihicichihiiiihhhhihhhchhichiicihhiiiiihchccccchichci").matches()); // Sensitive
    }
}
```

编译并执行：

```bash
$ java -version
java version "1.8.0_121"
Java(TM) SE Runtime Environment (build 1.8.0_121-b13)
Java HotSpot(TM) 64-Bit Server VM (build 25.121-b13, mixed mode)
$ javac Backtracking.java
$ java Backtracking
1.8.0_121
The first regex evaluation will never end in JDK <= 9:
```

在 Java 8 环境下，此段程序永远不会执行结束，且该 Java 进程会持续跑满 CPU。

在 Java 11 环境下，第一个表达式能执行结束，但第二个表达式依然会持续消耗大量资源：

```bash
$ java -version
openjdk version "11.0.23" 2024-04-16 LTS
OpenJDK Runtime Environment Microsoft-9394293 (build 11.0.23+9-LTS)
OpenJDK 64-Bit Server VM Microsoft-9394293 (build 11.0.23+9-LTS, mixed mode, sharing)
$ java Backtracking
11.0.23
The first regex evaluation will never end in JDK <= 9:
false
and the second regex evaluation will never end in any versions of the JDK:
```

# 风险原因

[Using slow regular expressions is security-sensitive](https://next.sonarqube.com/sonarqube/coding_rules?open=java%3AS5852&rule_key=java%3AS5852) 对这个问题进行了描述：大多数正则表达式引擎使用回溯（`backtracking`）来尝试正则表达式在评估输入时的所有可能执行路径，在某些情况下，这可能会导致性能问题，称为灾难性回溯（`catastrophic backtracking`）情况。在最坏的情况下，正则表达式的复杂度与输入大小成指数关系，这意味着一个精心构造的小输入（如20个字符）可以触发灾难性回溯并导致应用程序的拒绝服务。超线性正则表达式复杂度也可能导致相同的影响，在这种情况下，需要一个精心构造的大输入（数千个字符）。

# 风险评估

要确定代码中是否存在此风险，可以尝试回答如下问题：

- 输入是用户控制的。
- 输入大小没有限制为少量的字符。
- 没有设置超时来限制正则表达式的评估时间。

如果任何一个问题的回答为 `是`，那么就可能存在风险。

# 如何避免

在所有下述情况中，灾难性回溯只有在正则表达式的有问题部分后面跟随一个可能失败的模式时才会发生，从而导致回溯实际发生。请注意，当执行完全匹配（例如使用 `String.matches`）时，正则表达式的结尾被视为一个可能失败的模式，因为它只有在到达字符串结尾时才会成功。

- 如果正则表达式包含非占有性重复，如 `r*` 或 `r*?`，表示可以匹配零次或多次 `r`，但不会占有匹配的字符（即允许回溯），如果 `r` 可以在相同输入上产生不同的可能匹配（可能长度不同），最坏情况下的匹配时间可能是指数级的。这种情况可能发生在 `r` 包含可选部分、交替或额外重复时。使用JDK 9或更高版本时，如果重复是贪婪的且整个正则表达式不包含反向引用，则运行时间会优化为多项式或线性。
- 如果多个非占有性重复可以匹配相同内容且是连续的或仅由可选分隔符分隔，可能会导致多项式时间复杂度。例如，`a*b*` 没有问题，因为 `a*` 和 `b*` 匹配不同的东西，而 `a*_a*` 也没有问题，因为重复部分由一个 `_` 分隔，并且不能匹配该 `_`。然而，`a*a*` 和 `.*_.*` 具有二次运行时间。
- 如果你正在执行部分匹配（如使用 `Matcher.find`、`String.split`、`String.replaceAll` 等），并且正则表达式未锚定到字符串的开头，尤其难以避免二次运行时间。例如，`str.split("\\s*,")` 在完全由空格组成的字符串（或至少包含大量不跟随逗号的空格序列）上将以二次时间运行。

为避免这些问题，可以采取以下策略：

- 如果适用，使用有界量词（例如用 `{1,5}` 代替 `+`）限制重复次数。
- 重构嵌套量词（`nested quantifiers`）以限制内部组可以被外部量词匹配的数量。例如 `(ba+)+` 这种嵌套量词情况不会导致性能问题，实际上，只有存在每个组重复一次 `b` 字符时，内部组才能匹配。
- 使用占有量词（`possessive quantifiers`）和原子分组（`atomic grouping`）优化正则表达式。
- 使用否定字符类代替 `.` 来排除分隔符。例如，二次正则表达式 `.*_.*` 可以通过将其更改为 `[^_]*_.*` 变为线性。

如果无法重写正则表达式以避免性能问题，可以考虑以下方法：

- 不使用正则表达式解决问题。
- 使用非回溯的正则表达式实现，如Google的 [RE2](https://github.com/google/re2) 或 [RE2/J](https://github.com/google/re2j)。
- 使用多次处理，预处理或后处理字符串，或使用多个正则表达式。一个例子是将 `str.split("\\s*,\\s*")` 替换为 `str.split(",")`，然后在第二步中修剪字符串中的空格。
- 使用 `Matcher.find()` 时，通常可以通过使所有可能失败的部分可选来使正则表达式不可失败，这将防止回溯。当然，这意味着你将接受比预期更多的字符串，但这可以通过使用捕获组来检查可选部分是否匹配，然后在它们不匹配时忽略匹配来处理。例如，正则表达式 `x*y` 可以替换为 `x*(y)?`，然后将对 `matcher.find()` 的调用替换为 `matcher.find() && matcher.group(1) != null`。

# 修复示例

`NewBacktracking.java`

```java
public class NewBacktracking {
    public static void main(String[] args) {
        System.out.println(System.getProperty("java.version"));
        System.out.println("The first regex evaluation will end after modify:");
        System.out.println(java.util.regex.Pattern.compile("(a+)++").matcher(
"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"+
"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"+
"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"+
"aaaaaaaaaaaaaaa!").matches()); // Sensitive
        System.out.println("and the second regex evaluation will end after modify:");
        System.out.println(java.util.regex.Pattern.compile("(h|h|ih(((i|a|c|c|a|i|i|j|b|a|i|b|a|a|j))++h)ahbfhba|c|i)*").matcher(
"hchcchicihcchciiicichhcichcihcchiihichiciiiihhcchi"+
"cchhcihchcihiihciichhccciccichcichiihcchcihhicchcciicchcccihiiihhihihihi"+
"chicihhcciccchihhhcchichchciihiicihciihcccciciccicciiiiiiiiicihhhiiiihchccch"+
"chhhhiiihchihcccchhhiiiiiiiicicichicihcciciihichhhhchihciiihhiccccccciciihh"+
"ichiccchhicchicihihccichicciihcichccihhiciccccccccichhhhihihhcchchihih"+
"iihhihihihicichihiiiihhhhihhhchhichiicihhiiiiihchccccchichci").matches()); // Sensitive
    }
}
```

```bash
$ diff Backtracking.java NewBacktracking.java
1c1
< public class Backtracking {
---
> public class NewBacktracking {
4,5c4,5
<         System.out.println("The first regex evaluation will never end in JDK <= 9:");
<         System.out.println(java.util.regex.Pattern.compile("(a+)+").matcher(
---
>         System.out.println("The first regex evaluation will end after modify:");
>         System.out.println(java.util.regex.Pattern.compile("(a+)++").matcher(
10,11c10,11
<         System.out.println("and the second regex evaluation will never end in any versions of the JDK:");
<         System.out.println(java.util.regex.Pattern.compile("(h|h|ih(((i|a|c|c|a|i|i|j|b|a|i|b|a|a|j))+h)ahbfhba|c|i)*").matcher(
---
>         System.out.println("and the second regex evaluation will end after modify:");
>         System.out.println(java.util.regex.Pattern.compile("(h|h|ih(((i|a|c|c|a|i|i|j|b|a|i|b|a|a|j))++h)ahbfhba|c|i)*").matcher(
```

```bash
$ javac NewBacktracking.java
$ java NewBacktracking
1.8.0_121
The first regex evaluation will end after modify:
false
and the second regex evaluation will end after modify:
true
```

# 参考资料

- [Using slow regular expressions is security-sensitive](https://next.sonarqube.com/sonarqube/coding_rules?open=java%3AS5852&rule_key=java%3AS5852)
- OWASP - [Top 10 2017 Category A1 - Injection](https://owasp.org/www-project-top-ten/2017/A1_2017-Injection)
- CWE- [CWE-400 - Uncontrolled Resource Consumption](https://cwe.mitre.org/data/definitions/400)
- CWE- [CWE-1333 - Inefficient Regular Expression Complexity](https://cwe.mitre.org/data/definitions/1333)
- [owasp.org](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS) - OWASP Regular expression Denial of Service - ReDoS
- [stackstatus.net(archived)](https://web.archive.org/web/20220506215733/https://stackstatus.net/post/147710624694/outage-postmortem-july-20-2016) - Outage Postmortem - July 20, 2016
- [regular-expressions.info](https://www.regular-expressions.info/catastrophic.html) - Runaway Regular Expressions: Catastrophic Backtracking
- [docs.microsoft.com](https://docs.microsoft.com/en-us/dotnet/standard/base-types/backtracking-in-regular-expressions#backtracking-with-nested-optional-quantifiers) - Backtracking with Nested Optional Quantifiers
