---
author: 路边的阿不
title: 聊聊建站那些事
slug: lets-talk-about-website-building
description: ""
date: 2024-09-10 11:41:16
draft: false
ShowToc: true
TocOpen: true
tags:
  - Cloudflare
  - Svelte
categories:
  - 建站
---
这两天建了个[新站](https://yuzhi.tech/)，与[本博客建站](https://babyno.top/posts/2023/11/new-hugo-blog/)过程不同，因此想写篇文章记录下。

## 网站功能设计

最近上线了一个APP，因此需要一个网站来做产品说明，正好我还有一些其它待上线的项目，因此该网站的核心功能暂定为：

- 产品目录
- 产品介绍
- 产品文档

于是就有了网站最初的目录结构：

- 网站首页
- 产品首页
- 产品详情页
- 文档首页
- 文档详情页
- 隐私政策页

这里的隐私政策页是APP上线必须的。

## 技术选型

以简单为第一原则，现阶段的网站只需要静态页面即可。因此选择`Cloudflare Pages`作为托管服务，`svelte`作为开发框架。

`Cloudflare Pages`不仅免费托管，还免流量费用，还能免费享受到全球网络优化服务，还有什么可吐槽的呢？（除了百度收录外）

`svelte`的简洁以及轻量级的特性特别适合这种轻量级网站的开发。

## 准备工作

- 一个域名
- 一个网站`logo`
- 一个`favicon`
- 一个`github`仓库

说说`logo`和`favicon`，我认为这两个非常重要，最好在网站推广前设计好。具体怎么设计，如果你是设计师出身，那大可不必担心。如果你非设计出身，那这方面的工作还是挺痛苦的。建议这里找专业设计师或者AI帮助你设计。不要让AI给你画设计图，这样基本没法用。让它给你画svg图像，并且给你代码，你用代码进行修改。介绍几个svg相关的工具和资源站：

- https://iconpark.oceanengine.com/home
- https://www.svgviewer.dev/
- https://yqnn.github.io/svg-path-editor/

## 开始编码

使用`svelte cli`创建项目。

```shell
npm create svelte@latest yourApp
```

因为我们需要编译为静态网站，因此将`@sveltejs/adapter-auto`修改为`@sveltejs/adapter-static`。

```shell
npm uninstall @sveltejs/adapter-auto
npm i -D @sveltejs/adapter-static
```

如果遇到`@sveltejs/adapter-static: all routes must be fully prerenderable, but found the following routes that are dynamic:`

在`routes`目录创建`+layout.ts`，添加：

```javascript
export const prerender = true;
```

至此，你可以愉快的编写前端代码了，这里我没有太多的建议可以给你，我以前是后端开发。不过如果你使用了`tailwind`，我会推荐[`flowbite`网站](https://flowbite.com/docs/getting-started/introduction/)，这里有很多开箱即用的组件。

## 访问统计

如果想添加网站用户流量分析，可以添加访问统计脚本。以下是添加`Google Analytics`的`svelte`组件代码。

```typescript
<script context="module" lang="ts">
    declare const window: Window & { dataLayer: any[]; };
</script>
<script lang="ts">
    import { onMount } from "svelte";
    const analyticsId = import.meta.env.VITE_ANALYTICS_ID;

    if (analyticsId) {
        onMount(async () => {
            window.dataLayer = window.dataLayer || [];
            window.dataLayer.push('js', new Date());
            window.dataLayer.push('config', analyticsId);
            var s = document.createElement('script');
            s.src = `https://www.googletagmanager.com/gtag/js?id=${analyticsId}`;
            s.async = true;
            document.head.append(s);
        });
    }
</script>
```

## 巧用环境变量

如果想让统计代码只有在生产环境启用，本地运行的时候不启用，可以使用环境变量来控制。以上面那段`Google Analytics`代码为例，此时你可以创建`.env.production`文件，在其中添加`VITE_ANALYTICS_ID`变量。这样当使用`vite build`命令进行构建的时候，就会搜索到环境变量了。

此功能`Cloudflare Pages`同样提供，你需要提前在上面设置。

![](imgs/posts/2024-09-10-lets-talk-about-website-building/1.webp)

## 自动生成sitemap

网站地图是搜索引擎索引你网站的向导，我们可以自己编写脚本实现。具体思路是每次编译完成后，写一个脚本自动将html页面收集起来生成`sitemap.xml`。

在`package.json`文件中添加`postbuild`命令：

```json
"scripts": {
		"dev": "vite dev",
		"build": "vite build",
		"postbuild": "node scripts/generate-sitemap.js"
	},
```

`generate-sitemap.js`内容如下：

```javascript
// scripts/generate-sitemap.js

import { fileURLToPath } from 'url';
import { dirname, resolve, join } from 'path';
import fs from 'fs';
import glob from 'glob';

// 获取当前模块文件的路径
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// 获取项目根目录的路径
const projectRoot = resolve(__dirname, '..');

// 设置 build 目录的路径
const buildDir = join(projectRoot, 'build');
const sitemapPath = join(buildDir, 'sitemap.xml');

// 生成 sitemap 的函数
function generateSitemap() {
    // 查找 build 目录下的所有 HTML 文件
    glob(`${buildDir}/**/*.html`, (err, files) => {
        if (err) {
            console.error('查找 HTML 文件时出错:', err);
            process.exit(1);
        }

        // 生成 sitemap 的 XML 内容
        const urls = files
        .map(file => {
            const url = file
                .replace(buildDir, '')
                .replace(/index.html$/, '')
                .replace(/\\/g, '/')
                .replace(/\.html$/, '');
            return `    <url><loc>https://your.site${url}</loc></url>`;
        }).join('\n');

        const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls}
</urlset>`;

        if (fs.existsSync(sitemapPath)) {
            console.log('sitemap.xml 已存在，将会被覆盖。');
        }

        // 将 sitemap 写入文件
        fs.writeFileSync(sitemapPath, sitemap, 'utf8');
        console.log('Sitemap 生成成功!');
    });
}

// 运行生成 sitemap 的函数
generateSitemap();
```

如此，每次运行`build`命令后，就会生成`sitemap`。

## 自动部署

测试的差不多以后先将代码提交到`github`。此时去`cloudflare`创建一个新的`pages`，并且按照提示连接到`github`仓库。然后设置“构建配置”：

![](imgs/posts/2024-09-10-lets-talk-about-website-building/2.webp)

如果你有自己的域名，在这里设置：

![](imgs/posts/2024-09-10-lets-talk-about-website-building/3.webp)

如此设置完后，以后每次提交代码到`github`，你的网站都会自动部署。

## 上线后

上线后第一件事当然是向各搜索引擎提交你的网站了，以`google`为例，访问https://search.google.com/search-console，将`sitemap`提交上去，然后就等待收录吧。

![](imgs/posts/2024-09-10-lets-talk-about-website-building/4.webp)

最后说下百度，百度对建在`ckoudflare`上的网站收录不友好，因此如果你的网站极度依赖百度收录，可能需要其它的方案。