@echo off
echo ========================================
echo AI网页全自动批量处理工具 - 打包脚本
echo ========================================
echo.

echo [1/4] 检查 Python 环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo.
echo [2/4] 安装打包依赖...
pip install pyinstaller
if errorlevel 1 (
    echo 错误: 安装 pyinstaller 失败
    pause
    exit /b 1
)

echo.
echo [3/4] 安装 Playwright 浏览器...
playwright install chromium
if errorlevel 1 (
    echo 警告: Playwright 浏览器安装可能失败，程序可能无法正常运行
)

echo.
echo [4/4] 开始打包...
pyinstaller --clean build.spec

if errorlevel 1 (
    echo.
    echo 错误: 打包失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo 打包完成！
echo ========================================
echo.
echo 可执行文件位置: dist\AI网页全自动批量处理工具.exe
echo.
echo 使用说明:
echo 1. 双击运行 start_chrome_debug.bat 或 start_edge_debug.bat 启动浏览器
echo 2. 在浏览器中登录网页版AI平台
echo 3. 双击运行 dist\AI网页全自动批量处理工具.exe
echo.
pause
