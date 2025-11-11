# PowerShell script to start ExamShield License Server

Write-Host "Starting ExamShield License Server..." -ForegroundColor Green
Write-Host ""

# Activate virtual environment
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    & "venv\Scripts\Activate.ps1"
    pip install -r requirements.txt
}

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env from config.env..." -ForegroundColor Yellow
    Copy-Item config.env .env
    Write-Host ""
    Write-Host "IMPORTANT: Please edit .env file and add your secrets:" -ForegroundColor Yellow
    Write-Host "  - SMTP settings (Gmail App Password)" -ForegroundColor Yellow
    Write-Host "  - WEBHOOK_SECRET" -ForegroundColor Yellow
    Write-Host "  - ADMIN_SECRET" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to continue"
}

# Start server
Write-Host ""
Write-Host "Starting server on http://localhost:8080" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""
python license_server.py

