---
author: "路边的阿不"
title: 「RLE」算法在PS2中的应用
slug: rle-algorithm-in-ps2
description: "Experience the power of Run Length Encoding (RLE), a fundamental data compression algorithm. Witness its astounding application in PS2 for efficient image compression and unveil the intricacies behind its implementation."
date: 2023-10-16 12:30:58
draft: false
ShowToc: true
TocOpen: true
tags: ["RLE", "Python", "Algorithm", "Image Compression"]
categories: ["Programming"]
---

![](/imgs/posts/2023-10-16-rle-algorithm-in-ps2/run_length_f9030faa12.webp)

## RLE算法介绍
`RLE`（Run Length Encoding，行程长度编码）算法，是把文件内容用“重复次数x数据”的形式来表示的压缩方法。比如：有`AAAAAABBCDDEEEEEF`这样一段数据，在字符后面加上重复出现次数，就可以用`6A2B1C2D5E1F`来表示。可以看到原始数据是17字节，编码后是12字节，因此压缩是成功的。

让我们再看一串数据：`ABCDE`，如果按照上面的算法，编码后为`1A1B1C1D1E`，原始数据是5字节，编码后是10字节，毫无疑问这种压缩方式是失败的。

为什么第二种字符串压缩会失败呢？细心的朋友一定看出来是因为它的字符重复出现的次数很少，因此使用“重复次数x数据”反而增加了数据长度。那有没有办法解决这个“缺陷”呢？答案是有的。我们接下来介绍在`PS2`游戏机中，是如何使用`RLE`算法来压缩图片的。

## RLE算法在PS2中的应用
在`PS2`中，图片文件的前4个字节指示了压缩后文件的大小。接下来的数据按照`rle_code` + `数据块`的格式重复排列。需要注意的是，在`PS2`这里，`rle_code`和`数据块`中的每个数据，都是2字节，这点是与其它传统的`RLE`算法普遍为1字节最大的不同。

`rle_code`的最高位是标识位，如果这一位是`1`，则表示后面紧跟着的数据块是“非重复数据”，类似于上面的`ABCDE`。此时将`0x8000`减去`rle_code`的后7位，得到的是`数据块`的长度。此时只需取出后面紧跟的该长度的`数据块`即可。

如果标识位为`0`，则表示后面紧跟着的数据块是“重复数据”，类似于`AAAAA`，此时`rle_code`就是重复次数，只要取出后面紧跟着的一个`数据块`，重复`rle_code`次即可。

![](/imgs/posts/2023-10-16-rle-algorithm-in-ps2/2.gif)

伪代码如下：
```python
while rle_offset < compressed_size:
    rle_code = rle_code_struct.unpack_from(self.byte_val, rle_offset)[0]
    rle_offset += 2
    if rle_code & 0x8000:
        next_bytes = 0x8000 - (rle_code ^ 0x8000)
        texture_buf += self.byte_val[rle_offset: rle_offset + next_bytes * 2]
        rle_offset += next_bytes * 2
    else:
        times = rle_code
        if times > 0:
            next_byte = self.byte_val[rle_offset: rle_offset + 2]
            for _ in range(times):
                texture_buf += next_byte
            rle_offset += 2
```

## 总结
如果在一个文件中，能连续遇到大量重复的数据，`RLE`算法可以提供很好的压缩效果。但对于出现连续的“非重复数据”，需要使用改良过的算法进行优化。`PS2`使用的是众多改良算法的一种，比较简单，也很方便初学者对该算法的学习。