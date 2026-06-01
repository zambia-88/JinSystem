@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo  JinSystem 本地预览
echo  ─────────────────────────────────────
echo  请勿双击 dist\index.html（会导致样式丢失）
echo  本脚本会构建并通过 HTTP 服务预览
echo.

call npm run build
if errorlevel 1 (
  echo 构建失败，请检查上方错误信息。
  pause
  exit /b 1
)

echo.
echo  预览地址: http://localhost:4173/
echo  （若 4173 被占用，请看终端里实际端口）
echo  按 Ctrl+C 停止
echo.

call npm run preview
