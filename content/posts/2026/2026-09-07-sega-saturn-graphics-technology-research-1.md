---
author: "路边的阿不"
title: 世嘉土星图形技术研究1
slug: sega-saturn-graphics-technology-research-1
description: ""
date: 2026-09-07 15:48:02
draft: false
ShowToc: true
TocOpen: true
tags:
  - 土星逆向
categories:
  - 逆向工程
---

世嘉土星（Sega Saturn）的图形架构由两块分工明确的专用图形芯片构成：负责 3D 多边形与动态精灵绘制的 **VDP1**，以及负责多层 2D 背景、仿射变换与最终图像合成的 **VDP2**。本次实验使用 Data East 于 98 年出品的游戏《慟哭 そして…》进行测试，目标是提取游戏中精美的 CG 图片。

我会使用两个土星模拟器进行数据提取操作 —— [Ymir](https://github.com/ymir-emu/Ymir) 和 [Yabause](https://github.com/Yabause/yabause)。这是个人偏好，你完全可以仅使用`Yabause`操作。

## 提取原始数据

首先进入游戏，来到第一处静态界面。

![](imgs/posts/2026-09-07-sega-saturn-graphics-technology-research-1/0.webp)

点击`Ymir`菜单`Debug`下的`Dump all memory`。

![](imgs/posts/2026-09-07-sega-saturn-graphics-technology-research-1/11.webp)

找到`Ymir`安装目录下的`dumps`文件夹，在其中找到`vdp1-vram.bin`、`vdp2-cram.bin`和`vdp2-vram.bin`。

点击`Ymir`菜单`Debug`下的`Open memory viewer`。

![](imgs/posts/2026-09-07-sega-saturn-graphics-technology-research-1/9.webp)

点击`Main address space`边上的三角图标。

![](imgs/posts/2026-09-07-sega-saturn-graphics-technology-research-1/6.webp)

找到`VDP2 registers`。

![](imgs/posts/2026-09-07-sega-saturn-graphics-technology-research-1/7.webp)

点击左侧`Dump`按钮。

![](imgs/posts/2026-09-07-sega-saturn-graphics-technology-research-1/8.webp)

在`Ymir`安装目录下的`dumps`文件夹内找到刚刚 dump 下来的文件，改名为`vdp2-registers.bin`。

至此所有原始数据抓取完毕，将它们保存到同一个目录下。

## 提取配置数据

运行`Yabause`至相同页面，点击`View` - `Layer`，逐个勾选`Vdp1`、`NBGx`等按钮进行观察。在这一步你可以确认每个图层显示的内容，比如最大的那张背景图会显示在`NBG0`。

![](imgs/posts/2026-09-07-sega-saturn-graphics-technology-research-1/1.webp)

接下来提取`VDP1`和`VDP2`的配置数据。依次点击`Debug` - `VDP1` 和 `VDP2`。

![](imgs/posts/2026-09-07-sega-saturn-graphics-technology-research-1/2.webp)

在`VDP1`的`Debug`页面，你可以看到三个`Scaled Sprite`，这三个精灵图组合成了游戏中文字的背景图和光标。记下每个精灵图的`Command Info`。

![](imgs/posts/2026-09-07-sega-saturn-graphics-technology-research-1/3.webp)

在`VDP2`的`Debug`页面，你看到的是背景图图层的配置数据，由前面观察可知，`NBG0`是背景大图图层，`NBG3`是字幕图层，记下每个图层的配置。

![](imgs/posts/2026-09-07-sega-saturn-graphics-technology-research-1/4.webp)

## 稍作整理

目前我们得到了：

- `vdp1-vram.bin`（对话框背景、对话光标）
- `vdp2-cram.bin`（血腥的背景CG、文字图块）
- `vdp2-vram.bin`（调色板 Palette）
- `vdp2-registers.bin`（解码关键指令）

## 解码 VDP1

`VDP1`中有三个缩放精灵：

```
Scaled Sprite
Zoom Point: Center-center
xa = 159, ya = 191, xb = 319, yb = 63
Texture address = 00010B40
Texture width = 320, height = 64
Texture read direction: Normal
Pre-clipping Enabled
Transparent Pixel Enabled
Color mode: 8 BPP(128 color bank)
Color bank: 00000000
Color Calc. mode: Replace
```

- **左半边对话框底图：**
  - 数据位置：vdp1-vram.bin 的偏移量 **0x10B40**
  - 格式：8 BPP (256色)
  - 尺寸：宽 320，高 64

```
Scaled Sprite
Zoom Point: Center-center
xa = 479, ya = 191, xb = 319, yb = 63
Texture address = 00015B40
Texture width = 320, height = 64
Texture read direction: Normal
Pre-clipping Enabled
Transparent Pixel Enabled
Color mode: 8 BPP(128 color bank)
Color bank: 00000000
Color Calc. mode: Replace
```

- **右半边对话框底图：**
  - 数据位置：vdp1-vram.bin 的偏移量 **0x15B40**
  - 格式：8 BPP (256色)
  - 尺寸：宽 320，高 64
  - 验证计算： 左半张图大小 = 320 * 64 * 1 byte (8BPP) = 20,480 字节 = 十六进制的 0x5000。而 0x10B40 + 0x5000 = 0x15B40。完美吻合！

```
Scaled Sprite
Zoom Point: Center-center
xa = 600, ya = 211, xb = 31, yb = 15
Texture address = 00010000
Texture width = 32, height = 16
Texture read direction: Normal
Pre-clipping Enabled
Transparent Pixel Enabled
Color mode: 4 BPP(16 color bank)
Color bank: 00000400
Color Calc. mode: Replace
```

- **跳动的光标 (倒三角)：**
  - 数据位置：vdp1-vram.bin 的偏移量 **0x10000**
  - 格式：4 BPP (16色)
  - 尺寸：宽 32，高 16

这三个缩放精灵会交由 VDP1 在硬件内部渲染为四边形。由于其中直接显示了纹理的宽和高，我们大胆猜测这三个纹理各自是一张连续的矩形位图（bitmap），像素数据按行连续存储（从左到右、从上到下）。只需写一个脚本，从`vdp1-vram.bin`的偏移`0x10B40`处，提取`8 BPP`的`320 x 64`字节数据即可还原，当然别忘了去`vdp2-vram.bin`查找调色板。其左右半边对话框底图，如下：

![](imgs/posts/2026-09-07-sega-saturn-graphics-technology-research-1/12.webp)

![](imgs/posts/2026-09-07-sega-saturn-graphics-technology-research-1/13.webp)

未完待续。

---

欢迎关注我的公众号，第一时间获取最新文章。

![](https://babyno.top/imgs/qrcode.jpg)
