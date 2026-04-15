#!/bin/bash

echo "========================================"
echo "AI网页全自动批量处理工具 - 打包脚本"
echo "========================================"
echo ""

echo "[1/4] 检查PyInstaller是否安装..."
pip3 install pyinstaller --quiet

echo "[2/4] 清理旧的打包文件..."
rm -rf build dist
if ls *.spec 2>/dev/null | grep -v -q "build.spec"; then
    for f in *.spec; do
        if [ "$f" != "build.spec" ]; then
            mv "$f" build.spec
        fi
    done
fi

echo "[3/4] 开始打包..."
pyinstaller build.spec --clean

if [ $? -eq 0 ]; then
    echo ""
    echo "[4/4] 打包完成！"
    echo ""
    echo "========================================"
    echo "打包成功！"
    echo "可执行文件位于: dist/AI网页全自动批量处理工具"
    echo "========================================"
else
    echo ""
    echo "[ERROR] 打包失败，请检查错误信息"
fi

echo ""
