---
id: wrtie-clean-java-code-with-idea
title: "用 IDEA 写更整洁的 Java 代码"
description: "通过配置和插件，让编码更加整洁"
date: 2023.05.28 10:26
categories:
    - Java
tags: [Java, IDEA]
keywords: Actions on Save, Javadoc, comment
cover: /contents/wrtie-clean-java-code-with-idea/cover.png
---

# Tools | Actions on Save

新版本 IDEA 支持设置保存时的动作，在 `Preferences` 下的 `Tools | Actions on Save` 中：

![actions on save](/contents/wrtie-clean-java-code-with-idea/cover.png)

支持如下动作：

- [Reformat code](https://www.jetbrains.com/help/idea/reformat-and-rearrange-code.html#reformat-on-save): 根据当前代码风格设置执行格式化代码动作，可设置生效的文件类型及范围（整个文件、变更部分）
- [Optimize imports](https://www.jetbrains.com/help/idea/creating-and-optimizing-imports.html#optimize-on-save): 根据当前代码风格设置执行移除无用 import 及重新组织 import，可设置生效的文件类型
- [Rearrange code](https://www.jetbrains.com/help/idea/reformat-and-rearrange-code.html): 根据当前代码风格设置执行代码重排序动作
- [Run code cleanup](https://www.jetbrains.com/help/idea/resolving-problems.html#code-cleanup): 批量应用代码修正建议
- [Update copyright notice](https://www.jetbrains.com/help/idea/copyright.html): 更新版权信息
- [Run eslint --fix](https://www.jetbrains.com/help/idea/eslint.html): (IntelliJ IDEA Ultimate) 修正 ESlint 检查的问题
- [Run Prettier](https://www.jetbrains.com/help/idea/prettier.html): 用 Prettier 格式化代码
- [Upload to default server](https://www.jetbrains.com/help/idea/uploading-and-downloading-files.html): (IntelliJ IDEA Ultimate) 上传修改的文件至默认的部署服务器
- [Build project](https://www.jetbrains.com/help/idea/compiling-applications.html#compile_module): 编译所有 class 文件

官方文档：https://www.jetbrains.com/help/idea/saving-and-reverting-changes.html#actions-on-save

# Plugin: JavaDoc

JavaDoc 插件，可以用来根据方法名、参数名等信息，在代码中自动添加或移除 JavaDoc 注释。

- 插件地址：https://plugins.jetbrains.com/plugin/7157-javadoc
- 源码仓库：https://github.com/TSergey/intellij-javadocs

安装插件之后，可通过右键 `Generate...` 功能调出生成或移除 JavaDoc 的菜单点击使用，或直接使用对应快捷键操作：

![generate](/contents/wrtie-clean-java-code-with-idea/javadoc-generate.png)

可生成或移除选定元素的 JavaDoc，也可对文件中所有元素，乃至整个目录（在目录右键选择 JavaDoc 对应菜单，慎用）进行操作。

插件默认的配置在生成 JavaDoc 时会对已有的 JavaDoc 内容进行保留，不会覆盖掉手写的 JavaDoc 内容，只会补充缺失的部分。

以 [StringUtil.java](https://github.com/AlphaHinex/spring-roll/blob/develop/modules/blocks/roll-utils/src/main/java/io/github/springroll/utils/StringUtil.java) 为例，生成的 JavaDoc 内容如下：

```diff
@@ -4,6 +4,9 @@ import org.apache.commons.lang3.StringUtils;
 
 import java.util.Locale;
 
+/**
+ * The type String util.
+ */
 public class StringUtil extends StringUtils {
 
     /**
@@ -12,6 +15,12 @@ public class StringUtil extends StringUtils {
     private StringUtil() {
     }
 
+    /**
+     * Camel to snake string.
+     *
+     * @param camel the camel
+     * @return the string
+     */
     public static String camelToSnake(String camel) {
         String[] strings = StringUtil.splitByCharacterTypeCamelCase(camel);
         return StringUtil.join(strings, "_").toLowerCase(Locale.ENGLISH);

```

插件配置界面，支持进行基本配置及模板配置，可对生成的 JavaDoc 内容进行定制，详细可见 [Javadoc-templates](https://github.com/TSergey/intellij-javadocs/wiki/Javadoc-templates)：

![general](/contents/wrtie-clean-java-code-with-idea/javadoc-general.png)

![templates](/contents/wrtie-clean-java-code-with-idea/javadoc-templates.png)

# 注释缩进

IDEA 里默认的注释方式是在行首添加双斜线，如：

```java
    public static String camelToSnake(String camel) {
//        String[] strings = StringUtil.splitByCharacterTypeCamelCase(camel);
        return StringUtil.join(strings, "_").toLowerCase(Locale.ENGLISH);
    }
```

想调整为添加到首字符前，可双击 `Shift` 键，输入 `line comment at first column`，调整对应语言的配置，如下图：

![line comment](/contents/wrtie-clean-java-code-with-idea/line-comment.png)

取消 `Line comment at first column` 后，再选中 `Add a space at line comment start`，可得到如下风格的注释缩进：

```java
    public static String camelToSnake(String camel) {
        // String[] strings = StringUtil.splitByCharacterTypeCamelCase(camel);
        return StringUtil.join(strings, "_").toLowerCase(Locale.ENGLISH);
    }
```