# Database initialization script
# Run this after setting up your database credentials in .env

Write-Host "Creating database tables..." -ForegroundColor Yellow

# Get the script directory (backend folder)
if ($PSScriptRoot) {
  $scriptDir = $PSScriptRoot
}
else {
  # Running interactively, assume we're already in backend
  $scriptDir = Get-Location
}

# Ensure we're in the backend directory
if (Test-Path ".\app") {
  # Already in backend
  $scriptDir = Get-Location
}
elseif (Test-Path ".\backend\app") {
  # In project root, move to backend
  $scriptDir = Join-Path $scriptDir "backend"
}

Set-Location $scriptDir

# Activate virtual environment from backend folder
if (Test-Path ".\venv\Scripts\Activate.ps1") {
  & .\venv\Scripts\Activate.ps1
}
elseif (Test-Path "..\venv\Scripts\Activate.ps1") {
  & ..\venv\Scripts\Activate.ps1
}
else {
  Write-Host "Error: Virtual environment not found!" -ForegroundColor Red
  exit 1
}

# Create a Python script to initialize database
$initScript = @"
from app.database import engine, Base
from app.models import User, Student, TestResult, Questionnaire, MLPrediction, Report, AuditLog

print('Creating all tables...')
Base.metadata.create_all(bind=engine)
print('✓ Database tables created successfully!')
print('')
print('You can now start the server with:')
print('  uvicorn app.main:app --reload')
"@

$initScript | Out-File -FilePath "init_db.py" -Encoding UTF8

# Run the script
python init_db.py

# Clean up
Remove-Item init_db.py

Write-Host ""
Write-Host "Database initialization complete!" -ForegroundColor Green
