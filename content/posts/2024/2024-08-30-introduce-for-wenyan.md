---
author: "路边的阿不"
title: Markdown排版美化工具：文颜
slug: introduce-for-wenyan
description: ""
date: 2024-08-30 18:23:52
draft: false
ShowToc: true
TocOpen: true
tags:
  - OpenSource
categories:
  - 文颜
---

![wenyan logo](imgs/posts/2024-08-30-introduce-for-wenyan/wenyan.webp)

今天向大家介绍一个我自己开发并且开源的工具——[「文颜」](https://yuzhi.tech/wenyan)。

## 缘起

本项目的起源是我平常使用`markdown`写文章，再使用`hugo`发布到我的博客。但当我想把文章同步发布到诸如“公众号”、“知乎”、“今日头条”等平台时，发现需要针对每个平台进行格式转换，这会让我每次浪费很多时间。

后来我找到了 [Markdown Editor](https://markdown.com.cn/editor/) 这个网站，确实能很好的解决这些问题。但毕竟这是一个在线网站，我希望有个离线也能使用的工具。再加上我最近也在学`swift`，因此本项目应运而生。

本项目大部分灵感来源于`Markdown Editor`，由于我主要在`Macbook`上写文章，因此现阶段的「文颜」仅支持`MAC`平台。

## 功能介绍

本项目的核心功能是将编辑好的`markdown`文章转换成适配各个发布平台的格式，通过一键复制，可以直接粘贴到平台的文本编辑器，无需再做额外调整。

- 支持发布到多平台：公众号、知乎、今日头条、掘金等
- 支持代码高亮
- 支持公式
- 支持链接转脚注
- 支持识别`front matter`语法
- 即将支持：公众号主题样式模版
- 即将支持：公众号自定义样式

## 应用截图

![](imgs/posts/2024-08-30-introduce-for-wenyan/1.webp)

## 下载

本项目已上架`App Store`，你可以直接点击下方链接或搜索“文颜”下载：

<a href="https://apps.apple.com/cn/app/%E6%96%87%E9%A2%9C/id6670157335?mt=12&amp;itsct=apps_box_badge&amp;itscg=30200" style="display: inline-block; overflow: hidden; border-radius: 13px; width: 250px; height: 83px;"><img src="/imgs/posts/2024-08-30-introduce-for-wenyan/black.svg" alt="Download on the Mac App Store" style="border-radius: 13px; width: 250px; height: 83px;"></a>

## 源代码

[Github仓库](https://github.com/caol64/wenyan)。