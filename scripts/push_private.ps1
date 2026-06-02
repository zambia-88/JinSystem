# 将 source/ + permissions.json 推送到私有 GitHub 仓库
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

$Tmp = Join-Path $env:TEMP "JinSystem-private-push"
if (Test-Path $Tmp) { Remove-Item -Recurse -Force $Tmp }
New-Item -ItemType Directory -Path $Tmp | Out-Null

Copy-Item -Recurse -Force source (Join-Path $Tmp 'source')
Copy-Item -Force permissions.json, content-manifest.json, package.json, requirements.txt -Destination $Tmp -ErrorAction SilentlyContinue
Copy-Item -Recurse -Force scripts (Join-Path $Tmp 'scripts')
New-Item -ItemType Directory -Force -Path (Join-Path $Tmp '.github/workflows') | Out-Null
Copy-Item -Force '.github/workflows/sync-public.yml.template' (Join-Path $Tmp '.github/workflows/sync-public.yml')

Set-Location $Tmp
$prevEap = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
git init 2>&1 | Out-Null
git checkout -B $Branch 2>&1 | Out-Null
git add source permissions.json content-manifest.json scripts package.json requirements.txt .github 2>&1 | Out-Null
$commitMsg = "sync: private content $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
git commit -m $commitMsg 2>&1 | Out-Null
$ErrorActionPreference = $prevEap

$url = git -C $Root remote get-url $Remote 2>$null
if (-not $url) {
    Write-Host "未配置 git remote `"$Remote`"。请先：" -ForegroundColor Yellow
    Write-Host "  git remote add private https://github.com/zambia-88/JinSystem-source.git" -ForegroundColor Cyan
    exit 1
}

git remote add origin $url 2>&1 | Out-Null
$ErrorActionPreference = 'Continue'
git push -u origin $Branch --force
if ($LASTEXITCODE -ne 0) {
    Write-Host "push failed: check GitHub credentials" -ForegroundColor Red
    exit $LASTEXITCODE
}
$ErrorActionPreference = $prevEap
Write-Host "已推送到 $Remote ($Branch)" -ForegroundColor Green
