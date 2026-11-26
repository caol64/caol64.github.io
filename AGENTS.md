# 项目协作指南

## 项目概览

这是一个使用 Hugo 构建、通过 GitHub Pages 发布的多语言技术博客：

- 站点配置：`hugo.yml`
- 中文文章：`content/posts/**/*.md`
- 英文文章：通常使用同名 `.en.md` 文件
- 文章模板：`archetypes/post.md`
- 静态资源：`static/`
- 自定义主题样式：`assets/`
- 主题：`themes/PaperMod/`
- 生成目录：`public/`（不要手工编辑，也不要提交构建产物）

## 基本原则

- 优先保持现有目录结构、文章格式和 Hugo 配置风格。
- 文章内容以 Markdown 为主，沿用现有的 YAML front matter 字段和命名方式。
- 不要修改 `themes/PaperMod/` 中的通用主题代码来解决仅适用于本站的问题；优先使用 `layouts/`、`assets/` 或站点配置覆盖。
- 不要把 `.venv/`、`public/`、`.hugo_build.lock` 或本地工具生成的临时文件加入版本控制。
- 保留与文章对应的图片、音频等资源路径；新增文章资源优先放在 `static/imgs/` 或文章现有的资源目录中。
- 只修改与当前任务相关的文件，不要覆盖工作区中已有的未提交改动。

## AI Agent 工作流程

如果接收到的是“写作或改写”任务，读取`.agents/skills/agile-content-architect`技能，它们是标准动作流程。

**特别注意**：如果接收到的是“写作或改写”任务，无需继续以下工作。

## 本地开发与验证

需要预览文章时运行：

```bash
hugo server -D
```

执行生产构建时运行：

```bash
hugo --minify
```

生产构建命令应成功完成，且重点检查：

- 新文章是否能被 Hugo 识别；
- front matter 是否有效；
- 图片、音频等资源路径是否正确；
- 中英文页面和导航是否出现异常；
- 没有误修改或提交 `public/` 构建产物。

GitHub Actions 使用 Hugo `0.125.7` 执行 `hugo --minify`，本地遇到版本相关问题时应优先使用相同版本验证。

## 样式与模板

- 站点级样式放在 `assets/css/extended/`，遵循现有 CSS 文件的组织方式。
- 页面模板和局部覆盖放在 `layouts/`，不要直接改主题文件，除非任务明确要求更新主题。
- 修改 `hugo.yml` 时保持现有语言配置、菜单、永久链接和输出格式不变，除非这些内容属于任务范围。

## 提交前检查

提交前查看：

```bash
git status --short
git diff --check
```

确认 diff 只包含任务相关的变更，并避免提交生成文件、编辑器配置变更和敏感信息。
