# 推送 source/ 到私有库（不覆盖 Web Admin 维护的 permissions.json）
param(
    [string]$Remote = 'private',
    [string]$Branch = 'main'
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path 'source/docs')) {
    Write-Host '请先运行: npm run init:source' -ForegroundColor Red
    exit 1
}

$url = git -C $Root remote get-url $Remote 2>$null
if (-not $url) {
    Write-Host "未配置 git remote `"$Remote`"。请先：" -ForegroundColor Yellow
    Write-Host "  git remote add private https://github.com/zambia-88/JinSystem-source.git" -ForegroundColor Cyan
    exit 1
}

$Tmp = Join-Path $env:TEMP "JinSystem-private-push"
if (Test-Path $Tmp) { Remove-Item -Recurse -Force $Tmp }

$prevEap = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
git clone --depth 1 --branch $Branch $url $Tmp 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "克隆私有库失败，尝试空仓库初始化..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $Tmp | Out-Null
    Set-Location $Tmp
    git init 2>&1 | Out-Null
    git checkout -B $Branch 2>&1 | Out-Null
    git remote add origin $url 2>&1 | Out-Null
} else {
    Set-Location $Tmp
}
$ErrorActionPreference = $prevEap

# 更新内容（保留 permissions.json）
if (Test-Path source) { Remove-Item -Recurse -Force source }
Copy-Item -Recurse -Force (Join-Path $Root 'source') (Join-Path $Tmp 'source')
Copy-Item -Force (Join-Path $Root 'content-manifest.json') (Join-Path $Tmp 'content-manifest.json') -ErrorAction SilentlyContinue
Copy-Item -Recurse -Force (Join-Path $Root 'scripts') (Join-Path $Tmp 'scripts')
Copy-Item -Force (Join-Path $Root 'package.json') (Join-Path $Tmp 'package.json') -ErrorAction SilentlyContinue
Copy-Item -Force (Join-Path $Root 'requirements.txt') (Join-Path $Tmp 'requirements.txt') -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path (Join-Path $Tmp '.github/workflows') | Out-Null
Copy-Item -Force (Join-Path $Root '.github/workflows/sync-public.yml.template') (Join-Path $Tmp '.github/workflows/sync-public.yml')

if (-not (Test-Path (Join-Path $Tmp 'permissions.json'))) {
    if (Test-Path (Join-Path $Root 'permissions.json')) {
        Copy-Item -Force (Join-Path $Root 'permissions.json') (Join-Path $Tmp 'permissions.json')
    }
}

Set-Location $Tmp
$ErrorActionPreference = 'Continue'
git add source content-manifest.json scripts package.json requirements.txt .github
if (Test-Path permissions.json) { git add permissions.json }
git add -u 2>&1 | Out-Null
$commitMsg = "sync: private content $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
git diff --staged --quiet
if ($LASTEXITCODE -ne 0) {
    git commit -m $commitMsg 2>&1 | Out-Null
}
git push origin $Branch
if ($LASTEXITCODE -ne 0) {
    Write-Host "push failed: check GitHub credentials" -ForegroundColor Red
    exit $LASTEXITCODE
}
$ErrorActionPreference = $prevEap
Write-Host "已推送到 $Remote ($Branch)，permissions.json 未被本地覆盖" -ForegroundColor Green
