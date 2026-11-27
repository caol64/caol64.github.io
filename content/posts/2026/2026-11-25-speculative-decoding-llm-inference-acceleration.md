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
---

![](imgs/posts/2026-11-25-speculative-decoding-llm-inference-acceleration/hero.webp)

本地跑模型的人都见过这个画面：`nvidia-smi` 里 GPU 利用率 100%，Token 却一个一个往外蹦。

大多数人会以为算力不够。实际上 GPU 根本没在算，它在**等**——等权重从显存搬过来。推测解码（Speculative Decoding）就是拿这段等待时间做文章：让小模型先猜几个词，大模型一次核完。

## 为什么 GPU 闲着还那么慢

大模型生成文字是一个词一个词来的：

```
Token 1 → Token 2 → Token 3 → Token 4 → ...
```

每生成一个词，都要把几十 GB 的权重从头读一遍。真正用于计算的时间只占很小一截，剩下全花在把权重从显存搬进计算单元上。所以吞吐量的天花板不是 GPU 每秒能算多少次，而是显存每秒能搬多少字节。

`nvidia-smi` 的 “GPU-Util” 怎么还是 100%？因为它统计的是“这段时间里有没有 kernel 在跑”，不是“计算单元有多忙”。一个全程在等显存的 kernel，照样算 100%。

> 所以看利用率判断不了瓶颈，要看每秒能吐出几个 Token。

反过来，GPU 很擅长同时处理一批 Token：输入从 1 个变成 8 个，权重要读的量几乎不变，多出来的计算开销可以忽略不计。**推测解码就是把这批“几乎免费”的位置用起来。**

## 小模型猜，大模型核

设目标模型 30B、草稿模型 1B，每轮让它先猜 5 个，然后：

1. 小模型自回归，快速猜出接下来 5 个 Token。
2. 这 5 个候选连同上下文，一次性丢给大模型跑一次前向。
3. 大模型为每个位置算出自己的分布，从左往右逐个比对。
4. 遇到第一个不认同的位置就停下，用大模型自己的 Token 替换，后面的候选全部作废。
5. 不管收没收到底，大模型在下一个位置顺带算出的 Token 也直接收下，这叫**额外奖励 Token**（bonus token）。

两种结局放在一起看：

![情况 A：中途被拒——第一个候选就被拒，纠正出 jumps，后面全部作废，本轮推进 1 个](imgs/posts/2026-11-25-speculative-decoding-llm-inference-acceleration/speculation-round-partial.svg)

![情况 B：全部接受——5 个候选全中，第 6 个位置再收一个奖励 Token The，本轮推进 6 个](imgs/posts/2026-11-25-speculative-decoding-llm-inference-acceleration/speculation-round-all-accepted.svg)

同样是猜 5 个，结果从 1 个到 6 个不等，取决于草稿撞上大模型思路的次数。但不管一轮收几个，大模型只读了一遍权重，这就是省时间的地方。

### 验证到底怎么判断收不收

`temperature = 0` 时最简单：草稿和大模型的 top-1 一致就收，否则换成大模型的 top-1。

概率采样时不能只看“一不一样”，得用拒绝采样。设大模型给草稿 Token 的概率是 p，草稿模型给它的是 q：

- 以 `min(1, p/q)` 的概率接受；
- 拒绝时不是重新从 p 里抽，而是从残差分布 `norm(max(0, p − q))` 里抽。

```python
import numpy as np

# q 草稿分布、p 目标分布，都在同一个词表上归一化过
x = rng.choice(len(p), p=q)                  # 草稿提出的 Token
ratio = p[x] / max(q[x], 1e-9)
if rng.random() < min(1.0, ratio):
    token = x                                 # 接受
else:
    residual = np.maximum(0.0, p - q)
    token = rng.choice(len(p), p=residual / residual.sum())
```

关键在于那个残差分布：加上它之后，最终输出的分布和“老老实实用大模型采样”完全一致。草稿模型只在“大模型本来也会这么说”的地方帮忙省时间，不会改变大模型想说的话。

## 无损，但不是每次结果都一样

vLLM 官方称之“算法层面无损”，靠两套测试兜底：拒绝采样器的分布收敛性，以及贪心采样下开不开推测解码结果一致。逻辑上确实没有偷工减料。

