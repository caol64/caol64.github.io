---
author: 路边的阿不
title: 解析PS2记忆卡文件系统
slug: parsing-ps2-memcard-file-system
description: Immerse yourself in the intricate world of PS2 gaming nostalgia as we delve into the PS2 memory card file system. Uncover how your favorite PS2 games were stored and relive your gaming youth through the eyes of a programming expert.
date: 2023-09-26 15:15:16
draft: false
ShowToc: true
TocOpen: true
tags:
  - ps2mc-browser
categories:
  - 教程
---
![](imgs/posts/2023-09-26-parsing-ps2-memcard-file-system/Playstation_2_Memory_Card-3.jpg)

## 01 前言
作为一个80后的游戏老玩家，PS2游戏机在我心中一直有着特殊的地位。时至今日，已经过去了20多年，然而，最近我因为模拟器的缘故重新接触到了它。在重温了一段时间游戏后，我突发奇想，能否通过现在的知识来回忆年少时的自己？于是，我开始了这一系列文章的创作，从分析PS2存储卡的文件系统开始，逐步深入的解析其文件存储机制及每个游戏的存档文件。我的目标是，最终通过Python和OpenGL，模拟出游戏存档中经典的3D人物旋转效果，以此来纪念这个曾经陪伴我度过青春时光的经典游戏机。

这是系列的第一篇作品，解析PS2存储卡的文件系统。

## 02 词汇表
- `存储卡`
指PS2实体机使用的专用记忆卡介质，使用时插在主机上，与主机是相互独立的两个设备。
- `NAND`闪存
PS2存储卡使用的内部芯片，一种非易失性存储设备。
- `存储卡文件`
指PS2模拟器使用的存储卡镜像文件，保存在模拟器所在的电脑磁盘上，以`.ps2`为后缀。是我们这篇文章解析的目标。
- `SuperBlock`
`超级块`，位于文件系统开头的固定部分，由存储卡格式化时写入，不可更改，记录了存储卡的基本硬件指标。
- `page`
`页`，文件系统的最小读写单元，页的大小定义于超级块中。
- `cluster`
`簇`，文件系统中的最小分配单位，要保存一个文件至少需要一个簇。簇的大小定义于超级块中。
- `block`
`块`，文件系统的最小擦除单位，块的大小定义于超级块中。
- `擦除`
闪存初始化时页中的每一个`bit`都为1，写操作可以将`bit`置为0，但无法恢复为1。擦除是将`bit`恢复成1的唯一途径，但缺点是擦除以块为单位，哪怕只是修改一位数据，也得先擦除一个块，然后再用写操作把块的每一页恢复。这也是PS2游戏存档时普遍较慢的原因。
- `FAT`
`文件分配表`，与`FAT16`和`FAT32`文件系统中的文件分配表类似。由于文件会保存在多个簇上，而簇可以是不连续的，为了确保在存取文件时能够检索到所有连续或不连续的簇地址，文件分配表采用了“簇链”这种链表的记录方式。
- `ifc`
`indirect FAT cluster`间接FAT簇，是一个簇，其中保存有存储卡上`FAT`簇的列表。
- `ifc_list`
`ifc`的数组，定义于超级块中。通过它可以找到`ifc`簇。
- `ECC`
`纠错码（Error Correction Code）`，闪存特性，写入`page`时需要对每一页进行纠错码计算，并写入`spare area`中。
- `spare area`
`备用区域`，为每一个页保存`ECC`的一段空间。
- `entry`
`条目`，存储卡上保存的文件或目录的基本信息单元，比如：文件（目录）名、大小、第一个簇编号等。

## 03 文件系统结构
_**注：这里用标准的8M存储卡举例。**_

### 3.1 数据结构
从`超级块`中可得知`页`的大小是512字节，`簇`的大小是2个`页`。`spare area`可以根据公式`(page_len / 128) * 4`得到，是16字节，则文件系统基本数据结构如图：

![](imgs/posts/2023-09-26-parsing-ps2-memcard-file-system/%E5%AD%98%E5%82%A8%E5%8D%A1-%E6%96%87%E4%BB%B6%E7%B3%BB%E7%BB%9F.jpg)

### 3.2 逻辑结构
了解了最基本的数据结构，接下来我们划分一下存储卡的逻辑结构。如下图，一块存储卡大致能分为以下几个逻辑区块。（黑白部分本文不涉及，可以忽略。）注意：组成逻辑区块的最小单位是簇。

