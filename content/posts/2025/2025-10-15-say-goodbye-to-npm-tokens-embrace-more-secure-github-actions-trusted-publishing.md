---
author: "路边的阿不"
title: 告别npm令牌，拥抱更安全的GitHub Actions可信发布
slug: say-goodbye-to-npm-tokens-embrace-more-secure-github-actions-trusted-publishing
description: ""
date: 2025-10-15 09:53:33
draft: false
ShowToc: true
TocOpen: true
tags:
  - Secure
  - Tutorial
categories:
  - 网络安全
---

近期，npm 启动了一系列旨在增强生态系统安全性的重要更新。核心变化之一是逐步淘汰传统的、长期有效的经典访问令牌，并鼓励开发者转向一种更安全、更现代的发布方式：**可信发布 (Trusted Publishing)**。

如果你还在 CI/CD 工作流中使用 `NPM_TOKEN`，那么现在是时候进行升级了。本教程将引导你完成从传统令牌发布到将 GitHub Actions 设置为可信发布者的完整迁移过程。

## 为什么需要改变？

传统的 npm 令牌存在几个关键安全风险：
*   **长期有效**：一旦泄露，攻击者可以持续访问你的账户，直到令牌被手动撤销。
*   **权限过大**：经典令牌通常拥有账户的完全写入权限，远超发布所需。
*   **泄露风险**：这些令牌必须作为 `secret` 存储在 CI/CD 平台中，存在因配置不当或在日志中意外暴露的风险。

可信发布通过 OpenID Connect (OIDC) 解决了这些问题。它在 npm 和你的 CI/CD 提供商（如 GitHub Actions）之间建立信任关系，允许你的工作流通过临时的、自动生成的短效凭据进行身份验证，从而彻底告别长期令牌。

## 迁移步骤

迁移过程非常简单，只需在 npmjs.com 上进行配置，并对你的 GitHub Actions 工作流文件进行少量修改。

### 第 1 步：在 npmjs.com 上配置可信发布者

1.  登录 [npmjs.com](https://www.npmjs.com) 并导航到你想要配置的包。
2.  进入包的 “**Settings**”（设置）页面。
3.  在侧边栏找到 “**Trusted Publishers**”（可信发布者）部分。
4.  在 “**Select your publisher**”（选择你的发布者）下，点击 **GitHub Actions** 按钮。
5.  填写以下字段：
    *   **Organization or user**：你的 GitHub 用户名或组织名。
    *   **Repository**：你的仓库名称。
    *   **Workflow filename**：你用于发布的工作流文件名（例如 `publish.yml` 或 `release.yml`）。**注意：** 只需填写文件名，且必须包含 `.yml` 或 `.yaml` 扩展名。
    *   **Environment name** (可选)：如果你使用了 GitHub Environments 来保护部署，请填写环境名称。

![GitHub Actions 可信发布者配置表单](https://docs.npmjs.com/packages-and-modules/securing-your-code/trusted-publisher-github-actions.png)

配置完成后，npm 就准备好接受来自你指定 GitHub Actions 工作流的发布请求了。

### 第 2 步：更新你的 GitHub Actions 工作流

接下来，修改你的发布工作流 `.yml` 文件。

**修改前：**
你当前的工作流可能如下所示，依赖于 `secrets.NPM_TOKEN`：

```yaml
name: Publish Package

on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          registry-url: 'https://registry.npmjs.org'
      - run: npm ci
      - run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

**修改后：**
你需要进行以下三处关键改动：

1.  **移除 `NODE_AUTH_TOKEN`**：`npm publish` 步骤不再需要它。
2.  **添加 `permissions`**：在工作流顶部或 `job` 级别添加 `permissions` 块，并授予 `id-token: write` 权限。这是允许 GitHub Actions 生成 OIDC 令牌的关键。
3.  **(可选但推荐) 确保 npm 版本**：可信发布需要 `npm` CLI `v11.5.1` 或更高版本。添加一个步骤来更新 npm 是一个好习惯。

```yaml
name: Publish Package

on:
  push:
    tags:
      - 'v*'

# 1. 添加 OIDC 令牌所需的权限
permissions:
  id-token: write
  contents: read

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          registry-url: 'https://registry.npmjs.org'

      # 2. (推荐) 确保 npm 版本足够新
      - name: Update npm
        run: npm install -g npm@latest

      - run: npm ci
      
      # 3. 直接运行 npm publish，无需令牌
      - run: npm publish
```

提交这些更改后，当你的工作流再次运行时，`npm publish` 命令会自动检测 OIDC 环境并使用它进行身份验证。

## 如何处理私有依赖？

一个常见的场景是，你的项目依赖于私有的 npm 包。请注意，**可信发布仅适用于 `npm publish` 命令**。对于安装私有依赖（例如运行 `npm ci`），你仍然需要一个令牌。

最佳实践是创建一个**只读 (Read-only)** 的细粒度访问令牌，并将其用于安装依赖。这样即使令牌泄露，其危害也极其有限。

你的工作流将如下所示：

```yaml
# ... (前面的配置相同)
permissions:
  id-token: write
  contents: read

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      # ... (checkout, setup-node, update npm)

      # 使用只读令牌安装私有依赖
      - run: npm ci
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_READ_ONLY_TOKEN }}

      # 发布时无需令牌，将自动使用 OIDC
      - run: npm publish
```

## 最后一步：锁定包以获得最高安全性

在你成功通过可信发布发布了一个版本后，为了最大化安全性，建议你在 npm 上禁止该包使用传统令牌进行发布。

1.  再次进入包的 **Settings** → **Publish Access**。
2.  选择 **“Require two-factor authentication and forbid tokens”** （要求双重身份验证并禁止令牌）。
3.  点击 **Update package settings** 保存。

此设置不会影响你的可信发布工作流，但会阻止任何人（包括你自己）使用传统令牌发布此包的新版本。

## 迁移的好处

*   **无需再管理 `NPM_TOKEN`**：你可以从 GitHub `secrets` 中删除旧的发布令牌。
*   **显著提升安全性**：消除了因长期令牌泄露而导致账户被盗用的风险。
*   **自动生成来源证明**：当你使用可信发布时，npm 会自动为你的包生成来源证明 (provenance)，这向你的用户提供了关于包构建来源和方式的可验证信息，极大地增强了供应链的安全性。

## 总结

npm 正在向更安全的未来迈进，而迁移到可信发布是其中至关重要的一步。这个过程不仅简单，而且能从根本上消除一整类常见的安全漏洞。请尽快检查你的发布工作流，并按照本教程进行迁移，以确保你的包和用户都能得到更好的保护。