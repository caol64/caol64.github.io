---
author: caol64
title: '"ps2mc-browser" Shader Code Analysis'
slug: ps2mc-browsers-shader-introduction
description: Uncover the magic behind colorful 3D rendering using OpenGL Shader with the ps2mc-browser. Dive deep into how polygons, vertices, and textures combine to create vibrant tabletop graphics.
date: 2023-12-20 12:07:17
draft: false
ShowToc: true
TocOpen: true
tags:
  - Open Source
  - OpenGL
  - 3D Graphics
  - Tutorial
categories:
  - Graphics Development
---
How do we render the vertices and textures of polygons into a colorful scene? This is where OpenGL shaders come into play. Today, we'll discuss the shaders of `ps2mc-browser`.

To briefly introduce, [ps2mc-browser](https://github.com/caol64/ps2mc-browser) is a PS2 memory card viewer capable of parsing vertex and texture data from 3D icons within PS2 memory card files and rendering them using OpenGL.

In the following content, I'll dissect the six OpenGL shaders used in `ps2mc-browser` one by one. Let's dive into understanding how they work.

## Background Shaders (bg.frag and bg.vert)

These shaders are primarily responsible for rendering the background color. As we learned from previous articles, the `icon.sys` file provides data for the colors and transparency of the four vertices of the background.

Let's revisit the coordinate system we created:

![](imgs/posts/2023-10-09-rendering-ps2-3d-icon/%E5%AD%98%E5%82%A8%E5%8D%A1-%E5%9D%90%E6%A0%87%E7%B3%BB.jpg)

Since the space we create is a cube with each side having a length of 2, and the origin coordinates are at the center of the cube. Additionally, our camera is in the negative direction of the `z-axis`. Let's imagine which face of the cube should be the background face:

![](imgs/posts/2023-12-20-ps2mc-browsers-shader-introduction/image.webp)

Therefore, we can construct the coordinates of the four vertices of the background as:

```python
bg_vertex = [(-1, 1, 0.99), (-1, -1, 0.99), (1, -1, 0.99), (1, 1, 0.99)]
```

By the way, in shaders, rendering is done on a per-triangle basis. Therefore, this square face should be split into two triangles. Now, we'll fill in the corresponding color values for these 4 coordinates, and the shader will render the color for the entire face.

```glsl
// bg.frag
#version 330 core
in vec4 fragColor0;
out vec4 fragColor;
void main() {
    fragColor = fragColor0;
}
```

In the fragment shader for the background (`bg.frag`), we input a color (`fragColor0`), and then assign its value to the output color (`fragColor`). This process essentially renders the background color.

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

In the vertex shader for the background (`bg.vert`), we first define a vertex position (`vertexPos`) and a color value (`vertexColor`) as inputs. Then, we pass the color value to the fragment shader and set the vertex position (`gl_Position`).

It can be said that the main responsibility of the background shader is to fill the desired color onto the screen.

We're not done yet. Previously, we mentioned that besides color data, the background also has transparency data. How do we represent transparency? We'll add another layer behind the background layer, which we call the `skybox` layer, and add some color to this layer. This way, if the background layer has transparency, some of the color from the skybox layer will show through the background layer, achieving the desired visual effect.

```python
skybox_vertex = [(-1, 1, 0.999), (-1, -1, 0.999), (1, -1, 0.999), (1, 1, 0.999)]
skybox_colors = [
    (0.6, 0.6, 0.6, 1),
    (0.6, 0.6, 0.6, 1),
    (0.6, 0.6, 0.6, 1),
    (0.6, 0.6, 0.6, 1),
]
```

Finally, here's an example of the background effect. You can see that the color transition in the middle is automatically calculated by shader interpolation.

![](imgs/posts/2023-12-20-ps2mc-browsers-shader-introduction/截屏2023-12-20%2014.41.10.webp)

## Icon Shaders (icon.frag and icon.vert)

This is the most complex part, responsible for rendering the 3D icons parsed from the PS2 memory card files. As mentioned earlier, shaders render triangles formed by vertices one by one.

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

In the fragment shader for the icons (`icon.frag`), the "uniform" keyword introduces some constants, including the texture (`texture0`), ambient light (`ambient`), and lighting (`lights`).

Next, we calculate a unit normal vector (`normal`), retrieve the color from the texture, and compute the diffuse reflection (`diffuse`). Specifically, each light contributes to the diffuse reflection, which depends on the angle between the light direction and the normal vector. We sum up the contributions of all lights to obtain the final diffuse reflection.

Finally, we multiply the ambient light and diffuse reflection by the texture color to get the final color (`finalColor`), which is then passed to the output color (`fragColor`) of the fragment shader.

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

In the vertex shader for the icons (`icon.vert`), we use the `uniform` keyword to set up some matrices (`proj`, `view`, `model`) and an interpolation factor (`tweenFactor`).

Let's focus on the interpolation factor (`tweenFactor`) here. This value is crucial for achieving animation effects in 3D icons. Since each memory card contains not only the complete set of vertices for the icon but also additional vertex coordinates for different actions, which we refer to as action frames, animating the frames in a loop creates the animation effect. Therefore, we need to interpolate between adjacent action frames to calculate the vertex coordinates. The `tweenFactor` represents the time factor between the current frame and the next frame.

Next, we pass the texture coordinates (`uv0`) and the normal vector (`normal0`) to the fragment shader. We interpolate between the current vertex position (`vertexPos`) and the next vertex position (`nextVertexPos`) based on the tween factor. Then, we transform the interpolated position using the model matrix (`model`) and finally transform it into homogeneous clipping space using the view matrix (`view`) and projection matrix (`proj`).

With this, the icon shader's task is completed.

## Button Shaders (circle.frag and circle.vert)

Responsible for rendering interactive buttons for mouse interaction. `ps2mc-browser` can display various actions of characters in the memory card. Users can click on the corresponding buttons to switch between different actions.

```glsl
// circle.frag
#version 330 core
out vec4 fragColor;
void main() {
    fragColor = vec4(1.0, 1.0, 1.0, 0.6);
}
```

In this `circle.frag`, we directly set the color (`fragColor`) to semi-transparent white and do not accept any inputs.

```glsl
// circle.vert
#version 330 core
in vec2 vertexPos;
void main() {
    gl_Position = vec4(vertexPos, 0, 1.0);
}
```

In `circle.vert`, we only need to receive a vertex position (`vertexPos`) as input and then assign it to the OpenGL built-in variable `gl_Position`.

In simple terms, the button shader's job is to draw a semi-transparent white geometric shape as a button. The number of buttons it needs to render and their coordinates are all calculated by the program and passed to the shader.

## Summary

So far, we have detailed how `ps2mc-browser` renders 3D dynamic icons using OpenGL shaders. Both Python and OpenGL were new to me, and I didn't expect to integrate them together for this project. There may be some new features added to this project in the future, so until next time, goodbye.