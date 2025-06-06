---
author: 路边的阿不
title: 在本地跑一个AI模型(4) - 会说话的模型
slug: run-an-ai-model-locally-4
description: "Want your AI model to speak? Try using the XTTS v2 model! It can generate high-quality, natural-sounding voices from text in multiple languages. With just a few commands, you can turn your text into realistic speech. Give it a try now!"
date: 2024-04-15 10:36:13
draft: false
ShowToc: true
TocOpen: true
tags:
  - TTS
  - Voice Generation
  - Local AI
  - Tutorial
categories:
  - AI
---
大家好，好久不见。前三篇教程我们聊了如何在本地搭建一个大语言模型，它能够理解和生成文本，这确实是一个非常有趣且有前景的应用领域。今天，我们将更进一步，让你的AI模型具备实际的语音输出能力。

让AI模型将文字转化为语音我们通常称之为语音合成，也就是我们常说的文本转语音（`Text-to-Speech, TTS`）。在AI高速发展的今天，人们已经可以使用神经网络训练模型。我们今天介绍的**XTTS v2**即是由 `coqui-ai` 开源的一种基于神经网络的模型，可以从多种语言的文本生成语音。**XTTS v2** 以其高质量、自然的声音以及克隆声音的能力而闻名。

虽然`coqui-ai`公司正在关闭过程中，但我们仍能从其开源的`TTS`代码中获益。感谢开源，让我们有机会在本地运行它。

## 安装`TTS`

**截止目前，`TTS`项目尚不支持`python 3.12`版本，因此本文使用`venv`虚拟环境进行安装。**

```shell
# 使用3.10版本的python创建venv
/opt/homebrew/opt/python@3.10/libexec/bin/python3 -m venv .venv
# 激活venv
source .venv/bin/activate 
```

我们不需要进行二次开发和调试，因此直接使用`pip`进行安装：

```shell
pip install TTS
```

## 下载XTTS v2模型

和`Ollama`一样，`TTS`支持很多种模型。使用该命令查看一下所有支持的模型：

```shell
tts --list_models
```

虽然`TTS`会自动下载模型，但我相信大部分人还是喜欢自己下载模型，因为这样更快速和直接。

从[huggingface](https://huggingface.co/coqui/XTTS-v2/tree/main)下载所有文件，放至`~/Library/Application Support/tts/tts_models--multilingual--multi-dataset--xtts_v2`目录下（MAC用户）或`C:\users\你的用户名\AppData\Local\tts\tts_models–multilingual–multi-dataset–xtts_v2`（Windows用户）。

运行该命令进行验证：

```shell
tts --model_name tts_models/multilingual/multi-dataset/xtts_v2 --list_speaker_idxs
```

如果出现以下内容则说明模型下载正确：

```
 > tts_models/multilingual/multi-dataset/xtts_v2 is already downloaded.
 > Using model: xtts
 > Available speaker ids: 
 .....
```

`Available speaker ids`列出来的是该模型内置的语音样板，有男有女。普通用户只要选择其中一个使用就可以了。

## 制作语音样板

前面已经提到过**声音克隆**，也就是说它可以根据你提供的一个样本语音文件生成与样本文件中声音相似的语音。简单来说，就好像是样本中的那个人在说话一样。

如果你想AI克隆你的声音，那你可以自己制作一个语音样板。你可以朗读并录制一个大约30秒的音频文件，做成`.wav`格式即可。你也可以使用这个[示例样板](https://babyno.top/data/yanglan.wav)，是杨澜在TED上演讲的片段。

## python代码

让我们编写一段最简单的代码测试一下功能：

```python
import torch
from TTS.api import TTS


text = """
随着 AI 智能浪潮到来，AI 编码助手成为越来越多开发者的必备工具，将开发者从繁重的编码工作中解放出来，极大地提高了编程效率，帮助开发者实现更快、更好的代码编写。

如今，国内有一位 AI 程序员，已经在某互联网大厂上岗一段时间了。

它就是阿里云数万名工程师最近频繁打交道的新同事 ——「通义灵码」，专属工号「AI001」。

通义灵码在正式入职之前，先是在阿里云内部和外部「实习」了几个月。大家的评价都很不错，真实好评率超 80%。

而且，通义灵码的工作节奏比 996 还要极致：7x24 小时随叫随到……

以 API 开发测试工作为例，通义灵码可将数分钟甚至十几分钟的人工编写测试耗时缩短到秒级，节省了人类程序员 70% 以上的测试代码工作量。

通义灵码免费向全民开放，所有人可以随时随地在手机上写代码、读代码、学习编程技能。所有人可以前往下方链接写代码、读代码、学习编程技能！
"""


device = "cuda" if torch.cuda.is_available() else "cpu"
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

# generate speech by cloning a voice using default settings
tts.tts_to_file(text=text,
                file_path="output.wav",
                speaker_wav="yanglan.wav",
                # speaker='Sofia Hellen',
                language="zh-cn"
                )
```

注意这里的`speaker_wav`和`speaker`参数，如果你想让AI克隆语音，那就使用`speaker_wav`，并指定语音样板。如果你没有这方面的需求，可以直接使用`speaker`指定一个内置的语音样板。

等待代码执行的时间可能有些漫长，跟你的电脑配置有关。最后生成的语音文件为`output.wav`。

## 总结

最后试听一下`output.wav`吧，是不是跟你预期的有点差距？我特意挑选了一段比较复杂的文字来做实验，比如出现了`AI`、`996`、和`7x24`等等词汇。这些词汇模型确实不太好把握，而且还存在一个老生常谈的问题：所有模型对中文的支持都不太好。但也不用太悲观，我们现在还都是使用的默认配置不是吗？经过一番调教后模型是不是能更智能呢？