---
author: 路边的阿不
title: Base64编码在「Apple快捷指令」中的妙用
slug: the-wonders-of-base64-encoding-in-apple-shortcuts
description: Learn how to harness the power of Base64 encoding to insert attachments into Apple Shortcuts actions, boosting the efficiency and functionality of your daily errands beyond the obvious.
date: 2023-12-14 15:55:11
draft: false
ShowToc: true
TocOpen: true
tags:
  - 快捷指令
  - Apple Shortcuts
  - Automation
  - Tutorial
categories:
  - 生产力
---
苹果快捷指令是一款强大的工具，可以帮助我们自动化日常任务。在创建快捷指令时，有时我们需要添加附件，例如文本、图片、音频等。但是，苹果快捷指令本身并不支持添加附件，因此我们需要使用一些技巧来实现。

## Base64编码

Base64是一种编码格式，可以将任意数据转换为可存储和传输的字符串。苹果快捷指令支持添加文本，因此我们可以将附件编码成Base64字符串，然后通过文本的形式添加到快捷指令中。

## 示例

假设我们需要创建一个快捷指令，生成一个模版“numbers”文件。我们可以先将“numbers”文件编码成Base64字符串，然后通过文本的形式添加到快捷指令中。

以下是具体步骤：

1. 创建“numbers”文件，选择“文件”>“保存”。
2. 使用如下“快捷指令”将其生成Base64字符串并保存在剪贴板中。
![](imgs/posts/2023-12-14-the-wonders-of-base64-encoding-in-apple-shortcuts/1.webp)
1. 打开“快捷指令”应用，创建一个新的快捷指令。
2. 在“操作”列表中，找到“文本”>“输入文本”。
3. 在“文本”字段中，粘贴Base64字符串。
4. 点击“保存”。

现在，我们就可以使用这个快捷指令来生成“numbers”文件了。

下图是“[加油记录](https://github.com/caol64/apple-shortcuts/blob/main/FuelingRecord/README.md)”里的一个例子，首次执行快捷指令时，会自动创建一个模版numbers文件，这个模版文件就使用base64编码隐藏在快捷指令中。

![](imgs/posts/2023-12-14-the-wonders-of-base64-encoding-in-apple-shortcuts/2.webp)

## 注意事项

Base64编码后的字符串可能会很长，因此我们需要注意输入文本的字数限制。此外，Base64编码后的字符串可能包含非法字符，因此我们需要在使用前进行检查。

## 总结

Base64编码是一种可以帮助我们在苹果快捷指令中添加附件的有效技巧。它操作简单，而且可以应用于各种场景。