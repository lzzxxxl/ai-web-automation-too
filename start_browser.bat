@echo off
chcp 65001

:: 启动浏览器并开启远程调试模式
:: 默认端口9222

echo ========================================
echo 浏览器启动脚本
echo ========================================
echo.
echo 请选择要启动的浏览器：
echo 1. Chrome
echo 2. Edge
echo 3. Firefox
echo.
set /p choice=请输入选项 (1-3): 

echo.
set PORT=9222

if "%choice%"=="1" (
    echo 启动 Chrome 浏览器...
    :: 查找Chrome可执行文件路径
    if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
        set BROWSER_PATH="%ProgramFiles%\Google\Chrome\Application\chrome.exe"
    ) else if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
        set BROWSER_PATH="%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
    ) else (
        echo 未找到Chrome浏览器可执行文件
        pause
        exit /b 1
    )
    %BROWSER_PATH% --remote-debugging-port=%PORT% --user-data-dir="./browser_profile"
) else if "%choice%"=="2" (
    echo 启动 Edge 浏览器...
    :: 查找Edge可执行文件路径
    if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" (
        set BROWSER_PATH="%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
    ) else if exist "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" (
        set BROWSER_PATH="%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
    ) else (
        echo 未找到Edge浏览器可执行文件
        pause
        exit /b 1
    )
    %BROWSER_PATH% --remote-debugging-port=%PORT% --user-data-dir="./browser_profile"
) else if "%choice%"=="3" (
    echo 启动 Firefox 浏览器...
    :: 查找Firefox可执行文件路径
    if exist "%ProgramFiles%\Mozilla Firefox\firefox.exe" (
        set BROWSER_PATH="%ProgramFiles%\Mozilla Firefox\firefox.exe"
    ) else if exist "%ProgramFiles(x86)%\Mozilla Firefox\firefox.exe" (
        set BROWSER_PATH="%ProgramFiles(x86)%\Mozilla Firefox\firefox.exe"
    ) else (
        echo 未找到Firefox浏览器可执行文件
        pause
        exit /b 1
    )
    %BROWSER_PATH% -start-debugger-server %PORT%
) else (
    echo 无效的选项
    pause
    exit /b 1
)

echo.
echo 浏览器已启动，调试端口: %PORT%
echo 请保持浏览器窗口打开，然后在程序中连接
echo.
pause
