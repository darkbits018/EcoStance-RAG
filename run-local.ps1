# Start EcoStance Local Development
# This script starts all services without Docker.

Write-Host "Starting EcoStance Local Development Environment..." -ForegroundColor Cyan

# 1. Load Root .env file
if (Test-Path ".env") {
    Write-Host "Loading .env file..." -ForegroundColor Green
    foreach ($line in Get-Content .env) {
        if ($line -match '^([^#][^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [System.Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
}

# 2. Start Ecostance Agent Backend (Port 9000)
Write-Host "Starting Ecostance Agent Backend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd ecostance-agent-v1; . .venv\Scripts\activate; uvicorn app.main:app --host 0.0.0.0 --port 9000" -WindowStyle Normal

# 3. Start CRM Backend (Port 9001)
Write-Host "Starting CRM Backend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd c-crm-be; . .venv\Scripts\activate; python run.py" -WindowStyle Normal

# 4. Start Ecostance UI Frontend (Port 9002)
Write-Host "Starting Ecostance UI Frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd ecostance-ui-v1; npm run dev -- --port 9002" -WindowStyle Normal

# 5. Start CRM Frontend (Port 3001)
Write-Host "Starting CRM Frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd c-crm-fe; npm run dev -- --port 3001" -WindowStyle Normal

Write-Host "`nAll services are starting in separate windows." -ForegroundColor Cyan
Write-Host "Agent Backend: http://localhost:9000"
Write-Host "CRM Backend:   http://localhost:9001"
Write-Host "Agent UI:      http://localhost:9002"
Write-Host "CRM UI:        http://localhost:3001"
Write-Host "`nMaintain this window to keep environment variables if needed, or close it after services start."
