---
layout: post
title:  "调试跟进 tomcat 源码"
description: "调试 web 应用时，有时需要跟进 tomcat 的源码。下载 tomcat 源码并编译运行是一种方式，不过太麻烦，有没有简单点的办法呢？"
headline: "Hex"
date:   2015-10-14 15:19:47
categories: Java
tags: [Tomcat, Gradle, IDEA, Eclipse]
comments: true
featured: true
---

给项目加上 tomcat 的 jar 包作为运行时依赖，并附加源码，就可以在调试的时候跟进 tomcat 的源码了

以 [Gradle](http://gradle.org/) 和 [tomcat 7.0.63](http://tomcat.apache.org/download-70.cgi) 为例，只需在 `build.gradle` 的 `dependencies` 中加入如下代码即可：

    depencencies {
	    def tomcatVer = '7.0.63'
        runtime "org.apache.tomcat.embed:tomcat-embed-core:${tomcatVer}",
                "org.apache.tomcat.embed:tomcat-embed-logging-juli:${tomcatVer}",
                "org.apache.tomcat.embed:tomcat-embed-jasper:${tomcatVer}"
    }

> 如无 `gradle` 环境，可下载 [gradle-wrapper](/archives/gradle-wrapper/gradle-wrapper.zip)，将解压出的 `gradle/`、`gradlew` 和 `gradlew.bat` 放入项目根路径，即可使用 `gradlew` 命令。gradle wrapper 会在第一次执行时自动下载在 `gradle/wrapper/gradle-wrapper.properties` 中设置的 gradle 版本

Eclipse
-------

使用 `eclipse` 调试时，在 `build.gradle` 中加入

    apply plugin: 'java'
    apply plugin: 'war'
    apply plugin: 'eclipse-wtp'
    
使用

    $ ./gradlew eclipse
    
> 注：`windows` 环境下使用 `gradlew eclipse` 命令
    
生成 eclipse 所需文件后，即可将项目导入 eclipse 环境中。将 web 应用发布至 tomcat 后，加断点调试时会发现虽然能跟进 tomcat 的 class 里，确仍然没有源码。不过此时会有附加源码的按钮，选择 gradle 下载回的源码 jar 包就可以了

IDEA
----
          
使用 IDEA 则比较简单，在 `build.gradle` 中加入

    apply plugin: 'java'
    apply plugin: 'war'
    apply plugin: 'idea'
    
使用

    $ ./gradlew idea

生成 IDEA 所需文件后，导入 IDEA 并发布至 tomcat 即可在调试时跟进 tomcat 的源码

DEMO
----

[下载 Demo 项目](/archives/debug-into-tomcat/debug-into-tomcat.zip)

包含文件：

    build.gradle
    src/main/java/io/github/alphahinex/DemoServlet.java
    src/main/webapp/WEB-INF/web.xml
