---
id: java-dependency-tree
title: "【转】查看依赖树的利器"
description: "借助依赖树，可以更容易的分析间接依赖关系"
date: 2023.10.07 10:26
categories:
    - Java
tags: [Java, Maven, Gradle, IDEA]
keywords: maven, dependency tree, gradle, dependencies, java, pom, IDEA
cover: /contents/java-dependency-tree/idea_1.png
---

原文地址：https://wyiyi.github.io/amber/2023/10/01/Dependency%20Tree/

依赖树（Dependency Tree）工具，可以查看和分析项目的依赖关系。

本文将介绍 maven 和 gradle 两种构建如何查看依赖树。

## 使用命令行查看
1. 命令行工具来查看项目的依赖树，执行命令：
    
    ```bash
    mvn dependency:tree
    ```
   
    ```bash
    gradle dependencies
    ```

2. 对于大型项目，可以将输出结果保存到文件中：

    ```bash
    mvn dependency:tree > dependency_tree.txt
    ```

    ```bash
    gradle dependencies > dependencies.txt
    ```

## 使用 IDEA 查看 Show dependencies

1. 按下图操作：

- 找到 Dependencies 选项展开后即可查看项目的编译的依赖树
- 点击 show dependencies 显示依赖树结果图三（快捷键（ctrl+alt+shift+u）

  ![图一_maven](/contents/java-dependency-tree/idea_1.png)

  ![图一_gradle](/contents/java-dependency-tree/gradle_1.png)

2. 打开文件（pom.xml 或者 .gradle）右键，如图点击 show dependencies 后显示依赖树结果图三

  ![图二_maven](/contents/java-dependency-tree/idea_2.png)

  ![图二_gradle](/contents/java-dependency-tree/gradle_2.png)

3. 使用快捷键 ctrl + f 可以搜索要查找的 Jar 定位到依赖关系。（注意：IDEA 版本）

  ![图三_maven](/contents/java-dependency-tree/idea_3.png)

  ![图三_gradle](/contents/java-dependency-tree/gradle_3.png)

## 总结
依赖树功能是项目依赖管理的重要工具，能够帮助我们查看和分析项目的依赖关系，解决依赖冲突问题，并进行优化和调整。