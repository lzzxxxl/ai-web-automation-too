@echo off

:: 启动Edge浏览器并开启远程调试模式
:: 默认端口9222

set PORT=9222

:: 查找Edge可执行文件路径
if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" (
    set EDGE_PATH="%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
) else if exist "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" (
    set EDGE_PATH="%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
) else (
    echo 未找到Edge浏览器可执行文件
    pause
    exit /b 1
)

:: 启动Edge
%EDGE_PATH% --remote-debugging-port=%PORT% --user-data-dir="./edge_profile"

echo Edge已启动，调试端口: %PORT%
pause