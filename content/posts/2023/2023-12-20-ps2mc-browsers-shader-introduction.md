---
author: 路边的阿不
title: 「ps2mc-browser」着色器代码分析
slug: ps2mc-browsers-shader-introduction
description: Uncover the magic behind colorful 3D rendering using OpenGL Shader with the ps2mc-browser. Dive deep into how polygons, vertices, and textures combine to create vibrant tabletop graphics.
date: 2023-12-20 12:07:17
draft: false
ShowToc: true
TocOpen: true
tags:
  - OpenSource
categories:
  - Ps2mc
---
如何将多边形的顶点和纹理渲染成缤纷多彩的画面呢？它就是OpenGL着色器。今天我们就要聊聊`ps2mc-browser`的着色器。

这里简单介绍一下，[ps2mc-browser](https://github.com/caol64/ps2mc-browser)是一个ps2存档查看器，它有能力解析ps2存档中3D图标的顶点和纹理等数据，并通过`OpenGL`的能力将图标渲染出来。

在接下来的内容中，我将逐个解析`ps2mc-browser`中的六个`OpenGL`着色器。让我们一起深入理解他们是如何工作的吧。

## 背景着色器(bg.frag和bg.vert)

主要负责渲染背景色。通过之前的文章我们知道`icon.sys`文件里提供了背景的四个顶点的颜色以及透明度数据。

这里我们再回顾一下我们创建的坐标系统：

![](imgs/posts/2023-10-09-rendering-ps2-3d-icon/%E5%AD%98%E5%82%A8%E5%8D%A1-%E5%9D%90%E6%A0%87%E7%B3%BB.jpg)

因为我们创建出来的空间是一个每条边长度都是2的正立方体，而坐标所在的原点坐标是立方体的中心。此外我们的摄像机是在`z轴`的负方向，想象一下立方体的哪一个面应该是背景面：

![](imgs/posts/2023-12-20-ps2mc-browsers-shader-introduction/image.webp)

因此我们可以构建出背景的四个顶点坐标是：

```python
bg_vertex = [(-1, 1, 0.99), (-1, -1, 0.99), (1, -1, 0.99), (1, 1, 0.99)]
```

顺带一提，在着色器里，渲染是按照三角形为单位的，因此这个正方形的面应该是拆分成两个三角形组成。现在将这4个坐标分别填入对应的颜色值，着色器将渲染这整个面的颜色。

```glsl
// bg.frag
#version 330 core
in vec4 fragColor0;
out vec4 fragColor;
void main() {
    fragColor = fragColor0;
}
```

在背景的片元着色器(bg.frag)中，我们需要输入一个颜色(`fragColor0`)，然后将它的值赋给输出颜色(`fragColor`)。这个过程其实就是渲染背景颜色。

```glsl
// bg.vert
#version 330 core
in vec3 vertexPos;
in vec4 vertexColor;
out vec4 fragColor0;
void main() {
    fragColor0 = vertexColor;
    gl_Position = vec4(vertexPos, 1.0);
}
```

在背景的顶点着色器(bg.vert)中，我们首先定义了一个顶点的位置(`vertexPos`)和一个颜色值(`vertexColor`)作为输入。然后我们将颜色值传递给了片元着色器，并设定顶点的位置(`gl_Position`)。

可以说背景着色器的主要职责就是把我们希望看到的颜色填充到屏幕上。

到这里还没有完，我们之前提到背景除了颜色数据还有透明度数据，那怎么将透明度体现出来呢？我们在刚才的背景图层后面，再加一层我们称之为`skybox`的层，并未此层添加一些颜色，这样，如果背景层有透明度，那天空层的颜色就会透过背景层展现一部分出来，达到视觉上感知的效果。

```python
skybox_vertex = [(-1, 1, 0.999), (-1, -1, 0.999), (1, -1, 0.999), (1, 1, 0.999)]
skybox_colors = [
    (0.6, 0.6, 0.6, 1),
    (0.6, 0.6, 0.6, 1),
    (0.6, 0.6, 0.6, 1),
    (0.6, 0.6, 0.6, 1),
]
```

最后来一张背景图效果，可以看到中间的颜色过渡效果是着色器插值自动计算的。

![](imgs/posts/2023-12-20-ps2mc-browsers-shader-introduction/截屏2023-12-20%2014.41.10.webp)

## 图标着色器(icon.frag和icon.vert)

这是最复杂的一部分，它负责将从ps2存档中解析出来的3D图标绘制出来。上面提到，着色器是将顶点围成的三角形逐个渲染的。

```glsl
// icon.frag
#version 330 core
...
// Uniform variables
uniform sampler2D texture0;  // Texture
uniform vec4 ambient;        // Ambient light
uniform mat4 model;          // Model matrix
uniform Light lights[MAX_NUM_TOTAL_LIGHTS];  // Array of lights
void main() {
    // Calculate normalized normal vector
    vec3 normal = normalize(normal0).xyz;
    // Get color from the texture
    vec3 color = texture(texture0, uv0).rgb;
    // Calculate diffuse lighting
    vec3 diffuse = vec3(0);
    for (int i = 0; i < MAX_NUM_TOTAL_LIGHTS; i++) {
        vec3 lightDir = normalize(lights[i].dir.xyz);
        diffuse += max(dot(normal, lightDir), 0.0) * lights[i].color.rgb;
    }
    // Final color calculation
    vec4 finalColor = vec4((ambient.rgb + diffuse) * color, 1.0);
    fragColor = finalColor;
}
```

在图标的片元着色器(icon.frag)里，“uniform”关键字代介我们的一些常量，包含了纹理(`texture0`)，环境光(`ambient`)，以及光照(`lights`)等。

接着我们计算了一个单位法向量(`normal`)，从纹理中取得颜色，并计算漫反射光(`diffuse`)。具体来讲，每个灯光都会对漫反射光有贡献，这取决于灯光的方向和法向量的夹角。我们将所有灯光的贡献相加，就得到了最终的漫反射光。

最后，我们将环境光和漫反射光与纹理颜色相乘后得到最终的颜色(`finalColor`)，并将其传给片元着色器的输出颜色(`fragColor`)。

```glsl
// icon.vert
#version 330 core
...
// Output variables for fragment shader
out vec2 uv0;            // Texture coordinates for fragment shader
out vec4 normal0;        // Transformed normal for fragment shader
// Uniform matrices
uniform mat4 proj;       // Projection matrix
uniform mat4 view;       // View matrix
uniform mat4 model;      // Model matrix
uniform float tweenFactor; // Tweening factor for vertex animation
void main() {
    // Pass texture coordinates to fragment shader
    uv0 = texCoord;
    // Transform and pass normal to fragment shader
    normal0 = model * vec4(normal, 1);
    // Interpolate between current and next vertex positions based on tween factor
    vec4 basePos = vec4(mix(vertexPos, nextVertexPos, tweenFactor), 1.0);
    // Combine transformations and set the final vertex position
    gl_Position = proj * view * model * basePos;
}
```

在图标的顶点着色器(icon.vert)中，我们通过`uniform`关键字设定了一些矩阵(`proj`，`view`，`model`)和一个插值因子(`tweenFactor`)。

这里重点讲一下插值因子(`tweenFactor`)，这个值是3D图标能进行动画动作效果的关键。由于每个存档除了保存有图标完整的顶点外，还额外保存了完成一组动作的不同的顶点坐标，我们称之为动作帧，动作帧循环播放的时候就形成了动画效果。因此我们需要将相邻的动作帧的顶点坐标进行插值计算，`tweenFactor`就是当前的时间在本帧与下一帧之间的时间因子。

然后我们将纹理坐标(`uv0`)和和法向量(`normal0`)传递给片元着色器。我们按插值因子在当前顶点位置(`vertexPos`)和下一顶点位置(`nextVertexPos`)之间插值，之后再由模型矩阵(`model`)进行变换，得到实际的顶点位置，并最后再通过视图矩阵(`view`)和投影矩阵(`proj`)将其变换到齐次裁剪空间。

到这里图标着色器的任务就完成了。

## 按钮着色器(circle.frag和circle.vert)

负责渲染与鼠标交互的按钮，`ps2mc-browser`可以显示存档中角色的多种不同动作，通过鼠标点击相应的按钮切换不同的动作。

```glsl
// circle.frag
#version 330 core
out vec4 fragColor;
void main() {
    fragColor = vec4(1.0, 1.0, 1.0, 0.6);
}
```

在这个circle.frag里，我们直接将颜色(`fragColor`)设定为不完全透明的白色，并不接受任何输入。

```glsl
// circle.vert
#version 330 core
in vec2 vertexPos;
void main() {
    gl_Position = vec4(vertexPos, 0, 1.0);
}
```

在circle.vert中，我们只需要接收一个顶点位置(`vertexPos`)作为输入，然后赋给OpenGL的内建变量`gl_Position`。

简单来说，按钮着色器的工作就是画出一个不完全透明的白色的几何图形作为按钮。它要渲染的按钮数量和按钮坐标，都是由程序计算好以后传递给着色器的。

## 总结

至此，我们已经详细讲解了`ps2mc-browser`如何通过`OpenGL`着色器来渲染3D动态图标。`python`和`OpenGL`都是我第一次接触，把它们整合到一块做了这个项目一开始我是没有想到的。之后可能还会对这个项目添加一些新功能，那我们下回再见。