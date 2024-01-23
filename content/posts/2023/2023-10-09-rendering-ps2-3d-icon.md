---
author: "路边的阿不"
title: 使用Python和OpenGL渲染PS2存档3D图标
slug: rendering-ps2-3d-icon
description: "Step into the world of 3D icon rendering using tools like Python3, PyGame, Numpy, ModernGL and PyGLM. Discover their unique roles in creating animation effects, light additions, smooth transitions and more within PS2."
date: 2023-10-09 17:34:15
draft: false
ShowToc: true
TocOpen: true
tags: ["3D Rendering", "ps2mc-browser", "Python", "ModernGL"]
categories: ["Programming"]
---

![](imgs/posts/2023-10-09-rendering-ps2-3d-icon/1.jpg)

经过前面一系列文章的铺垫，PS2存档3D图标的文件已经全部解析完毕。本篇开始将介绍使用如下工具将3D图标渲染出来，并尽可能接近PS2主机原生的效果。
- Python3
- PyGame
- Numpy
- ModernGL
- PyGLM

## 01 初始化`PyGame`和`ModernGL`
第一步先初始化`PyGame`，设置窗口大小为`640x480`，`FPS`为`60`。开启`OpenGL`渲染模式，`OpenGL`的版本号设置为`3.3`。
```python
import pygame as pg

pg.init()
pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
pg.display.set_mode((640, 480), flags=pg.OPENGL | pg.DOUBLEBUF)
self.clock = pg.time.Clock()
self.clock.tick(60)
```

接着初始化`ModernGL`，非常简单，只要创建一个`context`，开启深度测试和面剔除。

```python
import moderngl as mgl

self.ctx = mgl.create_context()
self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)
```

## 02 获取顶点、纹理、法线等数据
这部分内容在上一篇[解析PS2游戏存档3D图标]()有详细描述，就不展开了，这里只贴一下`icon.sys`的数据结构供参考。

```c++
struct IconSys {
    char magic[4];
    uint16 unknown; // ignore
    uint16 subtitle_line_break;
    uint16 unknown; // ignore
    uint32 bg_transparency;
    uint32 bg_color_upper_left[4];
    uint32 bg_color_upper_right[4];
    uint32 bg_color_lower_left[4];
    uint32 bg_color_lower_right[4];
    float32 light_pos1[4];
    float32 light_pos2[4];
    float32 light_pos3[4];
    float32 light_color1[4];
    float32 light_color2[4];
    float32 light_color3[4];
    float32 ambient[4];
    char subtitle[68];
    char icon_file_normal[64];
    char icon_file_copy[64];
    char icon_file_delete[64];
    char zeros[512]; // ignore
};
```

## 03 坐标系统
这里以右手系统创建坐标系，但是原始的顶点是y轴颠倒的，如下图A。因此我们之后的工作将在转换后的图B坐标系下进行。
![](imgs/posts/2023-10-09-rendering-ps2-3d-icon/%E5%AD%98%E5%82%A8%E5%8D%A1-%E5%9D%90%E6%A0%87%E7%B3%BB.jpg)

## 04 变换矩阵
### 观察矩阵
上图B中，摄像机位置在z轴的负延伸方向，我们稍稍向y轴负方向移动一小段距离，这样可以使视线不是对着图标的脚部，而是稍稍靠上一点，因此将摄像机位置坐标设为`(0, -2, -10)`。因为要将y轴颠倒，可以直接将摄像机向上的方向设置为y轴的负方向。这样一来`lookAt`矩阵创建如下：
```python
self.position = glm.vec3(0, -2, -10)
self.up = glm.vec3(0, -1, 0)
self.view = glm.lookAt(self.position, glm.vec3(0, -2, 0), self.up)
```
### 投影矩阵
投影矩阵可以用如下公式获得
```python
self.proj = glm.perspective(glm.radians(50), window_width / window_height, 0.1, 100)
```
### 模型矩阵
创建模型矩阵的目的是控制模型对象在3D空间中的位置变化，在这里模型对象需要在空间里绕着y轴做360度的旋转。
```python
# 初始化模型矩阵
self.m_model = glm.mat4()
# 使模型绕y轴旋转，转过的角度为经过的时间。
# 初始化的180度是为了让模型在开始的时候背对着画面，更接近PS2主机的行为
m_model = glm.rotate(self.m_model, glm.radians(180) + animation_time / 2,
                     glm.vec3(0, 1, 0))
```
## 05 创建着色器
这里一共需要创建四个着色器
- 背景顶点着色器
- 背景片段着色器
- Icon顶点着色器
- Icon片段着色器

