---
author: 路边的阿不
title: 在本地跑一个AI模型(7) - 你打草稿，模型来画
slug: run-stable-diffusion-locally3-guide-image-generation
description: Unlock the power of guided image generation with Stable Diffusion! Learn how to control image output using ControlNet and Adapter technologies, and explore practical examples and comparisons of various detectors and adapters. Discover how to generate high-quality images that meet your specific requirements.
date: 2024-04-22 14:36:03
draft: false
ShowToc: true
TocOpen: true
tags:
  - Stable-Diffusion
  - AI
categories:
  - 教程
---
本文是[`Stable Diffusion`系列](https://babyno.top/tags/stable-diffusion/)第三篇。

前两篇文章我们介绍了在本地运行`Stable Diffusion`模型的方法，以及使用`LoRA`对模型生成的图片进行微调。

本篇文章中，我们将介绍两种技术来控制图像的生成过程，对模型图像生成进行引导，使得生成的图像更符合我们的需求。这样生成的图片，更具有商业价值。

## 图像生成引导技术

在 `Stable Diffusion`等文本转图像模型中，"对模型图像生成进行引导"是指通过提供额外的信息来控制图像生成过程，使其生成更符合预期的图像。引导的方法有多种，比如前两篇文章提及的“引导词”和`LoRA`都是引导技术的一种。在本篇文章中，重点介绍的是“使用参考图像”进行引导的方法，也就是`Image to Image`。试想一下：你先用草稿将绘画元素勾勒出来，然后利用该技术即可让`AI`对作品细节进行补充。

## `ControlNet`和`Adapter`

- `ControlNet`是一种基于神经网络的技术。`ControlNet`使用一个神经网络来学习图像和文本描述之间的关系，并利用该关系来引导图像生成过程。
- `Adapter`是一种基于提示嵌入`prompt embedding`的技术。提示嵌入是将文本提示转换为向量表示的过程。`Adapter`通过将提示嵌入与图像嵌入进行结合，来引导图像生成过程。

这个表格展示了这两种技术的工作原理及优缺点：

| 特性 | Adapter | ControlNet |
|---|---|---|
| 工作原理 | 基于提示嵌入 | 基于神经网络 |
| 优点 | 易于使用、灵活 | 效果好、可控性强 |
| 缺点 | 效果可能不佳、需要额外的训练数据 | 使用复杂、需要训练数据 |

## `controlnet-aux`

在开始前，我们先下载一个工具：

```shell
pip install controlnet-aux mediapipe
```

`controlnet-aux`提供了多种辅助模型，称为`Detector`。这些 `Detector`可以分析图像并提取特定的信息，然后将这些信息作为条件传递给 `ControlNet`，从而更精细地控制图像生成过程。这一步骤我们称之为生成“引导图”。以下是一些常见的`Detector`模型及其简介：

- **CannyDetector:**
    - 功能：利用 Canny 边缘检测算法提取图像的边缘信息。
    - 应用场景：生成卡通插画、突出图像中的线条和结构、控制图像的锐利程度。
- **HEDdetector:**
    - 功能：利用 HED 边缘检测算法提取图像的边缘信息，与 Canny 边缘检测相比，HED 能够检测更复杂的边缘。
    - 应用场景：类似于 CannyDetector，但适用于细节更丰富的图像。
- **LineartDetector:**
    - 功能：提取图像中的线条艺术信息，例如漫画和素描中的线条。
    - 应用场景：生成线条艺术图像、将照片转换为线条艺术风格。
- **MidasDetector:**
    - 功能：估计图像中物体的深度信息。
    - 应用场景：生成具有三维立体感和景深效果的图像、控制图像中景物的前后关系。
- **MLSDdetector (Multi-Line Style Detector):**
    - 功能：提取图像中多种线条的样式信息，例如粗细、颜色和纹理。
    - 应用场景：生成具有特定线条风格的图像，例如漫画的不同类型或者艺术流派。
- **NormalBaeDetector:**
    - 功能：估计图像中物体的表面法线信息，可以理解为物体表面的朝向。
    - 应用场景：生成更加逼真写实的图像，例如控制光照效果和材质质感。
- **OpenposeDetector:**
    - 功能：检测图像中人体关键点的位置，例如头部、肩部、肘部等。
    - 应用场景：生成包含人物的图像，并控制人物的姿势和动作。
- **ZoeDetector (Object detector):**
    - 功能：检测并识别图像中的物体类别。
    - 应用场景：控制图像中要生成或排除的物体类型，例如生成特定场景或物体组合的图像。

要使用这些`Detector`，需要先下载模型，地址：[https://huggingface.co/lllyasviel/Annotators](https://huggingface.co/lllyasviel/Annotators)。你需要哪些`Detector`就下载哪些模型。省事的话就全部下载。

## 各种`Detector`对比

首先写一段代码运行`Detector`：

```python
from controlnet_aux import HEDdetector
from diffusers.utils import load_image, make_image_grid

device = 'mps'
original_image = load_image("data/3.jpg")
hed = HEDdetector.from_pretrained("your/path/controlnet-annotators").to(device)

hed_image = hed(original_image)
image_grid = make_image_grid([original_image, hed_image], rows=1, cols=2)
image_grid.save("data/out.jpg")
```

代码很简单，就不做解释了，下面是各种`Detector`的效果演示：

- **CannyDetector:**
![](imgs/posts/2024-04-22-run-stable-diffusion-locally3-guide-image-generation/canny.jpg)
- **HEDdetector:**
![](imgs/posts/2024-04-22-run-stable-diffusion-locally3-guide-image-generation/hed.jpg)
- **LineartDetector:**
![](imgs/posts/2024-04-22-run-stable-diffusion-locally3-guide-image-generation/lineart.jpg)
- **MidasDetector:**
![](imgs/posts/2024-04-22-run-stable-diffusion-locally3-guide-image-generation/midas.jpg)
- **MLSDdetector (Multi-Line Style Detector):**
![](imgs/posts/2024-04-22-run-stable-diffusion-locally3-guide-image-generation/mlsd.jpg)
- **NormalBaeDetector:**
![](imgs/posts/2024-04-22-run-stable-diffusion-locally3-guide-image-generation/bae.jpg)
- **OpenposeDetector:**
![](imgs/posts/2024-04-22-run-stable-diffusion-locally3-guide-image-generation/pose.jpg)
- **ZoeDetector (Object detector):**
![](imgs/posts/2024-04-22-run-stable-diffusion-locally3-guide-image-generation/zoe.jpg)

## 各种`Controlnet`对比

以上我们使用`Detector`生成了各种“引导图”，接下来我们使用`Controlnet`对引导图进行创作。老规矩，先去`hugging face`下载模型，我们这次测试的`Controlnet`都是`sdxl`的，具体原因参考前两篇文章：

- `controlnet-canny-sdxl-1.0`
- `controlnet-openpose-sdxl-1.0`
- `controlnet-zoe-depth-sdxl-1.0`
- `controlnet-depth-sdxl-1.0`

编写代码：

```python
from diffusers import StableDiffusionXLControlNetPipeline, ControlNetModel, DPMSolverSinglestepScheduler
from diffusers.utils import load_image, make_image_grid
from controlnet_aux import CannyDetector


device = 'mps'
original_image = load_image("data/3.jpg")
canny = CannyDetector()
canny_image = canny(original_image)

controlnet = ControlNetModel.from_pretrained(
    "your/path/controlnet-canny-sdxl-1.0",
    use_safetensors=True
)

pipe = StableDiffusionXLControlNetPipeline.from_single_file(
    "your/path/dreamshaperXL_v21TurboDPMSDE.safetensors",
    controlnet=controlnet,
    use_safetensors=True
).to(device)
pipe.scheduler = DPMSolverSinglestepScheduler.from_config(pipe.scheduler.config, use_karras_sigmas=True)
# pipe.enable_model_cpu_offload()

prompt = "masterpiece, 1girl, long hair, asian, sundress, cartoon"
negative_prompt = 'low quality, bad quality, sketches'

image = pipe(
    prompt,
    negative_prompt=negative_prompt,
    image=canny_image,
    # controlnet_conditioning_scale=0.5,
    height=1024,
    width=576,
    num_inference_steps=6,
    guidance_scale=2,
).images[0]
image_grid = make_image_grid([original_image, image], rows=1, cols=2)
image_grid.save("data/out.jpg")
```

提示词与[上一篇](https://babyno.top/posts/2024/04/run-stable-diffusion-locally-with-lora/)文章一模一样，让我们来看一下生成的图片。

- 使用`CannyDetector`和`CannyControlnet`
![](imgs/posts/2024-04-22-run-stable-diffusion-locally3-guide-image-generation/canny-1.jpg)
- 使用`OpenposeDetector`和`PoseControlnet`
![](imgs/posts/2024-04-22-run-stable-diffusion-locally3-guide-image-generation/pose-1.jpg)
- 使用`MidasDetector`和`MidasControlnet`
![](imgs/posts/2024-04-22-run-stable-diffusion-locally3-guide-image-generation/midas_depth.jpg)

## 各种`Adapter`对比

与`Contronet`一样，先去`hugging face`上下载模型，这次我们使用腾讯的`t2i-adapter`进行测试：

- `t2i-adapter-openpose-sdxl-1.0`
- `t2i-adapter-depth-zoe-sdxl-1.0`
- `t2i-adapter-sketch-sdxl-1.0`
- `t2i-adapter-lineart-sdxl-1.0`
- `t2i-adapter-canny-sdxl-1.0`
- `t2i-adapter-depth-midas-sdxl-1.0`

编写代码：

```python
from diffusers import T2IAdapter, StableDiffusionXLAdapterPipeline, DPMSolverSinglestepScheduler
from diffusers.utils import load_image, make_image_grid
from controlnet_aux import CannyDetector

device = 'mps'
original_image = load_image("data/3.jpg")
canny = CannyDetector()
canny_image = canny(original_image)

adapter = T2IAdapter.from_pretrained("/Users/lei/Downloads/t2i-adapter-canny-sdxl-1.0")

pipe = StableDiffusionXLAdapterPipeline.from_single_file(
    "your/path/dreamshaperXL_v21TurboDPMSDE.safetensors",
    # controlnet=controlnet,
    adapter=adapter,
    use_safetensors=True
).to(device)
pipe.scheduler = DPMSolverSinglestepScheduler.from_config(pipe.scheduler.config, use_karras_sigmas=True)
# pipe.enable_model_cpu_offload()

prompt = "masterpiece, 1girl, long hair, asian, sundress, cartoon"
negative_prompt = 'low quality, bad quality, sketches'

image = pipe(
    prompt=prompt,
    negative_prompt=negative_prompt,
    image=canny_image,
    # controlnet_conditioning_scale=0.5,
    height=1024,
    width=576,
    num_inference_steps=6,
    guidance_scale=2,
).images[0]
image_grid = make_image_grid([original_image, image], rows=1, cols=2)
image_grid.save("data/out.jpg")
```

- 使用`CannyDetector`和`CannyAdapter`
![](imgs/posts/2024-04-22-run-stable-diffusion-locally3-guide-image-generation/canny_canny.jpg)
- 使用`OpenposeDetector`和`PoseAdapter`
![](imgs/posts/2024-04-22-run-stable-diffusion-locally3-guide-image-generation/pose_pose.jpg)
- 使用`CannyDetector`和`SketchAdapter`
![](imgs/posts/2024-04-22-run-stable-diffusion-locally3-guide-image-generation/canny_sketch.jpg)
- 使用`HEDdetector`和`SketchAdapter`
![](imgs/posts/2024-04-22-run-stable-diffusion-locally3-guide-image-generation/hed_sketch.jpg)
- 使用`LineartDetector`和`LineartAdapter`
![](imgs/posts/2024-04-22-run-stable-diffusion-locally3-guide-image-generation/lineart_lineart.jpg)
- 使用`MidasDetector`和`MidasAdapter`
![](imgs/posts/2024-04-22-run-stable-diffusion-locally3-guide-image-generation/midas_midas.jpg)

## 总结

从图片质量可以看出，`ControlNet`对于引导图的遵循和生成图片的质量都较`Adapter`高，具体使用情况如何，大家在使用前还是自己测试一下。