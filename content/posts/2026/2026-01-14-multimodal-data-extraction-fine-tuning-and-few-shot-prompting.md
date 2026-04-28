---
author: "路边的阿不"
title: 多模态数据提取：微调与少样本提示
slug: multimodal-data-extraction-fine-tuning-and-few-shot-prompting
description: ""
date: 2026-01-14 09:16:20
draft: false
ShowToc: true
TocOpen: true
tags:
  - LLM
  - Prompt Engineering
  - Tutorial
  - Fine-tune
categories:
  - AI
---

> 这是一篇偏实践向的记录，主要整理我在「用多模态大模型做发票数据结构化提取」过程中踩过的坑、验证过的方案，以及一些比较稳妥的落地思路。整体目标只有一个：**让模型稳定输出可直接用的 JSON，而不是“看起来很聪明”的一大段解释。**

## 背景与目标

实际业务里，我们经常会遇到这种需求：

- 输入：一张发票图片（拍照 / 扫描，质量参差不齐）
- 输出：结构化业务数据，比如

  - 供应商名称
  - 发票号、日期
  - 明细行（商品名、数量、单位、金额等）

- 格式要求：**标准 JSON，可直接进数据库或走 RPA**

传统 OCR + 规则方案在版式复杂、字段漂移时非常脆弱，而多模态大模型（VLM）正好补上了这一块：

- 能同时理解图像和指令
- 能在“看懂”的基础上做结构化输出

我们主要用以下模型做测试：Gemini 1.5 Pro、GPT-4o、Llama‑3.2‑Vision、Qwen2‑VL 等。

## 多模态微调数据

### 1. 一个典型的数据样例

下面这个结构，基本就是**多模态微调或评测时最小且有效的单元**：

```json
{
  "contents":[
    {
      "role":"user",
      "parts":[
        {"fileData":{"mimeType":"image/jpeg","fileUri":"/static/example_invoice.jpeg"}},
        {"text":"Extract the key business data from the provided input."}
      ]
    },
    {
      "role":"model",
      "parts":[
        {"text":"{\"supplier_name\": \"Lone Star Provisions Inc.\", \"invoice_number\": \"785670\", \"invoice_date\": \"2025-08-20\", \"inventory_items\": [{\"item_name\": \"TAVERN HAM WH\", \"total_quantity\": 15.82, \"total_unit\": \"LB\", \"total_cost\": 87.8}]}"}
      ]
    }
]
}
```

### 2. 为什么这种结构很重要？

它的价值主要体现在三点：

- **非常接近真实调用场景**：用户给图片 + 指令，模型直接回 JSON
- **一次性训练多种能力**：

  - OCR / 视觉理解
  - 指令理解
  - 严格格式输出

- **为下游系统负责**：避免“多一句解释就让解析失败”的尴尬

如果你的目标是「模型输出能不能直接被程序消费」，那这种数据格式几乎是必选项。

## 微调 vs 少样本 Prompt

实际落地时，我基本只在这两条路里选。

### 路线一：模型微调（Fine-tuning）

#### 1. 在线模型（Gemini / GPT-4o）托管微调

这是**最快、工程成本最低**的一条路。

**基本流程：**

1. 把上面的数据整理成平台要求的 JSONL
2. 上传到 Vertex AI / OpenAI
3. 选基座模型（比如 gemini‑1.5‑flash）
4. 默认参数直接训，一般就够用

训练完成后，会得到一个私有 `model_id`，调用方式和原模型几乎一致：

```
model = GenerativeModel("tunedModels/your-invoice-model-id")
response = model.generate_content([image, "Extract data"])
```

**优点：**

- 不用管显卡、不用管部署
- 推理速度快，稳定性好
- 多模态支持非常成熟

**不足：**

- 按 Token 计费
- 数据是否能上云，需要过合规

#### 2. 本地模型微调 + Ollama 推理

