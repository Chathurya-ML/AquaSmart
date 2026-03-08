@echo off
REM AquaSmart - System Test Script (Batch)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║          AquaSmart - Pre-Deployment System Test               ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

echo 📋 Test 1: Backend Health Check
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo Testing: http://localhost:8000/health
timeout /t 2 /nobreak
echo.

echo 📋 Test 2: API Documentation
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo Open in browser: http://localhost:8000/docs
echo.

echo 📋 Test 3: Frontend Dashboard
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo Open in browser: http://localhost:8501
echo.

echo 📋 Test 4: Forecast Endpoint
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo Testing: http://localhost:8000/forecast
echo.

echo 📋 Test 5: Alerts Endpoint
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo Testing: http://localhost:8000/alerts
echo.

echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║                    Test Summary                               ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

echo ✅ Manual Testing Instructions:
echo.
echo 1. Open http://localhost:8000/health in browser
echo    Expected: {"status": "healthy"}
echo.
echo 2. Open http://localhost:8000/docs in browser
echo    Expected: Swagger UI with API endpoints
echo.
echo 3. Open http://localhost:8501 in browser
echo    Expected: AquaSmart dashboard with real-time data
echo.
echo 4. Test endpoints:
echo    - GET http://localhost:8000/forecast
echo    - GET http://localhost:8000/alerts
echo    - POST http://localhost:8000/irrigation_decision
echo.
echo ✅ If all tests pass, your system is ready for Railway deployment!
echo.
echo Next steps:
echo 1. Run: RAILWAY_SETUP.bat
echo 2. Follow the prompts to deploy to Railway
echo 3. Set environment variables in Railway dashboard
echo 4. Your app will be live in ~10 minutes!
echo.

pause
