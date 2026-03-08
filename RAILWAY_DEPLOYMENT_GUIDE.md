# Railway Deployment Guide - AquaSmart

## ✅ Pre-Deployment Checklist

Your repository is now clean and ready for Railway deployment:
- ✅ 70 files tracked in git (no large unnecessary files)
- ✅ All source code included
- ✅ Docker configuration ready
- ✅ Environment variables configured
- ✅ Models included (soil_forecast_model.pt, proactive_irrigation_policy.zip)

---

## 🚀 Step-by-Step Railway Deployment

### Step 1: Create Railway Account
1. Go to https://railway.app
2. Click "Start for Free"
3. Sign up with GitHub (recommended)
4. Authorize Railway to access your GitHub account

### Step 2: Create New Project
1. Click "New Project" button (top right)
2. Select "Deploy from GitHub repo"
3. Search for your repository name (AquaSmart)
4. Click to select it
5. Click "Deploy Now"

**Railway will now:**
- Clone your repository
- Detect docker-compose.yml
- Build both backend and frontend images (~3-5 minutes)
- Start the services

### Step 3: Monitor Build Progress
1. Go to your project dashboard
2. You'll see two services: `backend` and `frontend`
3. Watch the build logs in real-time
4. Wait for both services to show "Running" status

### Step 4: Configure Environment Variables

#### For Backend Service:
1. Click on the "backend" service
2. Go to "Variables" tab
3. Add these environment variables:
   ```
   GROQ_API_KEY=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
   USE_AWS=false
   FALLBACK_ENABLED=true
   APP_ENV=production
   LSTM_MODEL_PATH=models/soil_forecast_model.pt
   RL_MODEL_PATH=models/proactive_irrigation_policy.zip
   SENSOR_DATA_PATH=data/sensor_readings.csv
   DECISION_DB_PATH=data/irrigation_decisions.db
   ```
4. Click "Save"

#### For Frontend Service:
1. Click on the "frontend" service
2. Go to "Variables" tab
3. Add this environment variable:
   ```
   BACKEND_URL=https://aquasmart-backend-production.up.railway.app
   ```
   (Replace with your actual backend URL from Railway)
4. Click "Save"

### Step 5: Get Your Public URLs

#### Backend URL:
1. Click on "backend" service
2. Look for "Public URL" section
3. Copy the URL (e.g., https://aquasmart-backend-production.up.railway.app)
4. Update the BACKEND_URL in frontend variables with this URL

#### Frontend URL:
1. Click on "frontend" service
2. Look for "Public URL" section
3. Copy the URL (e.g., https://aquasmart-frontend-production.up.railway.app)
4. **This is your hackathon submission link!**

### Step 6: Test Your Deployment

**Test Backend:**
```
https://your-backend-url/health
```
Should return: `{"status": "healthy"}`

**Test API Documentation:**
```
https://your-backend-url/docs
```
Should show Swagger UI with all endpoints

**Test Frontend:**
```
https://your-frontend-url
```
Should show the AquaSmart dashboard

### Step 7: Submit to Hackathon
Copy your frontend URL and submit it to the hackathon platform:
```
https://your-frontend-url
```

---

## 🔄 Auto-Deployment (Continuous Deployment)

Railway automatically deploys when you push to GitHub:

```bash
# Make changes to your code
git add .
git commit -m "Update feature"
git push origin main
```

Railway will automatically:
1. Detect the push
2. Rebuild Docker images
3. Deploy new version
4. Update your live URLs

**Deployment takes 2-5 minutes**

---

## 🐛 Troubleshooting

### Build Failed
**Error:** Docker build fails
**Solution:**
1. Check Railway build logs for specific error
2. Verify all files are committed to git
3. Check that models are in Code/backend/models/
4. Ensure requirements.txt files are present

### Frontend Can't Connect to Backend
**Error:** Dashboard shows connection error
**Solution:**
1. Verify BACKEND_URL is set correctly in frontend variables
2. Check that backend service is running
3. Ensure backend URL is accessible (test /health endpoint)
4. Restart frontend service

### Service Won't Start
**Error:** Service shows "Failed" status
**Solution:**
1. Click service and check logs
2. Look for error messages
3. Common issues:
   - Missing environment variables
   - Port conflicts
   - Missing dependencies
4. Restart the service

### Models Not Loading
**Error:** Backend returns 500 error
**Solution:**
1. Verify models are in git: `git ls-files | grep models/`
2. Check model paths in environment variables
3. Verify file permissions
4. Check backend logs for specific error

---

## 📊 Monitoring Your Deployment

### View Logs
1. Click on service
2. Go to "Logs" tab
3. See real-time logs from your application

### Check Health
1. Visit `https://your-backend-url/health`
2. Should return healthy status
3. Check response time

### Monitor Usage
1. Go to project settings
2. View CPU, memory, and bandwidth usage
3. Check if you're within free tier limits

---

## 💰 Railway Pricing

**Free Tier Includes:**
- $5 free credit per month
- Enough for small projects
- Auto-scales with usage

**Your Project Costs:**
- Backend service: ~$0.50-1.00/month
- Frontend service: ~$0.50-1.00/month
- Database (if used): ~$1.00/month
- **Total: ~$2-3/month** (well within free tier)

---

## 🔐 Security Notes

### Environment Variables
- ✅ GROQ_API_KEY is safely stored in Railway
- ✅ Not exposed in logs or frontend
- ✅ Can be rotated anytime

### Database
- ✅ Using local SQLite (no external DB needed)
- ✅ Data persists in Railway volumes
- ✅ Backed up automatically

### API
- ✅ CORS configured for frontend
- ✅ Health check endpoint available
- ✅ Error handling in place

---

## 📱 Quick Links

**Your Deployment:**
- Frontend: https://your-frontend-url
- Backend: https://your-backend-url
- API Docs: https://your-backend-url/docs
- Health Check: https://your-backend-url/health

**Railway Dashboard:**
- https://railway.app/dashboard

**Documentation:**
- Railway Docs: https://docs.railway.app
- Docker Docs: https://docs.docker.com

---

## ✨ Next Steps

1. **Deploy to Railway** (follow steps above)
2. **Test all endpoints** (use API docs)
3. **Verify dashboard** (check frontend)
4. **Submit to hackathon** (copy frontend URL)
5. **Monitor logs** (check for errors)
6. **Celebrate!** 🎉

---

## 📞 Support

If you encounter issues:

1. **Check Railway logs** - Most errors are in the logs
2. **Verify environment variables** - Common cause of failures
3. **Test locally first** - Run `docker-compose up` locally
4. **Check git status** - Ensure all files are committed
5. **Review this guide** - Most issues are covered above

---

## 🎯 Success Criteria

Your deployment is successful when:
- ✅ Both services show "Running" status
- ✅ Frontend URL is accessible
- ✅ Backend /health endpoint returns 200
- ✅ Dashboard loads without errors
- ✅ API documentation is available
- ✅ You can see real-time data

---

**You're ready to deploy! 🚀**

Follow the steps above and your AquaSmart system will be live on the internet in minutes!

