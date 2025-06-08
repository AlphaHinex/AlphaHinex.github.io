---
id: windows-auto-adhoc
title: "【转】如何开机自动开启移动热点"
description: "本文介绍了如何在 Windows 10/11 系统中设置开机自动启动移动热点的步骤，使用 PowerShell 脚本和批处理文件实现自动化。"
date: 2025.06.08 10:26
categories:
    - Windows
tags: [Windows, PowerShell, Shell]
keywords: Windows 10, Windows11, PowerShell, 移动热点, WinRT, .NET, Microsoft
cover: /contents/windows-auto-adhoc/cover.jpg
---

- 原文地址：https://answers.microsoft.com/zh-hans/windows/forum/all/%E5%A6%82%E4%BD%95%E5%BC%80%E6%9C%BA%E8%87%AA/d3671fd2-b17a-4f1c-a500-13120704ea98
- 原文作者：[彭迪斯](https://answers.microsoft.com/zh-hans/profile/ea4851f1-5f01-459c-9848-4f9fe1a4df56)

当我们经常需要使用移动热点的时候，可能希望开机便自启动移动热点。

一、 技术难度：★★★（3颗星）

阅读时间：大约3分钟

适用于：Windows10/11

二、执行步骤：

1、鼠标右击屏幕左下角的开始菜单，打开 Windows PowerShell（管理员）（A）

<span style="color: green">在Windows11中可以打开 Windows终端（管理员）（A）</span>

![start](https://alphahinex.github.io/contents/windows-auto-adhoc/01.png)

2、在打开的Windows PowerShell窗口中输入：

```ps
set-executionpolicy remotesigned
```

按下键盘上的回车键（Enter按键）。

![set-executionpolicy](https://alphahinex.github.io/contents/windows-auto-adhoc/02.png)

3、等待一会，将出现如下的提示。输入：a。然后按下回车键（Enter按键）。

（Windows11的终端中可能不显示提示，这是正常的。）

![set-executionpolicy-confirm](https://alphahinex.github.io/contents/windows-auto-adhoc/03.png)

4、关闭Windows PowerShell窗口。

打开资源管理器，并在地址栏输入：

```url
%appdata%\Microsoft\Windows\Start Menu\Programs\Startup
```

然后按下回车键（Enter按键）。

![startup](https://alphahinex.github.io/contents/windows-auto-adhoc/04.png)

5、将进入“启动”这个文件夹内。在空白处鼠标右击，选择“<span style="color: green">新建</span>”，选择“<span style="color: green">文本文档</span>”。

![new-text-document](https://alphahinex.github.io/contents/windows-auto-adhoc/05.png)

6、更改新建的这个文件的txt后缀为<span style="color: green">bat</span>。

![change-txt-to-bat](https://alphahinex.github.io/contents/windows-auto-adhoc/06.png)

7、若是出现下图提示，点击“<span style="color: green">是</span>”。

![change-txt-to-bat-confirm](https://alphahinex.github.io/contents/windows-auto-adhoc/07.png)

8、鼠标右键点击该文件，然后选择“<span style="color: green">编辑</span>”。

![edit-bat-file](https://alphahinex.github.io/contents/windows-auto-adhoc/08.png)

9、在打开的窗口粘贴以下内容，然后保存并关闭这个bat文件。

```ps
powershell -executionpolicy remotesigned -file "%appdata%\Microsoft\Windows\Start Menu\Programs\pondsihotspot.ps1"
exit
```

![edit-bat-file-content](https://alphahinex.github.io/contents/windows-auto-adhoc/09.png)

10、在资源管理器的地址栏输入：

```url
%appdata%\Microsoft\Windows\Start Menu\Programs
```

然后按下回车键（Enter按键），将进入“<span style="color: green">程序</span>”这个文件夹内。

在空白处鼠标右击，选择“<span style="color: green">新建</span>”，选择“<span style="color: green">文本文档</span>”。

更改新建的这个文件名字为“<span style="color: green">pondsihotspot.ps1</span>”。

若是出现重命名提示，点击“<span style="color: green">是</span>”。

![new-ps1-file](https://alphahinex.github.io/contents/windows-auto-adhoc/10.png)

11、鼠标右键点击该文件，选择“<span style="color: green">打开方式</span>”，选择“<span style="color: green">记事本</span>”打开。

![edit-ps1-file](https://alphahinex.github.io/contents/windows-auto-adhoc/11.png)

12、复制以下内容到文件内，完成后保存并关闭。

```ps
Add-Type -AssemblyName System.Runtime.WindowsRuntime 

$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | ? { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0] 

Function Await($WinRtTask, $ResultType) { 
    $asTask = $asTaskGeneric.MakeGenericMethod($ResultType) 
    $netTask = $asTask.Invoke($null, @($WinRtTask)) 
    $netTask.Wait(-1) | Out-Null 
    $netTask.Result 
} 

Function AwaitAction($WinRtAction) { 
    $asTask = ([System.WindowsRuntimeSystemExtensions].GetMethods() | ? { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and !$_.IsGenericMethod })[0] 
    $netTask = $asTask.Invoke($null, @($WinRtAction)) 
    $netTask.Wait(-1) | Out-Null 
} 

$connectionProfile = [Windows.Networking.Connectivity.NetworkInformation,Windows.Networking.Connectivity,ContentType=WindowsRuntime]::GetInternetConnectionProfile() 

$tetheringManager = [Windows.Networking.NetworkOperators.NetworkOperatorTetheringManager,Windows.Networking.NetworkOperators,ContentType=WindowsRuntime]::CreateFromConnectionProfile($connectionProfile) 

if ($tetheringManager.TetheringOperationalState -eq 1) { 
    "" 
} 
else{ 
    Await ($tetheringManager.StartTetheringAsync()) ([Windows.Networking.NetworkOperators.NetworkOperatorTetheringOperationResult]) 
}
```

![edit-ps1-file-content](https://alphahinex.github.io/contents/windows-auto-adhoc/12.png)

10、重启电脑，看下是否可以自动打开移动热点。


三、以上。