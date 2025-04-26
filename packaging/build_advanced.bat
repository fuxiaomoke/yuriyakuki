@echo off
setlocal enabledelayedexpansion

:: =============================================
:: ����ת��ĻС���� - �ռ������ű�
:: �ص㣺
:: 1. ���Python����������
:: 2. ���ɴ����ļ�EXE
:: 3. �Զ�����������ʱ�ļ�
:: 4. EXE�������Ŀ��Ŀ¼
:: =============================================

:: ������
set PROJECT_ROOT=%~dp0..
set EXE_NAME=����ת��ĻС����.exe
set REQUIREMENTS=%PROJECT_ROOT%\requirements.txt

:: ��վ��ļ�
echo [Ԥ����] ����ɹ���...
cd /d "%PROJECT_ROOT%"
if exist "%EXE_NAME%" del "%EXE_NAME%"
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"

:: ���Python����
echo [1/5] ���Python����...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [����] δ��⵽Python����ִ�У�
    echo 1. ��װPython 3.8+
    echo 2. ��ѡ"Add to PATH"
    pause
    exit /b 1
)

:: ��װ����
echo [2/5] ��װ����...
if not exist "%REQUIREMENTS%" (
    echo [����] δ�ҵ�requirements.txt�����԰�װ��������
    pip install PyQt6 elevenlabs==1.57.0 pyinstaller --quiet
) else (
    pip install -r "%REQUIREMENTS%" --quiet
)

if %errorlevel% neq 0 (
    echo [����] ������װʧ�ܣ����ֶ�ִ�У�
    echo pip install -r "%REQUIREMENTS%"
    pause
    exit /b 1
)

:: ����EXE
echo [3/5] �������ļ�EXE...
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
    echo [����] ����ʧ�ܣ�
    echo ����ԭ��
    echo 1. ȱ����Դ�ļ������assetsĿ¼��
    echo 2. ɱ���������
    pause
    exit /b 1
)

:: �ƶ�EXE
echo [4/5] �ƶ�EXE����Ŀ¼...
if exist "dist\%EXE_NAME%" (
    move "dist\%EXE_NAME%" "%PROJECT_ROOT%\" >nul
) else (
    echo [����] EXE�ļ�δ����
    pause
    exit /b 1
)

:: ��������
echo [5/5] ������ʱ�ļ�...
cd /d "%PROJECT_ROOT%\src"
rmdir /s /q "build" 2>nul
rmdir /s /q "dist" 2>nul
rmdir /s /q "__pycache__" 2>nul
del /q "*.spec" 2>nul

:: ��ɱ���
echo.
echo ========================================
echo �����ɹ���
echo �����ļ���%PROJECT_ROOT%\%EXE_NAME%
echo ========================================
timeout /t 5
