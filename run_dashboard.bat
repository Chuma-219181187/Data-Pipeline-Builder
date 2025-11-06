@echo off
echo 🎯 E-Commerce Dashboard Launcher
echo ================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo.
    echo 📥 Please install Python first:
    echo 1. Microsoft Store: Search "Python 3.11"
    echo 2. OR python.org/downloads
    echo 3. Make sure to check "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo ✅ Python found!

REM Install required packages
echo 📦 Installing required packages...
python -m pip install streamlit plotly pandas numpy

REM Run the dashboard
echo.
echo 🚀 Starting Dashboard...
echo 📱 Will open in your browser
echo ⏹️  Press Ctrl+C to stop
echo.
python -m streamlit run dashboard\app.py --browser.gatherUsageStats false

pause