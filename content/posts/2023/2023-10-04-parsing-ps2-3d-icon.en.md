---
author: caol64
title: Analysis of the PS2 Game Save 3D Icons
slug: parsing-ps2-3d-icon
description: Dive deep into the realm of PS2 game development as we demonstrate how to unpack 3D icon data from save files. Our intricate guide covers vertices, model animation, textures, lighting, and backgrounds, all with accurate coding details.
date: 2023-10-04 18:00:34
draft: false
ShowToc: true
TocOpen: true
tags:
  - ps2mc-browser
  - OpenGL
categories:
  - Tutorial
---
![](imgs/posts/2023-10-04-parsing-ps2-3d-icon/1.gif)

看到这个图片，对于熟悉PS2的老玩家来说应该不会陌生。它是PS2记忆卡管理界面中的游戏存档3D图标。本篇文章我们将介绍如何从存档文件里解析出这个活动的小人。

## 01 Parsing Objectives

A: What can we parse from the save file?
- All vertices and normals of the icon model
- Animation frames of the icon model
- Lighting information
- Textures and texture coordinates
- Background color and transparency

B: What do we need to do?
- Write shaders to render the background and icons
- Create animations from the animation frames of the icon model
- Build model matrices, view matrices, and perspective matrices to achieve a display close to the original PS2 effect

Completing the entire functionality will likely require two articles, with this one mainly focusing on A.

## 02 Parsing `icon.sys`

In the previous article, we discussed how to export the game's save files. In fact, each save file contains an `icon.sys` file, which can be considered as the configuration file for the icon. `icon.sys` is a fixed-size file (964 bytes), with the following structure:

| Offset | Length | Description |
|--------|--------|-------------|
| **0**  | byte[4] | `magic`: PS2D |
| **4**  | uint16 | 0 |
| **6**  | uint16 | Position of the newline character in the game title, Note 1 |
| **8**  | uint32 | 0 |
| **12** | uint32 | `bg_transparency`: Background transparency, 0-255 |
| **16** | uint32[4] | `bg_color`: Background color at the top-left corner (RGB, 0-255) |
| **32** | uint32[4] | `bg_color`: Background color at the top-right corner (RGB, 0-255) |
| **48** | uint32[4] | `bg_color`: Background color at the bottom-left corner (RGB, 0-255) |
| **64** | uint32[4] | `bg_color`: Background color at the bottom-right corner (RGB, 0-255) |
| **80** | uint32[4] | `light_pos1`: Light position 1 (XYZ, 0-1) |
| **96** | uint32[4] | `light_pos2`: Light position 2 (XYZ, 0-1) |
| **112** | uint32[4] | `light_pos3`: Light position 3 (XYZ, 0-1) |
| **128** | uint32[4] | `light_color1`: Light color 1 (RGB, 0-1) |
| **144** | uint32[4] | `light_color2`: Light color 2 (RGB, 0-1) |
| **160** | uint32[4] | `light_color3`: Light color 3 (RGB, 0-1) |
| **176** | uint32[4] | `ambient`: Ambient light (RGB, 0-1) |
| **192** | byte[68] | `sub_title`: Game title (null-terminated, SJIS encoding) |
| **260** | byte[64] | `icon_file_normal`: Normal icon filename (null-terminated), Note 2 |
| **324** | byte[64] | `icon_file_copy`: Copy icon filename (null-terminated), Note 2 |
| **388** | byte[64] | `icon_file_delete`: Delete icon filename (null-terminated), Note 2 |
| **452** | byte[512] | All zero |

Note 1: The game title `sub_title` is displayed in 2 lines, and this value indicates at which byte the newline occurs in the title.

![](imgs/posts/2023-10-04-parsing-ps2-3d-icon/1.jpg)

Note 2: Each game save file can correspond to 3 icon files, which are displayed in different scenes.

As you can see, the `icon.sys` file mainly provides data such as background and lighting. Another important part is the filename where the 3D icon is located.

