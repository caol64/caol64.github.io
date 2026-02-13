---
author: "路边的阿不"
title: 自己写一个智能体-让其理解Skills
slug: write-your-own-agent---understanding-skills
description: ""
date: 2026-01-23 10:00:00
draft: false
ShowToc: true
TocOpen: true
tags:
  - Agents
  - LLM
  - Prompt Engineering
  - Tutorial
categories:
  - AI
---

回顾一下我们的“造人”计划。

在[理论篇](https://babyno.top/posts/2024/12/write-your-own-agent---theory/)中，我们给智能体装上了“大脑”（LLM）；在[MCP实战篇](https://babyno.top/posts/2026/01/write-your-own-agent---using-mcp/)中，我们通过MCP协议给它接上了“手脚”（工具）。

现在，你的智能体已经很聪明，也能干活了。但你可能会发现一个新问题：它有时候太“随性”了。这就好比你招了一个天才员工，但他不知道公司的规章制度，也不知道具体的工作流程。

今天我们要聊的，就是如何给智能体注入“灵魂”，知道自己是谁，要干什么。通俗点讲，就是给其编写“员工手册”。在技术圈里，我们通常称之为 **Skills（技能）** 或 **System Instructions（系统指令）**。

## 什么是 Skills？

在智能体的架构中，`Skills` 本质上是一段结构化的文本。它不是代码逻辑，不需要编译，但它直接决定了智能体的**人设、职责、边界和工作流**。

如果说 LLM 提供了通用的智力，那么 Skills 就是将这份智力聚焦到特定领域的透镜。

> **智能体 = 大模型（大脑） + 工具（手脚） + Skills（灵魂）**

一个优秀的 `Skills` 定义通常包含以下几个要素：

1.  **Role (角色)**：你是谁？（比如：资深代码审查员）
2.  **Goal (目标)**：你要干什么？（比如：找出代码中的Bug并提出优化建议）
3.  **Constraints (约束)**：你不能干什么？（比如：只指出问题，不要直接重写代码）
4.  **Workflow (工作流)**：你思考的步骤是什么？（比如：先概括功能，再逐行分析，最后打分）

## 为什么需要独立维护 Skills？

很多初学者喜欢把这些提示词（Prompt）直接写死在代码里（Hardcode）。这样做有两个坏处：

1.  **调试困难**：每次修改提示词都要改代码、重启服务。
2.  **复用性差**：代码逻辑是通用的（比如“接收输入->调用模型->返回输出”），但业务逻辑是多变的。

最好的做法是将 Skills 剥离出来，存放在一个独立的 Markdown 文件（如 `skills.md`）中。

这样一来，你的 Python 或 Node.js 代码就变成了一个**通用的执行引擎**。你想让它变成“翻译官”，就加载翻译的 `skills.md`；想让它变成“心理咨询师”，就换一个文件。**这才是智能体开发的精髓——代码与配置分离。**

![agent-skills-structure](imgs/posts/2026-01-23-write-your-own-agent---write-your-own-agent---understanding-skills/skills-arch.jpg)

## 实战：构建一个“代码审查”智能体

让我们通过一个具体的例子来看看如何实现。我们将创建一个专门负责 Code Review 的智能体。

### 1. 编写 Skills 文件

首先，我们不用写代码，先用自然语言定义智能体的灵魂。新建一个 `reviewer_skills.md`：

```markdown
# Skill: CodeReview.Strict

## Responsibility
对用户提供的代码进行专业级代码审查，重点关注：
- 安全性
- 性能
- 可维护性

本 Skill **不负责**：
- 重构整体架构
- 改写全部实现

## Input
- 任意单段或多段代码
- 可能缺少上下文

## Output Contract
输出必须包含以下部分（按顺序）：
1. **Intent Summary**：一句话说明代码目的
2. **Issues**
   - Security
   - Performance
   - Best Practices
3. **Score**：0–100 的整数评分

## Review Rules
- 优先级顺序：Security > Correctness > Performance > Style
- 发现高危安全问题时，必须明确标注为 **Critical**

## Language-Specific Rules
- Python：必须检查类型注解完整性
- JavaScript / TypeScript：必须检查边界条件

## Modification Policy
- 默认仅提供局部修改建议
- 若问题无法通过局部修改解决，必须说明原因

## Format
- 使用 Markdown
- 使用清晰小标题
```

看到了吗？这完全是人类可读的文档，但它稍后将成为控制 AI 的指令。

### 2. 让代码“读取”灵魂

接下来，我们需要在代码层面做一件事：**读取这个文件，并将其作为 System Prompt (系统提示词) 注入给模型。**

大部分大模型 API（如 OpenAI, Anthropic, DeepSeek）都支持 `system` 角色。这个角色的权重非常高，模型会始终遵循 `system` 中的设定来处理 `user` 的输入。

*（具体代码实现请见文章末尾的代码示例）*

### 3. 动态加载的魔力

一旦你跑通了这个流程，你会发现很多有趣的事情：

- 觉得它评审太严了？改一下 Markdown 里的文字，保存即可生效，无需改代码。
- 需要它支持 Java 规范？在 Constraints 里加一行字就行。

这就是`Prompt Engineering as Code`（提示词即代码）。

## 总结

到这一篇为止，我们已经完成了一个最小化智能体的核心拼图：

1.  **理论篇**：理解了它为什么能听懂话。
2.  **MCP篇**：教会了它如何使用工具（Action）。
3.  **Skills篇**：教会了它如何遵守规范（Instruction）。

从能力建模角度看，AutoGPT、MetaGPT 等 Agent 框架的“智能”，主要来自对 Prompt（skills）的结构化拆分；真正的工程复杂度不在对话本身，而在状态管理、调度与执行闭环。

下一步，也许你可以尝试让你的智能体拥有“记忆”，或者让两个持有不同 Skills 的智能体“左右互搏”。

AI 的世界，才刚刚开始。

---

## 附录

### 代码示例

这里提供一套 `Node.js` 代码示例。

#### 1. 目录结构
```text
my-agent/
├── package.json
├── index.js
└── skills.md
```

#### 2. 准备 `skills.md`
在目录下新建 `skills.md`，内容如下：

```markdown
# Role
你是一个极其严格的代码审查员（Code Reviewer）。你的名字叫 "LintMaster"。
你不仅关注代码逻辑，还特别在意变量命名风格。

# Objectives
1. 接收用户输入的代码。
2. 分析代码中的逻辑错误。
3. 检查变量命名是否符合驼峰命名法（CamelCase）。
4. 给出最终评分（0-100分）。

# Style
- 说话简练，直击痛点。
- 如果代码写得太烂，可以用幽默讽刺的语气进行批评。
```

#### 3. 编写 `index.js`

你需要先安装 openai 库：`npm install openai`

```javascript
import fs from 'fs';
import path from 'path';
import OpenAI from 'openai';

// 配置你的 LLM (这里以兼容 OpenAI 协议的模型为例，如 DeepSeek, Moonshot 等)
// 请在环境变量中设置 API Key，或者直接替换下方的字符串
const client = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY || "sk-xxxxxx",
    baseURL: process.env.OPENAI_BASE_URL || "https://api.openai.com/v1"
});

// 核心函数：加载 Skills
function loadSkills(filename) {
    try {
        const filePath = path.join(process.cwd(), filename);
        const skillsContent = fs.readFileSync(filePath, 'utf-8');
        console.log(`成功加载 Skills: ${filename}`);
        return skillsContent;
    } catch (error) {
        console.error("加载 Skills 失败:", error.message);
        process.exit(1);
    }
}

async function runAgent() {
    // 1. 读取 Skills (作为智能体的“灵魂”)
    const systemInstruction = loadSkills('skills.md');

    // 2. 模拟用户的糟糕代码输入
    const userCode = `
        function caLculate_sum(a, b) {
            if (a = b) { // 典型的逻辑错误
                return a * 2;
            }
            let RESult_VaLue = a + b;
            return RESult_VaLue;
        }
    `;

    console.log("\nAgent 正在思考...\n");

    // 3. 构建对话上下文：System (Skills) + User (Task)
    const response = await client.chat.completions.create({
        model: "gpt-4o", // 或 deepseek-chat 等
        messages: [
            { role: "system", content: systemInstruction }, // 注入灵魂
            { role: "user", content: `请审查以下代码：\n${userCode}` }
        ],
        temperature: 0.7
    });

    // 4. 输出结果
    console.log("--- 审查报告 ---");
    console.log(response.choices[0].message.content);
}

runAgent();
```

#### 4. 运行效果

当你运行 `node index.js` 时，你会看到类似这样的输出（取决于模型的发挥）：

```text
成功加载 Skills: skills.md

Agent 正在思考...

--- 审查报告 ---
**LintMaster 审查报告**

哎哟，这代码看得我血压都升高了。💀

1. **逻辑炸弹**：
   在 `if (a = b)` 这里，你是在赋值而不是比较！你应该用 `==` 或者 `===`。写这种 bug 是想让测试工程师下班堵你吗？

2. **命名灾难**：
   `caLculate_sum`？`RESult_VaLue`？你的键盘是不是 Shift 键卡住了？
   请遵守驼峰命名法：`calculateSum`, `resultValue`。

**最终评分**：30/100。
（给你30分是因为你至少知道要用 `return`，赶紧重写！）
```
