# JinSystem 一键同步 Excel 并 push 到 GitHub
param(
    [string]$Message = '',
    [switch]$SyncOnly,
    [switch]$NoPush,
    [switch]$Mining
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host '==> 1/3 同步 Excel -> Markdown' -ForegroundColor Cyan
python scripts/excel_to_md.py
if ($LASTEXITCODE -ne 0) {
    Write-Host '同步失败，已中止。' -ForegroundColor Red
    exit $LASTEXITCODE
}

if ($Mining) {
    Write-Host '==> 额外：同步矿业专题' -ForegroundColor Cyan
    python scripts/build_mining.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host '矿业同步失败，已中止。' -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

if ($SyncOnly) {
    Write-Host '==> 仅同步，跳过 git。' -ForegroundColor Yellow
    exit 0
}

Write-Host '==> 2/3 提交变更' -ForegroundColor Cyan
git add docs/ scripts/sidebar-data.json
if ($Mining) {
    git add docs/mining/ docs/public/media/mining/ 2>$null
}

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

Write-Host '==> 3/3 push 到 GitHub' -ForegroundColor Cyan
git push origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host 'push 失败，请检查网络或 git 凭据。' -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host ''
Write-Host '完成。约 2 分钟后访问 https://jinsystem.cn' -ForegroundColor Green
