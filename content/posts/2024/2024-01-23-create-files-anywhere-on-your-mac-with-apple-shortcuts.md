---
author: "路边的阿不"
title: 使用「快捷指令」在Mac上的任何地方创建文件
slug: create-files-anywhere-on-your-mac-with-apple-shortcuts
description: "Discover how to simplify file creation in any directory on your Mac using Apple's Shortcuts. Enhance your productivity with this step-by-step guide!"
date: 2024-01-23 17:07:11
draft: false
ShowToc: true
TocOpen: true
tags: ["Apple Shortcuts", "Automation", "Efficiency"]
categories: ["效率"]
---

MAC有个令人“脑阔疼”的地方，没法在直接在某个目录下面创建文件，有的时候真的不方便。还好我们有“**快捷指令**”，这点问题不在话下。

## 原理介绍

使用**快捷指令**调用`applescript`脚本，再让`applescript`调用`Finder`内部接口创建文件。`Finder`会在用户所在的目录下生成文件。

通过**快捷指令**提供的对话框功能，可以在对话框里设置你想生成的文件的名称。

![input](imgs/posts/2024-01-23-create-files-anywhere-on-your-mac-with-apple-shortcuts/input.webp)

如果不输入文件名，就以默认名称生成文本文件。

## 指令设置

按照下面截图进行设置：

![shortcuts](imgs/posts/2024-01-23-create-files-anywhere-on-your-mac-with-apple-shortcuts/shortcuts.webp)

两段`applescript`脚本分别是:

```applescript
on run {input, parameters}
	tell application "Finder"
		set fileName to input
		set filePath to (the target of the front window) as text
		make new file at filePath with properties {name:fileName}
	end tell
	return input
end run
```

```applescript
tell application "Finder" to make new file at (the target of the front window) as alias
```

这里就不解释脚本的含义了。

此外，还要为这个指令设置快捷键，如下图：

![hotkey](imgs/posts/2024-01-23-create-files-anywhere-on-your-mac-with-apple-shortcuts/hotkey.webp)

在红框处只要设置自己喜欢的快捷键就行了。

## 看看成果

创建文本文件：

![example1](imgs/posts/2024-01-23-create-files-anywhere-on-your-mac-with-apple-shortcuts/example1.gif)

指定文件名创建文件：

![example2](imgs/posts/2024-01-23-create-files-anywhere-on-your-mac-with-apple-shortcuts/example2.gif)

## 下载地址

https://www.icloud.com/shortcuts/951edcaf19bb45d8be6f9a90532e253d