但它不等于每次跑出来一模一样。浮点精度、批大小变化、logprobs 本身不稳定，都会让两次运行的结果有细微差别。原因是批量验证和逐个生成走的是不同的矩阵运算路径，舍入方式不同；两个候选分数接近时，一点误差就能让贪心结果分叉。

> 质量不会掉，但别指望 bit 级复现。做评测要控制变量，基线跟着一起重跑。

## 在 vLLM 里开启

手头没有专门训练的草稿模型，从 Draft Model 或 N-gram 起步最快：

```bash
# 草稿模型配对：同架构、同分词器的小号模型
vllm serve Qwen/Qwen3-32B \
  --speculative-config '{
    "method": "draft_model",
    "model": "Qwen/Qwen3-0.6B",
    "num_speculative_tokens": 5
  }'

# 零成本方案：从请求上下文里找重复片段，适合改代码、补文档
vllm serve Qwen/Qwen3-32B \
  --speculative-config '{
    "method": "ngram",
    "num_speculative_tokens": 4,
    "prompt_lookup_min": 2,
    "prompt_lookup_max": 5
  }'
```

`num_speculative_tokens` 就是每轮最多猜几个。

选草稿模型有两个绕不开的问题：

**词表要对齐。** 最省事的配法是同架构、同 tokenizer 的小号模型。vLLM 新版本支持 `use_heterogeneous_vocab` 配对不同词表，它在启动时建立词级交集、把草稿的 logits 限制在共有 Token 上，但目前只能配 `draft_model` 方法，且只支持贪心草稿采样。

**草稿模型不能太重。** 它每轮都要先跑 5 次，延迟直接叠加在总耗时上。LM Studio 给的经验上限是主模型的 1/5 到 1/4：7B 配 ≤1B、14B 配 ≤3B、32B 配 ≤7B。超了这个量级，你就是在替草稿模型打工。

其他可用方法按代价从轻到重排：N-gram（白嫖）、Suffix Decoding（从历史请求的回答里找续写，对 Agent 循环很友好）、MTP（目标模型自带多 Token 预测，原生支持时首选）、EAGLE（复用目标模型隐藏状态，降延迟效果最好）。

## 打开之后先看这几个数

```bash
vllm serve Qwen/Qwen3-32B \
  --speculative-config '{"method": "draft_model", "model": "Qwen/Qwen3-0.6B", "num_speculative_tokens": 5}' \
  --per-request-spec-decode-metrics summary
```

每个响应都会多一段（示意，字段有删减）：

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

- `mean_acceptance_length`：每次验证平均推进几个 Token，含奖励 Token，等于 1 + 接受数 / 轮数，上限是 `num_speculative_tokens + 1`。
- `draft_acceptance_rate`：猜出来的 Token 有多少被接受。
- 两个数能互相核对：100 轮接受 220 个，长度 = 1 + 220/100 = 3.2；提满 5 个共 500 个，接受率 = 220/500 = 0.44。

**接受长度 3.2 不等于快 3.2 倍。** 一轮的真实耗时是“草稿跑 k 次 + 大模型验证一次”：

```
提速 ≈ L × T / (T_verify + k × T_draft)
```

L 是接受长度，T 是大模型普通一步的耗时。把它画出来看更直观：

![接受长度与真实提速的关系](imgs/posts/2026-11-25-speculative-decoding-llm-inference-acceleration/acceptance-vs-speedup.svg)

草稿一步只有大模型的 1/15 时，约 2.2 倍；慢到 1/5，就只剩 1.6 倍。接受率完全一样，草稿慢一点收益就少一半。曲线在 1/2 附近跌破 1x —— 那已经不是“提效不明显”，而是负优化。

再看两个实操细节：

- 流式响应的 `metrics` 挂在最后一个 usage chunk 上，必须开 `stream_options.include_usage`（或服务端加 `--enable-force-include-usage`），否则拿不到。
- 做 JSON、工具调用这类结构化输出时，部分草稿会先被语法约束剔除，它们算在 `num_draft_tokens` 里，不算进 `num_verified_draft_tokens`。看接受率时两个一起看。
- 需要知道“是前两个位置准还是一开始就崩”，把 `--per-request-spec-decode-metrics` 换成 `detailed`，会多出每步的接受数组。这组指标标着 experimental，依赖它请锁版本。

## 什么时候值得开

官方给的适用范围是中低 QPS、延迟敏感、受显存带宽限制的负载。落到本地 Agent 上，重点测这几种：

