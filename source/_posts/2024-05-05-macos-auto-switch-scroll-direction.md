---
id: macos-auto-switch-scroll-direction
title: "MacOS 实现自动切换鼠标滚动方向"
description: "AppleScript 虽然不容易使用，但功能很强大"
date: 2024.05.05 10:34
categories:
    - Mac
    - script
tags: [Mac, AppleScript, Shell]
keywords: macOS, AppleScript, Automator, crontab, osascript, Login Items, Accessibility Inspector
cover: /contents/macos-auto-switch-scroll-direction/10-inspector.png
---

实现效果
=======

想在 macOS 上实现如下效果：

1. 连接了（非 Magic Mouse）鼠标时，系统自动切换鼠标滚动方向为“非自然”；
2. 断开鼠标连接时（使用触控板），系统自动切换鼠标滚动方向为“自然”。

> 注：本文使用的脚本在 macOS Monterey 12.7.4 上测试通过，其他系统版本可能存在一些差异。

实现方式
=======

使用 AppleScript 实现切换滚动方向
------------------------------

### 切换滚动方向为 “自然”

[scroll-direction-trackpad.applescript](/contents/macos-auto-switch-scroll-direction/scroll-direction-trackpad.applescript)

```applescript
tell application "System Preferences"
	set current pane to pane "com.apple.preference.trackpad"
end tell

tell application "System Events"
	tell process "System Preferences"
		click radio button "Scroll & Zoom" of tab group 1 of window 1
		if (exists checkbox 1 of tab group 1 of window 1) then
			tell checkbox 1 of tab group 1 of window 1
				if value is 0 then click it
			end tell
		end if
	end tell
end tell

quit application "System Preferences"
```

执行脚本：

```bash
$ osascript scroll-direction-trackpad.applescript
```

### 切换滚动方向为 “非自然”

[scroll-direction-mouse.applescript](/contents/macos-auto-switch-scroll-direction/scroll-direction-mouse.applescript)

```applescript
tell application "System Preferences"
	set current pane to pane "com.apple.preference.trackpad"
end tell

tell application "System Events"
	tell process "System Preferences"
		click radio button "Scroll & Zoom" of tab group 1 of window 1
		if (exists checkbox 1 of tab group 1 of window 1) then
			tell checkbox 1 of tab group 1 of window 1
				if value is 1 then click it
			end tell
		end if
	end tell
end tell

quit application "System Preferences"
```

执行脚本：

```bash
$ osascript scroll-direction-mouse.applescript
```


使用 Shell 脚本检查鼠标连接状态并切换滚动方向
---------------------------------------

[scroll-direction-switcher.sh](/contents/macos-auto-switch-scroll-direction/scroll-direction-switcher.sh)

```shell
#!/bin/bash

# 鼠标设备关键字
mouse_keyword="Mouse"

# 检测是否连接了鼠标设备
system_profiler SPUSBDataType 2>/dev/null|grep -q "$mouse_keyword"

# 检查 grep 的退出状态
if [ $? -eq 0 ]; then
    # 检测到了鼠标设备
    osascript scroll-direction-mouse.applescript
else
    # 没检测到鼠标设备
    osascript scroll-direction-trackpad.applescript
fi
```

> 注：脚本中的 `mouse_keyword` 可以根据实际情况调整，以精确检测鼠标设备。


使用 Automator + Login Items 实现登录后自动检查
-------------------------------------------

### Automator

通常我们可能是在主要工作场所使用外接键鼠设备，在临时工作场所使用触控板。
这时候我们可以通过 macOS 自带的 Automator 应用，将上面的检测切换脚本制作成一个 app，
并设置为登录后自动执行，以实现不同工作场景自动切换鼠标滚动方向的效果。

通过系统自带的 `Spotlight Search` 或其他方式打开 `Automator` 应用：

![automator](/contents/macos-auto-switch-scroll-direction/01-automator.png)

