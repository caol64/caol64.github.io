---
author: "路边的阿不"
title: LLM推理加速：推测解码
slug: speculative-decoding-llm-inference-acceleration
description: ""
date: 2026-11-25 16:43:39
draft: false
ShowToc: true
TocOpen: true
tags:
  - vLLM
  - 推测解码
  - LLM推理
  - Agents
categories:
  - AI入局
cover:
  image: "imgs/posts/2026-11-25-speculative-decoding-llm-inference-acceleration/hero.webp"
  alt: "小模型打草稿，大模型验证：推测解码"
  hidden: false
---

本地跑模型时，最容易被误诊的问题就是“慢”。

`nvidia-smi` 一看，GPU 利用率拉满，显存也占得满满当当，可 Token 还是一个一个往外蹦。小模型如此，换成 70B 的大模型更是如此，而且越用 GPU 跑，越能感觉到那种“明明在干活，就是快不起来”的憋屈。

这篇聊聊推测解码（Speculative Decoding）：它是本地推理加速里性价比最高、也最值得自己动手测一测的技术之一。

## 为什么加载到 GPU 了还是慢？

先看自回归生成本身：

```
Token 1 → Token 2 → Token 3 → Token 4 → ...
```

每吐出一个 Token，都要把整个模型完整跑一遍。对大模型来说，这意味着把权重从显存里重新读一遍。

> 瓶颈不在算力，而在显存带宽。

生成阶段每次只处理一个 Token，矩阵乘法的形状小得可怜，GPU 的计算单元根本喂不饱，大部分时间都在等数据从显存搬到计算单元。

那为什么 `nvidia-smi` 显示利用率很高？因为它的“GPU-Util”统计的是**采样周期内有 kernel 在运行的时间占比**，不是计算单元有多忙。一个几乎全在等显存的 kernel，只要它在跑，利用率就照样算 100%。所以“利用率高”这件事很有欺骗性：它只说明 **GPU 一直有活**，不说明**算力被用满了**。

而 GPU 恰恰擅长另一件事：**一次处理一批 Token**。输入从 1 个变成 5 个、8 个，权重要读的量几乎不变，多出来的只是些微不足道的算力开销。

推测解码就是拿这个“免费额度”做文章。

## 小模型打草稿，大模型批改

核心思想一句话：**小模型猜，大模型核**。

假设目标模型 30B，另配一个 1B 的草稿模型。一轮的流程是这样：

1. 小模型自回归，快速猜出接下来 5 个 Token。
2. 把这 5 个候选连同已有上下文，一次性塞给大模型跑一次前向。
3. 大模型为这 5 个位置各算出一个概率分布，从左到右逐个决定收不收。
4. 某个位置被拒绝，就在这里换上一个新 Token，后面的候选全部作废；如果 5 个全被接受，大模型在第 6 个位置算出的那个 Token 也顺手收下，这就是**额外奖励 Token（bonus token）**。
5. 从新位置开始下一轮。

所以每一轮**至少**推进 1 个 Token（第一个就被拒，也有纠正出来的那个），**至多**推进 5 + 1 = 6 个。

示意一：中途被拒

```
已有上下文：The quick brown fox

Draft Model 猜：   runs   over   the   lazy   dog
Target 验证：      ✗ 它自己更倾向 jumps

Accepted：         （无）
Correction：       jumps        ← 替换被拒的 runs
作废：             over the lazy dog

本轮推进 1 个 Token，下一轮从 “The quick brown fox jumps” 继续
```

示意二：全部接受

```
已有上下文：The quick brown fox jumps

Draft Model 猜：   over   the   lazy   dog   .
Target 验证：      ✓      ✓     ✓      ✓     ✓

Accepted：         over the lazy dog .
Bonus：            The          ← 目标模型在第 6 个位置顺手算出的 Token

本轮推进 6 个 Token
```

> 小模型把 5 次串行的“读一遍 30B 权重”压成了 1 次，大模型只在最后做一次批量验证 → 显存带宽的访问次数减少 → 每个 Token 的平均延迟下降。

