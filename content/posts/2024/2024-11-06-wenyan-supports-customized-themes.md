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

到目前为止，[「文颜」](https://yuzhi.tech/wenyan)内置了7套主题，除了一套“默认”主题外，其它主题都来源于众多作者的开源主题，在这里向各位作者表示感谢🙏：

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

### 引用块美化

`h1, h2, h3, h4, h5, h6, blockquote`这几个标签可以与`::before`和`::after`伪元素配合实现前、后缀效果。让我们看个例子，给引用块添加一个彩虹图标前缀：

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

<img src="/imgs/posts/2024-11-06-wenyan-supports-customized-themes/6.webp" width="50%">

再比如给引用块添加两个引号：

```css
#wenyan blockquote::before {
    position: absolute;
    top: 0;
    left: 12px;
    font-family: Arial, serif;
    font-size: 2em;
    font-weight: 700;
    line-height: 1em;
    color: var(--main-6);
    content: "“";
}
#wenyan blockquote::after {
    position: absolute;
    bottom: 0;
    right: 12px;
    font-family: Arial, serif;
    font-size: 2em;
    font-weight: 700;
    line-height: 1em;
    color: var(--main-6);
    content: "”";
}
```

效果：

<img src="/imgs/posts/2024-11-06-wenyan-supports-customized-themes/13.webp" width="50%">

### 标题美化

可以给标题添加任意前后缀，比如添加一个`svg`图片：

```css
#wenyan h2::before {
    display: inline-block;
    content: "";
    width: 20px;
    height: 20px;
    background-image: url(data:image/svg+xml;base64,PHN中间省略...g==);
    background-repeat: no-repeat;
    background-size: 20px 20px;
    background-position-y: 4px;
    margin-right: 4px;
    vertical-align: text-top;
}
```

效果：

<img src="/imgs/posts/2024-11-06-wenyan-supports-customized-themes/12.webp" width="50%">

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

此外你也可以给背景添加网络图片，比如：

```css
#wenyan {
    background-image: url("https://marketplace.canva.com/EAGPIDVZ0-A/1/0/1131w/canva-peach-aesthetic-background-flyer-IqGDJ_simvM.jpg");
}
```

效果：

<img src="/imgs/posts/2024-11-06-wenyan-supports-customized-themes/14.webp" width="50%">

### 表格样式

以下几个属性可以修改表格样式：

```css
#wenyan table {
    border-collapse: collapse;
    border: 0.25em solid var(--table-border-color);
    margin: 1.4em auto;
    max-width: 100%;
    table-layout: fixed;
    text-align: left;
    overflow: auto;
    display: inline-block;
    word-wrap: break-word;
    word-break: break-all;
}
#wenyan table th {
    background-color: var(--th-bg-color);
}
#wenyan table th, td {
    font-size: .75em;
    text-align: center;
    border: 0.13em dashed var(--table-border-color);
    padding: 0.5em;
    height: 40px;
    padding: 9px 12px;
    line-height: 22px;
    min-width: 60px;
    vertical-align: top;
}
#wenyan table tr:nth-child(even) {
    background-color: var(--tr-bg-color);
}
```

### 脚注样式

如果使用了脚注功能，请注意以下几个属性：

```css
/* 添加在原始链接旁的脚注上标 1️⃣ */
#wenyan .footnote {
    color: rgb(31, 117, 255);
}
/* 脚注行，每行包括编号和文字 2️⃣ */
#wenyan #footnotes p {
    display: flex;
    margin: 0;
    font-size: 0.9em;
}
/* 脚注行内编号 3️⃣ */
#wenyan .footnote-num {
    display: inline;
    width: 10%;
}
/* 脚注行内文字 4️⃣ */
#wenyan .footnote-txt {
    display: inline;
    width: 90%;
    word-wrap: break-word;
    word-break: break-all;
}
```

添加在原始链接旁的脚注上标：

![alt text](imgs/posts/2024-11-06-wenyan-supports-customized-themes/10.webp)

脚注行：

![alt text](imgs/posts/2024-11-06-wenyan-supports-customized-themes/11.webp)

### 行内代码

```css
#wenyan p code {
    font-family: var(--monospace-font);
    color: #ff502c;
    padding: 4px 6px;
    font-size: .78em;
}
```

### 代码块

```css
/* 代码块外围 */
#wenyan pre {
    border-radius: 5px;
    font-size: .8em;
    line-height: 2;
    margin: 1em 0.5em;
    padding: 1em;
    background-color: #afb8c133;
}
/* 代码块 */
#wenyan pre code {
    font-family: var(--monospace-font);
    display: block;
    overflow-x: auto;
    margin: 0;
    padding: 0;
}
```

### 允许导入主题的图片

目前支持导入主题的图片包括：

- 直接引入的`svg`
    - `url("data:image/svg+xml;utf8,<svg>xxx</svg>"`
- `base64`引入的`svg`
    - `url(data:image/svg+xml;base64,xxxx)`
- 网络图片（不限格式）
    - `url(https://xx.com/x.jpg)`

## 微调内置主题

从版本`2.3`开始(`Windows`版`2.2`)，文颜开放了内置主题，你可以在任意内置主题的基础上生成自定义主题，并进行微调。以下是操作示例：

<video controls>
    <source src="https://yuzhi.tech/img/wenyan/custom_css.mp4" type="video/mp4">
    Your browser does not support the video tag.
</video>

## 导入外部主题

从版本`2.3`开始(`Windows`版`2.2`)，文颜支持导入外部`CSS`转换为自定义主题。对于成熟社区大量已有的主题可以直接导入，迅速形成自己的主题。以下是操作示例：

<video controls>
    <source src="https://yuzhi.tech/img/wenyan/import_css.mp4" type="video/mp4">
    Your browser does not support the video tag.
</video>

## 属性速查

所有属性可以在下面的网页查询到：[属性速查表](https://yuzhi.tech/docs/wenyan/themes)。

## 最后

问题讨论请移步[github discussions](https://github.com/caol64/wenyan/discussions/9)。

主题分享请移步[这里](https://github.com/caol64/wenyan/discussions/13)。