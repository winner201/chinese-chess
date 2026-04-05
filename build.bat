@echo off
echo ==========================================
echo   中国象棋 - Windows 一键打包脚本
echo ==========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未安装Python，请从 https://python.org 下载安装
    pause
    exit /b 1
)

REM 安装依赖
echo [1/3] 安装依赖（pygame）...
pip install pygame pyinstaller -q
if errorlevel 1 (
    echo [错误] 依赖安装失败，请以管理员身份运行
    pause
    exit /b 1
)

REM 打包
echo [2/3] 正在打包，请稍候...
pyinstaller --onefile --windowed --name "中国象棋" --add-data ".;." chinese_chess.py -q

echo [3/3] 完成！
echo.
echo 游戏文件: dist\中国象棋.exe
echo 按任意键打开目录...
explorer dist
pause