### 第 3、4 步到底怎么“核”

**贪心解码（temperature = 0）** 最简单：草稿 Token 和大模型的 argmax 一致就收，不一致就拒，并换成大模型的 argmax。

**概率采样**时不是比对“一不一样”，而是标准的拒绝采样。记目标模型在该位置给草稿 Token x 的概率为 p(x)，草稿模型给它的概率为 q(x)：

- 以 **min(1, p(x) / q(x))** 的概率接受 x；
- 一旦拒绝，新 Token **不是**直接从 p 里再抽一个，而是从**残差分布** norm(max(0, p − q)) 里抽。

正是这个残差分布，保证最终输出的分布**严格等于目标模型自己的分布**：草稿模型只在“大模型也会这么说”的地方省钱，而不改变它想说什么。贪心解码只是它在 temperature = 0 时的特例。

## “无损”这个词要拆开看

vLLM 官方对此的表述是“算法层面的无损”：它用拒绝采样器的收敛性测试，以及“贪心采样下开不开推测解码结果一致”的端到端测试来保证。换句话说，逻辑上没有偷工减料。

但“理论无损”不等于“每次跑出来一模一样”。文档里也承认了几处偏差来源：

* **浮点精度**：硬件数值精度的差异会带来概率分布上的细微扰动。
* **批大小与数值稳定性**：并发批量变了，logprobs 和输出概率就可能跟着抖。
* **logprobs 本身**：vLLM 目前不承诺跨次运行稳定。

背后的原因之一是：批量验证和逐个生成走的是不同的矩阵运算路径，舍入方式本来就不同。两个候选几乎打平时，一点舍入差异就可能让贪心结果分叉。

> 质量不会掉，但别指望 bit 级可复现。对做评测、跑对比的人来说，这意味着要控制变量，把基线一起重跑，而不是拿历史结果直接对。

反过来，如果贪心输出**早早就**分叉、而且分叉点上两个候选并不接近，那就不是数值问题，更可能是实现 bug，值得报给上游。（MLX-LM 就出现过超出滑动窗口后被拒草稿没从 KV Cache 撤回的问题。）

## 在 vLLM 里怎么用

vLLM 现在的方法不止一种，可以先看一眼选型：

| 方法 | 特点 |
| --- | --- |
| Draft Model | 独立小模型预测，最简单直接 |
| EAGLE | 复用目标模型的隐藏状态，用轻量头预测，属于高增益一档 |
| MTP | 用模型自带的 Multi-Token Prediction 能力，不用额外挂模型；目标模型原生支持时首选 |
| N-gram | 从当前请求已有文本里找重复片段，零成本，适合复制粘贴型任务 |
| Suffix Decoding | 不仅匹配当前请求，还能从**之前其他请求的回答**里找候选，按出现频率挑续写，对代码编辑、Agent 循环特别友好 |

官方文档给的定性结论：模型类方法（EAGLE、MTP、Draft Model、PARD、MLP）降延迟最好，低 QPS 下都属于“高增益”档，没有排出绝对先后；N-gram 和 Suffix 更轻，不需要额外的草稿模型。

手头没有专门训练的草稿模型，可以从 Draft Model 或 N-gram 起步：

```bash
vllm serve your-target-model \
  --speculative-config '{
    "method": "draft_model",
    "model": "your-draft-model",
    "num_speculative_tokens": 5
  }'
```

`num_speculative_tokens` 就是每轮最多提出几个候选。

N-gram 的写法：

```bash
vllm serve your-target-model \
  --speculative-config '{
    "method": "ngram",
    "num_speculative_tokens": 4,
    "prompt_lookup_min": 2,
    "prompt_lookup_max": 5
  }'
```

### 选草稿模型的两个坑

