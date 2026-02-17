
File: install.bat (root folder)
@echo off
echo ================================================
echo LocalEdit Installer
echo Simple. Local. Yours.
echo ================================================
echo.

echo Checking for Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    pause
    exit /b 1
)

echo Python found!
echo.

echo Checking for pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not installed!
    pause
    exit /b 1
)

echo pip found!
echo.

echo Installing LocalEdit dependencies...
pip install -r Requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Installation failed!
    pause
    exit /b 1
)

echo.
echo ================================================
echo Installation Complete!
echo ================================================
echo.
echo To run LocalEdit double-click run.bat
echo.
pause