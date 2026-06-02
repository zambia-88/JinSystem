# 私有仓库与 Web 权限管理 · 分步引导

> 目标：非公开内容 **不进** 公开仓库 `zambia-88/JinSystem`，只在私有库 `JinSystem-source`；Web 端切换公开/非公开后 **自动部署**。

---

## 一、本地先跑通（公开仓库内已完成脚本）

在 PowerShell 中：

```powershell
Set-Location -LiteralPath "F:\我的桌面{F盘}\个人知识库\website"

# 1. 复制当前 docs → source/docs（仅首次）
npm run init:source

# 2. 生成 permissions.json + content-manifest.json（首次会将现有内容标为公开）
npm run init:permissions

# 3. 按权限生成公开 docs/
npm run build:public

# 4. 验证站点
npm run build
```

之后日常发布：

```powershell
npm run publish
```

`publish` 会：Excel → `source/` → 过滤 → 只 push **公开** `docs/` 到 GitHub。

---

## 二、创建私有 GitHub 仓库

1. 打开 https://github.com/new  
2. **Repository name**：`JinSystem-source`  
3. 选择 **Private**  
4. 不要勾选 “Add a README”（空仓库即可）  
5. 点击 **Create repository**

---

## 三、把私有内容 push 到私有库

在 PowerShell（仍在 `website` 目录）：

```powershell
# 初始化私有库远程（只需一次）
git remote add private https://github.com/zambia-88/JinSystem-source.git

# 从公开库当前分支创建私有库专用分支内容
git subtree split --prefix=website -b private-source 2>$null

# 更简单的方式：直接在新目录推送私有文件
```

**推荐做法**（更直观）：

```powershell
# 在 website 上一级建私有库工作副本
cd "F:\我的桌面{F盘}\个人知识库"
git clone https://github.com/zambia-88/JinSystem-source.git JinSystem-source
cd JinSystem-source

# 复制私有文件（不要复制 node_modules / docs 公开输出）
xcopy /E /I /Y "..\website\source" "source"
copy /Y "..\website\permissions.json" .
copy /Y "..\website\content-manifest.json" .
xcopy /E /I /Y "..\website\scripts" "scripts"
copy /Y "..\website\package.json" .
copy /Y "..\website\requirements.txt" .

mkdir .github\workflows 2>$null
copy /Y "..\website\.github\workflows\sync-public.yml.template" ".github\workflows\sync-public.yml"

git add source permissions.json content-manifest.json scripts package.json requirements.txt .github
git commit -m "init: 私有内容库与权限配置"
git push -u origin main
```

---

## 四、创建 GitHub Personal Access Token

1. GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Fine-grained tokens**  
2. **Repository access**：选中 `JinSystem-source` 与 `JinSystem`  
3. **Permissions**：
   - Contents: Read and write  
   - Actions: Read and write  
4. 生成后 **复制 Token**（只显示一次）

---

## 五、配置私有库 Secrets

进入 `JinSystem-source` → **Settings** → **Secrets and variables** → **Actions**：

| Name | 值 |
|------|-----|
| `PUBLIC_REPO_TOKEN` | 上一步的 PAT（需能 push 公开库） |
| `PUBLIC_REPO` | `zambia-88/JinSystem` |

---

## 六、部署 Admin 管理页（Vercel）

1. 打开 https://vercel.com → **Add New Project**  
2. 导入 `JinSystem` 仓库，**Root Directory** 设为 `admin-server`（若 admin 在 website 子目录则选 `website/admin-server`）  
3. **Environment Variables**：

| 变量 | 值 |
|------|-----|
| `ADMIN_PASSWORD` | 你的管理密码（仅你知道） |
| `ADMIN_SECRET` | 随机长字符串（用于会话签名） |
| `GITHUB_TOKEN` | 同上 PAT |
| `GITHUB_PRIVATE_REPO` | `zambia-88/JinSystem-source` |
| `GITHUB_PUBLIC_REPO` | `zambia-88/JinSystem` |
| `GITHUB_BRANCH` | `main` |
| `GITHUB_WORKFLOW_FILE` | `sync-public.yml` |

4. Deploy 完成后，按下一节绑定 **`admin.jinsystem.cn`**。

### 6.1 绑定 admin.jinsystem.cn（推荐）

#### A. 在 Vercel 添加域名

1. 打开 Vercel → 你的 Admin 项目（如 `jin-system-azsi`）  
2. **Settings** → **Domains**  
3. 输入 `admin.jinsystem.cn` → **Add**  
4. Vercel 会显示需要添加的 DNS 记录（通常是 CNAME）

#### B. 在域名 DNS 控制台添加记录

登录 **jinsystem.cn** 的 DNS 管理（阿里云 / Cloudflare / 腾讯云等）：

| 类型 | 主机记录 | 记录值 |
|------|----------|--------|
| **CNAME** | `admin` | `cname.vercel-dns.com` |

> 以 Vercel Domains 页面显示的为准；若已有冲突的 `admin` A 记录，请先删除。

#### C. 等待生效

- DNS 传播：通常 **5–30 分钟**  
- Vercel 自动签发 HTTPS 证书  
- Domains 页显示 **Valid Configuration** 即可访问  

#### D. 访问

浏览器打开：**https://admin.jinsystem.cn**  
用 `ADMIN_PASSWORD` 登录即可管理公开 / 非公开权限。

#### 常见问题

| 现象 | 处理 |
|------|------|
| 域名未生效 | 检查 CNAME 是否指向 Vercel，等待 DNS 传播 |
| SSL 证书失败 | 确认无其他 CDN 占用 `admin` 子域 |
| 登录后 503 | 私有库需有 `content-manifest.json` |
| API 401 | 检查 Vercel 环境变量是否完整 |


## 七、Web 端使用

1. 打开 Admin 页面 → 输入 `ADMIN_PASSWORD`  
2. 列表中切换 **公开 / 非公开**  
3. 保存后自动触发 `sync-public.yml`：  
   - 私有库 `build_public.py` → 生成公开 `docs/`  
   - Push 到公开库 → GitHub Pages 部署  

**默认规则（已写入代码）：**

- **7b** 新 Excel 条目：默认 **非公开**  
- **8b** 手工页面：默认 **公开**  

---

## 八、日常维护流程

| 操作 | 做法 |
|------|------|
| 新增 Excel 内容 | 本地 `npm run publish` → 再 push `source/` + `permissions.json` 到 **私有库** |
| 改权限 | Web Admin 点开关（自动部署） |
| 改手工页 | 编辑 `source/docs/...` → push 私有库 → Admin 点「手动部署」或 push 触发 CI |

---

## 九、故障排查

| 现象 | 检查 |
|------|------|
| Admin 503 manifest 不存在 | 私有库是否已有 `content-manifest.json` |
| 切换后站点未变 | GitHub Actions `sync-public.yml` 是否成功 |
| 非公开仍能被搜到 | 确认公开库 `docs/` 中无对应 `.md` |

---

## 十、文件归属

| 文件/目录 | 公开库 JinSystem | 私有库 JinSystem-source |
|-----------|------------------|-------------------------|
| `docs/`（过滤后） | ✅ | ❌ |
| `source/` | ❌ gitignore | ✅ |
| `permissions.json` | ❌ | ✅ |
| `content-manifest.json` | ❌ | ✅ |
| `admin-server/` | ✅（仅 API 代码） | 可选 |

完成以上步骤后，在 Admin 回复「私有库已建好」我可帮你远程验证 Actions 与首屏列表。
