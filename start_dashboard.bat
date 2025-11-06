@echo off
echo 🚀 E-Commerce Analytics Dashboard Launcher
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo.
    echo 📥 Please install Python first:
    echo    1. Go to https://python.org/downloads
    echo    2. Download Python 3.11 or later
    echo    3. During installation, check "Add Python to PATH"
    echo    4. Restart this script after installation
    pause
    exit /b 1
)

echo ✅ Python found! Version:
python --version
echo.

REM Check if we're in the right directory
if not exist "dashboard\app.py" (
    echo ❌ Dashboard files not found!
    echo 📁 Make sure you're running this from the project root directory
    echo    Current directory: %CD%
    pause
    exit /b 1
)

echo 📦 Installing required packages...
echo.

REM Install required packages
pip install streamlit plotly pandas numpy --quiet
if %errorlevel% neq 0 (
    echo ❌ Failed to install packages
    echo 💡 Try running: pip install --user streamlit plotly pandas numpy
    pause
    exit /b 1
)

echo ✅ Packages installed successfully!
echo.

echo 🌐 Starting dashboard...
echo    - Dashboard will open in your default browser
echo    - Press Ctrl+C to stop the dashboard
echo    - Dashboard URL: http://localhost:8501
echo.

REM Start the dashboard
cd dashboard
python -m streamlit run app.py --browser.gatherUsageStats false

echo.
echo ✅ Dashboard stopped.
pause