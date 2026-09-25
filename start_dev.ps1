# SözLab - Avtomatlashtirilgan Ishga Tushirish Skripti (PowerShell)
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   SÖZLAB - AI CALL MARKAZI (Namangan AI Xakaton)        " -ForegroundColor Yellow
Write-Host "   Ta'lim va Innovatsiyalar Vazirligi                    " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan


# 1. Backendni ishga tushirish (FastAPI)
Write-Host "`n[1/2] FastAPI Backend ishga tushirilmoqda (Port 8000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

Start-Sleep -Seconds 2

# 2. Frontendni ishga tushirish (Next.js)
Write-Host "[2/2] Next.js Frontend ishga tushirilmoqda (Port 3000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev"

$localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notmatch 'Loopback|vEthernet' -and $_.IPAddress -notmatch '^169\.' } | Select-Object -First 1).IPAddress

Write-Host "`n✅ Barcha xizmatlar muvaffaqiyatli ishga tushirildi!" -ForegroundColor Green
Write-Host "   Frontend (Lokal): http://localhost:3000" -ForegroundColor Yellow
if ($localIP) {
    Write-Host "   Frontend (Wi-Fi / Lokal IP): http://$($localIP):3000" -ForegroundColor Cyan
    Write-Host "   (Jamoa a'zolari va hakamlar o'z telefon/noutbuklaridan ulanishi mumkin)" -ForegroundColor Gray
}
Write-Host "   Backend API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "   Ishonch telefoni: 1006 (Simulyatsiya)" -ForegroundColor Yellow