新建 `Document` 选择 `Application` 类型：

![application](/contents/macos-auto-switch-scroll-direction/02-application.png)

`Actions` 中筛选 `shell` 关键字，打开 `Run Shell Script` 窗口：

![shell](/contents/macos-auto-switch-scroll-direction/03-shell.png)

填入执行之前准备好的 `scroll-direction-switcher.sh` 脚本语句，如：

```bash
bash /path/to/scroll-direction-switcher.sh
```

此时点击右上角的运行按钮，可能会得到如下图的报错信息：

![error](/contents/macos-auto-switch-scroll-direction/04-error.png)

先不用在意，最后给权限就不会报错了。

之后保存应用，如 `ScrollDirectionSwitcher.app`：

![app](/contents/macos-auto-switch-scroll-direction/05-app.png)

双击创建出的应用，关闭弹出的报错信息后，到 `系统偏好设置` -> `安全性与隐私` -> `隐私` -> `辅助功能` 中添加刚刚创建的应用：

![accessibility](/contents/macos-auto-switch-scroll-direction/06-accessibility.png)

此时，双击 `ScrollDirectionSwitcher.app` 应用，就可以检测鼠标连接状态并根据结果切换滚轮方向了。

### Login Items

在 `系统偏好设置` -> `用户与群组` -> `登录项` 中添加刚刚创建的应用，这样每次登录后就会自动执行了。

![login](/contents/macos-auto-switch-scroll-direction/07-login.png)

使用 crontab 定时检查
-------------------

如果还有其他的临时切换工作场景的情况，仅凭登录时检测还不够（比如在登录后插入鼠标设备、到会议室开会等），
可以使用 `crontab` 定时检查鼠标连接状态并切换滚动方向。

```bash
$ crontab -e
```

添加定时任务：

```bash
# 每分钟检查一次鼠标连接状态并切换滚动方向
* * * * * /bin/bash /path/to/scroll-direction-switcher.sh
```

> 注意：使用 `crontab` 执行 AppleScript 时，同样需要在 `系统偏好设置` -> `安全性与隐私` -> `隐私` -> `辅助功能` 中添加 `cron`。


AppleScript
===========

关于 AppleScript 的资料并不丰富，[官方文档](https://developer.apple.com/library/archive/documentation/AppleScript/Conceptual/AppleScriptLangGuide/introduction/ASLR_intro.html) 还比较官方，编写脚本时可能需要借助一些工具。

Script Editor 编辑器
-------------------

Script Editor 编辑器是 macOS 自带的脚本编辑器，可以在 `应用程序` -> `实用工具` 中找到。在编辑器中保存脚本时，会自动检查语法错误，并高亮关键字。

Accessibility Inspector
-----------------------

在编写 AppleScript 时，可能需要定位界面中的元素。
Accessibility Inspector 是 macOS（Xcode）中自带的辅助工具，可以查看应用程序的 UI 元素。

可以直接通过 `Spotlight Search` 搜索 `Accessibility Inspector` 打开，也可以在 Xcode 中通过 `Open Developer Tool` 打开。

![spotlight](/contents/macos-auto-switch-scroll-direction/08-spotlight.png)

![xcode](/contents/macos-auto-switch-scroll-direction/09-xcode.png)

![inspector](/contents/macos-auto-switch-scroll-direction/10-inspector.png)

> 小贴士：在定位元素时，将操作系统使用的主语言改成英文，会有很大帮助。

参考资料
=======

* [Scriptable System Preferences](https://www.macosxautomation.com/applescript/features/system-prefs.html)
* [AppleScript - GUI Scripting and setting checkbox, radio button and field values](https://stackoverflow.com/questions/31162970/applescript-gui-scripting-and-setting-checkbox-radio-button-and-field-values)
* [使用脚本设置mac快捷键--自动化管理MacOSX系统偏好](https://www.jianshu.com/p/c6bec4103a5d)
