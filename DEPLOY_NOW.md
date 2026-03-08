# Deploy to Railway - Quick Guide

## Step 1: Commit and Push Changes

```bash
git add .
git commit -m "Fix Dockerfiles and simplify history page"
git push origin main
```

## Step 2: Go to Railway

1. Visit https://railway.app
2. Sign up with GitHub (if not already)
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your AquaSmart repository
6. Click "Deploy Now"

Railway will auto-detect `docker-compose.yml` and deploy both services.

## Step 3: Wait for Build (~5 minutes)

You'll see:
- ✓ Building backend...
- ✓ Building frontend...
- ✓ Services running

## Step 4: Configure Environment Variables

### Backend Service:
1. Click "backend" service
2. Go to "Variables" tab
3. Add:
```
GROQ_API_KEY=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
USE_AWS=false
FALLBACK_ENABLED=true
APP_ENV=production
```

### Frontend Service:
1. Click "frontend" service
2. Go to "Variables" tab
3. Add:
```
BACKEND_URL=https://your-backend-url-from-railway
```

(Replace with actual backend URL from Railway)

## Step 5: Get Your Submission Link

1. Click "frontend" service
2. Copy the "Public URL"
3. This is your hackathon submission link!

## Done! 🚀

Your system is now live on the internet.
