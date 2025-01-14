---
author: "路边的阿不"
title: 球会04游戏逆向-存档文件解析
slug: sakatsuku-04-game-reverse-save-file-analysis
description: ""
date: 2025-01-14 11:00:40
draft: false
ShowToc: true
TocOpen: true
tags:
  - Reverse
categories:
  - Sakatsuku04
---

本系列将和大家一起探索PS2游戏——J联盟创造球会04（J.League Pro Soccer Club o Tsukurou! 04）的逆向研究。本文先解析一下游戏存档。

## 存档文件目录

将游戏存档导出后，文件目录如下：

```
BISLPM-65530Saka_G03
├── BISLPM-65530Saka_G03
├── head.dat
├── icon.sys
├── mc_main_1.ico
├── mc_main_2.ico
└── mc_main_3.ico
```

目录名为`BISLPM-65530Saka_G`后面跟一个数字，如果在同一个记忆卡上有多条记录，后面的数字会从`01`开始递增。

`BISLPM-65530Saka_G03`文件是主存档文件，保存着所有游戏数据。它使用`Bit-Packing`技术进行压缩，再使用`BlowFish`算法进行加密。

`head.dat`保存着一些简单的游戏信息，比如球会名、游戏中的日期等。它并没有经过任何的压缩和加密。

`icon.sys`和三个`mc_main_x.ico`文件是存档的3D图标，这在我以前的文章里介绍过。[链接](https://babyno.top/posts/2023/10/parsing-ps2-3d-icon/)

## 文件结构

`BISLPM-65530Saka_G03`和`head.dat`有着相同的文件结构，如下图：

![](imgs/posts/2025-01-14-sakatsuku-04-game-reverse-save-file-analysis/saka_tool.jpg)

可以看到每个文件都分为4部分，`Header`、`Data Block1`、`CRC`、`Data Block2`。

文件的前4个字节是`Header`，从中可以提取出`Data Block`的总大小。根据该大小，就可以推算出`Data Block1`、`CRC`、`Data Block2`的具体位置。最后，将`Data Block1`和`Data Block2`拼接后即可。

以`head.dat`为例：

![](imgs/posts/2025-01-14-sakatsuku-04-game-reverse-save-file-analysis/2.jpg)

图中深色标出的分别是`Header`和`CRC`，白色的两块分别是`Data Block1`和`Data Block2`。