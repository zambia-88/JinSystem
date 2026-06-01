@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo  JinSystem 开发模式
echo  ─────────────────────────────────────
echo  预览地址: http://localhost:5201/
echo  修改代码后会自动热更新
echo  按 Ctrl+C 停止
echo.

call npm run dev