* **词表必须对齐**：最简单的配对是同架构、同分词器的小号模型。vLLM 新版本支持 `use_heterogeneous_vocab`，允许不同分词器的模型配对：它在初始化时建立词级交集，把草稿模型的 logits 限制在共有 Token 上再采样。但这条路**只能配合 `method: "draft_model"` 使用**，而且目前只支持贪心草稿采样，概率采样还不支持。
* **草稿模型不能太慢**：草稿模型的延迟直接叠加在每轮耗时上，每轮要先跑 k 次草稿前向。草稿和目标的体量差得越大越好。LM Studio 给过一组经验上限：7B 主模型配 ≤1B，14B 配 ≤3B，32B 配 ≤7B。超过这个量级，基本就是在给草稿模型打工。这些都是经验值，最终以实测为准。

### Suffix Decoding 的两个注意点

* **语料是共享的**：已完成请求的回答会进入一个 GPU 语料库（默认 100 万 Token，先进先出），而且**不区分 `cache_salt` 和 LoRA 适配器**，所有请求都能从里面打草稿。草稿不会改变输出分布，但接受了多少会体现在速度上。多租户、请求之间必须互不影响的场景，设 `suffix_decoding_corpus_tokens: 0` 关掉它。
* **高并发下可能反而更慢**：Suffix 每轮固定提出 `num_speculative_tokens` 个候选，匹配不上的位置用上一个 Token 凑数，不开自适应验证时每个位置都要验证。GPU 一旦不再受带宽限制，这些凑数的位置就是纯开销，官方文档明说此时它可能比不开推测解码还慢。高并发用 Suffix，记得配合自适应验证。

另外，旧文档里控制推测深度的 `suffix_decoding_max_spec_factor`、`suffix_decoding_min_token_prob` 已经废弃、不再生效，别再照着调。

## 怎么判断它到底有没有变快

别只看 GPU 利用率。推测解码是否划算，先看**接受率**，再看**真实延迟**。

vLLM 0.32 支持按请求收集推测解码指标：

```bash
vllm serve your-target-model \
  --speculative-config '{
    "method": "draft_model",
    "model": "your-draft-model",
    "num_speculative_tokens": 5
  }' \
  --per-request-spec-decode-metrics summary
```

响应里会多出一段（以下为示意，字段有删减）：

```json
{
  "metrics": {
    "speculative_decoding": {
      "mean_acceptance_length": 3.2,
      "draft_acceptance_rate": 0.44,
      "num_spec_steps": 100,
      "num_accepted_draft_tokens": 220,
      "num_draft_tokens": 500
    }
  }
}
```

几个字段的含义：

* `mean_acceptance_length`：每次验证平均推进几个 Token，**包含额外奖励的那个 Token**，等于 1 + 接受的草稿数 / 验证轮数。下限 1.0，上限 `num_speculative_tokens + 1`。
* `draft_acceptance_rate`：草稿提出的 Token 里有多少被接受，等于接受的草稿数 / 提出的草稿数。
* `num_spec_steps`：这一请求一共验证了多少轮。

两个数可以互相核对：上面 100 轮共接受 220 个草稿，平均接受长度 = 1 + 220/100 = 3.2；每轮提满 5 个、共 500 个，接受率 = 220/500 = 0.44。

平均接受长度 3.2，意味着大模型每做一次前向就能往前推 3.2 个 Token，而普通解码是 1 个。

### 接受长度 3.2 ≠ 快 3.2 倍

这一步最容易被跳过。每轮的真实耗时，是“草稿模型跑 k 次”加“大模型验证 1 次”，所以粗略估算：

$$
\text{提速} \approx \frac{L \times T_{\text{target}}}{T_{\text{verify}} + k \times T_{\text{draft}}}
$$

* L：平均接受长度
* T_target：大模型普通解码一步的耗时
* T_verify：大模型一次验证 k+1 个位置的耗时（带宽受限时接近 T_target，但会略高）
* T_draft：草稿模型一步的耗时

举个例子：L = 3.2，k = 5，T_verify ≈ 1.1 × T_target，草稿模型每步只有目标的 1/15。代进去约 3.2 / (1.1 + 5/15) ≈ **2.2 倍**。如果草稿模型每步是目标的 1/4，就只剩 3.2 / (1.1 + 1.25) ≈ **1.4 倍**。接受率一模一样，草稿慢一点，收益就少了一大截。

