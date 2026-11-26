---
author: "路边的阿不"
title: 世嘉土星图形技术研究3
slug: sega-saturn-graphics-technology-research-3
description: ""
date: 2026-09-18 08:28:02
draft: false
ShowToc: true
TocOpen: true
tags:
  - 土星逆向
  - 纹理编码
  - 文件格式解析
  - 2D图像
categories:
  - 逆向工程
---
本篇文章总结一下在《慟哭そして．．．》游戏中出现的三种图片存储格式。

从最终的颜色表示来看，世嘉土星（Sega Saturn）的 VDP1 和 VDP2 都支持 15-bit RGB，也就是 R、G、B 各使用 5 bit，可以表示 32768 种颜色。对于 VDP1 的 RGB mode，像素以 16 bit 存储，其中最高位用于标识 RGB code；VDP2 的 15-bit RGB format 同样由 R、G、B 各 5 bit 组成。

但游戏中的图片并不一定直接以这种 RGB 数据保存。为了适应不同的图像类型和运行时的渲染方式，游戏采用了不同的数据组织形式。

本文目前整理出了三种比较典型的图片格式：DGT2、Raw 16×16，以及基于 Palette、Map 和 Character/Cell 组织的 Mapped 2×2。

它们最终都可以还原为屏幕上的 RGB 颜色，但实现方式并不相同：

* **DGT2** 是一种相对完整、独立的图片格式，包含图片尺寸、颜色模式、调色板以及像素数据等信息。
* **Raw 16×16** 更接近裸像素数据，图片没有明显的文件头，像素以 16-bit RGB 数据保存，并按照 16×16 宏块组织。
* **Mapped 2×2** 则采用典型的 Tile/Cell 思路，通过 Map 指定 Character，通过 Character 组合 8×8 Cell，再通过 Palette 将像素索引转换成实际颜色。

因此，这三种格式真正的区别并不是“如何保存 RGB555”，而是**如何组织和描述一张图片，以及如何在有限的存储空间和 VRAM 条件下复用这些图形数据**。

接下来分别分析这三种格式的数据结构，以及它们最终是如何还原成我们看到的图片的。

## DGT2 格式

DGT2 是世嘉为土星主机设计的官方图像格式，手册在[这里](https://docs.exodusemulator.com/Archives/SSDDV25/segahtml/index.html?page=grph/frm/mac_dgt2.htm)查看。

游戏中出现的是 DGT2 的 DC 模式，不存在调色板，像素以 16-bit RGB 数据保存。图片的宽和高直接保存在文件头中，因此解析起来是最方便的。代表文件就是游戏中的两张 LOGO。

![](imgs/posts/2026-09-18-sega-saturn-graphics-technology-research-3/LOGO001.webp)

![](imgs/posts/2026-09-18-sega-saturn-graphics-technology-research-3/LOGO002.webp)

## Raw 16×16 格式

与 DGT2 类似的是，不存在调色板，像素以 16-bit RGB 数据保存。不同点在于，没有文件头，因此不知道宽和高；像素不是直接像素流，而是以 2×2 Cell 拼接。每个 Cell 是 8 x 8 像素，因此像素的组织形式是 16 x 16 的宏块，每个宏块占据 256 个像素，即 512 字节，如下图。

```
+--------+--------+
|  8×8   |  8×8   |
|        |        |
+--------+--------+
|  8×8   |  8×8   |
|        |        |
+--------+--------+
```

代表文件是游戏结局 CG 和游戏中全屏人物 CG。

![](imgs/posts/2026-09-18-sega-saturn-graphics-technology-research-3/ED001.webp)

![](imgs/posts/2026-09-18-sega-saturn-graphics-technology-research-3/MF037.webp)

## Mapped 2×2 格式

这就是[上一篇](https://babyno.top/posts/2026/09/sega-saturn-graphics-technology-research-2/)我们解析的一种格式，真正体现 Saturn Tile 思维的格式。上一篇已经详细解析过了，这里就不展开了。

代表文件是人物立绘，全屏建筑背景 CG。

![](imgs/posts/2026-09-18-sega-saturn-graphics-technology-research-3/MC_21.webp)

![](imgs/posts/2026-09-18-sega-saturn-graphics-technology-research-3/MN000.webp)

## 开源代码

如果你对本文介绍的图片解析算法感兴趣，可以查看 [Github](https://github.com/caol64/doukoku-image-extractor) 项目，代码已开源。

## 参考资料

https://docs.exodusemulator.com/Archives/SSDDV25/segahtml/index.html?page=index.htm

---

欢迎关注我的公众号，第一时间获取最新文章。

![](https://babyno.top/imgs/qrcode.jpg)
