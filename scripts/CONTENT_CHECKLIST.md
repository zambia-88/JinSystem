# Excel 填表 Checklist · JinSystem 内容维护

> 数据源：`F:\我的桌面{F盘}\个人知识库\个人知识库2025-2035.xlsx`  
> 一键发布：双击 `publish.bat`，或在网站目录运行 `npm run publish`

---

## 一、新增一条内容

在对应 **Sheet** 最后一行填写（Sheet 名见下表）：

| 列名 | 必填 | 说明 |
|------|------|------|
| **主题/标题** | ✅ | 文章标题 |
| **核心内容简述** | ✅ | 正文（可换行） |
| 序号 | 建议 | 填数字，用于稳定文件名（如 `015-标题.md`） |
| 记录日期 | 可选 | 首页排序用 |
| 来源/出处 | 可选 | 文末显示来源 |
| 个人感悟 | 可选 | 生成「个人感悟」小节 |
| 封面 | 可选 | 如 `/media/images/covers/xxx.jpg` |
| 上线 | 可选 | **已废弃** — 公开/非公开请在 Web 管理页设置（见 SETUP-PRIVATE-REPO.md） |

**对应 Sheet：**

| Sheet 名 | 网站栏目 |
|----------|----------|
| 格局提升 | `/cognition/mindset/` |
| 人性洞察 | `/cognition/insight/` |
| 人工智能 | `/tools/ai/` |
| Excel | `/tools/excel/` |
| Word | `/tools/word/` |
| PPT | `/tools/ppt/` |
| 日常生活 | `/life/daily/` |
| 旅游 | `/life/travel/` |

填完后 → **保存 Excel** → 运行 `npm run publish`（或双击 `publish.bat`）。

---

## 二、删除 / 下线一条内容

任选 **一种** 方式（最简单：直接删行）：

| 方式 | 操作 |
|------|------|
| **A. 删行** | 在 Excel 中删除整行 → 保存 → `npm run publish` |
| **B. 标记删除** | 「删除」列填 **是** → 保存 → `npm run publish` |
| **C. 暂时下线** | 「上线」列填 **否** → 保存 → `npm run publish`（以后改回空或「是」可恢复） |

同步脚本会自动删除网站上对应的 `.md` 并更新侧边栏。

---

## 三、修改已有内容

1. 在 Excel 找到对应行，改标题/正文等  
2. 保存 Excel  
3. `npm run publish`

> 若改了「序号」或「标题」，文件名可能变化；旧文件会在同步时被自动清理。

---

## 四、一键发布流程

`publish.bat` / `npm run publish` 会依次：

1. `python scripts/excel_to_md.py` — Excel → Markdown + 侧边栏  
2. `git add` + `git commit`（有变更时）  
3. `git push origin main` — 触发 GitHub Pages 部署  

**可选参数（PowerShell）：**

```powershell
npm run publish -- -SyncOnly          # 只同步，不提交
npm run publish -- -NoPush            # 提交但不 push
npm run publish -- -Message "content: 更新 Excel 技巧"
npm run publish -- -Mining            # 同步后额外运行矿业脚本
```

---

## 五、矿业 / 手工页面（不走 Excel）

| 类型 | 操作 |
|------|------|
| 矿业 docx | 更新源文件 → `npm run mining` → 手动 git push |
| Now / 关于 / 社区等 | 直接改 `docs/` 下 `.md` → git commit + push |

---

## 六、发布前自检（30 秒）

- [ ] Excel 已保存  
- [ ] 新增行「主题/标题」「核心内容简述」已填  
- [ ] 要删除的行已删行或「删除」= 是  
- [ ] 本地可选：`npm run dev` 打开 http://localhost:5201 看一眼  
- [ ] 运行 `npm run publish`  
- [ ] 约 2 分钟后访问 https://jinsystem.cn 确认  

---

## 七、留言审核（与 Excel 无关）

- 后台：https://jin-system.vercel.app/ui  
- 新留言需审核通过后才会在页面显示  
