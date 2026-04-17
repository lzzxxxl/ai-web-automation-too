@echo off

:: 启动Chrome浏览器并开启远程调试模式
:: 默认端口9222

set PORT=9222

:: 查找Chrome可执行文件路径
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH="%ProgramFiles%\Google\Chrome\Application\chrome.exe"
) else if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH="%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
) else (
    echo 未找到Chrome浏览器可执行文件
    pause
    exit /b 1
)

:: 启动Chrome
%CHROME_PATH% --remote-debugging-port=%PORT% --user-data-dir="./chrome_profile"

echo Chrome已启动，调试端口: %PORT%
pause