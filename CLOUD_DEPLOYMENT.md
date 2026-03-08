# 🚀 Cloud Deployment Guide - AquaSmart

Deploy your Smart Irrigation System to the cloud for a public URL.

---

## 📋 Quick Comparison

| Platform | Setup Time | Cost | Best For |
|----------|-----------|------|----------|
| **Railway** | 5 min | Free tier available | Easiest, Docker-native |
| **Render** | 5 min | Free tier available | Simple, reliable |
| **Heroku** | 10 min | Paid only | Popular, well-known |
| **AWS** | 30 min | Pay-as-you-go | Production, scalable |

---

## 🚂 Option 1: Railway (Recommended - Easiest)

### Step 1: Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Create new project

### Step 2: Connect GitHub Repository
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Authorize Railway to access your GitHub
4. Select your AquaSmart repository

### Step 3: Configure Services
Railway will auto-detect `docker-compose.yml`:

1. Click "Add Service"
2. Select "Docker Compose"
3. Railway creates two services:
   - `backend` (port 8000)
   - `frontend` (port 8501)

### Step 4: Set Environment Variables
1. Go to each service settings
2. Add variables from `.env`:
   ```
   GROQ_API_KEY=your_key_here
   HUGGINGFACE_API_KEY=your_key_here
   USE_AWS=false
   FALLBACK_ENABLED=true
   ```

### Step 5: Deploy
1. Click "Deploy"
2. Wait 3-5 minutes for build
3. Get public URLs:
   - Frontend: `https://your-project-frontend.railway.app`
   - Backend: `https://your-project-backend.railway.app`

**Your hackathon link:** `https://your-project-frontend.railway.app`

---

## 🎨 Option 2: Render (Alternative)

### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Create new project

### Step 2: Deploy Backend
1. Click "New +"
2. Select "Web Service"
3. Connect GitHub repo
4. Configure:
   - **Name:** aquasmart-backend
   - **Environment:** Docker
   - **Build Command:** `docker build -t backend ./Code/backend`
   - **Start Command:** `uvicorn app:app --host 0.0.0.0 --port 8000`
   - **Port:** 8000

### Step 3: Deploy Frontend
1. Click "New +"
2. Select "Web Service"
3. Configure:
   - **Name:** aquasmart-frontend
   - **Environment:** Docker
   - **Build Command:** `docker build -t frontend ./Code/frontend`
   - **Start Command:** `streamlit run dashboard.py --server.port 8501`
   - **Port:** 8501

### Step 4: Set Environment Variables
For each service, add:
```
GROQ_API_KEY=your_key
BACKEND_URL=https://aquasmart-backend.onrender.com (for frontend)
```

### Step 5: Deploy
Click "Create Web Service" and wait for deployment.

**Your hackathon link:** `https://aquasmart-frontend.onrender.com`

---

## 🐳 Option 3: Manual Docker Hub + Heroku

### Step 1: Push to Docker Hub
```bash
# Login to Docker Hub
docker login

# Tag images
docker tag aquasmart-backend:latest your-username/aquasmart-backend:latest
docker tag aquasmart-frontend:latest your-username/aquasmart-frontend:latest

# Push
docker push your-username/aquasmart-backend:latest
docker push your-username/aquasmart-frontend:latest
```

### Step 2: Deploy to Heroku
```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create aquasmart-app

# Set environment variables
heroku config:set GROQ_API_KEY=your_key

# Deploy
git push heroku main
```

---

## 🔧 Pre-Deployment Checklist

Before deploying to cloud:

- [ ] All models in `Code/backend/models/` directory
- [ ] `.env` file configured with API keys
- [ ] `docker-compose.yml` updated with correct ports
- [ ] Backend Dockerfile uses `uvicorn` (not Flask)
- [ ] Frontend Dockerfile uses Streamlit
- [ ] `.dockerignore` excludes unnecessary files
- [ ] Git repository is public (for cloud platforms)

---

## 📝 Create .dockerignore

Create `.dockerignore` to reduce image size:

```
.git
.gitignore
.pytest_cache
.hypothesis
__pycache__
*.pyc
*.pyo
*.egg-info
.venv
venv
.env.local
.DS_Store
node_modules
.kiro
```

---

## 🔐 Environment Variables for Cloud

**Required:**
```
USE_AWS=false
FALLBACK_ENABLED=true
GROQ_API_KEY=your_groq_key
```

**Optional:**
```
HUGGINGFACE_API_KEY=your_hf_key
OPENWEATHER_API_KEY=your_weather_key
```

Get free API keys:
- Groq: https://console.groq.com
- HuggingFace: https://huggingface.co/settings/tokens

---

## 🚨 Troubleshooting Cloud Deployment

### Build Fails
```
Error: Models not found
Solution: Ensure models/ directory is committed to Git
```

### Frontend Can't Connect to Backend
```
Error: Connection refused
Solution: Update BACKEND_URL in frontend environment
```

### Out of Memory
```
Error: Container killed
Solution: Upgrade to paid tier or optimize models
```

### Slow Startup
```
Issue: Takes > 2 minutes to start
Solution: Pre-load models in startup script
```

---

## 📊 Cost Estimates

### Railway
- **Free tier:** 5GB/month
- **Paid:** $5/month minimum

### Render
- **Free tier:** Limited hours
- **Paid:** $7/month minimum

### Heroku
- **Free tier:** Discontinued (was free)
- **Paid:** $7/month minimum

### AWS
- **Free tier:** 12 months
- **Estimated:** $20-50/month

---

## 🎯 For Hackathon

**Recommended approach:**
1. Use **Railway** (easiest setup)
2. Deploy both services
3. Get public URL in 5 minutes
4. Submit URL to hackathon

**Backup approach:**
1. Keep local Docker running
2. Demo locally at `localhost:8501`
3. Show judges the code on GitHub

---

## 📱 Testing Cloud Deployment

Once deployed, test:

```bash
# Test backend health
curl https://your-backend-url/health

# Test frontend
Open https://your-frontend-url in browser

# Test API
curl -X POST https://your-backend-url/irrigation_decision \
  -H "Content-Type: application/json" \
  -d '{"soil_moisture": 35, "temperature": 28, ...}'
```

---

## 🔄 Continuous Deployment

Most platforms auto-deploy on Git push:

1. Make code changes
2. Commit and push to GitHub
3. Platform auto-builds and deploys
4. New version live in 2-5 minutes

---

## 💡 Pro Tips

1. **Keep models small** - Large models slow down deployment
2. **Use caching** - Docker layer caching speeds up rebuilds
3. **Monitor logs** - Check cloud platform logs for errors
4. **Set up alerts** - Get notified if service goes down
5. **Use CDN** - Serve static files from CDN for speed

---

## 🎉 You're Ready!

Choose your platform and deploy in 5 minutes!

**Railway:** https://railway.app
**Render:** https://render.com
**Heroku:** https://heroku.com

Good luck with your hackathon! 🚀
