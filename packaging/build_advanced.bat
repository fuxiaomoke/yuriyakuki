@echo off
echo Building Subtitle Converter Application...

REM 检查Python环境
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found in PATH
    pause
    exit /b 1
)
 
REM 安装依赖（自动跳过已安装的包）
echo Installing dependencies...
pip install -r ..\..\requirements.txt --quiet

REM 创建临时构建目录
echo Creating build environment...
if exist build_temp rmdir /s /q build_temp
mkdir build_temp
cd build_temp

REM 复制必要文件（修正资源路径）
echo Copying source files...
copy ..\..\src\main_optimized.py .
xcopy /Y ..\..\assets\*.* assets\

REM 构建可执行文件
echo Building executable with PyInstaller...
pyinstaller --noconfirm ^
            --onefile ^
            --windowed ^
            --add-data "assets;assets" ^  # 修改这里
            --icon="assets\icon.ico" ^
            --name="SubtitleConverter" ^
            --hidden-import="PIL" ^
            --clean ^
            main_optimized.py

if %errorlevel% neq 0 (
    echo Build failed!
    cd ..
    rmdir /s /q build_temp
    pause
    exit /b 1
)

REM 复制构建结果
echo Copying output files...
if not exist ..\..\dist mkdir ..\..\dist
copy dist\SubtitleConverter.exe ..\..\dist\
xcopy /Y /E assets ..\..\dist\assets\

REM 清理临时文件
echo Cleaning up...
cd ..\..
rmdir /s /q build_temp

echo Build succeeded!
echo Output: dist\SubtitleConverter.exe
pause
