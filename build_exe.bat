@echo off
echo ========================================
echo AI网页全自动批量处理工具 - 打包脚本
echo ========================================
echo.

echo [1/4] 检查PyInstaller是否安装...
python -m pip install pyinstaller --quiet >nul 2>&1

echo [2/4] 清理旧的打包文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec (
    if not exist build.spec (
        ren *.spec build.spec
    )
)

echo [3/4] 开始打包...
pyinstaller build.spec --clean

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [4/4] 打包完成！
    echo.
    echo ========================================
    echo 打包成功！
    echo 可执行文件位于: dist\AI网页全自动批量处理工具.exe
    echo ========================================
) else (
    echo.
    echo [ERROR] 打包失败，请检查错误信息
)

echo.
pause
