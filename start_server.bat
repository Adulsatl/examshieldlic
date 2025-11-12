@echo off
echo Starting ExamShield License Server...
echo.

cd server

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies if needed
if not exist "venv\Lib\site-packages\flask" (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Check if .env exists
if not exist ".env" (
    echo Creating .env from config.env template...
    copy config.env .env
    echo.
    echo IMPORTANT: Please edit .env file and configure:
    echo   - SMTP settings (or leave blank for testing)
    echo   - WEBHOOK_SECRET (any random string)
    echo   - ADMIN_SECRET (any random string)
    echo.
    pause
)

REM Create data directory
if not exist "..\data" mkdir ..\data

REM Start server
echo.
echo Starting server on http://localhost:8080
echo Press Ctrl+C to stop
echo.
python license_server.py

pause

