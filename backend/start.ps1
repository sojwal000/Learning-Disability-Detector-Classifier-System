# Start Backend Server
# Run this script from the backend directory

Write-Host "Starting Learning Disability Detector Backend..." -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
& .\venv\Scripts\Activate.ps1

# Start the server
Write-Host "Backend server starting at http://localhost:8000" -ForegroundColor Green
Write-Host "API Documentation available at http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
