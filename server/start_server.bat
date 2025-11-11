@echo off
echo Starting ExamShield License Server...
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist ".env" (
    echo Creating .env from config.env...
    copy config.env .env
    echo.
    echo IMPORTANT: Please edit .env file and add your secrets:
    echo   - SMTP settings (Gmail App Password)
    echo   - WEBHOOK_SECRET
    echo   - ADMIN_SECRET
    echo.
    pause
)

REM Start server
echo.
echo Starting server on http://localhost:8080
echo Press Ctrl+C to stop
echo.
python license_server.py

pause