![](imgs/posts/2023-09-26-parsing-ps2-memcard-file-system/%E5%AD%98%E5%82%A8%E5%8D%A1-%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84.jpg)

#### 超级块
位于整个文件开头（也就是第一个簇）的前**340**个字节，这是文件系统中唯一具有固定位置的部分。下图示意了一个存储卡文件的超级块。

![](imgs/posts/2023-09-26-parsing-ps2-memcard-file-system/image.png)

_**注：PS2存储卡的字节序是小端序Little-endian。**_

| Offset | Name              | Length    | Default | Description  |
|--------|-------------------|-----------|---------|--------------------------------------------------------   |
| 0      | magic             | byte[28]  | -       | 固定字符串"Sony PS2 Memory Card Format"， 表明该卡已成功初始化  |
| 28     | version           | byte[12]  | 1.X.0.0 | 版本号     |
| 40     | page_len          | uint16    | 512     | `page`的大小(以字节为单位)    |
| 42     | pages_per_cluster | uint16    | 2       | 簇中的页数    |
| 44     | pages_per_block   | uint16    | 16      | 块中的页数  |
| 46     | -                 | uint16    | 0xFF00  | 未知  |
| 48     | clusters_per_card | uint32    | 8192    | 卡的总大小(以簇为单位)  |
| 52     | alloc_offset      | uint32    | 41      | 第一个可分配簇  |
| 56     | alloc_end         | uint32    | 8135    | 最后一个可分配簇  |
| 60     | rootdir_cluster   | uint32    | 0       | 根目录的第一个簇，相对于alloc_offset  |
| 64     | backup_block1     | uint32    | 1023    | 本文无用   |
| 68     | backup_block2     | uint32    | 1022    | 本文无用  |
| 80     | ifc_list          | uint32[32]| 8       | 间接 FAT 簇列表，在标准 8M 卡上只有一个间接 FAT 簇  |
| 208    | bad_block_list    | uint32[32]| -1      | 本文无用  |
| 336    | card_type         | byte      | 2       | 必须是2，说明这是一张PS2存储卡  |
| 337    | card_flags        | byte      | 0x52    | 存储卡的物理特性   |

字段`page_len`、`pages_per_cluster`、`pages_per_block`和`cluster_per_card`定义文件系统的基本几何结构。可以使用`ifc_list`访问`FAT`，`rootdir_cluster`给出根目录的第一个簇。`FAT`和目录项中的簇偏移量都与`alloc_offset`相关。

#### FAT
文件分配表是一个链表，当你找到一个文件的起始簇时，你想象有两个线程，线程x用来读取这个簇里的内容（即数据），线程y去FAT里寻找下一个簇，交由x读取，然后不断循环，当然两个线程不是必须的。这里引用一张图说明一下这种工作方式：
- 已知文件A，起始簇是8
- 线程x去簇8读取第一块数据A0
- 线程y去FAT查找8的下一个簇是13
- 线程x继续读取簇13的数据A1
- 线程y去FAT查找13的下一个簇是7
- 不断循环

![](imgs/posts/2023-09-26-parsing-ps2-memcard-file-system/file-allocation-table-fat1-l.jpg)

图片来源：https://www.slideserve.com/yahto/file-system-implementation

#### 直接FAT

由前文可以得知，直接FAT和间接FAT都是保存在簇里的。簇里的数据必须有一个良好的结构，才能使我们简单的解析成FAT链表。FAT在簇里的结构可以想象成长这样：

![](imgs/posts/2023-09-26-parsing-ps2-memcard-file-system/%E5%AD%98%E5%82%A8%E5%8D%A1-FAT1.jpg)

这是一个矩阵M，行定义为FAT所在的簇，列定义为每个FAT簇里的数据。每个FAT簇，保存的都是4字节32位的整形数组，数量为`1024 / 4 = 256`个，因此矩阵有256列。FAT一共有多少个簇呢？这点可以在间接FAT的簇中解析出来，我们之后再讲。在这里FAT一共占据了32个簇，因此矩阵有32行。

M矩阵的大小为`32 * 256 = 8192`，意味着这个FAT可以管理8192个簇。假设现在要找簇`n`在矩阵中的位置`row`和`column`，可以根据简单的计算得出：

