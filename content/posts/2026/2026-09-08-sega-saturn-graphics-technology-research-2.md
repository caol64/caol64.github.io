---
author: "路边的阿不"
title: 世嘉土星图形技术研究2
slug: sega-saturn-graphics-technology-research-2
description: ""
date: 2026-09-08 11:40:02
draft: false
ShowToc: true
TocOpen: true
tags:
  - 土星逆向
  - 纹理编码
  - 2D图像
categories:
  - 逆向工程
---

[上篇文章](https://babyno.top/posts/2026/09/sega-saturn-graphics-technology-research-1/)仓促结了尾，本章继续。

## VDP2 基础概念

VDP2 负责多层 2D 背景、仿射变换与最终图像合成，支持多图层硬件混合，包含：

* **4 个普通滚动背景**（`NBG0`~`NBG3`）
* **2 个旋转仿射背景**（`RBG0` / `RBG1`）
* **1 个外部视频输入层**（`EXBG`）

VDP2 的滚动屏幕支持两种数据存储与渲染格式：**单元格式（Cell format）** 与 **位图格式（Bitmap format）**。

### 单元格式（Cell Format）数据层级

单元型滚动屏幕在 VRAM 中由下至上构建了严密的五级网格层级：

1. **单元（Cell）**：基本图像单元，固定的 8 x 8 像素点阵。
2. **字符图案（Character Pattern / Character）**：由 Cell 按 1 x 1（8 x 8px）或 2 x 2（16 x 16px）排列构成的基本图块。
3. **页（Page）**：由字符图案按 32 x 32 或 64 x 64 的网格矩阵排列构成的独立逻辑块。
4. **平面（Plane）**：由 Page 按 1 x 1、2 x 1 或 2 x 2 排列构成的逻辑画面。
5. **地图（Map）**：VDP2 最终寻址的卷轴全景图。普通滚动屏（NBG）为 2 x 2 Planes，旋转滚动屏（RBG）最大支持 4 x 4 Planes。

![](imgs/posts/2026-09-08-sega-saturn-graphics-technology-research-2/3.webp)

### 核心数据结构说明

* **字符图案数据（Character Pattern Data）**：
存储在 VRAM 中的原始像素点阵集（图库）。由 `CHCTLA/B` 寄存器定义其 Tile 尺寸（8 x 8 或 16 x 16px）与色彩模式（16色/4bpp、256色/8bpp、RGB555/16bpp 等）。它只包含纯粹的像素数据，不包含任何显示坐标与布局状态。
* **图案名称表（Pattern Name Table, PNT）**：
VRAM 中用于管理屏幕排版映射的结构表（即 Map/Tilemap）。PNT 在逻辑上被划分为多个 Page，按行列网格顺序存放着每一个位置所对应的 **Pattern Name Data**。
* **图案名称数据（Pattern Name Data）**：
PNT 映射表中的单个条目（占用 1 Word / 16位 或 2 Words / 32位，由 `PNCN0/1` 寄存器设定）。相当于一个“图块实例化指令”，具体包含以下属性位：
* **Character Number**：指向该位置要调用的 Character Pattern 在 VRAM 中的物理首地址索引。
* **Palette / Color Bank**：指定该图块使用的调色板基地址。
* **H / V Flip Bit**：水平翻转与垂直翻转控制位。
* **Priority Bits**：图层内与图层间的像素渲染优先级。
* **Special Bits**：控制是否开启 Color Calculation（色彩加减算/半透明）或 Shadow 效果。

## VDP2 寄存器

在转储的 `vdp2-registers.bin` 文件中，保存了当前帧 VDP2 内存映射 I/O（MMIO，基地址 `0x25F80000`）的配置快照。通过解析这些 16 位寄存器的状态，可以完全还原画面图层的渲染管线：

- `0x0000 TVMD` (TV Screen Mode Register)
  - **屏幕显示模式**：控制全局显示开关（DISP）、视频输出分辨率（HRES/VRES，如 320×224 / 704×480）、扫描线隔行/逐行模式（LSMD）及屏灭状态。
- `0x0004 TVSTAT` (TV Status Register)
  - **屏幕状态寄存器（只读）**：提供实时硬件状态，用于同步诊断。包含场消隐（V-Blank）、行消隐（H-Blank）标志，以及 NTSC/PAL 偶数/奇数场（ODD/EVEN）指示。
- `0x000E RAMCTL` (RAM Control Register)
  - **VRAM 控制寄存器**：划分 VRAM（Bank A0, A1, B0, B1 共 512KB）的内存控制模式。决定各个 Bank 是作为字符/图块数据区（Character Data）、映射表区（Map）还是外部 Framebuffer 读取区。
- `0x0028 CHCTLA` (Character Control Register A)
  - **NBG0/NBG1 图块控制**：定义 NBG0 和 NBG1 背景层的字符图块尺寸（1×1 / 2×2，即 8×8px 或 16×16px）与色彩模式（16色/4bpp、256色/8bpp、2048色、RGB555/16bpp 等）。
- `0x002A CHCTLB` (Character Control Register B)
  - **NBG2/NBG3/RBG0 图块控制**：与 `CHCTLA` 结构一致，专门定义 NBG2、NBG3 及旋转背景 RBG0 的图块尺寸与色彩模式。
- `0x0030–0x0038 PNCN0～PNCR` (Pattern Name Control Registers)
  - **图案名称控制（NBG0～NBG3, RBG0）**：设置各个图层 PNT（映射表）的数据条目格式（1 Word / 16位 或 2 Words / 32位）。2 Words 模式下支持额外的补足位（Supplement Bits），用于扩充字符编号和调色板索引范围。
- `0x003A PLSZ` (Plane Size Register)
  - **平面尺寸控制**：定义各个背景层逻辑 Plane 的拼贴排列规格（如 1×1、2×1 或 2×2 Pages），决定单个完整背景 Plane 的宽高网格。
- `0x003C MPOFN` (Map Offset Register NBG0~NBG3)
  - **地图高位偏移**：提供 NBG0～NBG3 各图层地图物理基地址的高位偏移（高 3 位），与 `MPABN` 配合锁定 Map 在 VRAM 中的绝对物理起始地址。
- `0x0040–0x004E MPABN0～MPCDN3` (Map Page Registers)
  - **地图平面页选择**：为 NBG0～NBG3 和 RBG0 的各个 Plane（A、B、C、D）独立指定 VRAM Page 页号。结合 `MPOFN` 即可精确定位出整个 PNT（Pattern Name Table）在显存中的寻址起点。

这是游戏中实际的寄存器数据。

![](imgs/posts/2026-09-08-sega-saturn-graphics-technology-research-2/4.webp)

## 解析 NBG0

在上篇我们已经知道，CG 大图在 NBG0，字幕在 NBG3。我们先来看一下如何通过寄存器中的数据，推论对我们有用的信息。

结合上图中`0x0028 CHCTLA`指令的值为`0x1111`，查阅[文档](https://docs.exodusemulator.com/Archives/SSDDV25/segahtml/index.html?page=hard/vdp2/hon/p16_10.htm)，得到：

- `N0CHSZ` = 1，说明 Character 是由 2×2 Cell 组成的

```
2 × 2 Cell

┌────────┬────────┐
│ 8 × 8  │ 8 × 8  │
├────────┼────────┤
│ 8 × 8  │ 8 × 8  │
└────────┴────────┘

       ↓

    16 × 16 px
```

这是一个极其重要的信息，我们接着往下看。由于推论过程非常复杂，这里就省略了，直接出结果：

```
① TVMD
   │
   └── HRESO/VRESO
          ↓
      640 × 224
          │
          ↓
② CHCTLA
   │
   └── N0CHSZ = 1
          ↓
      2×2 Cell Character
          │
          ↓
      16 × 16 pixels
          │
          ↓
③ 屏幕划分
   │
   ├── 640 / 16 = 40 Character
   └── 224 / 16 = 14 Character
          │
          ↓
      当前可见区域 = 40×14 Character
          │
          ↓
④ PNT
   │
   └── 每个 Character 坐标找到一个 PNT entry
          │
          ↓
⑤ PNT entry
   │
   ├── Character Number
   └── Palette Number
          │
          ↓
⑥ Character Pattern
   │
   └── 2×2 Cell
          │
          ├── Cell 0 → 8×8
          ├── Cell 1 → 8×8
          ├── Cell 2 → 8×8
          └── Cell 3 → 8×8
          │
          ↓
⑦ 每个 byte = 一个 256 色 palette index
          │
          ↓
⑧ CRAM
          │
          ↓
⑨ RGB
          │
          ↓
       640×224 PNG
```

再结合通过`Yabause`抓取的 NBG0 配置：

```
NBG0 mode
8-bit(256 colors)
Tile(2H x 2V)
Plane Size = 2H x 2V
Pattern Name data size = 1 word
Character Number Supplement bit = 0
Special Priority bit = 0
Special Color Calculation bit = 0
Supplementary Palette number = 0
Supplementary Color number = 0
Plane A Address = 00074000
Plane B Address = 00074000
Plane C Address = 00074000
Plane D Address = 00074000
Screen Scroll x = 0, y = 0
Coordinate Increments x = 1.000000, y = 1.000000
Window disabled whole screen
Color Ram Address Offset = 0
Priority = 3
Color Offset A Enabled
R = 0, G = 0, B = 0
Special Color Calculation 0
```
我们就有了足够多的信息来解析数据了。

## 解析图片

```
屏幕
  │
  ├── 40 × 14 Character
  │
  │     每个 Character
  │          │
  │          └── 2 × 2 Cell
  │                 │
  │                 └── 每个 Cell = 8 × 8
  │
  └── 最终 = 640 × 224
```

### PNT 寻址

屏幕分辨率为 `640×224`，每个 Character 为 `16×16` 像素，因此画面包含 `40 列 × 14 行` 个 Character 。每个 Character 在 PNT 中对应一个 16 位条目，该条目包含：

- **调色板 bank**（高 3 位，bit 12–14）：`pal_bank = (map_val >> 12) & 0x7`
- **字符号**（低 12 位，bit 0–11）：`char_num = map_val & 0x0FFF`

PNT 的地址计算逻辑基于 Plane Size = 2H × 2V（即由 2 x 2 个 Page 拼成一个 Map），由于当前 Character 尺寸为 16 x 16 px，一个 512 x 512 px 的 Page 在网格上包含 32 x 32 个 Character。

对于屏幕上任意位置的 Character 坐标 `(tx, ty)`（其中 `tx` 范围 0 ～ 39，`ty` 范围 0 ～ 13），通用的 PNT VRAM 物理地址计算公式为：

```python
# 1. 计算所在的 Page 编号 (Plane 布局为 2x2 Page)
page_x = tx // 32
page_y = ty // 32
page_index = page_y * 2 + page_x  # Page 0, 1, 2, 3

# 2. 计算 Page 内的局域坐标
local_x = tx % 32
local_y = ty % 32

# 3. 计算 VRAM 偏移 (每个 Page 占 32x32x2 = 0x800 字节)
page_offset = page_index * 0x800
entry_offset = (local_y * 32 + local_x) * 2

pnt_addr = map_base + page_offset + entry_offset
```

对于左上角首个 Character `tx=0, ty=0` -> `page_index=0` -> `pnt_addr = map_base`（即 `0x74000`）。

### Character Pattern Data 寻址

在 **8bpp（256 色）模式** 下，一个 16 x 16 px 的 Character 包含 16 x 16 = 256 个像素点，占用 **256 字节（0x100）**。

根据 `char_num` 计算其点阵数据在 VRAM 中的基地址：

```python
base_addr = (char_num << 2) * 0x20   # 等价于 char_num * 0x80
```

该图案由 4 个 8 x 8 的 Cell 构成，排列顺序及 VRAM 内部偏移为：

- `base_addr + 0x000`：左上 8×8 Cell
- `base_addr + 0x040`：右上 8×8 Cell
- `base_addr + 0x080`：左下 8×8 Cell
- `base_addr + 0x0C0`：右下 8×8 Cell

### 调色板处理

从 CRAM 读取 4096 字节（2048 个 16 位小端/大端 integer），每个 16 位色彩值按土星 RGB555 规则解码，并**扩展映射至 8-bit（0 ~ 255）颜色空间**：

```python
r_5bit = value & 0x1F
g_5bit = (value >> 5) & 0x1F
b_5bit = (value >> 10) & 0x1F

# 将 5-bit (0~31) 映射到 8-bit (0~255)
r = (r_5bit << 3) | (r_5bit >> 2)
g = (g_5bit << 3) | (g_5bit >> 2)
b = (b_5bit << 3) | (b_5bit >> 2)
```

解码得到的 2048 个 RGB 颜色分为 8 个 Bank（每个 Bank 包含 256 色）。

### 渲染流程

对每个 Character 中的 4 个 8 x 8 Cell 依次进行像素填充：

1. 逐字节读取 64 个像素的颜色索引值 `color_idx`。
2. 计算该像素在 CRAM 中的绝对颜色索引：`abs_color_idx = pal_bank * 256 + color_idx`
3. 从 `palettes` 列表中取出对应的 RGB 颜色。_(注意：对于 NBG0 全屏背景 CG，`color_idx = 0` 通常为有效背景颜色值而非透明像素，需正常渲染)_。
4. 将 RGB 颜色写入输出图像的对应像素坐标。

按照此流程遍历 40 x 14 个 Character，即可还原出标准的 `640×224` PNG 图像。


### 数据流总结

```
VRAM 空间
├── 0x74000 (map_base)  →  Pattern Name Table (PNT)
│     └─ 40×14 个 16 位条目 → 提取 (pal_bank, char_num)
│
└── 0x00000 (pattern_base) → Character Pattern Data
      └─ char_num × 0x100 定位 256 字节像素点阵 (4 个 8×8 Cell)

CRAM 空间
└── 0x0000 (cram_base)  →  2048 个 RGB555 颜色
      └─ (pal_bank × 256 + color_idx) 定位 RGB 值
```

完整渲染链：

PNT 条目 -> `char_num` -> 读取 VRAM 像素点阵索引 -> 结合 `pal_bank` 计算 CRAM 偏移 -> 取出 RGB555 映射为 RGB888 -> 写入屏幕位置

## 最终结果

最终从 NBG0 中解析出来的图片如下：

![](imgs/posts/2026-09-08-sega-saturn-graphics-technology-research-2/1.webp)

将输出分辨率调整为 `320 x 224`，就完美了。

![](imgs/posts/2026-09-08-sega-saturn-graphics-technology-research-2/2.webp)

未完待续。

## 参考资料

https://docs.exodusemulator.com/Archives/SSDDV25/segahtml/index.html?page=index.htm

---

欢迎关注我的公众号，第一时间获取最新文章。

![](https://babyno.top/imgs/qrcode.jpg)
