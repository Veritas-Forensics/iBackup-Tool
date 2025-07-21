@echo off
echo ========================================
echo iDevice Manager - Windows Build Script
echo ========================================
echo.

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
REM Get the project root directory (one level up from scripts)
set "PROJECT_DIR=%SCRIPT_DIR%.."

echo Script directory: %SCRIPT_DIR%
echo Project directory: %PROJECT_DIR%
echo.

REM Change to project directory
cd /d "%PROJECT_DIR%"
if errorlevel 1 (
    echo ERROR: Failed to change to project directory
    pause
    exit /b 1
)

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo ERROR: requirements.txt not found in project directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not installed
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo Setting up virtual environment...
if exist "build_env" (
    echo Removing existing build environment...
    rmdir /s /q build_env
)

python -m venv build_env
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo Activating virtual environment...
call build_env\Scripts\activate.bat

echo Installing dependencies...
pip install --upgrade pip
echo Installing from: %CD%\requirements.txt
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo Installing PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

echo Building executable...
if not exist "dist" mkdir dist

REM Check if main.py exists in idevice_manager directory
if not exist "idevice_manager\main.py" (
    echo ERROR: idevice_manager\main.py not found
    echo Current directory: %CD%
    dir idevice_manager
    pause
    exit /b 1
)

echo Building from: %CD%\idevice_manager\main.py
pyinstaller --onefile ^
    --windowed ^
    --name "iDevice_Manager" ^
    --distpath dist ^
    --workpath build ^
    --specpath build ^
    idevice_manager\main.py

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo Executable location: dist\iDevice_Manager.exe
echo.
echo To test the build:
echo 1. Copy dist\iDevice_Manager.exe to a test location
echo 2. Run the executable
echo.
echo Deactivating virtual environment...
deactivate

pause