所以接受率只是必要条件，最后还是要拿 ITL（Token 间延迟）说话。

### 更细的指标与流式响应

`summary` 之外还有 `detailed` 级别，会给出每一步的 `per_step_accepted` / `per_step_drafted` / `per_step_verified` 数组，便于定位“是前两个位置猜得准，还是一开始就崩”。注意这组指标标注为 experimental，结构未来可能变，依赖它的时候记得锁版本号。

还有一个容易忽略的地方：流式响应下，这段 `metrics` 挂在最后一个 usage chunk 上，必须开启 `stream_options.include_usage`（或服务端加 `--enable-force-include-usage`），否则你永远拿不到它。

如果你在做工具调用、JSON 输出这类**结构化生成**，还要知道：部分草稿 Token 会在送进大模型之前就被语法约束剔除，它们算在 `num_draft_tokens` 里，却不算在 `num_verified_draft_tokens` 里。看接受率时，把这两个数一起看。

## 什么时候最值得用

官方给出的适用范围很明确：**中低 QPS、延迟敏感、受显存带宽限制**的负载。它不是万能加速键，也不保证吞吐提升。

对本地 Agent，重点测这几类：

* **代码生成**：连续输出结构相似的代码，模式可预测，接受率高。
* **长文本生成**：Token 数量大，延迟收益被成倍放大。
* **Agent 工具调用**：生成较长的结构化参数或调用计划，格式约束强，猜得准（注意上面说的语法剔除）。
* **端侧推理**：单用户、无并发、带宽吃紧，正好踩在最合适的区间。
* **重复型工作**：修改代码、多轮自反思、多智能体共享上下文。这类场景里，Suffix Decoding 或 N-gram 往往比另挂一个小模型更划算。

反过来，**创意写作**这类“下一句有一百种合理写法”的任务，小模型很难猜中大模型的选择，接受率通常偏低，别对它抱太大期望。

## 什么时候会适得其反

推测解码不是免费的。三种典型翻车：

* **草稿模型的延迟吃掉收益**：每轮验证前要先花时间打草稿，草稿越重，净收益越薄（见上面的估算）。
* **接受率太低**：提出 5 个只收 1 个，剩下的 4 个都是白跑的算力。
* **占用了一部分本属于 KV Cache 的显存**：草稿模型要权重，还要自己的 KV（每请求一份，随上下文和并发一起涨）。分给目标模型的缓存变少，能同时跑的请求变少，吞吐可能不升反降。

第三点最隐蔽。高并发时，草稿 Token 开始和真实 Token 抢同一批计算资源，每被拒绝一个就是纯亏损。vLLM 的文档写得很直白：批大小为 1 时 GPU 受带宽限制、算力有余，“多猜几个几乎免费”；批大小到 256 时，这笔账就完全不同了。

这种随负载移动的交叉点，也让“固定一个 `num_speculative_tokens`”变得很难调对。

### 一个顺手的解法：自适应验证

vLLM 提供了 `enable_adaptive_verification`，让引擎**按步决定验证多少**：给每个候选位置算一个“存活概率”（该位置及之前各位置被接受概率的连乘估计），在全局预算内挑概率最高的位置验证。不同请求之间也会互相竞争：一个很有把握的请求的第 5 个位置，可能排在一个没把握的请求的第 1 个位置前面。预算由启动时对每种形状做性能剖析得到的成本模型给出，目标是最大化每秒期望接受的 Token 数。

好处很实用：一套配置能覆盖整个负载区间，不用按部署环境反复调 `num_speculative_tokens`。

代价也要看清：

* **默认关闭**，需要在 speculative-config 里显式打开。
* **适用范围有限**：支持模型类草稿方法（EAGLE、MTP、DFlash、DSpark 等）和 Suffix Decoding；**N-gram 不在支持列表里**，独立的 Draft Model 也没有被明确列出。官方主页面的选型表甚至写着“目前仅 DSpark”，各页面口径不一，用之前在你的版本上确认一下。
* 对注意力后端有要求，必须用全量 CUDA Graph（`--enforce-eager` 会在启动时被拒），不支持 LoRA 和流水线并行。

