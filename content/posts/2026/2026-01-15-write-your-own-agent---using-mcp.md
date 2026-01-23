---
author: "路边的阿不"
title: 自己写一个智能体-使用MCP服务
slug: write-your-own-agent---using-mcp
description: ""
date: 2026-01-15 15:30:00
draft: false
ShowToc: true
TocOpen: true
tags:
  - Agents
  - LLM
  - MCP
  - Tutorial
categories:
  - AI
---

还记得我们在[上一篇文章](https://babyno.top/posts/2024/12/write-your-own-agent---theory/)中聊过的“智能体”理论吗？

我们提到，智能体之所以比单纯的语言模型强大，是因为它拥有了“手”和“脚”——也就是**使用工具的能力**。

> 智能体 = 大语言模型（大脑） + 规划（前额叶） + 工具（手脚）

理论说得再多，终究要落地。今天我们就来聊聊如何通过 **MCP (Model Context Protocol)** 协议，真正的让你的智能体“动”起来。我们将以一个实际场景为例：**写一段代码，让AI自动把一篇文章发布到微信公众号。**

## 什么是 MCP？

在开始写代码之前，得先解决一个痛点。

以前我们要让 GPT 连接外部工具（比如读取文件、搜索网页、操作数据库），通常需要针对不同的 API 写一大堆胶水代码。如果你用 `LangChain`，你得遵循它的接口规范；如果你换个框架，可能全得重写。

**MCP (Model Context Protocol)** 就是 AI 时代的 **USB-C 接口**。它是由 Anthropic 等公司推动的一个开放标准。

- **MCP Server**：提供工具（比如：文件读取服务、微信发布服务）。
- **MCP Client**：也就是我们的智能体（负责连接模型和服务端）。
- **LLM**：负责决策调用哪个工具。

只要大家遵循这个协议，你的智能体就可以无缝连接任何支持 MCP 的工具，而不需要关心底层的具体实现。

## 实战：构建公众号发布智能体

接下来，我们通过一段 `Node.js` 代码，演示如何把一个本地 Markdown 文件，通过 MCP 服务发布到微信公众号。

### 1. 准备工作

在这个例子中，我们需要三个角色的配合：

1.  **大脑**：一个支持 Function Calling 的大模型（如 GPT-4o 或 DeepSeek 等兼容 OpenAI 格式的模型）。
2.  **工具箱 (MCP Server)**：这里我们使用 `caol64/wenyan-mcp`，这是一个封装了微信公众号发布功能的 MCP 服务，我们通过 Docker 运行它。
3.  **智能体 (MCP Client)**：我们自己写的这段 JS 代码。

### 2. 连接 MCP 服务

首先，我们需要建立与 MCP Server 的连接。在代码中，我们通过 `StdioClientTransport` 来启动一个 Docker 容器作为我们的工具服务。

```javascript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

// ... 环境变量检查代码 ...

const pwd = process.cwd();
// 建立传输通道：通过 Docker 运行 wenyan-mcp 服务
const transport = new StdioClientTransport({
    command: "docker",
    args: [
        "run",
        "--rm",
        "-i",             // 必须开启交互模式，以便通过 stdio 通信
        "--env-file", ".env.test", // 传入公众号的 AppID 等凭证
        "-e", `HOST_FILE_PATH=${pwd}`,
        "-v", `${pwd}:/mnt/host-downloads`, // 挂载目录，让容器能读取到文章
        "caol64/wenyan-mcp",
    ],
});

const client = new Client(
    { name: "wenyan-client", version: "1.0.0" },
    { capabilities: {} }
);

await client.connect(transport);
```

这段代码对应了上一篇提到的**“工具使用”**的前提——智能体得先能拿得起工具。

### 3. 获取工具列表

连接成功后，智能体需要知道自己有哪些工具可用。这对应了理论篇中的**“问题分类”**准备阶段，只有知道有哪些工具，模型才能决定用哪个。

```javascript
// 获取 MCP 服务端提供的所有工具
const mcpResponse = await client.listTools();

// 将 MCP 的工具定义转换为 OpenAI 兼容的 Function Calling 格式
const openaiTools = mcpResponse.tools.map((tool) => ({
    type: "function",
    function: {
        name: tool.name,
        description: tool.description,
        parameters: tool.inputSchema, // MCP 的 schema 通常直接兼容
    },
}));
```

此时，`openaiTools` 里就装满了诸如 `publish_article` 之类的方法描述。

### 4. 思考与决策

现在进入核心环节。我们将文章内容和需求告诉 LLM，让它自己判断该做什么。

```javascript
const llmClient = new OpenAI({ apiKey: LLM_API_KEY, baseURL: LLM_BASE_URL });
const content = "./test/publish.md"; // 待发布的文章路径

// 用户的指令：既包含了目标（发布），也包含了参数（使用 phycat 主题）
const userPrompt = { 
    role: "user", 
    content: `使用phycat主题将这篇文章发布到微信公众号：\n\n${content}` 
};

// 第一轮对话：询问 LLM
const response = await llmClient.chat.completions.create({
    model: LLM_MODEL,
    messages: [userPrompt],
    tools: openaiTools, // 把工具箱展示给它
    tool_choice: "auto", // 让模型自己决定是否用工具
});
```

在这里，模型会分析 `userPrompt`。它发现你的意图是“发布”，并且它看到了 `openaiTools` 里有一个能发布的工具，于是它不会直接回答“好的”，而是会返回一个 `tool_calls` 请求。

### 5. 执行工具与反馈

智能体捕获到模型的调用请求，真正的去执行操作，并将结果反馈给模型。这就是**“优化答案”**的前奏。

```javascript
const assistantMessage = response.choices[0].message;

if (assistantMessage.tool_calls) {
    for (const toolCall of assistantMessage.tool_calls) {
        const name = toolCall.function.name;
        const args = JSON.parse(toolCall.function.arguments);

        // 关键步骤：通过 MCP Client 真正的调用 Docker 里的服务
        const result = await client.callTool({
            name: name,
            arguments: args,
        });

        // 获取工具执行结果（比如：发布成功的链接）
        const toolContent = result.content.map((item) => item.text).join("\n");
        
        // 将结果拼接回对话历史
        const finalMessages = [
            userPrompt,
            assistantMessage,
            {
                role: "tool",
                tool_call_id: toolCall.id,
                content: toolContent,
            },
        ];

        // 第二轮对话：让 LLM 根据工具执行结果给用户一个最终回复
        const finalResponse = await llmClient.chat.completions.create({
            model: LLM_MODEL,
            messages: finalMessages,
        });

        console.log(finalResponse.choices[0].message.content);
    }
}
```

## 发生了什么？

让我们回顾一下整个流程：

1.  **User**: "帮我把 `publish.md` 发到公众号。"
2.  **LLM**: (思考：我不能直接操作微信，但我有一个叫 `publish_article` 的工具。我需要提取参数：文件路径和主题。) -> **发出指令**。
3.  **Agent (JS代码)**: 收到指令，通过 MCP 协议告诉 Docker 容器里的服务：“嘿，运行一下这个函数”。
4.  **MCP Server**: 执行实际的 API 调用，转换 Markdown，上传素材，保存到草稿箱，返回结果：“发布成功，文章链接是 xxx”。
5.  **LLM**: 收到结果，组织语言。 -> **最终回复**: "您的文章已成功发布，使用了 phycat 主题，链接如下：xxx。"

![mcp-workflow](imgs/posts/2026-01-15-write-your-own-agent---theory/1.jpg)

## 总结

通过引入 MCP，我们把“智能体”的代码写得非常通用。

注意到了吗？上面这段代码里，**没有任何一行是关于微信 API 的具体实现的**。如果不加载 `wenyan-mcp`，而是换成一个 `filesystem-mcp`，这段代码逻辑几乎不用变，智能体就能拥有操作文件的能力。

这就是现代智能体架构的魅力：**大模型负责逻辑，MCP 负责能力，智能体程序负责连接。**
