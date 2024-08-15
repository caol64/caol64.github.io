---
author: 路边的阿不
title: 解析PS2游戏存档3D图标
slug: parsing-ps2-3d-icon
description: Dive deep into the realm of PS2 game development as we demonstrate how to unpack 3D icon data from save files. Our intricate guide covers vertices, model animation, textures, lighting, and backgrounds, all with accurate coding details.
date: 2023-10-04 18:00:34
draft: false
ShowToc: true
TocOpen: true
tags:
  - OpenSource
categories:
  - Ps2mc
---
![](imgs/posts/2023-10-04-parsing-ps2-3d-icon/1.gif)

看到这个图片，对于熟悉PS2的老玩家来说应该不会陌生。它是PS2记忆卡管理界面中的游戏存档3D图标。本篇文章我们将介绍如何从存档文件里解析出这个活动的小人。

## 01 解析目标

A：我们能从存档文件中解析到什么？
- 图标模型的所有顶点、法线
- 图标模型的动作帧
- 光照
- 纹理及纹理坐标
- 背景颜色及透明度

B：我们需要做什么？
- 编写着色器渲染背景和图标
- 将图标模型的动作帧组成动画
- 构建模型矩阵、视图矩阵、透视矩阵，使显示接近PS2原生效果

完成整个功能估计需要两篇文章，本篇主要介绍A。

## 02 解析`icon.sys`

上一篇我们介绍了如何导出游戏的存档文件，事实上每个存档里都会有一个`icon.sys`的文件，这个可以看作图标的配置文件。`icon.sys`是一个固定大小（964字节）的文件，其结构如下：

|offset|length|description|
|----|----|----|
|**0**|byte[4]|`magic`：PS2D|
|**4**|uint16|0|
|**6**|uint16|游戏标题换行符所在位置，注1|
|**8**|uint32|0|
|**12**|uint32|`bg_transparency`，背景透明度，0-255|
|**16**|uint32[4]|`bg_color`，背景左上角颜色（RGB-，0-255）|
|**32**|uint32[4]|`bg_color`，背景右上角颜色（RGB-，0-255）|
|**48**|uint32[4]|`bg_color`，背景左下角颜色（RGB-，0-255）|
|**64**|uint32[4]|`bg_color`，背景右下角颜色（RGB-，0-255）|
|**80**|uint32[4]|`light_pos1`，光源1（XYZ-，0-1）|
|**96**|uint32[4]|`light_pos2`，光源2（XYZ-，0-1）|
|**112**|uint32[4]|`light_pos3`，光源3（XYZ-，0-1）|
|**128**|uint32[4]|`light_color1`，光源1颜色（RGB-，0-1）|
|**144**|uint32[4]|`light_color2`，光源2颜色（RGB-，0-1）|
|**160**|uint32[4]|`light_color3`，光源3颜色（RGB-，0-1）|
|**176**|uint32[4]|`ambient`，环境光（RGB-，0-1）|
|**192**|byte[68]|`sub_title`，游戏标题（空字符结尾, S-JIS编码）|
|**260**|byte[64]|`icon_file_normal`，普通图标文件名（空字符结尾），注2|
|**324**|byte[64]|`icon_file_copy`，拷贝图标文件名（空字符结尾），注2|
|**388**|byte[64]|`icon_file_delete`，删除图标文件名（空字符结尾），注2|
|**452**|byte[512]|全0|

注1：游戏标题`sub_title`显示为2行，该值即为在标题的第几个字节换行，如图：

![](imgs/posts/2023-10-04-parsing-ps2-3d-icon/1.jpg)

注2：每个游戏存档可以对应3个图标`icon`文件，分别在不同场景显示。

可以看到`icon.sys`文件里主要提供了背景、光照等数据，另外一个比较重要的部分是3d图标所在的文件名。

## 03 解析`icon`文件

不像`icon.sys`文件，每个游戏的`icon`文件是不确定的，大小不确定，数量也不确定，但至少会有1个。有的游戏拷贝图标和删除图标与普通图标共用一个图标。

### 3.1 文件结构

|名称|说明|
|----|----|
|Icon头|固定大小，20个字节|
|顶点段|保存图标模型的所有顶点和法线数据|
|动画段|保存图标模型动画帧信息|
|纹理段|保存图标模型纹理|

### 3.2 `Icon`头

`Icon`头存储了我们解码不同数据段所需的所有重要信息，其中包括：
- “顶点段”中包含的顶点数量以及动画形状的数量
- 纹理数据是否经过压缩

在图标文件中，`Icon`头总是位于偏移量 0 处。以下是`Icon`头结构：

|Offset|Length|Description|
|----|----|----|
|0000|uint32|`magic`：`0x010000`|
|0004|uint32|`animation_shapes`，动画形状，注1|
|0008|uint32|`tex_type`，纹理类型，注2|
|0012|uint32|未知，固定值`0x3F800000`|
|0016|uint32|`vertex_count`，顶点数量，必定是3的倍数|

注1：图标模型有几套不同的顶点数据，对应不同的动作，称之为“形状”。将不同的形状循环渲染，即可形成动画效果。

注2：“纹理类型”这部分尚不明确，该值是4字节整形，我总结出来每个位相应的功能如下表，未必正确：

|mask|Description|
|----|----|
|0001|未知|
|0010|未知|
|0100|图标文件中存在纹理数据，有些游戏（如ICO）没有纹理数据，图标全黑|
|1000|图标文件中的纹理数据是被压缩过的|

