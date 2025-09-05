---
author: "路边的阿不"
title: 从命令行到公众号，一键发布 Markdown — 文颜 CLI
slug: wenyan-cli-released
description: ""
date: 2025-09-05 15:17:08
draft: false
ShowToc: true
TocOpen: true
tags:
  - Open Source
  - 文颜
  - Software Releases
categories:
  - 项目介绍
---

## 什么是文颜 CLI？

文颜 CLI 是一个基于 Node.js 的命令行工具，它可以让你：

* ✅ 使用与 [文颜](https://yuzhi.tech/wenyan) 相同的主题系统对 Markdown 自动排版
* ✅ 将文章直接上传到微信公众号草稿箱
* ✅ 自动上传本地或网络图片，无需手工处理
* ✅ 保持全流程在终端完成，支持脚本化与自动化

换句话说，文颜 CLI 非常适合自动化完成「从写作到发布」的全流程。

## 工作原理

`wenyan-cli` 内置了一个 `publish` 子命令，用来执行完整的 Markdown → 微信公众号 草稿的转换与上传。

它会完成几件事：

1. 解析 Markdown
2. 应用指定的主题与代码高亮样式
3. 自动上传本地或远程图片到公众号素材库
4. 调用微信 API，将文章推送至公众号草稿箱

整个过程对用户是透明的，你只需要在命令行里执行一条指令。

## 如何使用？

### 安装

```bash
npm install -g @wenyan-md/cli
```

### 环境变量配置

发布到公众号需要配置两个环境变量：

* `WECHAT_APP_ID`
* `WECHAT_APP_SECRET`

#### macOS / Linux

```bash
export WECHAT_APP_ID=xxx
export WECHAT_APP_SECRET=yyy
```

#### Windows PowerShell

```powershell
$env:WECHAT_APP_ID="xxx"; $env:WECHAT_APP_SECRET="yyy"
```

> ⚠️ 记得把服务器 IP 加入公众号后台的 **IP 白名单**，否则接口会报错。

### 命令行示例

直接传入 Markdown 内容：

```bash
wenyan publish "# Hello, Wenyan" -t lapis -h solarized-light
```

从文件读取并关闭 Mac 风格代码块：

```bash
cat example.md | wenyan publish -t lapis -h dracula --no-mac-style
```

更多内置主题请见：[主题预览](https://yuzhi.tech/docs/wenyan/theme)

## 与文颜 MCP Server 的协同使用

如果说 **文颜 CLI** 更适合「开发者」和「写作者」的日常使用场景（比如：本地脚本、CI/CD 自动化），那么 **[文颜 MCP Server](https://babyno.top/posts/2025/06/wenyan-mcp-server-released/)** 就是面向 **LLM 协作场景** 的另一把利器。

* 在命令行里：你用 `wenyan-cli` 把文章一键发布到公众号；
* 在对话中：你让 LLM 调用 `wenyan-mcp` 的工具，让它自动完成文章排版与上传。

两者结合，可以覆盖 **自动化操作** 与 **AI 辅助操作** 的完整工作流：

* 想要快速写作和自动化发布？用 `wenyan-cli`。
* 想要和大语言模型自然协作？用 `wenyan-mcp`。

它们共享同一套主题和上传逻辑，保证排版效果一致。

## 适合谁？

* **自媒体作者**：再也不用为公众号排版发愁
* **技术写作者**：Markdown → 公众号，一条命令
* **团队/企业**：可以集成到 CI/CD 流程，实现自动发布
* **AI 用户**：配合 MCP Server，把文章发布交给大语言模型完成

## 总结

文颜 CLI 让写作者们告别了手动排版的痛点。
从命令行运行一条命令，就能把 Markdown 文件变成一篇公众号草稿，自动处理主题、图片和格式，让写作回归「写内容」的本质。

👉 GitHub 地址：[https://github.com/caol64/wenyan-cli](https://github.com/caol64/wenyan-cli)