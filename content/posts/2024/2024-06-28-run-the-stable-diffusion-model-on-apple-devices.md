---
author: 路边的阿不
title: 在苹果设备上运行Stable Diffusion模型
slug: run-the-stable-diffusion-model-on-apple-devices
description: ""
date: 2024-06-28 15:18:47
draft: false
ShowToc: true
TocOpen: true
tags:
  - Stable Diffusion
  - CoreML
categories:
  - AI
---
## 模型类别

首先要下载模型，`Stable Diffusion`模型可以在[huggingface](https://huggingface.co/models)或者[Civitai](https://civitai.com/)下载到。但是在这两个网站上下载的模型可能会有三种格式。

### `CoreML`格式

这种类别的模型较少，文件主要以`.mlmodelc`或`.mlmodel`为主，其文件结构大致为：

```
├── TextEncoder.mlmodelc
├── TextEncoder2.mlmodelc
├── Unet.mlmodelc
├── VAEDecoder.mlmodelc
├── merges.txt
└── vocab.json
```

### `Diffusers`格式

在`huggingface`上下载的模型大多是这种类型，其文件结构大致为：

```
├── model_index.json
├── scheduler
│   └── scheduler_config.json
├── text_encoder
│   ├── config.json
│   └── pytorch_model.bin
├── tokenizer
│   ├── merges.txt
│   ├── special_tokens_map.json
│   ├── tokenizer_config.json
│   └── vocab.json
├── unet
│   ├── config.json
│   └── diffusion_pytorch_model.bin
└── vae
    ├── config.json
    └── diffusion_pytorch_model.bin
```

### `safetensors`格式

在`Civitai`网站下载的大多是这种格式，就一个文件，非常方便。

## 模型转换

接下来，需要把下载下来的模型都转成`CoreML`格式，如果你在第一步下载的模型已经是`CoreML`格式，那么这一步就可以跳过。

### `Diffusers`格式转`CoreML`格式

首先下载该仓库代码：[ml-stable-diffusion](https://github.com/apple/ml-stable-diffusion)。查看`System Requirements`检查自己的设备是否支持。然后安装依赖：

```shell
pip install -r requirements.txt
```

找到`torch2coreml.py`文件，执行以下命令：

```shell
python torch2coreml.py \
--bundle-resources-for-swift-cli \
--xl-version \
--convert-unet \
--convert-text-encoder \
--convert-vae-decoder \
--attention-implementation ORIGINAL \
--model-version /your/model/path \
-o /your/model/output/path
```

注意有个参数`--xl-version`，如果模型是`sdxl`类型的，就加上，否则把这行删除。另外如果你的模型支持图生图，你可以加上`--convert-vae-encoder`参数。

运行完该命令，应该在你指定的目录生成了文件，在`Resources`目录下的文件就是转换好的`CoreML`格式。

### `safetensors`格式转`Diffusers`格式

首先下载该仓库代码：[Diffusers](https://github.com/huggingface/diffusers)。然后安装依赖：

```shell
pip install --upgrade diffusers
```

找到`convert_original_stable_diffusion_to_diffusers.py`文件并执行以下命令：

```shell
python convert_original_stable_diffusion_to_diffusers.py \
--checkpoint_path /your/model/path \
--dump_path /your/model/output/path \
--from_safetensors \
--half \
--device mps
```

这里`--half`表示转换时精度为`fp16`，`--device mps`表示模型使用`mps(GPU)`进行推理。

运行完该命令，会生成`Diffusers`格式的模型，再利用`Diffusers`格式转`CoreML`格式的步骤，将模型转换为`CoreML`格式。

## `Swift`调用`Stable Diffusion`模型

使用`Huggingface`提供的[swift-coreml-diffusers](https://github.com/huggingface/swift-coreml-diffusers)库。我的[AquariusAI](https://github.com/caol64/aquarius-ai)项目提供了示例代码。

![](imgs/posts/2024-06-28-run-the-stable-diffusion-model-on-apple-devices/2.webp)

## 最后

那到底什么是`CoreML`呢？

> Core ML 是Apple Silicon芯片产品（包括macOS、iOS、watchOS 和 tvOS）中使用的机器学习框架，用于执行快速预测或推理，在边缘轻松集成预训练的机器学习模型，从而可以对设备上的实时图像或视频进行实时预测。
> 
> Core ML 通过利用 CPU、GPU 和 神经网络引擎 ，同时最大程度地减小内存占用空间和功耗，来优化设备端性能。 由于模型严格地在用户设备上，因此无需任何网络连接，这有助于保护用户数据的私密性和 App 的响应速度。

简而言之，如果你的模型运行在`Silicon`芯片的苹果设备上，利用`Core ML`可以获得更快的性能和更低的内存及能耗。

