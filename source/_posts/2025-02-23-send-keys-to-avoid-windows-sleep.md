---
id: send-keys-to-avoid-windows-sleep
title: "【转】防止锁屏脚本"
description: "虽已官宣将弃用，但尚未明确彻底移除时间，仍可一用"
date: 2025.02.23 10:26
categories:
    - script
tags: [Windows, VBS]
keywords: vbs, SendKeys, NUMLOCK, 防止锁屏, VBScript, Visual Basic Script
cover: /contents/covers/send-keys-to-avoid-windows-sleep.png
---

原文地址：https://blog.csdn.net/tangtao_xp/article/details/105017873

win7测试通过，该脚本的优点就是简单无需任何依赖，windows平台通用。

电脑配置受到计算机管理员的限制无法关闭屏保锁屏设置，因此每5分钟进行一次NUM键，防止计算机认为误操作自动进入屏保锁屏。

```vbs
' author tangtao
' created on 20200321
'
' [HKEY_CURRENT_USER\Software\Policies\Microsoft\Windows\Control Panel\Desktop]
' "ScreenSaveTimeOut"="300" 屏保时间300秒，5分钟
' "ScreenSaverIsSecure"="1" 屏保是否锁屏
' "ScreenSaveActive"="1" 是否开启屏保
' "SCRNSAVE.EXE"="%windir%\\20190702.scr" 屏保文件

' 每5分钟，激活两次NUM键，防止屏保锁屏
Dim durationHour
durationHour = InputBox("输入锁屏小时数（整数或者小数）", "防止锁屏脚本 by tangtao", 4)

Dim durationLoops
' durationHour * 60 / 5 => durationHour * 12
durationLoops = CInt(CDbl(durationHour) * 12) + 1
' 先定义一个Shell对象
Set wshShell = WScript.CreateObject("WScript.Shell")

' 一次循环花费5分钟，与屏保时间相同
for i = 0 to durationLoops
' 设置成比屏保时间短点就可以(单位毫秒)
    wshShell.SendKeys "{NUMLOCK}"
    WScript.Sleep 500
    wshShell.SendKeys "{NUMLOCK}"
    WScript.Sleep 299400
next

MsgBox "脚本运行结束"
```
