---
author: "路边的阿不"
title: PS2纹理图片编码算法「A1B5G5R5」
slug: ps2-texture-encoding-algorithm-a1b5g5r5
description: "Delve into the unique texture mapping coding algorithm, A1B5G5R5, utilized by PS2. Our detailed guide takes you through the principle behind this lossy yet efficient form of image encoding that significantly reduces image size."
date: 2023-10-20 14:48:31
draft: false
ShowToc: true
TocOpen: true
tags: ["A1B5G5R5", "Python", "Algorithm", "Texture Encoding", "Image Compression"]
categories: ["Programming"]
---

在[上一篇文章](../rle-algorithm-in-ps2/)里我们介绍了`PS2`使用的图片压缩算法`RLE`，这次我们再来研究一下它的纹理贴图编码算法——`A1B5G5R5`。

## 简介
对于纹理来说，常用的图片编码格式如`jpg`或`png`都不适合。因为图片是由`GPU`读取并进行渲染的，你总不能送过去一张`jpg`图片，让`GPU`要读取其中一个像素的时候，先把整个图片解码吧？因此最理想的图片格式是未经压缩的位图格式，可以根据像素点坐标直接获取`RGB`数据。今天要介绍的`A1B5G5R5`正是这种编码格式之一。

## 分析
![](/imgs/posts/2023-10-20-ps2-texture-encoding-algorithm-a1b5g5r5/3.jpg)

上面两张纹理图片是从`PS2`存档中提取出来的，它们以`位图`的形式储存，像素数量为`128x128`。

标准的`32位`位图，每个像素占用`4字节`数据，分别储存了`RGBA`四个通道的数据。因此上面两个纹理图片的图片大小为`128x128x4`字节。`32位RGBA`每像素数据结构如下：

![](/imgs/posts/2023-10-20-ps2-texture-encoding-algorithm-a1b5g5r5/RGBA.jpg)

对于`A1B5G5R5`编码来说，每个像素占用`2字节`数据，其中`alpha通道`占用`1位`，其它3种颜色各占`5位`。每像素数据结构如下：

![](/imgs/posts/2023-10-20-ps2-texture-encoding-algorithm-a1b5g5r5/A1B5G5R5.jpg)

将`A1B5G5R5`解码为`32位RGBA`可以用下图的方法进行。

![](/imgs/posts/2023-10-20-ps2-texture-encoding-algorithm-a1b5g5r5/decode.jpg)

伪代码如下：
```python
while tex_offset < len(self.texture):
    b = tex_struct.unpack_from(self.texture, tex_offset)[0]
    out[rgb_tex_offset] = (b & 0x1F) << 3 # R
    out[rgb_tex_offset + 1] = ((b >> 5) & 0x1F) << 3 # G
    out[rgb_tex_offset + 2] = ((b >> 10) & 0x1F) << 3 # B
    rgb_tex_offset += 3
    tex_offset += tex_struct.size
```

很明显可以看到，将`32位`的`RGBA`图片编码成`16位`的`A1B5G5R5`，会丢失每种色彩的最后3个`bit`数据，是一种有损编码格式，但带来的好处是压缩比2:1，图片缩小了一半。再配合上一篇讲到的`RLE`编码，可以进一步缩小图片大小。

## 最后
最后放上上面两个纹理图片渲染后的效果，有小伙伴还记得这两个游戏吗？

![](/imgs/posts/2023-10-20-ps2-texture-encoding-algorithm-a1b5g5r5/4.jpg)
