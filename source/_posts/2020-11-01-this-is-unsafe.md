---
id: this-is-unsafe
title: "危险！不要打开！"
description: "进来是个坏主意,但我还是要进去"
date: 2020.11.01 10:26
categories:
    - Chrome
tags: [Chrome]
keywords: Chrome, thisisunsafe, badidea, danger, NET::ERR_CERT_INVALID, Chromium, HTTPS
cover: /contents/this-is-unsafe/cover.jpg
---

![隐私设置错误](/contents/this-is-unsafe/cover.jpg)

使用 Chrome 访问某些网站时可能会遇到上面的情况。

点击 `高级` 按钮，有些场景下会有继续访问该网站的链接，点击后即可继续访问；但有些时候会出现如下界面，无法继续访问：

![高级](/contents/this-is-unsafe/adv.jpg)

## 安全提示

**除非你知道自己要访问的网站里面都包含什么，也清楚进去之后会产生什么后果，否则请立刻关闭此页面。**

**除非你知道自己要访问的网站里面都包含什么，也清楚进去之后会产生什么后果，否则请立刻关闭此页面。**

**除非你知道自己要访问的网站里面都包含什么，也清楚进去之后会产生什么后果，否则请立刻关闭此页面。**

## 如何绕过

当出现如上图所示情况时，可在此页面中（点击页面空白处），录入 `thisisunsafe`，过程中不会有任何反馈，输入完毕，页面即可跳过 Chrome 的警告页，访问到网站页面。

## 怎么不好用

因为这是一个危险的行为，随时都有可能被废弃掉。

此行为包含在当前 [Chromium master](https://github.com/chromium/chromium/tree/master) 分支的 [interstitial_large.js](https://github.com/chromium/chromium/blob/master/components/security_interstitials/core/browser/resources/interstitial_large.js#L11-L29) 文件中：

```js
/**
 * This allows errors to be skippped by typing a secret phrase into the page.
 * @param {string} e The key that was just pressed.
 */
function handleKeypress(e) {
  // HTTPS errors are serious and should not be ignored. For testing purposes,
  // other approaches are both safer and have fewer side-effects.
  // See https://goo.gl/ZcZixP for more details.
  const BYPASS_SEQUENCE = window.atob('dGhpc2lzdW5zYWZl');
  if (BYPASS_SEQUENCE.charCodeAt(keyPressState) === e.keyCode) {
    keyPressState++;
    if (keyPressState === BYPASS_SEQUENCE.length) {
      sendCommand(SecurityInterstitialCommandId.CMD_PROCEED);
      keyPressState = 0;
    }
  } else {
    keyPressState = 0;
  }
}
```

`BYPASS_SEQUENCE` 即注释中提到的 `secret phrase`，从 console 中直接执行 `window.atob('dGhpc2lzdW5zYWZl')` 即可看到 Base64 解码后的明文：

```js
> window.atob('dGhpc2lzdW5zYWZl')
< "thisisunsafe"
```

从 Chromium 的提交记录中，我们也可以看到开发人员对此方式被滥用而感到的担忧：

2014 年这个 `BYPASS_SEQUENCE` 第一次被 [提交](https://github.com/chromium/chromium/commit/476d5156284adc4958807d7db6d8b74f990e6844#diff-01324c494c7d2692f9b3d23af31da6dcf2b7dd8ca8b9b1a491bbda3b4a6736f4R25) 时：

```js
var BYPASS_SEQUENCE = 'danger';
```

2015 年专门针对此关键字进行了一次修改 [Change the interstitial bypass keyword](https://github.com/chromium/chromium/commit/90b6605758feea9d4f2a56ad3f6992e1e868b445)：

```diff
- var BYPASS_SEQUENCE = 'danger';
+ var BYPASS_SEQUENCE = 'badidea';
```

2018 年 1 月 3 日 [Change the interstitial bypass keyword](https://github.com/chromium/chromium/commit/cb8501aaf28904ff1e39962aaed380a1618a6222)：

```diff
- var BYPASS_SEQUENCE = 'badidea';
+ var BYPASS_SEQUENCE = 'thisisnotsafe';
```

并在提交说明中描述了这么做的意义：

```text
The security interstitial bypass keyword hasn't changed in two years and
awareness of the bypass has been increased in blogs and social media.
Rotate the keyword to help prevent misuse.
```

在 8 天之后再次 [调整](https://github.com/chromium/chromium/commit/d8fc089b62cd4f8d907acff6fb3f5ff58f168697) 此部分代码，将这个 keyword 进行了 Base64 编码以增加干扰：

```diff
- var BYPASS_SEQUENCE = 'thisisnotsafe';
+ // HTTPS errors are serious and should not be ignored. For testing purposes,
+ // other approaches are both safer and have fewer side-effects.
+ // See https://goo.gl/ZcZixP for more details.
+ var BYPASS_SEQUENCE = window.atob('dGhpc2lzdW5zYWZl');
```

随着时间的流逝，再次修改这个关键字也是很有可能的，所以当你看到这段文字时，上面的方法很有可能已经失效了。

如果你有不得已的苦衷，一定要绕过这个安全提示，可以尝试在安全提示页面，打开 console 直接输入：

```js
> sendCommand(SecurityInterstitialCommandId.CMD_PROCEED)
```

## 如何恢复

通过上述方式绕过安全提示之后，以后再次访问此网站时即可直接访问了。如果想恢复安全提示界面，可点击地址栏前面的 `不安全` 图标，并点击 `重新启用警告功能`，如下图：

![重新启用警告功能](/contents/this-is-unsafe/reset.jpg)

## 参考资料

* [Does using 'badidea' or 'thisisunsafe' to bypass a Chrome certificate/HSTS error only apply for the current site? [closed]](https://stackoverflow.com/questions/35274659/does-using-badidea-or-thisisunsafe-to-bypass-a-chrome-certificate-hsts-error/35275060#35275060)
