# JinSystem 一键同步 Excel → source → 公开 docs → push 到 GitHub
param(
    [string]$Message = '',
    [switch]$SyncOnly,
    [switch]$NoPush,
    [switch]$Mining
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path 'source/docs')) {
    Write-Host '==> 首次运行：初始化 source/docs' -ForegroundColor Yellow
    python scripts/init_source.py
    python scripts/init_permissions.py
}

Write-Host '==> 1/4 同步 Excel -> source/docs' -ForegroundColor Cyan
python scripts/excel_to_md.py
if ($LASTEXITCODE -ne 0) {
    Write-Host '同步失败，已中止。' -ForegroundColor Red
    exit $LASTEXITCODE
}

if ($Mining) {
    Write-Host '==> 额外：同步矿业专题 -> source/docs' -ForegroundColor Cyan
    python scripts/build_mining.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host '矿业同步失败，已中止。' -ForegroundColor Red
        exit $LASTEXITCODE
    }
    python scripts/init_permissions.py
}

Write-Host '==> 2/4 按权限生成公开 docs/' -ForegroundColor Cyan
python scripts/build_public.py
if ($LASTEXITCODE -ne 0) {
    Write-Host 'build_public 失败，已中止。' -ForegroundColor Red
    exit $LASTEXITCODE
}

if ($SyncOnly) {
    Write-Host '==> 仅同步，跳过 git。' -ForegroundColor Yellow
    exit 0
}

Write-Host '==> 3/4 提交公开内容（不含 source/ 私有库）' -ForegroundColor Cyan
git add docs/ scripts/sidebar-data.json
git add docs/.vitepress/posts.json 2>$null

$Status = git status --porcelain
if (-not $Status) {
    Write-Host '无文件变更，跳过 commit / push。' -ForegroundColor Yellow
    exit 0
}

if (-not $Message) {
    $Date = Get-Date -Format 'yyyy-MM-dd'
    $Message = "content: sync $Date"
}

git commit -m $Message
if ($LASTEXITCODE -ne 0) {
    Write-Host 'commit 失败。' -ForegroundColor Red
    exit $LASTEXITCODE
}

if ($NoPush) {
    Write-Host '==> 已提交，未 push（-NoPush）。' -ForegroundColor Yellow
    exit 0
}

Write-Host '==> 4/4 push 到 GitHub（公开仓库）' -ForegroundColor Cyan
git push origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host 'push 失败，请检查网络或 git 凭据。' -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host ''
Write-Host '完成。公开内容已 push；source/ 与 permissions.json 请同步到私有仓库。' -ForegroundColor Green
Write-Host '约 2 分钟后访问 https://jinsystem.cn' -ForegroundColor Green