## 不用 vLLM，本地工具怎么开

vLLM 主要面向 Linux + NVIDIA 的服务端部署。用消费级显卡或 Mac 的读者，可以在这些工具里找到对应的能力：

| 工具 | 怎么开 | 适合谁 |
| --- | --- | --- |
| **llama.cpp**（`llama-server`） | `-md 草稿.gguf`；或 `--spec-type ngram-mod` 等无草稿方案；也支持 EAGLE-3、DFlash、DSpark | 想精细调参的 NVIDIA / AMD / Mac 用户，方法最全 |
| **Ollama** | 用带 MTP 的现成模型标签，或在 Modelfile 里写 `DRAFT` + `ollama create --experimental` | Mac 用户、想省事；新版本会自动选草稿长度 |
| **LM Studio** | 侧边栏选一个同词表的小模型当草稿 | 只想先体验效果 |
| **MLX-LM** | `--draft-model` + `--num-draft-tokens` | Apple Silicon 原生；长上下文 + 滑动窗口模型先确认版本 |

llama.cpp 有两个参数正好对应上文的“显存被草稿模型挤占”：`-ngld` 控制草稿模型放多少层到显存，`-ctkd` / `-ctvd` 可以量化草稿模型的 KV Cache。

```bash
# 草稿模型配对
llama-server -m Qwen3-32B-Q4_K_M.gguf -md Qwen3-0.6B-Q8_0.gguf --spec-draft-n-max 5

# 改代码、重构这类重复内容多的任务：不需要草稿模型
llama-server -m model.gguf --spec-type ngram-mod
```

参数名各不相同，但下面的测量方法是通用的。

## 收尾：别只比接受率

判断该不该开，建议三项一起量，而且都用同一份真实流量：

1. **ITL（Token 间延迟）**：交互体验的直接体现。
2. **整体输出吞吐**：每秒能产出多少 Token，以及并发升高时的拐点。
3. **显存与 KV Cache 容量**：牺牲了多少并发槽位。

只比接受率是典型的“局部最优”：接受率 0.8，但显存被草稿模型吃光、并发腰斩，整体体验反而更差。

一个务实的顺序是：

0. **先测不开推测解码的基线**，同一模型、同一量化精度、同一批 prompt、同一采样参数。没有这一步，后面所有“提速”都没有参照物。vLLM 自带 `examples/features/speculative_decoding/spec_decode_offline.py` 和 benchmark CLI，可以直接用。
1. 用 N-gram 或 Suffix 这种零成本方案，看看重复型任务能捡多少便宜。
2. 上 Draft Model 对比；目标模型原生支持 MTP 的，直接试 MTP。
3. 接受率不理想，换 EAGLE 这类专门训练过的草稿头。
4. 最后才考虑调 `num_speculative_tokens`，以及在支持的方法上开自适应验证。

只有 ITL 明显下降、吞吐不比基线差、显存代价可以接受，三条同时满足，才算真的变快了。

参考：[vLLM Speculative Decoding 官方文档](https://docs.vllm.ai/en/v0.32.0/features/speculative_decoding/)、[Per-Request Acceptance Metrics](https://docs.vllm.ai/en/latest/features/speculative_decoding/acceptance_metrics/)、[Adaptive Verification](https://docs.vllm.ai/en/latest/features/speculative_decoding/adaptive_verification/)、[Suffix Decoding](https://docs.vllm.ai/en/latest/features/speculative_decoding/suffix/)、[llama.cpp Speculative Decoding](https://github.com/ggml-org/llama.cpp/blob/master/docs/speculative.md)、[LM Studio Speculative Decoding](https://lmstudio.ai/docs/app/advanced/speculative-decoding)。


---

欢迎关注我的公众号，第一时间获取最新文章。

![](https://babyno.top/imgs/qrcode.jpg)
