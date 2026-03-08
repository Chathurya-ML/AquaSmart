# AquaSmart - System Test Script (PowerShell)

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                                ║" -ForegroundColor Cyan
Write-Host "║          AquaSmart - Pre-Deployment System Test               ║" -ForegroundColor Cyan
Write-Host "║                                                                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Test 1: Check Backend Health
Write-Host "📋 Test 1: Backend Health Check" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Backend is healthy" -ForegroundColor Green
        Write-Host "Response: $($response.Content)" -ForegroundColor Green
    } else {
        Write-Host "❌ Backend returned status: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Backend not responding" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 2: Check API Documentation
Write-Host "📋 Test 2: API Documentation" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ API documentation is accessible" -ForegroundColor Green
        Write-Host "URL: http://localhost:8000/docs" -ForegroundColor Green
    } else {
        Write-Host "❌ API docs returned status: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ API documentation not accessible" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 3: Check Frontend
Write-Host "📋 Test 3: Frontend Dashboard" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8501" -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Frontend is accessible" -ForegroundColor Green
        Write-Host "URL: http://localhost:8501" -ForegroundColor Green
    } else {
        Write-Host "❌ Frontend returned status: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Frontend not accessible" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 4: Check Forecast Endpoint
Write-Host "📋 Test 4: Forecast Endpoint" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/forecast" -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Forecast endpoint working" -ForegroundColor Green
        $data = $response.Content | ConvertFrom-Json
        Write-Host "Forecast data points: $($data.Count)" -ForegroundColor Green
    } else {
        Write-Host "❌ Forecast endpoint returned status: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Forecast endpoint error" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 5: Check Alerts Endpoint
Write-Host "📋 Test 5: Alerts Endpoint" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/alerts" -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Alerts endpoint working" -ForegroundColor Green
        $data = $response.Content | ConvertFrom-Json
        Write-Host "Active alerts: $($data.Count)" -ForegroundColor Green
    } else {
        Write-Host "❌ Alerts endpoint returned status: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Alerts endpoint error" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Summary
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                                ║" -ForegroundColor Cyan
Write-Host "║                    Test Summary                               ║" -ForegroundColor Cyan
Write-Host "║                                                                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ If all tests passed, your system is ready for Railway deployment!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Run: RAILWAY_SETUP.bat" -ForegroundColor Yellow
Write-Host "2. Follow the prompts to deploy to Railway" -ForegroundColor Yellow
Write-Host "3. Set environment variables in Railway dashboard" -ForegroundColor Yellow
Write-Host "4. Your app will be live in ~10 minutes!" -ForegroundColor Yellow
Write-Host ""
