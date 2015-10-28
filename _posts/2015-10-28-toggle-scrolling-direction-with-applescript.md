---
layout: post
title:  "使用 AppleScript 切换 OSX 鼠标/触控板 滚动方向"
description: "OSX 的鼠标和触控板共享相同的滚动方向设置。假设这样一个场景：在工作时给 MacBook 接上鼠标，休闲时直接使用触控板，通过系统偏好设置界面来调整滚动方向在切换频繁时很麻烦且低效，有没有更便捷的方式？"
headline: "Hex"
date:   2015-10-28 10:16:47
categories: script
tags: [Mac, AppleScript]
comments: true
featured: true
---

使用 [AppleScript](https://en.wikipedia.org/wiki/AppleScript) 脚本可以通过命令行方式来切换滚动方向

以 `OS X EI Capitan` 为例，其他系统版本脚本可能会有差异

    tell application "System Preferences"
        set current pane to pane "com.apple.preference.mouse"
    end tell

    tell application "System Events"
        tell process "System Preferences"
            click checkbox 1 of window 1
        end tell
    end tell

    quit application "System Preferences"
    
将上面脚本代码存储至文本文件，如：`toggle-scrolling-direction.applescript`

在终端中可使用 `osascript toggle-scrolling-direction.applescript` 执行

> 注意：执行过程中会弹出是否允许终端控制电脑的安全确认，如不允许脚本将无法执行。可在 `系统偏好设置` - `安全性与隐私` - `隐私` - `辅助功能` 中修改对应用的控制

可以为 `osascript toggle-scrolling-direction.applescript` 指令定义一个 `alias`，这样切换的时候就更方便了：）

**参考资料**

* [Changing trackpad scroll direction with AppleScript in Yosemite](http://apple.stackexchange.com/questions/153243/changing-trackpad-scroll-direction-with-applescript-in-yosemite)
* [Toggle Natural scrolling from command line with reload](http://apple.stackexchange.com/questions/60877/toggle-natural-scrolling-from-command-line-with-reload)
* [Add applescript to reverse the scroll direction](https://github.com/epochblue/annoy-a-tron/pull/9/files)