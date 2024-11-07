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

### 标题及块元素的前缀和后缀

`h1, h2, h3, h4, h5, h6, blockquote`这几个标签可以与`::before`和`::after`伪元素配合`content`属性实现标签的前、后缀效果。让我们看个例子，给所有`blockquote`添加一个彩虹图标前缀：

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

此外，你也可以使用一些`css`的其它技巧来绘制简单的几何图形，比如在`h2`标签前面添加一个`gradient`渐变图形，后面添加一个三角形图标：

```css
#wenyan h2:before {
    display: inline-block;
    content: "";
    background: radial-gradient(#f69d3c, #3f87a6);
    height: 2em;
    width: 2em;
    vertical-align: bottom;
}
#wenyan h2:after {
    display: inline-block;
    content: "";
    vertical-align: bottom;
    border-bottom: 36px solid #efebe9;
    border-right: 20px solid transparent;
}
```

效果：

![alt text](imgs/posts/2024-11-06-wenyan-supports-customized-themes/8.webp)

***注意：虽然在预览页面中，所有标签的伪元素看上去都是正常的，但是粘贴到公众号后，只有上面列举的这些标签和伪元素才会起作用。***

***注意：目前`background-image`还不支持图片格式的背景图案（包括url引入或者base64引入），或许以后的版本会支持。***

### 修改字体

文颜默认使用用户系统的默认字体，如果你想使你的文章看起来更独特，可以考虑修改默认字体。比如：将字体修改为系统自带的“华文仿宋”：

```css
/* 全局变量 */
:root {
    --sans-serif-font: "华文仿宋";
    --monospace-font: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "liberation mono", "courier new", monospace;
}
```

效果：

![alt text](imgs/posts/2024-11-06-wenyan-supports-customized-themes/7.webp)

***注意：修改字体会影响未安装该字体的用户的阅读体验，因此请确保你有一定该方面的经验，保留保底字体。***

***注意：目前不支持`web字体`，即url引入的字体。***

### 背景图案

如果你想修改公众号平平无奇的白色背景，可以使用`gradient`添加一些背景图案。下面这个例子将为你的文章背景添加淡淡的网格：

```css
#wenyan {
    font-family: var(--sans-serif-font);
    line-height: 1.75;
    background-image: linear-gradient(90deg, rgba(50, 0, 0, 0.04) 3%, rgba(0, 0, 0, 0) 3%), linear-gradient(360deg, rgba(50, 0, 0, 0.04) 3%, rgba(0, 0, 0, 0) 3%);
    background-size: 20px 20px;
    background-position: center center;
}
```

效果：

![alt text](imgs/posts/2024-11-06-wenyan-supports-customized-themes/9.webp)

***注意：目前`background-image`还不支持图片格式的背景图案（包括url引入或者base64引入），或许以后的版本会支持。***

## 最后

问题讨论请移步[github discussions](https://github.com/caol64/wenyan/discussions/9)。

主题分享请移步[这里](https://github.com/caol64/wenyan/discussions/13)。