#!/bin/bash

# AquaSmart - Railway Deployment Setup Script
# This script automates the Railway deployment process

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║          AquaSmart - Railway Deployment Setup                 ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Check if Railway CLI is installed
echo "📋 Step 1: Checking Railway CLI..."
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g railway
    echo "✅ Railway CLI installed"
else
    echo "✅ Railway CLI already installed"
fi

# Step 2: Check if git is clean
echo ""
echo "📋 Step 2: Checking git status..."
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Git working directory is not clean"
    echo "Please commit all changes first:"
    echo "  git add ."
    echo "  git commit -m 'Your message'"
    exit 1
fi
echo "✅ Git working directory is clean"

# Step 3: Initialize Railway project
echo ""
echo "📋 Step 3: Initializing Railway project..."
echo "Note: You'll be prompted to select your project"
railway init

# Step 4: Link repository
echo ""
echo "📋 Step 4: Linking repository..."
railway link

# Step 5: Display environment variables to set
echo ""
echo "📋 Step 5: Environment Variables"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Set these environment variables in Railway dashboard:"
echo ""
echo "For BACKEND service:"
echo "  GROQ_API_KEY=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"
echo "  USE_AWS=false"
echo "  FALLBACK_ENABLED=true"
echo "  APP_ENV=production"
echo ""
echo "For FRONTEND service:"
echo "  BACKEND_URL=https://your-backend-url.railway.app"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 6: Deploy
echo "📋 Step 6: Deploying to Railway..."
echo "This will build and deploy your application..."
railway up

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║              ✅ Deployment Complete!                          ║"
echo "║                                                                ║"
echo "║  Your AquaSmart system is now live on Railway!                ║"
echo "║                                                                ║"
echo "║  Next steps:                                                   ║"
echo "║  1. Set environment variables in Railway dashboard            ║"
echo "║  2. Get your public URLs                                      ║"
echo "║  3. Test your deployment                                      ║"
echo "║  4. Submit to hackathon                                       ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📚 For more information, see: RAILWAY_DEPLOYMENT_CLEAN.md"
