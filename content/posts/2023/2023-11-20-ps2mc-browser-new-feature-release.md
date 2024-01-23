---
author: "路边的阿不"
title: 「ps2mc-browser」新功能发布
slug: ps2mc-browser-new-feature-release
description: "Check out the new features and updates in the PS2MC-Browser, a PS2 save file viewer that can now interactively display dynamic 3D Icons, provide enhanced visibility with a skybox layer, and much more."
date: 2023-11-20 14:52:18
draft: false
ShowToc: true
TocOpen: true
tags: ["ps2mc-browser", "ModernGL", "3D Rendering", "Python"]
categories: ["开源"]
---

`ps2mc-browser`是一个`PS2`存档文件查看器，使用`OpenGL`画布显示存档里的3D动态图标。依赖如下：
- Python3
- WxPython
- Numpy
- ModernGL
- PyGlm

`Github`地址[戳这里](https://github.com/caol64/ps2mc-browser)。

## 新功能
一些`PS2`游戏存档内置了三套不同的图标动画，分别对应玩家进行“浏览”、“拷贝”和“删除”这三种不同的操作。

新发布的功能使得`ps2mc-browser`界面不仅仅只是展示图标的动画，还可以与用户进行交互，响应用户的鼠标操作。这样一来，图标的动画可以根据用户的选择而变化。

![](imgs/posts/2023-11-20-ps2mc-browser-new-feature-release/2.gif)

## 其它更新
每个存档动画的背景图案都保存在`icon.sys`文件里（具体请查阅[解析PS2游戏存档3D图标](../../10/parsing-ps2-3d-icon)），实际上它是有透明度的，在`PS2`实体机上比较容易看出来。

因此，在`OpenGL`渲染背景时，在`bg`背景层的后面，加了一层`skybox`。这两层的`z`坐标分布为`0.99`和`0.999`，且`skybox`的`RGBA`为`(0.6, 0.6, 0.6, 1)`不透明。这样如果`bg`有透明效果，那就会显示出`skybox`的颜色。

以`Viewtiful Joe`为例，它的`bg`透明度是`100%`，如果不加`skybox`，其效果如下：
![](imgs/posts/2023-11-20-ps2mc-browser-new-feature-release/3.gif)

加上后效果如下：
![](imgs/posts/2023-11-20-ps2mc-browser-new-feature-release/4.gif)

## 未解决问题
光源问题尚未解决，导致很多游戏光照不正确显示效果不佳。详情见[解析PS2游戏存档3D图标](../../10/parsing-ps2-3d-icon)。