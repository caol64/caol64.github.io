---
author: caol64
title: PS2 Texture Image Encoding Algorithm "A1B5G5R5"
slug: ps2-texture-encoding-algorithm-a1b5g5r5
description: Delve into the unique texture mapping coding algorithm, A1B5G5R5, utilized by PS2. Our detailed guide takes you through the principle behind this lossy yet efficient form of image encoding that significantly reduces image size.
date: 2023-10-20 14:48:31
draft: false
ShowToc: true
TocOpen: true
tags:
  - Python
  - Algorithm
categories:
  - Tutorial
---
In the [previous article](../rle-algorithm-in-ps2/), we discussed the `RLE` image compression algorithm used in `PS2`. This time, let's delve into its texture mapping encoding algorithm—`A1B5G5R5`.

## Introduction
For textures, common image encoding formats like `jpg` or `png` are not suitable. This is because images are read and rendered by the GPU. You wouldn't want to send a `jpg` image over and have the GPU decode the entire image just to read one pixel, right? Therefore, the most ideal image format is an uncompressed bitmap format, allowing direct access to `RGB` data based on pixel coordinates. The `A1B5G5R5` format we're introducing today is one such encoding format.

## Analysis
![](imgs/posts/2023-10-20-ps2-texture-encoding-algorithm-a1b5g5r5/3.jpg)

The above two texture images are extracted from `PS2` archives, stored in bitmap format with a pixel count of `128x128`.

In a standard `32-bit` bitmap, each pixel occupies `4 bytes` of data, storing data for the `RGBA` channels. Therefore, the size of the two texture images above is `128x128x4` bytes. The data structure for each pixel in `32-bit RGBA` format is as follows:

![](imgs/posts/2023-10-20-ps2-texture-encoding-algorithm-a1b5g5r5/RGBA.jpg)

For the `A1B5G5R5` encoding, each pixel occupies `2 bytes` of data, with the `alpha channel` using `1 bit`, and the other three colors each using `5 bits`. The data structure for each pixel is as follows:

![](imgs/posts/2023-10-20-ps2-texture-encoding-algorithm-a1b5g5r5/A1B5G5R5.jpg)

Decoding `A1B5G5R5` into `32-bit RGBA` can be achieved using the method depicted in the following image:

![](imgs/posts/2023-10-20-ps2-texture-encoding-algorithm-a1b5g5r5/decode.jpg)

The pseudo-code is as follows:
```python
while tex_offset < len(self.texture):
    b = tex_struct.unpack_from(self.texture, tex_offset)[0]
    out[rgb_tex_offset] = (b & 0x1F) << 3 # R
    out[rgb_tex_offset + 1] = ((b >> 5) & 0x1F) << 3 # G
    out[rgb_tex_offset + 2] = ((b >> 10) & 0x1F) << 3 # B
    rgb_tex_offset += 3
    tex_offset += tex_struct.size
```

It's evident that encoding a `32-bit` `RGBA` image into a `16-bit` `A1B5G5R5` format results in the loss of the last 3 bits of data for each color, making it a lossy encoding format. However, the benefit is a compression ratio of 2:1, effectively halving the size of the image. When combined with the `RLE` encoding discussed in the previous article, further reduction in image size can be achieved.

## Conclusion
Finally, here are the rendered effects of the two texture images mentioned above. Do any of you remember these two games?

![](imgs/posts/2023-10-20-ps2-texture-encoding-algorithm-a1b5g5r5/4.jpg)
