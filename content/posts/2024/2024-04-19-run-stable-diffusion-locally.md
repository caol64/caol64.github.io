---
author: "路边的阿不"
title: 在本地跑一个AI模型(5) - Stable Diffusion
slug: run-stable-diffusion-locally
description: "Learn how to run Stable Diffusion locally using `diffusers` and generate stunning images from text prompts. Discover the basics of text-to-image synthesis, including model selection, prompt engineering, and image generation. Get started with this comprehensive guide and unlock the power of AI-generated art."
date: 2024-04-19 10:17:47
draft: false
ShowToc: true
TocOpen: true
tags:
  - Stable Diffusion
categories:
  - AI
---
在之前的文章中，我们使用[`ollama`](https://babyno.top/tags/ollama/)在本地运行了大语言模型，它可以与你聊天，帮助你理解和生成文本内容。使用[`coqui-tts`](https://babyno.top/tags/coqui/)在本地运行了文本转语音模型，它可以将大语言模型生成的文字转换成语音，让你的应用更有趣。今天我们将要介绍`Stable Diffusion`，一种扩散神经网络的深度学习模型，使用它可以生成各种不可思议的图片。

我们使用的工具是`huggingface`提供的`diffusers`，一个在纯`python`环境下运行的库。废话不多说，我们进入今天的教程。

## 安装

`diffusers`目前不支持`python 3.12`，因此我们使用虚拟环境来安装。

```shell
# 使用3.10版本的python创建venv
/opt/homebrew/opt/python@3.10/libexec/bin/python3 -m venv .venv
# 激活venv
source .venv/bin/activate 
```

安装`diffusers`及其依赖：

```shell
pip install diffusers accelerate transformers
```

## 下载模型

和之前文章里介绍的一样，模型我们还是选择自己下载。你可以到`huggingface`网站下载已经训练好的模型，比如[`runwayml/stable-diffusion-v1-5`](https://huggingface.co/runwayml/stable-diffusion-v1-5)。

> Tips：你可以使用如下命令下载`huggingface`上的模型：

```shell
git lfs install
git clone git@hf.co:<MODEL ID> # example: git clone git@hf.co:bigscience/bloom
```

此外，`diffusers`支持`AUTOMATIC1111`的模型，因此你可以去[Civitai](https://civitai.com/)下载各种`CheckPoint`和`LoRA`。本文使用的模型就是`Civitai`的[dreamshaper](https://civitai.com/models/112902/dreamshaper-xl)。选择模型时要注意以下几点：

- 根据自己的喜好选择模型的风格，比如“写实”、“动漫”或者“魔幻”
- 模型有一个属性是“基础模型”，如下图。对应的诸如`SD 1.5`、`SDXL 1.0`、`SDXL Turbo`等等。`SD`系列只能生成`512x512`的图片，`SDXL`系列可以生成`1024x1024`及以上的图片。而`Turbo`系列可以将生成所需的时间缩短。根据自己的电脑配置选择合适的模型吧。

![Civitai Model](imgs/posts/2024-04-19-run-stable-diffusion-locally/1.jpg)

选择好模型后，就点击`Download`下载吧。

## 加载模型

如果你的模型是单个`safetensors`格式的，使用`from_single_file`加载，如果是从`huggingface`下载的预训练模型，使用`from_pretrained`加载。此外如果你的模型是`SDXL`，使用`StableDiffusionXLPipeline`，因此`dreamshaperXL`模型加载的代码如下：

```python
from diffusers import StableDiffusionXLPipeline

pipe = StableDiffusionXLPipeline.from_single_file("your/path/dreamshaperXL_v21TurboDPMSDE.safetensors")
```

## 使用GPU运行

`windows`用户可以根据如下代码判断自己的电脑能否进行`GPU`推理：

```python
device = "cuda" if torch.cuda.is_available() else "cpu"
```

`MAC`的`M1`和`M2`芯片可以使用如下代码：

```python
device = 'mps'
```

然后：

```python
pipe = pipe.to(device)
```

## 调度器

`diffusers`的调度器对应的是`AUTOMATIC1111`中的`Sampling method`，它对获得高质量的图像至关重要。`Sampling method`和`diffusers`的调度器的对应关系可以参照[此处](https://huggingface.co/docs/diffusers/v0.27.2/en/api/schedulers/overview)。

![Diffusers Scheduler](imgs/posts/2024-04-19-run-stable-diffusion-locally/2.jpg)

至于如何选择调度器，在模型的详情页可以找到作者给出的建议，比如：

![](imgs/posts/2024-04-19-run-stable-diffusion-locally/3.jpg)

这里作者建议的是`DPM++ SDE Karras`，可以参照上面的对应表找到对应的调度器为`DPMSolverSinglestepScheduler`，初始化参数为`use_karras_sigmas=True`。

调度器代码如下：

```python
pipe.scheduler = DPMSolverSinglestepScheduler.from_config(pipe.scheduler.config, use_karras_sigmas=True)
```

## 提示词

提示词的质量对最终生成的图像质量有很大的影响。提示词的写法这里不做展开，提示词的例子：

```python
prompt = "masterpiece, cat wizard, gandalf, lord of the rings, detailed, fantasy, cute, adorable, Pixar, Disney"

negative_prompt = "worst quality, low quality, normal quality, lowres, low details, oversaturated, undersaturated, overexposed, underexposed"
```

提示词目前有77个长度的限制，要突破这个限制，可以将提示词向量化，以下是代码例子：

```shell
pip install compel
```

```python
compel = Compel(
    tokenizer=[pipe.tokenizer, pipe.tokenizer_2] ,
    text_encoder=[pipe.text_encoder, pipe.text_encoder_2],
    returned_embeddings_type=ReturnedEmbeddingsType.PENULTIMATE_HIDDEN_STATES_NON_NORMALIZED,
    requires_pooled=[False, True]
)

conditioning, pooled = compel(prompt)
negative_prompt_embeds, negative_pooled = compel(negative_prompt)
```

## 图片生成

```python
image = pipe(
            prompt_embeds = conditioning,
            pooled_prompt_embeds=pooled,
            negative_prompt_embeds = negative_prompt_embeds,
            negative_pooled_prompt_embeds=negative_pooled,
            # height=800,
            # width=512,
            num_inference_steps=6,
            guidance_scale=2,
            strength=0.5
        ).images[0]

image.save("data/out.jpg")
```

这里对图片生成质量有影响的几个参数是`guidance_scale`和`num_inference_steps`，这两个参数分别对应`AUTOMATIC1111`里的`CFG Scale`和`Sampling steps`。你也可以在模型的详情页找到作者给出的建议：

![](imgs/posts/2024-04-19-run-stable-diffusion-locally/4.jpg)

至此，运行代码，你应该可以获得模型生成的图片了。

## 总结

本文介绍了使用`diffusers`在本地运行`Stable Diffusion`的方法，并进行了一次基本的`Text to Image`的实践。下篇文章将继续介绍`diffusers`使用`LoRA`，`ControlNet`和`Adapter`生成高级图片的实践。