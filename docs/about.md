---
title: 关于
---

# 关于 JinSystem

**JinSystem** 是基于 Excel 知识库自动生成的个人认知站点，遵循一个简单原则：

> **物质低配 · 认知高配 · 心态顶配**

## 内容范围

本站仅发布可公开分享的内容，包括：

- 格局提升与人性洞察
- AI 与 Office 效率工具
- 生活技巧与旅行笔记

情绪日记、投资记录、创业细节等私密内容**不会**出现在本站。

## 更新方式

1. 在 Excel 中维护 `个人知识库2025-2035.xlsx`
2. 运行 `npm run sync` 同步 Markdown
3. 运行 `npm run dev` 本地预览，或 `npm run build` 构建静态站

## 技术栈

- [VitePress](https://vitepress.dev/) — 静态知识库站点
- Python + openpyxl — Excel 导出

## GitHub Pages 部署

### 访问地址

**https://zambia-88.github.io/JinSystem/**

仓库名须为 **`JinSystem`**，与站点路径一致。

### 首次发布

1. 在 GitHub 新建仓库 **`JinSystem`**（或推送至已有同名仓库）
2. 将 `website` 目录**内的全部文件**推送到 `main` 分支
3. 打开 **Settings → Pages → Build and deployment**
4. **Source** 选择 **GitHub Actions**
5. 推送后等待 Actions 完成，访问上方地址

### 本地推送示例

```powershell
cd "F:\我的桌面{F盘}\个人知识库\website"
git init
git add .
git commit -m "feat: JinSystem 个人知识库站点"
git branch -M main
git remote add origin https://github.com/zambia-88/JinSystem.git
git push -u origin main
```

本地开发预览地址为 `http://localhost:5173/`；线上构建会自动使用 `/JinSystem/` 路径。

若远程仓库已有内容，先执行 `git pull origin main --rebase` 再 push。

### 日常更新

```powershell
npm run sync          # Excel 变更后同步 Markdown
git add docs scripts
git commit -m "content: 同步知识库"
git push
```

推送后 GitHub Actions 会自动重新部署，无需手动上传。