如果你**对数据隐私非常敏感**，那基本只能走本地路线。

需要注意的是：**Ollama 只负责推理，不负责训练。**

一个相对可行的流程是：

1. 用 Unsloth / Axolotl / LLaMA‑Factory
2. 选择支持视觉的模型（Llama‑3.2‑Vision、Qwen2‑VL 等）
3. 通过 QLoRA 做低成本微调
4. 合并权重并量化成 GGUF（llama.cpp）
5. 用 Modelfile 导入 Ollama

```
FROM ./your-custom-model.gguf
SYSTEM "You are a specialized invoice extractor. Always output JSON without extra text."
```

**优点：**

- 数据完全不出本地
- 没有持续调用成本
- 规则和行为可控

**现实成本：**

- 至少 24GB 显存会舒服很多
- CUDA / 量化 / 模型格式有学习成本
- 运维复杂度明显高于云方案

### 路线二：少样本提示（Few‑Shot Prompting）

如果你：

- 样本不多
- 想快速验证效果
- 或者发票版式相对固定

那我会**优先推荐 Few‑Shot Prompt**。

#### 1. 核心思路

不改模型权重，而是：

> **在 Prompt 里“教会”模型你想要什么样的输出。**

关键不是示例多，而是示例对。

#### 2. 一个推荐的 Prompt 结构

重点就一句话：**图片 + JSON 一定要成对。**

```
你是专业的发票数据提取专家，请严格按照示例 JSON 格式输出，不要添加任何解释。

示例 1：
[图片 A]
输出：{...JSON...}

示例 2：
[图片 B]
输出：{...JSON...}

现在请处理：
[目标发票图片]
输出：
```

这种方式对模型的“版式学习”非常友好。

代码示例：

```python
from google.generativeai import GenerativeModel
from PIL import Image

model = GenerativeModel("gemini-1.5-pro")

image_example = Image.open("example_invoice.jpg")
image_target = Image.open("target_invoice.jpg")

response = model.generate_content([
    "你是专业的发票数据提取专家，只输出 JSON。",
    image_example,
    "示例 1 输出：{...JSON...}",
    image_target,
    "现在请处理目标发票"
])

print(response.text)
```

#### 3. 三种常见 Prompt 方案对比

| 方案 | 特点 | 实际效果 | 适合情况 |
|----|----|------|------|
| 纯文本 JSON 示例 | 省 Token | 格式准，视觉弱 | 发票极度统一 |
| 图片 + JSON（推荐） | Token 多一点 | 稳定性最好 | 复杂/真实场景 |
| 1 个示例 + 字段说明 | 折中方案 | 成本与效果平衡 | 通用业务 |

#### 4. 一个 Gemini 的省钱技巧

如果你用的是 Gemini 1.5 系列，可以：

- 把固定示例（图片 + JSON）放进上下文缓存
- 后续请求只传新发票

这样**示例不重复计费**，效果和成本都比较友好。

## 一些实践层面的优化建议

### 1. 数据别只放“好样本”

无论微调还是 Few‑Shot，都建议加一些：

- 模糊发票
- 残缺照片
- 甚至非发票图片

并明确告诉模型：

> 识别不了就返回 null / error

这比“强行猜一个答案”要安全得多。

### 2. 永远在 System Prompt 里强调格式

比如：

> **仅输出 JSON，不要任何多余文本。**

这句话的性价比极高。

### 3. 下游一定要做校验

模型再牛，也要：

- 校验日期格式
- 校验数值范围
- 防止空字段

把模型当成一个**高概率正确、但不是绝对可信的组件**，系统会更健康。

## 结语

整体跑下来，我的体会是：

- **短期落地最快**：Few‑Shot + Gemini / GPT‑4o
- **长期规模化**：微调（云或本地）
- **真正的关键**：始终让模型“看图学结构”，而不是只学 JSON 格式

好了，希望对大家有帮助。
