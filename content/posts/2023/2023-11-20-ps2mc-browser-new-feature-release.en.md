---
author: caol64
title: '"ps2mc-browser" New Feature Release'
slug: ps2mc-browser-new-feature-release
description: Check out the new features and updates in the PS2MC-Browser, a PS2 save file viewer that can now interactively display dynamic 3D Icons, provide enhanced visibility with a skybox layer, and much more.
date: 2023-11-20 14:52:18
draft: false
ShowToc: true
TocOpen: true
tags:
  - ps2mc-browser
  - Python
  - Open-Source
categories:
  - Share
---
`ps2mc-browser` is a `PS2` memory card file viewer that utilizes an `OpenGL` canvas to display 3D dynamic icons from the memory card. It relies on the following dependencies:
- Python3
- WxPython
- Numpy
- ModernGL
- PyGlm

You can find the GitHub repository [here](https://github.com/caol64/ps2mc-browser).

## New Features
Some `PS2` game memory card files contain three sets of different animated icons, corresponding to three different operations: "browse," "copy," and "delete."

The newly released feature allows the `ps2mc-browser` interface not only to display animated icons but also to interact with users and respond to mouse operations. Consequently, the animation of icons can vary based on user selection.

![](imgs/posts/2023-11-20-ps2mc-browser-new-feature-release/2.gif)

## Other Updates
The background pattern of each animated memory card icon is stored in the `icon.sys` file (refer to [Parsing PS2 Game Memory Card 3D Icons](../../10/parsing-ps2-3d-icon) for details). In reality, it has transparency, which is more apparent on a physical `PS2` console.

Therefore, when rendering the background in `OpenGL`, an additional layer of `skybox` is added behind the `bg` background layer. The `z` coordinates of these two layers are distributed as `0.99` and `0.999`, and the `RGBA` of the `skybox` is `(0.6, 0.6, 0.6, 1)` opaque. This setup ensures that if the `bg` has transparency, the color of the `skybox` will be displayed.

Taking `Viewtiful Joe` as an example, its `bg` has `100%` transparency. Without the `skybox`, the effect would be as follows:
![](imgs/posts/2023-11-20-ps2mc-browser-new-feature-release/3.gif)

With the `skybox` added, the effect is as follows:
![](imgs/posts/2023-11-20-ps2mc-browser-new-feature-release/4.gif)

## Unresolved Issues
The problem with lighting has not been resolved, resulting in incorrect lighting for many games and poor display effects. For more details, refer to [Parsing PS2 Game Memory Card 3D Icons](../../10/parsing-ps2-3d-icon).