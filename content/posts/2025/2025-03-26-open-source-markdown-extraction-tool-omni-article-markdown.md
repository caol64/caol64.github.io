---
author: "路边的阿不"
title: 开源Markdown提取工具-Omni Article Markdown
slug: open-source-markdown-extraction-tool-omni-article-markdown
description: ""
date: 2025-03-26 17:25:27
draft: false
ShowToc: true
TocOpen: true
tags:
  - OpenSource
categories:
  - Markdown Tool
---

`Omni Article Markdown`，轻松将网页文章（博客、新闻、文档等）转换为 `Markdown` 格式。

## 功能介绍

此脚本的开发初衷，是为了解决一个问题：如何将来自互联网上各种不同网站的文章内容，精准且高效地转换成统一的Markdown格式。

众所周知，万维网上的网站设计风格迥异，其HTML结构也呈现出千差万别的特点。这种多样性给自动化内容提取和格式转换带来了巨大的困难。要实现一个能够适应各种复杂HTML结构的通用解决方案，并非易事。

我的想法是：从特定的网站开始适配，以点到面，逐步抽取出通用的解决方案，最后尽可能多的覆盖更多网站。目前支持较好的网站有：

- 掘金
- Medium
- Freedium（先保存至本地）
- 公众号
- 简书
- 知乎专栏（先保存至本地）
- 今日头条（先保存至本地）

其它网站暂未适配，但理论上都可以转换。需要注意的是有些网站不支持python直接抓取，或者有防机器人检测机制，这样的网站需要手动保存为 HTML 文件，再使用本工具。

## 安装与运行

### 安装依赖

确保 Python 环境可用，并安装必要依赖：
```sh
pip install -r requirements.txt
```

### 运行命令

```sh
python omni_article_md_cli.py <URL_OR_PATH> [-s [SAVE_PATH]]
```

## 参数说明

| 参数               | 说明 |
|--------------------|------|
| `URL_OR_PATH`     | **必填**，目标网页 URL 或本地 HTML 文件路径。 |
| `-s, --save`      | **可选**，启用保存：<br> `-s`：默认保存至 `./`。<br> `-s <SAVE_PATH>`：保存至指定路径。 |

## 使用示例

### 仅转换

```sh
python omni_article_md_cli.py https://example.com
```

### 转换并保存到默认路径

```sh
python omni_article_md_cli.py https://example.com -s
```

### 转换并保存到指定路径

```sh
python omni_article_md_cli.py https://example.com -s /home/user/data
```

## 项目代码

源代码开放在 [github](https://github.com/caol64/omni-article-markdown) 上。