### 背景着色器
背景着色器比较简单，只要创建一个覆盖整个坐标系的矩形，并且设置在离摄像机最远的那个坐标平面上即可。参考上面的图B，这个平面应该是z轴的0.9999。这个矩形的四个顶点的坐标分别为(-1, 1), (-1, -1), (1, -1), (1, 1)，对应的颜色在`icon.sys`中可以解析出来。根据这四个顶点和颜色，就可以构建背景VBO及VAO，这里不做过多描述。
```glsl
// bg.vert
#version 330 core

in vec2 vertexPos;
in vec4 vertexColor;

out vec3 fragColor0;

void main() {
    fragColor0 = vertexColor.rgb;
    gl_Position = vec4(vertexPos.xy, 0.9999, 1.0);
}
```

```glsl
// bg.frag
#version 330 core

in vec3 fragColor0;

out vec4 fragColor;

uniform float alpha0;

void main() {
    fragColor = vec4(fragColor0, alpha0);
}
```

### Icon着色器
Icon着色器会比较复杂，我们先尝试着把Icon顶点渲染出来。还记得每个图标有多个形状吗？形状与动画相关，我们现在只取其中的一个形状组成VBO和VAO。
```glsl
// icon.vert
#version 330 core

in vec4 vertexPos;

uniform mat4 proj;
uniform mat4 view;
uniform mat4 model;

void main() {
    gl_Position = proj * view * model * vec4(vertexPos.xyz, 1);
}
```

```glsl
// icon.frag
#version 330 core

out vec4 fragColor;

void main() {
    fragColor = vec4(0, 0, 0, 1);
}
```

以下是运行代码后的效果：

![](imgs/posts/2023-10-09-rendering-ps2-3d-icon/3.gif)

### 添加纹理
在上面的基础上，引入纹理坐标和纹理数据。
```glsl
// icon.vert
#version 330 core

in vec4 vertexPos;
in vec2 texCoord;
in vec4 vertexColor;

out vec4 fragColor0;
out vec2 uv0;

uniform mat4 proj;
uniform mat4 view;
uniform mat4 model;

void main() {
    uv0 = texCoord;
    fragColor0 = vertexColor;
    gl_Position = proj * view * model * vec4(vertexPos.xyz, 1);
}
```

```glsl
// icon.frag
#version 330 core

in vec2 uv0;
in vec4 fragColor0;

out vec4 fragColor;

uniform sampler2D texture0;

void main() {
    float alpha = fragColor0.a;
    vec3 color = fragColor0.rgb * texture(texture0, uv0).rgb;
    fragColor = vec4(color, alpha);
}
```
![](imgs/posts/2023-10-09-rendering-ps2-3d-icon/4.gif)

### 添加光照
在上面的基础上，引入光源，环境光以及法线数据。
```glsl
// icon.vert
#version 330 core

in vec4 vertexPos;
in vec2 texCoord;
in vec4 vertexColor;
in vec4 normal;

out vec4 fragColor0;
out vec2 uv0;
out vec3 normal0;
out vec3 fragPos0;

uniform mat4 proj;
uniform mat4 view;
uniform mat4 model;

void main() {
    uv0 = texCoord;
    fragColor0 = vertexColor;
    normal0 = mat3(model) * normalize(normal.xyz);
    gl_Position = proj * view * model * vec4(vertexPos.xyz, 1);
    fragPos0 = gl_Position.xyz;
}
```
```glsl
// icon.frag
#version 330 core
#define MAX_NUM_TOTAL_LIGHTS 3

in vec2 uv0;
in vec4 fragColor0;
in vec3 normal0;
in vec3 fragPos0;

out vec4 fragColor;

struct Light {
    vec4 pos;
    vec4 color;
};

uniform sampler2D texture0;
uniform vec4 ambient;

uniform Light lights[MAX_NUM_TOTAL_LIGHTS];

void main() {
    vec3 normal = normalize(normal0);
    float alpha = fragColor0.a;
    vec3 color = fragColor0.rgb * texture(texture0, uv0).rgb;
    vec3 diffuse = vec3(0.0, 0.0, 0.0);
    for (int i = 0; i < MAX_NUM_TOTAL_LIGHTS; i++) {
        vec3 lightDir = normalize(lights[i].pos.xyz - fragPos0);
        float diff = max(dot(lightDir, normal), 0.0);
        diffuse += diff * lights[i].color.rgb;
    }
    color = (ambient.rgb + diffuse) * color;
    fragColor = vec4(color, alpha);
}
```
![](imgs/posts/2023-10-09-rendering-ps2-3d-icon/5.gif)

