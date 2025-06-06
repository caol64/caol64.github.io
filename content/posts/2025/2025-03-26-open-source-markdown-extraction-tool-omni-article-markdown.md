---
author: "路边的阿不"
title: 开源Markdown提取工具 - 墨探
slug: open-source-markdown-extraction-tool-omni-article-markdown
description: ""
date: 2025-03-26 17:25:27
draft: false
ShowToc: true
TocOpen: true
tags:
  - Open Source
  - Markdown
  - 墨探
  - Software Releases
categories:
  - 项目介绍
---

墨探 (omni-article-markdown) - 轻松将网页文章（博客、新闻、文档等）转换为 `Markdown` 格式。

![](imgs/posts/2025-03-26-open-source-markdown-extraction-tool-omni-article-markdown/1.gif)

## 功能介绍
墨探的开发初衷，是为了解决一个问题：如何将来自互联网上各种不同网站的文章内容，精准且高效地转换成统一的Markdown格式。

众所周知，万维网上的网站设计风格迥异，其HTML结构也呈现出千差万别的特点。这种多样性给自动化内容提取和格式转换带来了巨大的困难。要实现一个能够适应各种复杂HTML结构的通用解决方案，并非易事。

我的想法是：从特定的网站开始适配，以点到面，逐步抽取出通用的解决方案，最后尽可能多的覆盖更多网站。以下是一些我经常访问的的网站，支持的都不错：

- 掘金
- CSDN
- Medium
- Freedium
- 公众号
- 简书
- 知乎专栏
- 今日头条
- towardsdatascience
- quantamagazine

只需要一条命令：

```sh
mdcli https://example.com
```

你还可以将网页手动保存为 HTML 文件，再使用本工具解析，也是支持的。

```sh
mdcli your/path/example.html
```

## 开源代码

源代码开放在 [github](https://github.com/caol64/omni-article-markdown) 上。

此外，你还可以配合「[文颜](https://yuzhi.tech/wenyan)」将转换后的 markdown 文章一键发布到公众号、今日头条、知乎等平台。