```python
row = (n // 256) % 256
column = n % 256
```

既然已经计算出了位置，那就可以取到对应的值了，没错，这个值`?`就是下一个簇。通过不断循环，直到取到的值为`0xFFFFFFFF`，表示簇链到结尾了，不需要再查找了。

_**注：FAT表里储存的值为32位，最高位为8代表正常使用的簇，其它值代表簇未分配，最高位为8时，取低31位的整形值。值为`0xFFFFFFFF`代表已是簇链末尾。**_

#### 间接FAT

前文留了一个问题，为什么FAT占有了32个簇？

在超级块中有一个字段`ifc_list`，是一个4字节32位的整形数组，再想象一下上面出现的矩阵。`ifc_list`是一个只有一行的矩阵，虽然它有32个元素，但只有第一个有值，其值8即间接FAT簇`ifc`。将簇8的内容按照上文的方法解析出来，再形成一个矩阵，行是`ifc_list`的个数，理论上是32，但由于只有1个元素，因此这个矩阵的行也为1。矩阵的列依然是256。解析其中的值，可以得到FAT所在的簇为9到40，即32个。

![](imgs/posts/2023-09-26-parsing-ps2-memcard-file-system/%E5%AD%98%E5%82%A8%E5%8D%A1-FAT.jpg)

#### 可分配簇
是一个范围，从`alloc_offset`开始到`alloc_end`结束。除去超级块、FAT、保留簇等的位置，所有的游戏存档都位于可分配簇内。

## 04 文件和目录
接着我们要研究下可分配簇里，每个簇都保存了些什么东西？简单来说，可分配簇里只有两种簇：“条目簇”和“数据簇”。保存条目的簇称为“条目簇”，保存数据的簇称为“数据簇”。

### 4.1 条目
每个目录或文件都有一个“条目”，可以看作是元数据，保存有文件名、大小、创建和修改时间等属性。每个“条目”的长度为 512 字节，因此每个 1024 簇中只能容纳两个“条目”。“条目簇”不会保存文件数据，即使“条目簇”里只有一个“条目”。

除了根目录没有`root`这个“条目”外，每个目录都有以自己的目录名命名的“条目”，每个文件也有以自己的文件名命名的“条目”，“条目”的结构如下表：

| Offset | Name      | Length   | Description    |
|--------|-----------|----------|----|
| 0      | mode      | uint16   | 标识该文件的属性|
| 4      | length    | uint32   | 如果是文件，以字节为单位；如果是目录，以项为单位。 |
| 8      | created   | byte[8]  | 创建时间|
| 16     | cluster   | uint32   | 条目对应的第一个簇，是相对于alloc_offset的相对值。 |
| 20     | dir_entry | uint32   | 无用  |
| 24     | modified  | byte[8]  | 修改时间|
| 32     | attr      | uint32   | 用户属性|
| 36     | name      | byte[32] | 文件名，`x00`以后的需截断 |

- `mode`字段请参考：https://www.ps2savetools.com/ps2memcardformat.html 。是一个4字节整形数，每个字节用对应的掩码比对，即可识别“条目”对应的文件类型。比如：`0x8427`代表一个目录，`0x8497`代表一个文件。
- `cluster`字段代表了“条目”的第一个簇。如果本条目是目录，则这个簇指向的是当前目录的下一个“条目簇”；如果本条目是文件，则这个簇指向的是文件的第一个“数据簇”。
- 每个目录下的第一个“条目簇”一定是名为`.`和`..`的两个目录，这两个目录项代表当前目录和父目录，就像在`Unix`中一样。
- 目录下有几个“条目”以及文件有几个字节都是由`length`字段决定的，当你按照“簇链”读取文件的时候，需要自己记录最后一个簇的哪里是最后一个字节。

## 05 结尾
至此，相信大家对一个ps2存储文件有了大致认识了吧。有兴趣的可以自己写一个程序解析下了。稍后我也会创建一个项目，附上本篇文章涉及的源代码。

下一篇文章我们将开始把游戏存档从存储卡里导出来，看看每个游戏存档都有哪些文件。

## 06 参考文献
本文主要参考了如下文章，在此表示感谢🙏：
- [Ross Ridge - PlayStation 2 Memory Card File System](https://www.ps2savetools.com/ps2memcardformat.html)