### 3.3 顶点段

PS2 图标中的多边形总是由三个顶点形成的三角形组成。由于顶点是按一定规律排列的，因此只需按照规律读取顶点数据，就能轻松构建多边形。利用`OpenGL`或类似工具渲染这些数据，就能得到一个漂亮的图标线框。

“顶点段”包含图标中所有顶点的数据。每个顶点数据包含一组顶点坐标、法线坐标、纹理坐标以及一组`RGBA`数据，因此，拥有`m`个顶点和 `n`个形状的“顶点段”数据结构如下：


![](imgs/posts/2023-10-04-parsing-ps2-3d-icon/%E5%AD%98%E5%82%A8%E5%8D%A1-Vertex.jpg)

#### 顶点坐标

每个顶点坐标占用8字节，结构如下：

|Offset|Length|Description|
|----|----|----|
|0000|int16|X坐标，使用时需除以4096|
|0002|int16|Y坐标，使用时需除以4096|
|0004|int16|Z坐标，使用时需除以4096|
|0006|uint16|未知|

#### 法线坐标

每个法线坐标与顶点坐标数据结构一致。

#### 纹理坐标

每个纹理坐标占用4字节，结构如下：

|Offset|Length|Description|
|----|----|----|
|0000|int16|U坐标，使用时需除以4096|
|0002|int16|V坐标，使用时需除以4096|

#### 顶点RGBA

每个顶点颜色占用4字节，结构如下：

|Offset|Length|Description|
|----|----|----|
|0000|uint8|R，0-255|
|0001|uint8|G，0-255|
|0002|uint8|B，0-255|
|0003|uint8|A，0-255|

### 3.4 动画段

很遗憾关于“动画段”里的大部分内容，我还没完全搞懂含义。不过不用太在意，利用“顶点坐标插值”，仍然可以完成动画动作。

以下是“动画段”的数据结构：

![](imgs/posts/2023-10-04-parsing-ps2-3d-icon/%E5%AD%98%E5%82%A8%E5%8D%A1-Animation.jpg)

“动画段”包含“动画头”和若干“动画帧”，每个“动画帧”包含若干“关键帧”。

#### 动画头

“动画头”结构如下：

|Offset|Length|Description|
|----|----|----|
|0000|uint32|`magic`：0x01|
|0004|uint32|`frame length`：“动画帧”完成一个循环所需的“播放帧”，根据这个值可以计算出每个“动画帧”对应的“播放帧”数量|
|0008|float32|`anim speed`：播放速度，作用未知|
|0012|uint32|`play offset`：起始播放帧，作用未知|
|0016|uint32|`frame count`：“动画段”一共有几个“动画帧”，一般一个“形状”对应一个“动画帧”|

#### 帧数据`Frame Data`

“帧数据”直接位于“动画头”之后。

|Offset|Type|Description|
|----|----|----|
|0000|u32|Shape id|
|0004|u32|Number of keys|
|0008|u32|UNKNOWN|
|0012|u32|UNKNOWN|

#### 关键帧`Frame Key`

|Offset|Type|Description|
|----|----|----|
|0000|f32|Time|
|0004|f32|Value|

### 3.5 纹理段

纹理是像素为`128x128`的图片，使用`TIM`图像格式进行编码。根据`Icon头`里的`tex_type`字段，纹理分为未压缩和压缩两种类型。

#### 未压缩纹理

未压缩纹理的像素格式为`BGR555`，其中B、G、R各占用5`bit`，总共15`bit`，占用2字节（1个`bit`冗余）。如图：

```
High-order byte:    Low-order byte:
X B B B B B G G     G G G R R R R R

X = Don't care, R = Red, G = Green, B = Blue
```

因此原始图片大小固定为128x128x2字节。如果需将它的像素格式转为`RGB24`，可以用如下方法：

```
High-order byte:     Middle-order byte:    Low-order byte:
R R R R R 0 0 0      G G G G G 0 0 0       B B B B B 0 0 0
```

将5`bit`的色彩值转为8`bit`时，需将低3位补0。经过上述转换，每像素字节数变为3字节。同理也可将格式转为`RGBA32`，每像素字节数变为4字节。


#### 压缩纹理

压缩纹理使用非常简单的`RLE`算法进行压缩。第一个`u32`是压缩纹理数据的大小。其后的数据始终为`u16`的`rle_code`和`rle_data`交替出现，直到结束。
`rle_data`有两个变量：`data`数量`x`和重复次数`y`。`rle_code`作为计数器存在，如果小于`0xFF00`，则`x = 1`，`y = rle_code`；如果大于等于`0xFF00`，则`x = (0x10000 - rle_code)`，`y = 1`。如下图。

![](imgs/posts/2023-10-04-parsing-ps2-3d-icon/%E5%AD%98%E5%82%A8%E5%8D%A1-RLE.jpg)


将压缩纹理解压后，再根据上一节的内容即可转换为`RGB24`或`RGBA32`的图片。

## 04 结尾

至此为止图标的相关文件已经解析完毕了，万事俱备只欠东风，下一篇我们即将开始渲染模式，使用`PyGame`和`ModernGL`将渲染动画显示出来。

## 05 参考资料

- [gothi - icon.sys format](https://www.ps2savetools.com/documents/iconsys-format/)
- [Martin Akesson - PS2 Icon Format v0.5](http://www.csclub.uwaterloo.ca:11068/mymc/ps2icon-0.5.pdf)
