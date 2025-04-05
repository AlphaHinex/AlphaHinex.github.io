#!/bin/bash

# 鼠标设备关键字
mouse_keyword="Mouse"

# 检测是否连接了鼠标设备
system_profiler SPUSBDataType 2>/dev/null|grep -q "$mouse_keyword"

# 检查 grep 的退出状态
if [ $? -eq 0 ]; then
    # 检测到了鼠标设备
    osascript /Users/alphahinex/github/origin/AlphaHinex.github.io/source/contents/macos-auto-switch-scroll-direction/scroll-direction-mouse.applescript
else
    # 没检测到鼠标设备
    osascript /Users/alphahinex/github/origin/AlphaHinex.github.io/source/contents/macos-auto-switch-scroll-direction/scroll-direction-trackpad.applescript
fi