---
author: "路边的阿不"
title: 从Markdown到公众号，自动发布新体验 — 文颜 MCP Server
slug: wenyan-mcp-server-released
description: ""
date: 2025-06-04 15:48:14
draft: false
ShowToc: true
TocOpen: true
tags:
  - OpenSource
categories:
  - 文颜
---

不管你是自媒体作者还是技术人员，在创作的工作流中，有没有让你头疼的时刻？Markdown 写得很爽，但发布到微信公众号却要：

- 重新排版
- 手动上传图片
- 一遍遍调格式

因为此，我开发了[文颜](https://yuzhi.tech/wenyan)，专门为了解决这个问题。而今天，随着`文颜 MCP Server`的发布，这个工作流程又迎来了全新的面貌。

## 什么是文颜 MCP Server？
文颜 MCP Server 是一款基于模型上下文协议（MCP）的开源服务器组件，它可以：

- ✅ 将 Markdown 文章自动排版成公众号格式
- ✅ 一键上传本地或网络图片
- ✅ 使用与 文颜 一致的主题美化内容
- ✅ 自动发布到微信公众号草稿箱

而所有这些功能，你可以在与LLM（大语言模型）的聊天中自然而然的完成，完全不用打开“文颜”这样的排版工具。

## 全新的交互流程

先看视频：

<p>
    <video controls width="100%">
        <source src="https://yuzhi.tech/img/wenyanmcp/intro.mp4" type="video/mp4">
    </video>
</p>

视屏中展示了一个常见的工作流：先向模型询问`文颜 MCP Server`支持哪几种公众号主题，然后让模型将 Markdown 文章使用指定的主题发布到公众号，简单明了。

## 工作原理

`文颜 MCP Server`实现了`MCP`协议，为与之对接的 LLM 模型提供了两个工具：

- list_themes
- publish_article

这两个工具让模型知道自己具备了将文章发布到公众号的能力，同时也知道了可以支持哪些主题。因此你在让模型发布文章的时候，它会自动调用这两个工具。

## 如何使用

目前还处于公测阶段，想要尝鲜的小伙伴可以去[github仓库](https://github.com/caol64/wenyan-mcp)克隆代码并在本地部署。