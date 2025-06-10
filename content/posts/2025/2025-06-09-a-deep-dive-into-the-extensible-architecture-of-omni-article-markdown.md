---
author: "路边的阿不"
title: 「墨探」是如何使用插件机制构建可扩展架构的
slug: a-deep-dive-into-the-extensible-architecture-of-omni-article-markdown
description: ""
date: 2025-06-09 15:47:32
draft: false
ShowToc: true
TocOpen: true
tags:
  - Open Source
  - Markdown
  - 墨探
  - Software Architecture
categories:
  - 项目介绍
---

> 让网页内容一键转 Markdown，从未如此优雅。

![demo](https://yuzhi.tech/img/amarkdown/1.gif)

互联网上的内容无所不在 —— 新闻、博客、技术文章、公众号推文、知乎专栏……信息丰富，却五花八门。当我们希望将它们转换为结构清晰、易于发布和归档的 Markdown 格式时，却不得不面对 HTML 结构的混乱、样式的割裂和内容提取的困扰。

为了解决这个问题，开源项目 **omni-article-markdown**（中文名「墨探」）应运而生。但它并非仅是一个“爬虫”工具，更像一个可持续进化的“阅读器平台”。

## 架构初探

「墨探」的架构非常简单，它构建于两个模块之上：

![架构](imgs/posts/2025-06-09-a-deep-dive-into-the-extensible-architecture-of-omni-article-markdown/omni-article-markdown-1.jpg)

- Reader 模块的功能是提取网页内容
- Parser 模块的功能是将网页内容转换成`Markdown`

## 插件为核心

> 插件如何让「墨探」可适应所有网站？

其核心亮点，便在于它构建于 `pluggy` 插件机制之上。

在传统方案中，提取网页内容往往依赖硬编码的规则。如果目标网站一改版，就前功尽弃。而「墨探」通过引入 [pluggy](https://pluggy.readthedocs.io/en/latest/)，构建了一套通用插件注册系统，允许开发者为特定网站编写自定义解析器，无需修改主程序，就能“无缝接入”。

![架构](imgs/posts/2025-06-09-a-deep-dive-into-the-extensible-architecture-of-omni-article-markdown/omni-article-markdown-2.jpg)

## 插件工作机制

插件的工作机制也是十分简单，当「墨探」遇到一个 URL 时，询问所有插件谁能处理它。一旦某个插件声明“我可以处理这个 URL”，主应用就会优先调用它进行内容提取，而不是使用默认的 HTML 提取器。这种机制让工具具备了「策略模式」的灵活性，但又通过 `pluggy` 实现了解耦与统一管理。

### 插件的实现方式

项目使用 `pluggy` 定义了一个关键钩子（hooks）：

```python
@hookspec(firstresult=True)
def get_custom_reader(url: str) -> Optional[ReaderPlugin]:
  ...
```

而作为插件开发者，首先就是要实现这个钩子。以“知乎插件”为例：

```python
# 实例化插件
zhihu_plugin_instance = ZhihuReader()

@hookimpl
def get_custom_reader(url: str) -> Optional[ReaderPlugin]:
    if zhihu_plugin_instance.can_handle(url):
        return zhihu_plugin_instance
    return None
```

这个钩子，返回的是一个`ReaderPlugin`的实例，`ReaderPlugin`是为了简化和规范插件开发而定义的协议，它定义了两个接口：

```python
class ReaderPlugin(Protocol):
    def can_handle(self, url: str) -> bool:
        ...

    def read(self, url: str) -> str:
        ...
```

- `can_handle()`：判断是否能处理当前 URL。
- `read()`：返回网页原始 HTML。

现在你只要编写`ZhihuReader`实现这两个接口即可完成自定义插件。

### 插件注册与加载

墨探使用 `pluggy` **自动发现并通过 `setuptools` 的入口点（entry points）机制加载插件**。插件开发者无需修改主程序代码，只需在插件项目的配置文件中添加如下声明：

```toml
[project.entry-points."mdcli"]
my_plugin = "my_plugin_module:plugin_object"
```

安装后，墨探在运行时会自动发现并加载该插件。

插件机制带来的优势包括：

* **解耦**：核心应用不依赖插件实现，插件与主程序相互独立。
* **可扩展性**：任何符合规范的插件都可自动接入，无需修改主程序。
* **模块化**：每个插件都可以单独开发、测试、分发，便于协作。
* **生态潜力**：社区可贡献更多插件，形成一个内容提取生态系统。

得益于这种插件注册机制，墨探得以从一个简单的网页解析工具，演进为一个可持续演化、社区可共建的内容提取平台。

### 插件安装与管理

墨探的命令行工具 `mdcli` 提供了便捷的插件管理命令：

```sh
mdcli install zhihu
mdcli uninstall zhihu
```

支持从 PyPI 或本地路径安装。目前已发布的插件包括：

- `zhihu`：知乎专栏
- `toutiao`：今日头条
- `freedium`：绕过 Medium 限制的 Freedium

## 核心能力概览

### 一键 Markdown 转换

墨探支持从网页 URL 或本地 HTML 文件中提取正文并转为 Markdown：

```sh
mdcli https://example.com
mdcli your/path/example.html
```

支持内容包括：标题、段落、列表、代码块、图片、表格、引用、公式、GitHub Gist 等。

### 灵活的保存选项

你可以将输出结果直接保存到当前目录或指定路径：

```sh
mdcli https://example.com -s
mdcli https://example.com -s /home/user/data.md
```

### 默认支持的网站

即使不开启插件，墨探已对多个网站内置支持：

- 掘金、CSDN、Medium、简书
- 微信公众号
- towardsdatascience、quantamagazine 等

## 使用场景推荐

- 构建 Markdown 文档库：将博客收藏一键导出为 `.md`，便于归档与搜索。
- 微信公众号写作：写作素材来自网页，导出 Markdown 后可直接发布。
- AI 数据整理：将网页文本标准化为 Markdown，供大模型处理或训练。

## 为什么推荐你使用墨探

- **轻量纯粹**：CLI 工具，开箱即用，无需繁重依赖。
- **插件扩展**：支持任意网站接入，适配灵活。
- **社区驱动**：人人可写插件，共建生态圈。
- **格式优雅**：生成 Markdown 结构清晰，语义准确。

## 快速开始

1. 安装主程序

```sh
pip install omni-article-markdown
```

2. 安装插件（可选）

```sh
mdcli install zhihu
```

3. 运行命令：

```sh
mdcli https://zhuanlan.zhihu.com/p/123456789 -s
```

4. 打开刚保存的 Markdown 文件，享受清爽的阅读体验！

## 项目地址与贡献方式

- GitHub 项目主页：
  [https://github.com/caol64/omni-article-markdown](https://github.com/caol64/omni-article-markdown)

欢迎提交 Issue、Pull Request 或编写插件参与贡献！

## 结语

如果你喜欢这个项目，不妨[喂作者家的猫吃点罐头](https://yuzhi.tech/sponsor)。

**墨探，正在让阅读变得简单且优雅。**
