@echo off
REM AquaSmart - Railway Deployment Setup Script (Windows)
REM This script automates the Railway deployment process

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║          AquaSmart - Railway Deployment Setup                 ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Step 1: Check if Railway CLI is installed
echo 📋 Step 1: Checking Railway CLI...
where railway >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Railway CLI not found. Installing...
    call npm install -g railway
    echo ✅ Railway CLI installed
) else (
    echo ✅ Railway CLI already installed
)

REM Step 2: Check if git is clean
echo.
echo 📋 Step 2: Checking git status...
git status --porcelain >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Git working directory is not clean
    echo Please commit all changes first:
    echo   git add .
    echo   git commit -m "Your message"
    exit /b 1
)
echo ✅ Git working directory is clean

REM Step 3: Initialize Railway project
echo.
echo 📋 Step 3: Initializing Railway project...
echo Note: You'll be prompted to select your project
call railway init

REM Step 4: Link repository
echo.
echo 📋 Step 4: Linking repository...
call railway link

REM Step 5: Display environment variables to set
echo.
echo 📋 Step 5: Environment Variables
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo Set these environment variables in Railway dashboard:
echo.
echo For BACKEND service:
echo   GROQ_API_KEY=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
echo   USE_AWS=false
echo   FALLBACK_ENABLED=true
echo   APP_ENV=production
echo.
echo For FRONTEND service:
echo   BACKEND_URL=https://your-backend-url.railway.app
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Step 6: Deploy
echo 📋 Step 6: Deploying to Railway...
echo This will build and deploy your application...
call railway up

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║              ✅ Deployment Complete!                          ║
echo ║                                                                ║
echo ║  Your AquaSmart system is now live on Railway!                ║
echo ║                                                                ║
echo ║  Next steps:                                                   ║
echo ║  1. Set environment variables in Railway dashboard            ║
echo ║  2. Get your public URLs                                      ║
echo ║  3. Test your deployment                                      ║
echo ║  4. Submit to hackathon                                       ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo 📚 For more information, see: RAILWAY_DEPLOYMENT_CLEAN.md
echo.

pause
