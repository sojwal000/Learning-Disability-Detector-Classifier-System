# Quick Setup Script for Learning Disability Detector System
# Run this script from the project root directory

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Learning Disability Detector - Quick Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
  $pythonVersion = python --version 2>&1
  Write-Host "✓ $pythonVersion found" -ForegroundColor Green
}
catch {
  Write-Host "✗ Python not found. Please install Python 3.10 or higher." -ForegroundColor Red
  exit 1
}

# Check if Node.js is installed
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
try {
  $nodeVersion = node --version 2>&1
  Write-Host "✓ Node.js $nodeVersion found" -ForegroundColor Green
}
catch {
  Write-Host "✗ Node.js not found. Please install Node.js 18 or higher." -ForegroundColor Red
  exit 1
}

# Backend Setup
Write-Host ""
Write-Host "Setting up Backend..." -ForegroundColor Cyan
Set-Location backend

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
py -3.10 -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing Python dependencies (this may take a few minutes)..." -ForegroundColor Yellow
pip install -r requirements.txt

# Create .env if it doesn't exist
if (-not (Test-Path .env)) {
  Write-Host "Creating .env file..." -ForegroundColor Yellow
  Copy-Item .env.example .env
  Write-Host "✓ .env created. Please edit it with your database credentials." -ForegroundColor Green
}

# Create storage directories
Write-Host "Creating storage directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "storage\audio" | Out-Null
New-Item -ItemType Directory -Force -Path "storage\handwriting" | Out-Null
New-Item -ItemType Directory -Force -Path "storage\reports" | Out-Null
Write-Host "✓ Storage directories created" -ForegroundColor Green

Set-Location ..

# Frontend Setup
Write-Host ""
Write-Host "Setting up Frontend..." -ForegroundColor Cyan
Set-Location frontend

# Install dependencies
Write-Host "Installing Node.js dependencies (this may take a few minutes)..." -ForegroundColor Yellow
npm install

Set-Location ..

# Final instructions
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Configure your database:" -ForegroundColor White
Write-Host "   - Create PostgreSQL database: ld_detector" -ForegroundColor Gray
Write-Host "   - Edit backend/.env with your credentials" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Start the Backend:" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Gray
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   uvicorn app.main:app --reload" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Start the Frontend (new terminal):" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Gray
Write-Host "   npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Access the application:" -ForegroundColor White
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor Gray
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor Gray
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host ""
Write-Host "For detailed instructions, see README.md" -ForegroundColor Cyan
Write-Host ""