## 03 Parsing the `icon` File
Unlike the `icon.sys` file, the `icon` file for each game is variable in size and quantity, but there is always at least one. Some games may use the same icon for both copying and deleting icons as the regular icon.

### 3.1 File Structure
| Name | Description |
| ---- | ----------- |
| Icon Header | Fixed size, 20 bytes |
| Vertex Segment | Contains all vertices and normals data of the icon model |
| Animation Segment | Stores information about animation frames of the icon model |
| Texture Segment | Stores texture data of the icon model |

### 3.2 `Icon` Header
The `Icon` header stores all the essential information needed to decode the different data segments. This includes:
- Number of vertices contained in the "Vertex Segment" and the number of animation shapes
- Whether the texture data is compressed

In the icon file, the `Icon` header is always located at offset 0. Here's the structure of the `Icon` header:

| Offset | Length | Description |
| ------ | ------ | ----------- |
| 0000 | uint32 | `magic`: `0x010000` |
| 0004 | uint32 | `animation_shapes`: Number of animation shapes, Note 1 |
| 0008 | uint32 | `tex_type`: Texture type, Note 2 |
| 0012 | uint32 | Unknown, fixed value `0x3F800000` |
| 0016 | uint32 | `vertex_count`: Number of vertices, always a multiple of 3 |

Note 1: The icon model has different sets of vertex data for different actions, called "shapes." Rendering different shapes in a loop creates animation effects.

Note 2: The purpose of the "Texture type" part is not yet clear. This value is a 4-byte integer. Below is a summary of the functionality of each bit, which may not be accurate:

| Mask | Description |
| ---- | ----------- |
| 0001 | Unknown |
| 0010 | Unknown |
| 0100 | Texture data exists in the icon file. Some games (like ICO) have no texture data, resulting in a fully black icon. |
| 1000 | Texture data in the icon file is compressed. |

### 3.3 Vertex Segment
Polygons in PS2 icons are always composed of triangles formed by three vertices. Since the vertices are arranged according to a certain pattern, simply reading the vertex data according to this pattern can easily construct the polygons. Rendering this data using OpenGL or similar tools produces a beautiful wireframe icon.

The "Vertex Segment" contains data for all the vertices in the icon. Each vertex data includes a set of vertex coordinates, normal coordinates, texture coordinates, and a set of RGBA data. Therefore, the data structure of the "Vertex Segment" with `m` vertices and `n` shapes is as follows:

![](imgs/posts/2023-10-04-parsing-ps2-3d-icon/%E5%AD%98%E5%82%A8%E5%8D%A1-Vertex.jpg)

#### Vertex Coordinates
Each vertex coordinate occupies 8 bytes and has the following structure:

| Offset | Length | Description              |
| ------ | ------ | ------------------------ |
| 0000   | int16  | X-coordinate (divide by 4096 when in use) |
| 0002   | int16  | Y-coordinate (divide by 4096 when in use) |
| 0004   | int16  | Z-coordinate (divide by 4096 when in use) |
| 0006   | uint16 | Unknown                  |

#### Normal Coordinates
Each normal coordinate has the same structure as the vertex coordinate data.

#### Texture Coordinates
Each texture coordinate occupies 4 bytes and has the following structure:

| Offset | Length | Description              |
| ------ | ------ | ------------------------ |
| 0000   | int16  | U-coordinate (divide by 4096 when in use) |
| 0002   | int16  | V-coordinate (divide by 4096 when in use) |

#### Vertex RGBA
Each vertex color occupies 4 bytes and has the following structure:

| Offset | Length | Description              |
| ------ | ------ | ------------------------ |
| 0000   | uint8  | Red (0-255)              |
| 0001   | uint8  | Green (0-255)            |
| 0002   | uint8  | Blue (0-255)             |
| 0003   | uint8  | Alpha (0-255)            |

### 3.4 Animation Segment
Unfortunately, I haven't fully understood the meaning of most of the content in the "Animation Segment" yet. However, it's not a big concern as animation actions can still be accomplished using "Vertex Coordinate Interpolation".

