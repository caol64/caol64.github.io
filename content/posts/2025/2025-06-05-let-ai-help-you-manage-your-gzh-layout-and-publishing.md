---
author: "路边的阿不"
title: 让AI帮你管理公众号的排版和发布
slug: let-ai-help-you-manage-your-gzh-layout-and-publishing
description: ""
date: 2025-06-05 09:32:05
draft: false
ShowToc: true
TocOpen: true
tags:
  - OpenSource
categories:
  - 文颜
---

随着人工智能的飞速发展，我们的内容创作方式也正在发生深刻变化。从灵感生成到润色校对，从图像处理到音视频剪辑，AI 已逐步成为创作者不可或缺的助手。上一篇文章我们介绍了「文颜 MCP Server」，今天让我们来看看怎样让它与 AI 结合，发挥最大生产力。

## 全新的交互方式：AI 对话即发布

借助 LLM（大语言模型）与 MCP 协议的结合，现在你可以通过自然语言直接操控整个公众号排版与发布流程。完整视频可以在[这里](https://babyno.top/posts/2025/06/wenyan-mcp-server-released/)观看。

你可以像朋友一样对模型说：

> “帮我用 OrangeHeart 主题发布这篇 Markdown 到公众号。”

模型会理解你的意图，并通过 文颜 MCP Server 自动完成以下步骤：

- 识别你指定的主题
- 对 Markdown 进行排版
- 自动上传图片并替换链接
- 提交至微信公众号草稿箱

整个过程不需要你打开编辑器、不需要上传图片、不需要调 CSS。效率翻倍，心情愉快。

## 如何上手

目前 文颜 MCP Server 已开源且正处于公测阶段，感兴趣的朋友可以前往 GitHub 仓库：https://github.com/caol64/wenyan-mcp ，根据文档部署到本地。

### 环境要求

确保已安装 [Node.js](https://nodejs.org/) 环境。

### Clone 仓库

```bash
git clone https://github.com/caol64/wenyan-mcp.git
cd wenyan-mcp
```

### 构建项目

```bash
npm install
npm run build
```

此时应该在`wenyan-mcp`项目下生成`dist`目录。

### 准备 MCP 客户端

接下来你需要准备一个支持 MCP 协议的客户端，比如`Claude`、`Cursor`等。我这里以`VSCode`的“通义灵码”插件为例。

打开`VSCode`的插件管理界面，下载[通义灵码](https://marketplace.visualstudio.com/items?itemName=Alibaba-Cloud.tongyi-lingma)。

### 将文颜 MCP Server与MCP客户端集成

![](imgs/posts/2025-06-05-let-ai-help-you-manage-your-gzh-layout-and-publishing/1.jpg)

点击左侧“灵码”面板，在你的账号下拉框出点击`Your settings`。（注意你可能需要先注册一个灵码账号）

![](imgs/posts/2025-06-05-let-ai-help-you-manage-your-gzh-layout-and-publishing/2.jpg)

在下方的`MCP Servers`面板点击添加按钮。

![](imgs/posts/2025-06-05-let-ai-help-you-manage-your-gzh-layout-and-publishing/3.jpg)

点击`Add by JSON`按钮。

![](imgs/posts/2025-06-05-let-ai-help-you-manage-your-gzh-layout-and-publishing/4.jpg)

在出现的对话框中输入以下内容：

```json
{
  "mcpServers": {
    "wenyan-mcp": {
      "name": "公众号助手",
      "type": "stdio",
      "command": "node",
      "args": [
        "Your/path/to/wenyan-mcp/dist/index.js"
      ],
      "env": {
        "WECHAT_APP_ID": "your_app_id",
        "WECHAT_APP_SECRET": "your_app_secret"
      }
    }
  }
}
```

如果你已经添加过其它 MCP Server，则只要在`mcpServers`节点下添加`wenyan-mcp`节点即可。

![](imgs/posts/2025-06-05-let-ai-help-you-manage-your-gzh-layout-and-publishing/5.jpg)

确保`MCP Server`的开关打开，连接变绿即可。

### 开始与 AI 对话

经过上述配置，文颜 MCP Server 已经为 AI 提供两个关键能力：

- list_themes：列出所有支持的主题
- publish_article：将文章发布到公众号

回到对话界面，你可以问一下 AI ：

> 有多少公众号主题可以选择？

![](imgs/posts/2025-06-05-let-ai-help-you-manage-your-gzh-layout-and-publishing/6.jpg)

接下来你就可以让 AI 帮你发布文章了：

> 用 xxx 主题将这篇文章发布到公众号

![](imgs/posts/2025-06-05-let-ai-help-you-manage-your-gzh-layout-and-publishing/7.jpg)

此时这篇文章就会出现在你的公众号账号的草稿箱中，随时等待你的发布。

## 文颜 MCP Server 为你做了什么

首先，帮你把 Markdown 文章按照指定的主题排版，支持的主题可以参考[文颜项目](https://yuzhi.tech/wenyan)。

接下来，识别文章中的图片，如果是本地图片或者非公众号网页上的网络图片，将图片上传到你的公众号资源库中，同时更新文章中的链接。

再然后，根据你指定的封面图或者从正文中选择一张作为封面图，上传到你的公众号资源库中。

最后，发布文章。

## 待改进的

文颜 MCP Server 尚处于公测版，有些功能和配置尚未完全确定下来。比如：为了符合公众号发布接口的定义，每篇文章必须指定一张封面图片和标题。而如何指定这张图片，现在采用的是在 Markdown 文章的开头添加一段`frontmatter`，比如：

```
---
title: 这是标题
cover: 这是封面
---
```

后续正在考虑更优雅的方式。

## 写作，只是开始

如果说过去的 AI 让你写文章更快、更顺手，那么接下来的 AI，会让你写完就能发布，一句话就能排版。

文颜 MCP Server 是这种新工作模式的重要一环，它让 AI 不再只是生成内容的工具，更是串联整个创作流程的智能执行者。

公众号创作，不必再忍受繁琐和重复。现在，你可以把它交给 AI，专注做你最擅长的事：创造。