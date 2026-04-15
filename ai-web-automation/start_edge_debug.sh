#!/bin/bash

# 启动Edge浏览器并开启远程调试模式
# 默认端口9222

PORT=9222

# 查找Edge可执行文件路径
if [ -f "/usr/bin/microsoft-edge" ]; then
    EDGE_PATH="/usr/bin/microsoft-edge"
elif [ -f "/usr/bin/edge" ]; then
    EDGE_PATH="/usr/bin/edge"
elif [ -f "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" ]; then
    EDGE_PATH="/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
else
    echo "未找到Edge浏览器可执行文件"
    exit 1
fi

# 启动Edge
$EDGE_PATH --remote-debugging-port=$PORT --user-data-dir="./edge_profile"

echo "Edge已启动，调试端口: $PORT"