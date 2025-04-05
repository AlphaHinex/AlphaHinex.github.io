---
id: windows-auto-login
title: "【转】4 种实用方法：如何设置 Windows 10/11 自动登录"
description: "更改注册表方案简单实用"
date: 2025.04.06 10:34
categories:
    - Windows
tags: [Windows]
keywords: Windows 10, Windows 11, 自动登录, Autologon, regedit, 注册表, 用户账户, 密码, 空密码
cover: /contents/windows-auto-login/cover.png
---

原文地址：https://www.sysgeek.cn/windows-auto-login/

![](/contents/windows-auto-login/cover.png)

当启动 Windows PC 时，登录界面会列出一个或多个用户账户。你需要选择一个账户并通过身份验证才能进入桌面。Windows 支持多种登录验证方式，如密码和 [Windows Hello](https://www.sysgeek.cn/introduction-windows-hello-business/)，这对于多用户设备来说会十分便利。

虽然现代计算机加载 Windows 的速度已经非常快，但跳过登录验证可以更快地开始工作。如果你是电脑的唯一使用者，还可以选择取消登录验证。接下来，我们就介绍如何在 Windows 11/10 设备上设置自动登录。

# 什么是 Windows 自动登录

自动登录是 Windows 的一项便捷功能，允许不输入密码或 PIN 码即可登录电脑。它不仅能缩短开机时间，还能在从睡眠状态唤醒时省去重复验证的步骤，从而提升效率。

## 使用场景与潜在风险

通常情况下，我们不推荐在 Windows 设备上启用自动登录。因为任何能够物理接触到设备的人都能轻松访问你的敏感信息，并获得完整的管理权限。

在决定启用 Windows 自动登录之前，请考虑以下几点：

- 不推荐在笔记本电脑、平板电脑或其他便携设备上启用，因为这些设备通常会带着到处跑。
- 不推荐在多人共用的电脑上启用。
- 可以在没有重要数据的虚拟机上启用。
- 可以在仅个人使用的家用电脑上启用（相对安全）。

如果你的 Windows 中有多个用户账户，也可以只为某一个账户单独设置自动登录，从而保持其他主要账户的安全。

# 在 Windows 中设置自动登录

Windows 并没有直接开启自动登录的选项，但我们可以通过以下 4 种方法来实现自动登录。

## 方法 1：通过「用户账户」设置

1. 如果你使用 Microsoft 账户，请用 `Windows + I` 快捷键打开「Windows 设置」。
2. 选择「账户」-「登录选项」，然后关闭「为了提高安全性，仅允许对此设备上的 Microsoft 账户使用 Windows Hello 登录 」开关。

![Windows 10](/contents/windows-auto-login/win10.png)

![Windows 11](/contents/windows-auto-login/win11.png)

3. 使用 `Windows + R` 快捷键调出「运行」对话框，输入 `netplwiz` 打开「用户账户」设置窗口。
4. 取消勾选「要使用本计算机，用户必需输入用户名和密码」，然后点击「应用」按钮。

![通过「用户账户」设置 Windows 自动登录](/contents/windows-auto-login/user_account.png)

5. 此时会弹出「自动登录」对话框，在此输入密码两次，确认无误后点击「确定」即可。

![输入账户密码](/contents/windows-auto-login/auto_login.png)

设置完成后，在登录时会自动帮你验证密码，但密码并未删除。如果你更改了账户密码，需要按以上步骤重新设置。

## 方法 2：更改注册表设置

我们也可以更改注册表配置来实现 Windows 10/11 自动登录，操作步骤如下：

1. 使用 `Windows + R` 快捷键打开「运行」，输入 `regedit` 打开注册表编辑器。
2. 浏览到以下路径：
```text
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon
```
3. 在右侧窗口中并双击名为 `AutoAdminLogon` 的**字符串值**（如果没有就新建一个），并将其值设置为：
- `0` 禁用自动登录
- `1` 启用自动登录
4. 在右侧窗口中分别并双击名为 `DefaultUserName` 和 `DefaultPassword` 的**字符串值**（如果没有就新建），并将其值设置为：
- `DefaultUserName` 用于自动登录的账户名称
- `DefaultPassword` 对应的账户密码

![通过注册表设置 Windows 自动登录](/contents/windows-auto-login/regedit.png)

注册表更改完成后，重启 Windows 就会生效。

> 手动更改注册表时，`DefaultPassword` 使用的是明文。使用 Autologon 时，密码在注册表中会加密为 LSA 密文。

## 方法 3：使用 Autologon 工具

如果想用更简单的方式来设置自动登录，[Sysinternals](https://www.sysgeek.cn/what-is-sysinternals-tools/) 提供的 Autologon 工具是个不错的选择。它会自动修改注册表，帮助你启用 Windows 的自动登录功能，而无需去手动编辑。

1. 从 Microsoft 官方网站[下载 Autologon 工具](https://learn.microsoft.com/en-us/sysinternals/downloads/autologon)。
2. 解压下载的文件，并根据你的 Windows 系统架构运行对应的 Autologon 程序。
3. 在打开的界面中核对用户名，然后在「Password」栏填入登录密码，并点击「Enable」按钮。一般家用电脑都是工作组环境，因此「Domain」一栏通常无需更改。

![使用 Autologon 工具设置 Windows 自动登录](/contents/windows-auto-login/autologon.png)

> Autologon 不会校验密码是否正确，也不会检查用户账户是否有权限登录。
4. 设置成功后，屏幕会有「Autologon successfully configured」提示。点击「OK」完成设置。

完成以上步骤后，只需重启 Windows PC，就能实现免密码登录。要关闭此功能，可以重新打开 Autologon 并点击「Disable」禁用即可。

## 方法 4：使用空密码账户（不推荐）

我们也可以通过删除账户密码，也就是使用「空密码」来实现 Windows 自动登录。以下是操作步骤：

1. 使用 `Windows + R` 快捷键打开「运行」，输入 `lusrmgr.msc` 打开「本地用户和组」。
2. 在打开的窗口中，点击左侧的「用户」选项卡，然后在右侧面板中选择要删除密码的账户，右键点击并选择「设置密码」。
3. 当出现警告框时，点击「继续」按钮。
4. 在接下来的对话框中，不要输入任何内容，保持「新密码」和「确认密码」栏为空，直接点击「确定」完成设置。

![使用空密码账户实现 Windows 自动登录](/contents/windows-auto-login/empty_password.png)

执行以上步骤后，Windows 将不再要求输入密码来登录账户，也可以实现自动登录。

> 因为账户没有了密码保护，所带来的安全风险极大。而且空密码默认无法使用远程桌面协议（RDP）和 NTLM 认证服务。

---

开启 Windows 的自动登录功能虽然会带来便利，但也伴随着一定的安全风险。如果你已经权衡利弊并决定使用，可以参考本文介绍的 4 种方法来设置。