@echo off
setlocal enabledelayedexpansion

:: =============================================
:: 语音转字幕小帮手 - 终极构建脚本
:: 特点：
:: 1. 检查Python环境和依赖
:: 2. 生成纯单文件EXE
:: 3. 自动清理所有临时文件
:: 4. EXE输出到项目根目录
:: =============================================

:: 配置区
set PROJECT_ROOT=%~dp0..
set EXE_NAME=语音转字幕小帮手.exe
set REQUIREMENTS=%PROJECT_ROOT%\requirements.txt

:: 清空旧文件
echo [预处理] 清理旧构建...
cd /d "%PROJECT_ROOT%"
if exist "%EXE_NAME%" del "%EXE_NAME%"
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"

:: 检查Python环境
echo [1/5] 检查Python环境...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python，请执行：
    echo 1. 安装Python 3.8+
    echo 2. 勾选"Add to PATH"
    pause
    exit /b 1
)

:: 安装依赖
echo [2/5] 安装依赖...
if not exist "%REQUIREMENTS%" (
    echo [警告] 未找到requirements.txt，尝试安装基础依赖
    pip install PyQt6 elevenlabs==1.57.0 pyinstaller --quiet
) else (
    pip install -r "%REQUIREMENTS%" --quiet
)

if %errorlevel% neq 0 (
    echo [错误] 依赖安装失败，请手动执行：
    echo pip install -r "%REQUIREMENTS%"
    pause
    exit /b 1
)

:: 构建EXE
echo [3/5] 构建单文件EXE...
cd /d "%PROJECT_ROOT%\src"
pyinstaller --noconfirm ^
            --onefile ^
            --windowed ^
            --add-data "../assets/icon.ico;." ^
            --add-data "../assets/background.png;." ^
            --icon="../assets/icon.ico" ^
            --name "%EXE_NAME%" ^
            --hidden-import PIL ^
            --clean ^
            main_optimized.py

if %errorlevel% neq 0 (
    echo [错误] 构建失败！
    echo 常见原因：
    echo 1. 缺少资源文件（检查assets目录）
    echo 2. 杀毒软件拦截
    pause
    exit /b 1
)

:: 移动EXE
echo [4/5] 移动EXE到根目录...
if exist "dist\%EXE_NAME%" (
    move "dist\%EXE_NAME%" "%PROJECT_ROOT%\" >nul
) else (
    echo [错误] EXE文件未生成
    pause
    exit /b 1
)

:: 最终清理
echo [5/5] 清理临时文件...
cd /d "%PROJECT_ROOT%\src"
rmdir /s /q "build" 2>nul
rmdir /s /q "dist" 2>nul
rmdir /s /q "__pycache__" 2>nul
del /q "*.spec" 2>nul

:: 完成报告
echo.
echo ========================================
echo 构建成功！
echo 生成文件：%PROJECT_ROOT%\%EXE_NAME%
echo ========================================
timeout /t 5
