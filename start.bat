@echo off
echo ==============================
echo   证件照生成工具 - 快捷启动
echo ==============================
echo.

cd /d "%~dp0"

echo [1/2] 安装依赖...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo 依赖安装失败，请检查 Python 和 pip 是否可用
    pause
    exit /b 1
)

echo [2/2] 启动服务...
echo.
echo 启动完成后访问: http://localhost:8000
echo 按 Ctrl+C 停止服务
echo.
python run.py

