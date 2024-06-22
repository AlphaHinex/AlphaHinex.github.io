---
id: speech-synthesis
title: "Web Speech API 之 Speech Synthesis"
description: "浏览器自带的语音合成功能"
date: 2024.06.23 10:26
categories:
    - Web
tags: [Web, HTML5]
keywords: SpeechSynthesis, SpeechSynthesisUtterance, SpeechSynthesisVoice, Web Speech API, onvoiceschanged
cover: /contents/covers/speech-synthesis.png
---

# Speech synthesis

Speech synthesis（语音合成，也被称作是文本转为语音，英语简写是 TTS）包括接收 app 中需要语音合成的文本，再在设备扬声器或音频输出连接中播放出来这两个过程。

Web Speech API 对此有一个主要控制接口 —— [`SpeechSynthesis`](https://developer.mozilla.org/zh-CN/docs/Web/API/SpeechSynthesis) ，外加一些处理如何表示要被合成的文本 (也被称为 utterances)，用什么声音来播出 utterances 等工作的相关接口。同样的，许多操作系统都有自己的某种语音合成系统，在这个任务中我们调用可用的 API 来使用语音合成系统。

## Demo

为了展示 Web 语音合成的简单使用，我们提供了一个例子 —— [Speak easy synthesis](https://github.com/mdn/dom-examples/tree/main/web-speech-api/speak-easy-synthesis) 。例子是一套表单控件，包括输入需要被合成的文本，设置音调、语速和说出文本时需要的语音。在输入文本之后，按下 <kbd>Enter</kbd>/<kbd>Return</kbd> 键使它播放。

![UI](/contents/covers/speech-synthesis.png)

想跑这个例子，你可以 git clone Github 仓库中的部分 (或者[直接下载](https://github.com/mdn/dom-examples/archive/refs/heads/main.zip))，在桌面版支持的浏览器打开 index.html 文件，或者在移动端浏览器直接导向 [live demo URL](https://mdn.github.io/dom-examples/web-speech-api/speak-easy-synthesis/) ，像 Chrome 和 Firefox OS。

## 浏览器兼容性

[api.SpeechSynthesis](https://developer.mozilla.org/zh-CN/docs/Web/API/Web_Speech_API#api.speechsynthesis)

## HTML 和 CSS

HTML 和 CSS 还是无足轻重，只是简单包含一个标题，一段介绍文字，以及一个表格带有一些简单控制功能。[select](https://developer.mozilla.org/zh-CN/docs/Web/HTML/Element/select) 元素初始是空的，之后会通过 JavaScript 使用 [option](https://developer.mozilla.org/zh-CN/docs/Web/HTML/Element/option) 填充。

```html
<h1>Speech synthesiser</h1>

<p>
  Enter some text in the input below and press return to hear it. change voices
  using the dropdown menu.
</p>

<form>
  <input type="text" class="txt" />
  <div>
    <label for="rate">Rate</label
    ><input type="range" min="0.5" max="2" value="1" step="0.1" id="rate" />
    <div class="rate-value">1</div>
    <div class="clearfix"></div>
  </div>
  <div>
    <label for="pitch">Pitch</label
    ><input type="range" min="0" max="2" value="1" step="0.1" id="pitch" />
    <div class="pitch-value">1</div>
    <div class="clearfix"></div>
  </div>
  <select></select>
</form>
```

## JavaScript

让我们看看 JavaScript 在这个 app 中的强大表现。

### 设置变量

首先我们获得 UI 中涉及的 DOM 元素的引用，但更有趣的是，我们获得了[`Window.speechSynthesis`](https://developer.mozilla.org/zh-CN/docs/Web/API/Window/speechSynthesis) 的引用。这是 API 的入口点 —— 它返回了[`SpeechSynthesis`](https://developer.mozilla.org/zh-CN/docs/Web/API/SpeechSynthesis) 的一个实例，对于 web 语音合成的控制接口。

```js
var synth = window.speechSynthesis;

var inputForm = document.querySelector("form");
var inputTxt = document.querySelector(".txt");
var voiceSelect = document.querySelector("select");

var pitch = document.querySelector("#pitch");
var pitchValue = document.querySelector(".pitch-value");
var rate = document.querySelector("#rate");
var rateValue = document.querySelector(".rate-value");

var voices = [];
```

### 填充 select 元素

为使用设备上可用的不同的语音选项填充 [select](https://developer.mozilla.org/zh-CN/docs/Web/HTML/Element/select) 元素，我们写了一个 `populateVoiceList()` 方法。首先调用 [`SpeechSynthesis.getVoices()`](https://developer.mozilla.org/zh-CN/docs/Web/API/SpeechSynthesis/getVoices) ，这个函数返回包含所有可用语音 ([`SpeechSynthesisVoice`](https://developer.mozilla.org/zh-CN/docs/Web/API/SpeechSynthesisVoice)对象) 的列表。接下来循环这个列表，每次创建一个 [option](https://developer.mozilla.org/zh-CN/docs/Web/HTML/Element/option) 元素，设置它的文本内容以显示声音的名称（从 [SpeechSynthesisVoice.name](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisVoice/name) 获取），语音的语言（从 [SpeechSynthesisVoice.lang](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisVoice/lang) 获取），如果某个语音是合成引擎默认的 (检查 [SpeechSynthesisVoice.default](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisVoice/default) 为 `true` 的属性) 在文本内容后面添加 `-- DEFAULT`。

对于每个 `option` 元素，我们也创建了 `data-` 属性，属性值是语音的名字和语言，这样在之后我们可以轻松获取这个信息。之后把所有的 `option` 元素作为孩子添加到 `select` 元素内。

```js
function populateVoiceList() {
  voices = synth.getVoices();

  for (const voice of voices) {
    const option = document.createElement("option");
    option.textContent = `${voice.name} (${voice.lang})`;

    if (voice.default) {
      option.textContent += " — DEFAULT";
    }

    option.setAttribute("data-lang", voice.lang);
    option.setAttribute("data-name", voice.name);
    voiceSelect.appendChild(option);
  }
}
```

早期版本的浏览器不支持 [voiceschanged](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis/voiceschanged_event) 事件，只有当 [SpeechSynthesis.getVoices()](https://developer.mozilla.org/zh-CN/docs/Web/API/SpeechSynthesis/getVoices) 被触发时才返回语音列表。
而其他浏览器，比如 Chrome 中，你必须等待 `voiceschanged` 事件触发后才能获得可用语音列表。
为了兼容这两种情况，我们运行如下代码：

```js
populateVoiceList();
if (speechSynthesis.onvoiceschanged !== undefined) {
  speechSynthesis.onvoiceschanged = populateVoiceList;
}
```

### 说出输入的文本

接下来我们创建一个事件处理器（event handler），开始说出在文本框中输入的文本。我们把 [onsubmit](https://developer.mozilla.org/zh-CN/docs/Web/API/HTMLFormElement/submit_event) 处理器挂在表单上，当 <kbd>Enter</kbd>/<kbd>Return</kbd> 被按下，对应行为就会发生。我们首先通过构造函数创建一个新的 [SpeechSynthesisUtterance()](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesisUtterance/SpeechSynthesisUtterance) 实例 —— 把文本输入框中的值作为参数传递。

接下来，我们需要弄清楚使用哪种语音。使用 [HTMLSelectElement](https://developer.mozilla.org/en-US/docs/Web/API/HTMLSelectElement) `selectedOptions` 属性返回当前选中的 [`<option>`](https://developer.mozilla.org/zh-CN/docs/Web/HTML/Element/option) 元素。然后使用元素的`data-name`属性，找到 [`SpeechSynthesisVoice`](https://developer.mozilla.org/zh-CN/docs/Web/API/SpeechSynthesisVoice) 对象的`name`匹配`data-name` 的值。把匹配的语音对象设置为[`SpeechSynthesisUtterance.voice`](https://developer.mozilla.org/zh-CN/docs/Web/API/SpeechSynthesisUtterance/voice) 的属性值。

最后，我们设置 [`SpeechSynthesisUtterance.pitch`](https://developer.mozilla.org/zh-CN/docs/Web/API/SpeechSynthesisUtterance/pitch) 和[`SpeechSynthesisUtterance.rate`](https://developer.mozilla.org/zh-CN/docs/Web/API/SpeechSynthesisUtterance/rate) 属性值为对应范围表单元素中的值。哈哈所有准备工作就绪，调用 [`SpeechSynthesis.speak()`](https://developer.mozilla.org/zh-CN/docs/Web/API/SpeechSynthesis/speak) 开始说话。把 [`SpeechSynthesisUtterance`](https://developer.mozilla.org/zh-CN/docs/Web/API/SpeechSynthesisUtterance) 实例作为参数传递。

```js
inputForm.onsubmit = function(event) {
  event.preventDefault();

  var utterThis = new SpeechSynthesisUtterance(inputTxt.value);
  var selectedOption = voiceSelect.selectedOptions[0].getAttribute('data-name');
  for (const voice of voices) {
    if (voice.name === selectedOption) {
      utterThis.voice = voice;
    }
  }
  utterThis.pitch = pitch.value;
  utterThis.rate = rate.value;
  synth.speak(utterThis);
```

在事件处理器的最后部分，我们加入了一个 [`SpeechSynthesisUtterance.onpause`](https://developer.mozilla.org/zh-CN/docs/Web/API/SpeechSynthesisUtterance/onpause) 处理器，来展示[`SpeechSynthesisEvent`](https://developer.mozilla.org/zh-CN/docs/Web/API/SpeechSynthesisEvent) 如何可以很好地使用。当 [`SpeechSynthesis.pause()`](https://developer.mozilla.org/zh-CN/docs/Web/API/SpeechSynthesis/pause) 被调用，这将返回一条消息，报告该语音暂停时的字符编号和名称。

```js
utterThis.onpause = (event) => {
  const char = event.utterance.text.charAt(event.charIndex);
  console.log(
    `Speech paused at character ${event.charIndex} of "${event.utterance.text}", which is "${char}".`,
  );
};
```

最后，我们在文本输入框添加了 [blur()](https://developer.mozilla.org/zh-CN/docs/Web/API/HTMLElement/blur) 方法。这主要是在 Firefox 操作系统上隐藏键盘

```js
  inputTxt.blur();
}
```

### 更新 pitch 和 rate 的显示数值

代码的最后部分，在每次滑动条移动时，更新 `pitch/rate` 在 UI 中展示的值。

```js
pitch.onchange = () => {
  pitchValue.textContent = pitch.value;
};

rate.onchange = () => {
  rateValue.textContent = rate.value;
};
```

# 参考资料

- https://developer.mozilla.org/zh-CN/docs/Web/API/Web_Speech_API/Using_the_Web_Speech_API#speech_synthesis
- https://github.com/mdn/translated-content/pull/21832
- https://pr21832.content.dev.mdn.mozit.cloud/zh-CN/docs/Web/API/Web_Speech_API/Using_the_Web_Speech_API#speech_synthesis