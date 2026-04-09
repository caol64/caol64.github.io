---
author: "路边的阿不"
title: 告别套用模板，亲手打造主题：公众号排版Skill
slug: wenyan-skill-unique-wechat-theme
description: ""
date: 2026-04-09 11:41:27
draft: false
ShowToc: true
TocOpen: true
tags:
  - 文颜
categories:
  - 项目介绍
---

自从各类“龙虾”AI 工具流行起来，能自动发布公众号的技能越来越多，内容生成变得越来越轻松，可文章排版反而越来越千篇一律。排版工具自带的那几套主题，要么过于简单平淡，要么看多了很容易审美疲劳。

前几天有朋友问我：“有没有办法让公众号文章看起来更专业，又不用去学前端开发？”

其实这个问题我自己也琢磨了很久。直到最近，我给文颜上线了一项新能力——**微信公众号自定义主题生成 Skill**，才算真正把这个痛点解决掉。

## 文颜：覆盖多场景的 Markdown 排版工具

先简单说下文颜。

**[文颜（Wenyan）](https://wenyan.yuzhi.tech)** 是一款多平台 Markdown 排版与发布工具，支持将 Markdown 一键转换并发布至：

- 微信公众号
- 知乎
- 今日头条
- 以及其它内容平台（持续扩展中）

它的核心目的就一个：**让写作者专注内容，而不是排版和平台适配**。

目前文颜已经覆盖了不同使用场景，形成了完整工具链：

- **[macOS App Store 版](https://github.com/caol64/wenyan)** - MAC 桌面应用
- **[跨平台桌面版](https://github.com/caol64/wenyan-pc)** - Windows/Linux
- **[CLI 版本](https://github.com/caol64/wenyan-cli)** - 命令行工具
- **[MCP 版本](https://github.com/caol64/wenyan-mcp)** - AI 自动发文

在文颜的整套工具里，`wenyan-cli`一直是开发者和硬核写作者最爱的 “极客版”。它把原本繁琐的发布流程压缩成一行命令，排版、发布全程不用再手动点来点去，现在也已经成了不少公众号相关 Skill 的默认集成工具。

还不了解文颜的朋友，可以先看看文颜的[内置主题](https://yuzhi.tech/docs/wenyan/theme)，一共8套。

今天要说的方法，能让你做出**完全属于自己的个性化主题**，并且在文颜全工具链里通用。

## 用自然语言生成公众号主题

简单来说，以前你想做一套专属公众号主题，需要自己写 CSS 样式；现在不用写代码，直接用自然语言告诉 AI 想要什么风格，AI 就能帮你生成可用的主题样式。

核心逻辑很简单：**让 AI 帮你完成排版设计**。

你可以在两个平台找到文颜的这个 Skill：

- [腾讯 SkillHub](https://skillhub.tencent.com/skills/generate-wenyan-theme)
- [ClawHub](https://clawhub.ai/caol64/generate-wenyan-theme)

## 如何安装 Skill（以 Claude Code 为例）

安装 Skill 其实很简单，我用 Claude Code 做个演示：

1. 打开 Claude Code 终端
2. 输入 `/skills` 命令
3. 搜索 `generate-wenyan-theme`
4. 点击安装即可

安装完成后，你就可以随时让 AI 帮你生成公众号主题了。

## 一键生成公众号主题

安装好 Skill 之后，使用方式非常自然。比如你对 AI 说：

> "帮我生成一个赛博朋克风格的公众号主题，主色调是霓虹蓝和品红，代码块要深色背景"

AI 就会根据你的描述，直接生成完整 CSS 文件并保存到本地。

整个过程不需要你懂任何 CSS 知识，只需要用日常语言描述你想要的效果就行。

## 实战案例：漫画风格主题

前两天我让 Skill 生成一个**漫画风格**的主题，效果出乎意料地好。

我是这样描述的：

> "生成一个漫画风格的主题，像是日漫的感觉，标题可以有手绘边框的效果，引用块像漫画对话框，整体活泼一点"

AI 给我生成的主题文件保存在 `theme-comic.css`，直接套用就能用。

这个主题的特点：

- 标题带手绘马克笔边框
- 引用块做成漫画气泡对话框，带尖角尾巴
- 整体配色明亮，适合轻松向内容

## 预览 & 微调主题

生成主题后，你可以在**文颜 Web 版**实时预览效果：

1. 打开 [文颜 Web 版](https://wenyan.yuzhi.tech/web)
2. 点击"**样式**"
3. 创建新主题，选择"**从模版新建**"
4. 把生成的 CSS 内容粘贴至左侧编辑器内，保存即可预览

如果不满意，可以继续让 AI 调整。比如：

> "把标题颜色再深一点"
> "引用块的气泡尾巴改到左边"
> "代码块背景再暗一些"

反复调整到满意为止。

## 不同版本使用主题

主题做好后，各版本文颜都能直接用。

### Web 版 / 桌面端

直接点击复制按钮，然后粘贴到公众号编辑器中即可。

### CLI 版

CLI 用户有两种选择：

**临时使用**（单次生效）：

```bash
wenyan publish -f article.md --custom-theme ./my-theme.css
```

**永久注册**（重复使用）：

```bash
wenyan theme --add --name my-theme --path ./my-theme.css
wenyan publish -f article.md -t my-theme
```

### MCP 版

如果你用的是 MCP 版本，整个过程更自然，直接对 AI 说：

> "把 ./my-theme.css 注册成主题，名字叫 xiuluochang"

然后：

> "用 xiuluochang 主题，把 article.md 发布到微信公众号"

AI 会自动完成注册、排版、发布全流程。

## 写在最后

做这个 Skill 的初衷很简单：让不会写 CSS 的普通用户，也能轻松拥有专属公众号排版。

整个流程就四步：

1. 安装 Skill
2. 用大白话描述风格
3. AI 生成 CSS
4. 预览、调整、发布

整个过程不需要写一行代码。

如果你有想尝试的排版风格，可以去试试这个 Skill，也欢迎在评论区说说你想要什么样的主题。
