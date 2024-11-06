---
author: "路边的阿不"
title: 文颜支持自定义主题
slug: wenyan-supports-customized-themes
description: ""
date: 2024-11-06 16:11:11
draft: false
ShowToc: true
TocOpen: true
tags:
  - OpenSource
categories:
  - 文颜
---

到目前为止，「文颜」内置了7套主题，除了一套“默认”主题外，其它主题都来源于众多作者的开源主题，在这里向各位作者表示感谢🙏：

-   [Orange Heart - evgo2017](https://github.com/evgo2017/typora-theme-orange-heart)
-   [Rainbow - thezbm](https://github.com/thezbm/typora-theme-rainbow)
-   [Lapis - YiNN](https://github.com/YiNNx/typora-theme-lapis)
-   [Pie - kevinzhao2233](https://github.com/kevinzhao2233/typora-theme-pie)
-   [Maize - BEATREE](https://github.com/BEATREE/typora-maize-theme)
-   [Purple - hliu202](https://github.com/hliu202/typora-purple-theme)

但是这7套主题远远不能满足广大用户的需求，因此文颜已经上线了“自定义主题”功能。

## 什么是自定义主题

“自定义主题”可以使你的公众号文章别具一格，具备自己独特的外观，从而创造出独特的视觉体验。其原理是通过开放对主题的`CSS`（层叠样式表）的修改功能，来对页面进行定制。

用户可以创建3套个性化的“自定义主题”，以创造3种不同的视觉体验。

## 创建主题

在主题选择菜单点击“创建新主题”按钮。

<img src="/imgs/posts/2024-11-06-wenyan-supports-customized-themes/1.webp" width="50%">

此时会弹出一个“主题编辑和预览”页面，你可以在左侧编辑器中自定义`CSS`，右侧预览页面可以实时进行效果预览。

![alt text](imgs/posts/2024-11-06-wenyan-supports-customized-themes/2.webp)

最后保存即可。

## 使用主题

保存的自定义主题可以在主题菜单直接选择使用。

<img src="/imgs/posts/2024-11-06-wenyan-supports-customized-themes/3.webp" width="50%">

## 修改和删除主题

点击“自定义主题”边上的编辑按钮，会弹出“主题编辑和预览”页面，和创建主题一样。

<img src="/imgs/posts/2024-11-06-wenyan-supports-customized-themes/4.webp" width="50%">

如果要删除主题，点击“删除”按钮。

![alt text](imgs/posts/2024-11-06-wenyan-supports-customized-themes/5.webp)

## 小贴士

### 有限支持的伪元素

`h1, h2, h3, h4, h5, h6, blockquote`这几个标签支持`::after`和`::before`伪元素，让我们看个例子：

```css
#wenyan blockquote::before {
    display: block;
    height: 2em;
    width: 1.5em;
    content: "🌈";
    font-size: 1.2em;
}
```

效果：

![alt text](imgs/posts/2024-11-06-wenyan-supports-customized-themes/6.webp)

注意：虽然在预览页面中，其它标签可能也会支持伪元素，但是粘贴到公众号后，只有上面列举的这些标签和伪元素才会起作用。

## 最后

有关“自定义主题”如果有相关问题，可以到[这里](https://github.com/caol64/wenyan/discussions/9)进行讨论。

另外也欢迎大家将自己的主题分享到[这里](https://github.com/caol64/wenyan/discussions/13)。