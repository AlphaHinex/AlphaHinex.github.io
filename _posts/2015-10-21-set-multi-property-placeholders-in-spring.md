---
layout: post
title:  "在 Spring 项目中配置多个 property-placeholder"
description: "使用 context:property-placeholder 的默认配置，在 Spring 项目中设置多处时会遇到其中某些配置的占位符不能正确替换的情况，如何解决？"
headline: "Hex"
date:   2015-10-22 09:31:47
categories: Java
tags: [Spring, placeholder]
comments: true
featured: true
---

提供两个方案：

1. 只设置一处 `context:property-placeholder`

        <context:property-placeholder location="classpath*:path/to/*.properties" />
    
    假设你的 `profile` 是通过 `.properties` 文件设置差异的，用这种方法会将所有 `profile` 的配置都加载并覆盖只保留一份，丧失了设置 `profile` 的功能。
    
2. 设置 `ignore-unresolvable` 为 `true`

        <context:property-placeholder location="classpath*:path/to/module.properties" ignore-unresolvable="true" />

    未能正确替换占位符的原因是 bean 在配置文件加载之前初始化了。`ignore-unresolvable` 属性正是用来解决这个问题的，当其设置为 `true`（默认值为 `false`）时，遇到不能处理的占位符会被忽略，交由其他配置来处理。需要在可能优先加载的配置中设置该属性，或在所有配置中都设置上。