Below is the data structure of the "Animation Segment":

![](imgs/posts/2023-10-04-parsing-ps2-3d-icon/%E5%AD%98%E5%82%A8%E5%8D%A1-Animation.jpg)

The "Animation Segment" consists of an "Animation Header" and several "Animation Frames", with each "Animation Frame" containing several "Key Frames".

#### Animation Header
The structure of the "Animation Header" is as follows:

| Offset | Length | Description              |
| ------ | ------ | ------------------------ |
| 0000   | uint32 | Magic: 0x01              |
| 0004   | uint32 | Frame Length: The number of frames needed to complete one cycle of the animation. This value helps calculate the number of "play frames" corresponding to each "animation frame". |
| 0008   | float32| Anim Speed: Play speed, purpose unknown |
| 0012   | uint32 | Play Offset: Starting frame, purpose unknown |
| 0016   | uint32 | Frame Count: Total number of "animation frames" in the animation segment, typically one "animation frame" corresponds to one "shape". |

#### Frame Data
The "Frame Data" immediately follows the "Animation Header".

| Offset | Type  | Description        |
| ------ | ----- | ------------------ |
| 0000   | u32   | Shape id           |
| 0004   | u32   | Number of keys     |
| 0008   | u32   | UNKNOWN            |
| 0012   | u32   | UNKNOWN            |

#### Key Frame
| Offset | Type  | Description        |
| ------ | ----- | ------------------ |
| 0000   | f32   | Time               |
| 0004   | f32   | Value              |

### 3.5 Texture Segment
Textures are images with dimensions of `128x128` pixels, encoded using the `TIM` image format. Depending on the `tex_type` field in the `Icon Header`, textures can be classified into two types: uncompressed and compressed.

#### Uncompressed Texture
Uncompressed textures have a pixel format of `BGR555`, where each of B, G, and R occupies 5 bits, totaling 15 bits, and occupying 2 bytes (with 1 bit redundancy). The format is as follows:
```
High-order byte:    Low-order byte:
X B B B B B G G     G G G R R R R R

X = Don't care, R = Red, G = Green, B = Blue
```

Therefore, the original image size is fixed at 128x128x2 bytes. To convert its pixel format to `RGB24`, the following method can be used:
```
High-order byte:     Middle-order byte:    Low-order byte:
R R R R R 0 0 0      G G G G G 0 0 0       B B B B B 0 0 0
```

When converting 5-bit color values to 8-bit, the lower 3 bits need to be padded with zeros. After the above conversion, the number of bytes per pixel becomes 3 bytes. Similarly, the format can also be converted to `RGBA32`, where the number of bytes per pixel becomes 4 bytes.

#### Compressed Texture
Compressed textures use a very simple `RLE` algorithm for compression. The first `u32` is the size of the compressed texture data. The data that follows alternates between `u16` `rle_code` and `rle_data` until the end. `rle_data` has two variables: the number of `data` (denoted as `x`) and the repetition count (denoted as `y`). The `rle_code` serves as a counter. If it is less than `0xFF00`, then `x = 1` and `y = rle_code`; if it is greater than or equal to `0xFF00`, then `x = (0x10000 - rle_code)` and `y = 1`. See the diagram below.

![](imgs/posts/2023-10-04-parsing-ps2-3d-icon/%E5%AD%98%E5%82%A8%E5%8D%A1-RLE.jpg)

After decompressing the compressed texture, it can be converted to an `RGB24` or `RGBA32` image based on the content of the previous section.

## 04 Conclusion
With the completion of the analysis of the relevant icon files, everything is ready except for the east wind. In the next article, we will start rendering mode and use `PyGame` and `ModernGL` to display the rendered animation.

## 05 References
- [gothi - icon.sys format](https://www.ps2savetools.com/documents/iconsys-format/)
- [Martin Akesson - PS2 Icon Format v0.5](http://www.csclub.uwaterloo.ca:11068/mymc/ps2icon-0.5.pdf)
