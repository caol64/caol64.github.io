---
author: "路边的阿不"
title: 在本地跑一个AI模型(6) - Stable Diffusion模型微调
slug: run-stable-diffusion-locally-with-lora
description: "Learn how to fine-tune your local Stable Diffusion model with LoRA, a low-rank adaptation technique that adds more details to generated images. Discover how to download and use pre-trained LoRA models from the community, and explore examples of using LoRA with different styles, such as Chinese illustration and pixel art."
date: 2024-04-22 11:53:55
draft: false
ShowToc: true
TocOpen: true
tags:
  - Stable-Diffusion
  - AI
categories:
  - 教程
---
本文是[`Stable Diffusion`系列](https://babyno.top/tags/stable-diffusion/)第二篇。

在[上一篇文章中](https://babyno.top/posts/2024/04/run-stable-diffusion-locally/)，我们介绍了在本地使用`Diffusers`运行`Stable Diffusion`模型，并使用`Text to Image`技术使用提示词让`AI`生成了图片。在本篇文章中，我们将介绍如何使用社区提供的`LoRA`对模型的输出进行微调。

## LoRA

`LoRA（Low-Rank Adaptation）`是模型训练中的一种模型微调技术，用于在少量数据上快速训练新的模型。`LoRA`通过冻结基础模型的大部分参数，只对少量参数进行微调来实现这一点。`LoRA`可以使生成的图片增加更多的细节，例如生成特定的角色、动作、背景等。它可以基于现有模型而不必从头开始训练，优点是训练时间短、占用内存少。因此在`hugging face`和`Civitai`上可以下载到大量社区提供的`LoRA`。

今天我们示例的`LoRA`如下：
- [国风插画](https://civitai.com/models/120206/sdxlchinese-style-illustration)
- [电影照片](https://civitai.com/models/158945/sdxl-film-photography-style)
- [像素风格](https://civitai.com/models/120096/pixel-art-xl)
- [添加细节](https://civitai.com/models/122359/detail-tweaker-xl)

**请注意，在详情页关注`Base Model`选项，根据你运行的模型的`Base Model`选择合适的`LoRA`。比如，本文示例的模型为[`DreamShaper XL`](https://civitai.com/models/112902/dreamshaper-xl)，因此选择`LoRA`时应该对应的`Base Model`为`SDXL 1.0`。这在上一篇文章中有提到。**

## 基准图片

使用如下代码生成基准图片：

```python
from diffusers import StableDiffusionXLPipeline, DPMSolverSinglestepScheduler


device = 'mps'

pipe = StableDiffusionXLPipeline.from_single_file(
    "your/path/dreamshaperXL_v21TurboDPMSDE.safetensors",
    use_safetensors=True
).to(device)
pipe.scheduler = DPMSolverSinglestepScheduler.from_config(pipe.scheduler.config, use_karras_sigmas=True)
# Recommended if your computer has < 64 GB of RAM
pipe.enable_attention_slicing()

prompt = "masterpiece, 1girl, long hair, asian, sundress, cartoon, add detail"
negative_prompt = 'low quality, bad quality, sketches'

image = pipe(
    prompt,
    negative_prompt=negative_prompt,
    num_inference_steps=6,
    guidance_scale=2,
).images[0]
image.save("data/out.jpg")
```

注意提示词为`一个穿背心裙的长发亚洲女孩（卡通风格）`，其它参数在上一篇文章中有介绍。

![](imgs/posts/2024-04-22-run-stable-diffusion-locally-with-lora/out.jpg)

## 使用LoRA

首先在上面给出的网页上下载`safetensors`格式的`LoRA`文件，然后在代码中加上一行代码：

```python
pipe.load_lora_weights("your/path", weight_name="lora_name.safetensors")
```

这里有两个参数，前面一个参数是`LoRA`所在的目录，第二个参数是`LoRA`的文件名。

此外，阅读`LoRA`详情页，一般作者都会提供触发关键词，如果作者未提供关键词，可能该`LoRA`会自动触发，也可以尝试在提示词中添加这个`LoRA`的名字。

接下来我们看下分别使用这4个`LoRA`的效果。

### 国风插画

触发关键词：`guofeng`或`Chinese style`。

![](imgs/posts/2024-04-22-run-stable-diffusion-locally-with-lora/guofeng_out.jpg)

### 电影照片

触发关键词：无（自动触发）。

![](imgs/posts/2024-04-22-run-stable-diffusion-locally-with-lora/filem_photo_out.jpg)

### 像素风格

触发关键词：`pixel。

![](imgs/posts/2024-04-22-run-stable-diffusion-locally-with-lora/pixel_out.jpg)

### 添加细节

触发关键词：`(add detail)++++++++`。

![](imgs/posts/2024-04-22-run-stable-diffusion-locally-with-lora/add_detail_out.jpg)

## 总结

本文介绍了使用`LoRA`为本地`Stable Diffusion`模型进行微调，并介绍了如何下载和使用社区提供的已经训练好的`LoRA`。使用`LoRA`可以使生成的图片增加更多的细节。`LoRA`是`Text to Image`技术对提示词优化的一种补充。

下一篇将介绍如何使用`ControlNet`和`Adapter`，使用`Image to Image`和`Text to Image`技术相结合，使用“草稿”对`AI`生成的图像进行规划和约束。