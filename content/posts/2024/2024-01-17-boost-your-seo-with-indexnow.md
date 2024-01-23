---
author: "路边的阿不"
title: 使用IndexNow提升Github Pages网站SEO
slug: boost-your-seo-with-indexnow
description: "Learn how to optimize SEO for your Github Pages site by using IndexNow. From understanding the purpose of SEO to detailed steps on applying IndexNow, enhance your website visibility efficiently!"
date: 2024-01-17 14:42:30
draft: false
ShowToc: true
TocOpen: true
tags: ["Cloudflare", "Github Pages", "SEO", "IndexNow"]
categories: ["建站"]
---

我之前写过[一篇文章](https://babyno.top/posts/2023/11/new-hugo-blog/)，介绍了[本站](https://babyno.top/)是使用`Hugo`进行构建并发布在`Github Pages`上的。也向大家介绍过将网站提交给搜索引擎的方法，但是手工提交未免繁琐和低效。今天给大家介绍下如何通过`IndexNow` 对网站进行`SEO`优化。

## SEO的作用

**搜索引擎优化 (SEO)** 对于网站的重要性无法忽视。如果你想让你的网站获得更多的曝光，那么你需要理解 `SEO` 的作用，以及它是如何帮助你获得更高的搜索引擎排名的。以下是使用 `SEO` 的 5 大理由：

1. 提高可见性
2. 提高网站流量
3. 提供用户友好的体验
4. 建立信任和信誉
5. 获得竞争优势

## IndexNow介绍

`IndexNow`是一个开源协议，由微软提出并开发。它使网站无论是新增页面，更新页面或删除页面，发布者都可以使用 `IndexNow` 协议将这些更新快速推送至搜索引擎。

对于 `SEO`，`IndexNow` 有着直接的影响。使用 `IndexNow` 的网站可以使其内容更快地呈现在搜索结果中，从而提高网站的 `SEO` 排名。由于搜索结果的新鲜度是影响 `SEO` 的一个重要因素，因此 `IndexNow` 的使用对于 `SEO` 而言具有重大价值。

另一个巨大优势在于：支持 `IndexNow` 协议的搜索引擎会立即共享数据至其它的搜索引擎，因此您只需通知其中一个搜索引擎即可。目前支持的搜索引擎有：`Bing`，`Naver`，`Seznam.cz`，`Yandex`。

## 接入准备

访问[https://www.bing.com/indexnow](https://www.bing.com/indexnow)，上面给出了接入步骤分为4步：

- Generate API Key
- Host API key
- Submit URLs with parameters
- Get details on how many submitted

实际上准备工作就是上面的步骤1和步骤2。在上面的网站上生成一个`API Key` （按钮1），下载`API Key`文件（按钮2），最后将文本文件放置在你的网站根目录下。

![IndexNow Implementation Steps](imgs/posts/2024-01-17-boost-your-seo-with-indexnow/Untitled.webp)

IndexNow Implementation Steps

这样准备工作就完成了。

## 利用Github Actions自动提交

由于我的网站是通过`Hugo` 在本地生成静态页面，然后推送到仓库，通过`Guthub Actions`部署到`Github Pages`上的，因此我这里做了如下改动：

- 写了一个`python`脚本，读取`sitemap`里最近更新的10篇文章的`url`。构建一个`POST`请求，将`url`提交给`IndexNow`。
- 新增加一个`workflow` ，在代码推送至仓库时，调用上面这个`python`脚本。

代码参考：

```python
def get_latest_posts(sitemap_path, n=10):
    # Parse the XML sitemap.
    tree = ET.parse(sitemap_path)
    root = tree.getroot()

    # Namespace dictionary to find the 'loc' and 'lastmod' tags.
    namespaces = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

    # Get all URLs.
    urls = [(url.find('s:loc', namespaces).text, url.find('s:lastmod', namespaces).text)
            for url in root.findall('s:url', namespaces)
            if "/posts/2" in url.find('s:loc', namespaces).text]

    # Sort URLs by the lastmod tag (in descending order), hence most recent pages come first.
    urls.sort(key=lambda x: x[1], reverse=True)

    # Return the n most recent URLs.
    return [url[0] for url in urls[:n]]

def ping_bing(url_list):
    # Prepare the URL and headers.
    url = 'https://www.bing.com/indexnow'
    headers = {
      'Content-Type': 'application/json; charset=utf-8',
    }

    # Prepare the body data.
    data = {
      "host": HOST,
      "key": KEY,
      "keyLocation": f"https://{HOST}/{KEY}.txt",
      "urlList": url_list
    }

    # Send the POST request.
    response = requests.post(url, headers=headers, json=data)
    return response

if __name__ == "__main__":

    sitemap_path = "../sitemap.xml"
    url_list = get_latest_posts(sitemap_path, 9)
    url_list.insert(0, f'https://{HOST}/')
    print(url_list)

    response = ping_bing(url_list)
    # Print the response.
    print(response.status_code)
    print(response.text)
```

```yaml
# Simple workflow for deploying static content to GitHub Pages
name: Submit IndexNow Request To Bing

on:
  # Runs on pushes targeting the default branch
  push:
    branches: ["main"]
  # Allows you to run this workflow manually from the Actions tab
  workflow_dispatch:

jobs:
  indexnow:
    name: IndexNow
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: 3.11

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install requests

      - name: Run script
        run: |
          cd .github
          python ping_bing.py
```

最后查看下效果，登录[Bing Webmaster Tools](https://www.bing.com/webmasters/indexnow)，选择左边菜单栏的`IndexNow`：

![IndexNow on Bing Webmaster Tools](imgs/posts/2024-01-17-boost-your-seo-with-indexnow/Untitled%201.webp)

IndexNow on Bing Webmaster Tools

## ****使用 Cloudflare 集成 IndexNow****

`Cloudflare`已经集成了`IndexNow`，[https://blog.cloudflare.com/cloudflare-now-supports-indexnow](https://blog.cloudflare.com/cloudflare-now-supports-indexnow)。所以如果你的网站是托管在`Cloudflare`上的，可以直接在控制台里设置。这个功能免费用户可用。

1. Sign in to your Cloudflare Account.
2. In the dashboard, navigate to the **Cache tab.**
3. Click on the **Configuration** section.
4. Locate the Crawler Hints sign up card and enable. It's that easy.

![Cloudflare Crawler Hints](imgs/posts/2024-01-17-boost-your-seo-with-indexnow/Untitled%202.webp)

Cloudflare Crawler Hints

但是有个奇怪的地方，我没有用`Cloudflare Pages`进行网站托管，仅仅使用了它的`DNS`解析，开启`Crawler Hints`后，效果很差。它并不能将我的文章`url`准确推送给`IndexNow`，相反推送的是一些图片和`txt`文件。