### 动画效果
动画效果是让着色器按照时间渲染不同形状的顶点数据。我们可以设计一个计时器和一个计数器，以确定当前时间应该渲染哪个形状的顶点。

- `frame_length` 完成动画效果需要的实际帧数，实际帧率等于60FPS
- `animation_time` 动画运行时间
- `anim_speed` 动画播放速度
- `frame_length` / animation_shapes 一个形状包含多少帧

```python
animation_time = time.time() - self.start_time
curr_frame = int(animation_time * self.window.fps * self.icon.anim_speed)
             % self.icon.frame_length
curr_shape = int(curr_frame // (self.icon.frame_length / self.icon.animation_shapes))
```

![](imgs/posts/2023-10-09-rendering-ps2-3d-icon/6.gif)

### 使动画平滑过渡
使动画平滑过渡需要使用着色器的顶点插值技术。我们在发送着色器顶点的时候，将当前形状和下一个形状的顶点数据同时发送。这样再根据时间因子，着色器会自动计算两个形状之间的顶点。

- `tween_factor` 计算当前时间戳在整个形状中所占帧的百分比

```python
curr_frame_in_shape = curr_frame % frames_in_shape / frames_in_shape
tween_factor = glm.float32(curr_frame_in_shape)
```

```glsl
// icon.vert
#version 330 core

in vec4 vertexPos;
in vec2 texCoord;
in vec4 vertexColor;
in vec4 nextVertexPos;
in vec4 normal;

out vec4 fragColor0;
out vec2 uv0;
out vec3 normal0;
out vec3 fragPos0;

uniform mat4 proj;
uniform mat4 view;
uniform mat4 model;
uniform float tweenFactor;

void main() {
    uv0 = texCoord;
    fragColor0 = vertexColor;
    normal0 = mat3(model) * normalize(normal.xyz);
    vec4 basePos = vec4(mix(vertexPos.xyz, nextVertexPos.xyz, tweenFactor), 1.0);
    gl_Position = proj * view * model * basePos;
    fragPos0 = gl_Position.xyz;
}
```

```glsl
// icon.frag
#version 330 core
#define MAX_NUM_TOTAL_LIGHTS 3

in vec2 uv0;
in vec4 fragColor0;
in vec3 normal0;
in vec3 fragPos0;

out vec4 fragColor;

struct Light {
    vec4 pos;
    vec4 color;
};

uniform sampler2D texture0;
uniform vec4 ambient;

uniform Light lights[MAX_NUM_TOTAL_LIGHTS];

void main() {
    vec3 normal = normalize(normal0);
    float alpha = fragColor0.a;
    vec3 color = fragColor0.rgb * texture(texture0, uv0).rgb;
    vec3 diffuse = vec3(0.0, 0.0, 0.0);
    for (int i = 0; i < MAX_NUM_TOTAL_LIGHTS; i++) {
        vec3 lightDir = normalize(lights[i].pos.xyz - fragPos0);
        float diff = max(dot(lightDir, normal), 0.0);
        diffuse += diff * lights[i].color.rgb;
    }
    color = (ambient.rgb + diffuse) * color;
    fragColor = vec4(color, alpha);
}
```

最终效果：

![](imgs/posts/2023-10-09-rendering-ps2-3d-icon/7.gif)

## 06 尾声
所有代码均可在 https://github.com/caol64/ps2mc-browser 下载到。在我的第一篇文章中，我也提到了这个系列的创作初衷：为了纪念逝去的青春，以及对技术永不磨灭的热情。在此收尾，也算还了年少时的一个梦想。

## 07 参考文献
- [gothi - icon.sys format](https://www.ps2savetools.com/documents/iconsys-format/)
- [Martin Akesson - PS2 Icon Format v0.5](http://www.csclub.uwaterloo.ca:11068/mymc/ps2icon-0.5.pdf)
- [Florian Märkl - mymcplus](https://git.sr.ht/~thestr4ng3r/mymcplus)
- [Ross Ridge - PlayStation 2 Memory Card File System](https://www.ps2savetools.com/ps2memcardformat.html)
