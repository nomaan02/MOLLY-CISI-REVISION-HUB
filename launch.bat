@echo off
title CISI Revision Hub
echo.
echo  ==============================
echo   CISI Revision Hub - Starting
echo  ==============================
echo.

:: Navigate to app directory
cd /d "%~dp0"

:: Check if streamlit is installed
where streamlit >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] Streamlit not found. Installing...
    pip install -r requirements.txt
    echo.
)

echo [*] Launching in your browser...
echo [*] Press Ctrl+C in this window to stop.
echo.

streamlit run app.py --server.port 8501 --browser.gatherUsageStats false
pause
