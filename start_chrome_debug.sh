#!/bin/bash

# 启动Chrome浏览器并开启远程调试模式
# 默认端口9222

PORT=9222

# 查找Chrome可执行文件路径
if [ -f "/usr/bin/google-chrome" ]; then
    CHROME_PATH="/usr/bin/google-chrome"
elif [ -f "/usr/bin/chromium" ]; then
    CHROME_PATH="/usr/bin/chromium"
elif [ -f "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
    CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
else
    echo "未找到Chrome浏览器可执行文件"
    exit 1
fi

# 启动Chrome
$CHROME_PATH --remote-debugging-port=$PORT --user-data-dir="./chrome_profile"

echo "Chrome已启动，调试端口: $PORT"