- **代码生成与重构**：结构高度可预测，接受率高。
- **Agent 工具调用**：参数格式固定，猜得准。
- **长文输出**：Token 基数大，延迟收益被成倍放大。
- **端侧推理**：单用户、无并发，正好踩在最舒服的区间。
- **重复型任务**：改代码、自反思循环、多智能体共享上下文，用 Suffix 或 N-gram 往往比外挂小模型更划算。

> 反过来说，创意写作这类“下一句有一百种合理写法”的任务，小模型猜不中，别对它抱期望。

三种情况会让它变成负优化：草稿太慢吃掉收益、接受率低到 0.2 以下、草稿模型的权重和 KV Cache 挤掉了本跑并发请求的显存。最后一种最隐蔽——批大小为 1 时多猜几个几乎免费，批大小到 256 时，每次拒绝都在烧算力。

### 自适应验证：让引擎自己决定猜几个

`enable_adaptive_verification` 会给每个候选位置估一个“存活概率”，在预算内挑概率最高的位置验证，而不是每轮都验证满。好处是一套配置能覆盖整个负载区间，不用随并发反复调 `num_speculative_tokens`。

代价是它默认关闭，主要支持 EAGLE、MTP、DFlash、DSpark 这类模型类草稿和 Suffix Decoding（N-gram 和独立草稿模型不在支持列表），并且需要全量 CUDA Graph，不支持 LoRA 和流水线并行。

## 本地工具怎么开

Linux + NVIDIA 用 vLLM 最方便，其它环境各有对应开关：

| 工具 | 怎么开 | 适合谁 |
| --- | --- | --- |
| llama.cpp | `-md 草稿.gguf`；或 `--spec-type ngram-mod` | 想精细调参 |
| Ollama | 用带 MTP 的模型标签，或 Modelfile 里写 `DRAFT` + `ollama create --experimental` | Mac 用户 |
| LM Studio | 侧边栏选一个同词表的小模型当草稿 | 先体验 |
| MLX-LM | `--draft-model` + `--num-draft-tokens` | Apple Silicon |

```bash
# 草稿配对；-ngld 控制草稿放多少层进显存，避免挤占主模型的显存
llama-server -m Qwen3-32B-Q4_K_M.gguf -md Qwen3-0.6B-Q8_0.gguf \
  --spec-draft-n-max 5 -ngld 99 -ctkd q8_0

# 改代码、重构：不需要草稿模型
llama-server -m model.gguf --spec-type ngram-mod
```

llama.cpp 的 `-ctkd` / `-ctvd` 可以量化草稿模型的 KV Cache，这个参数就是专门解决“草稿把显存吃光”的问题。

## 三个数一起量，才有结论

只有 ITL（Token 间延迟）明显下降、吞吐不比基线差、显存代价可以接受，三条同时满足，才算真的变快了。只看接受率是典型的局部最优：接受率 0.8，显存被草稿模型吃光、并发腰斩，体验反而更差。

量的时候用同一批真实 prompt，顺序建议这样：

![开启顺序：先免费方案，再外挂模型，最后调参](imgs/posts/2026-11-25-speculative-decoding-llm-inference-acceleration/tuning-order.svg)

0. 先跑不开推测解码的基线。vLLM 自带 `examples/features/speculative_decoding/spec_decode_offline.py`，直接用。
1. 用 N-gram 或 Suffix 试免费的午餐。
2. 上 Draft Model 对比；目标模型原生支持 MTP 就直接试 MTP。
3. 接受率还是不行，再换 EAGLE 这类专门训练的草稿头。
4. 最后才是调 `num_speculative_tokens` 和开自适应验证。

参考：[vLLM Speculative Decoding](https://docs.vllm.ai/en/v0.32.0/features/speculative_decoding/)、[Per-Request Acceptance Metrics](https://docs.vllm.ai/en/latest/features/speculative_decoding/acceptance_metrics/)、[Adaptive Verification](https://docs.vllm.ai/en/latest/features/speculative_decoding/adaptive_verification/)、[Suffix Decoding](https://docs.vllm.ai/en/latest/features/speculative_decoding/suffix/)、[llama.cpp Speculative Decoding](https://github.com/ggml-org/llama.cpp/blob/master/docs/speculative.md)、[LM Studio Speculative Decoding](https://lmstudio.ai/docs/app/advanced/speculative-decoding)。

---

欢迎关注我的公众号，第一时间获取最新文章。

![](https://babyno.top/imgs/qrcode.jpg)
