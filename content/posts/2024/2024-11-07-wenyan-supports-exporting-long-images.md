---
author: "路边的阿不"
title: 文颜支持导出长图
slug: wenyan-supports-exporting-long-images
description: ""
date: 2024-11-07 16:22:06
draft: false
ShowToc: true
TocOpen: true
tags:
  - OpenSource
categories:
  - 文颜
---

[「文颜」](https://yuzhi.tech/wenyan)是一款多平台写作工具，因此也适合图片社交媒体的内容发布。目前文颜可将内容按照预览效果导出成长图，这可以满足一些特殊的发布需求。

## 如何导出长图

直接点击悬浮按钮“长图”即可，应用会询问你将图片保存到哪里。

<img src="/imgs/posts/2024-11-07-wenyan-supports-exporting-long-images/1.webp" width="75%">

一般来讲，这种长图可以直接发布到任何社交媒体。

<video controls width="100%">
    <source src="https://yuzhi.tech/img/wenyan/1.mp4" type="video/mp4">
    Your browser does not support the video tag.
</video>

## 制作海报

将导出长图和[自定义主题](https://babyno.top/posts/2024/11/wenyan-supports-customized-themes/)功能相结合，文颜具备了制作海报的能力。当然只能制作简单的海报，我们这里举个例子。

首先创建一个自定义主题：

```css
#wenyan {
    font-family: ui-sans-serif, system-ui, sans-serif;
    line-height: 1.75;
    background-image: url('https://marketplace.canva.com/EAGPIDVZ0-A/1/0/1131w/canva-peach-aesthetic-background-flyer-IqGDJ_simvM.jpg');
    background-size: cover;
    color: #5a4b3b;
}

#wenyan h1 {
    text-align: center;
    font-size: 1.8em;
    color: #3a3128;
    margin-bottom: 20px;
}
#wenyan h6 {
    font-size: 1em;
    font-weight: bold;
    text-align: right;
}
```

然后粘贴以下内容：

```markdown
# 产品发布会邀请函

尊敬的张XX先生，

您好！

我们诚挚地邀请您出席**某品牌**的产品发布会。此次发布会将揭晓我们最新的产品系列，展示最前沿的科技成果，并探讨未来发展趋势。您的莅临将是我们的莫大荣幸。

**发布会信息如下：**

- **时间**：XX年XX月XX日，XX:XX
- **地点**：XX市XX区XX路XX号

###### 某品牌
```

软件截图如下：

![alt text](imgs/posts/2024-11-07-wenyan-supports-exporting-long-images/2.webp)

这是最后导出的海报图片：

![alt text](imgs/posts/2024-11-07-wenyan-supports-exporting-long-images/out.jpeg)