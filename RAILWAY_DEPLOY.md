# 🚂 Railway Deployment - Step by Step

Deploy your AquaSmart to Railway in 5 minutes.

---

## Step 1: Create Railway Account

1. Go to **https://railway.app**
2. Click **"Start for Free"**
3. Sign up with **GitHub**
4. Authorize Railway to access your GitHub account

---

## Step 2: Create New Project

1. Click **"New Project"** (top right)
2. Select **"Deploy from GitHub repo"**
3. Search for your **AquaSmart** repository
4. Click to select it
5. Click **"Deploy Now"**

Railway will auto-detect your `docker-compose.yml` and create services.

---

## Step 3: Wait for Build

Railway will:
1. Build backend Docker image (~2 min)
2. Build frontend Docker image (~2 min)
3. Start both services (~1 min)

**Total time: ~5 minutes**

You'll see:
```
✓ Building backend...
✓ Building frontend...
✓ Deploying...
✓ Services running
```

---

## Step 4: Configure Environment Variables

### For Backend Service:

1. Click **"backend"** service
2. Go to **"Variables"** tab
3. Add these variables:

```
GROQ_API_KEY=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
USE_AWS=false
FALLBACK_ENABLED=true
APP_ENV=production
```

4. Click **"Save"**

### For Frontend Service:

1. Click **"frontend"** service
2. Go to **"Variables"** tab
3. Add this variable:

```
BACKEND_URL=https://aquasmart-backend-production.up.railway.app
```

(Replace with your actual backend URL from Railway)

4. Click **"Save"**

---

## Step 5: Get Your Public URLs

1. Click **"frontend"** service
2. Look for **"Public URL"** section
3. Copy the URL (looks like: `https://aquasmart-frontend-production.up.railway.app`)

**This is your hackathon submission link!**

Also note backend URL:
1. Click **"backend"** service
2. Copy the **"Public URL"**

---

## Step 6: Test Your Deployment

### Test Frontend
```
Open: https://your-frontend-url
Should see: AquaSmart dashboard
```

### Test Backend
```
Open: https://your-backend-url/docs
Should see: Swagger API documentation
```

### Test Health
```
Open: https://your-backend-url/health
Should see: {"status": "healthy"}
```

---

## Step 7: Submit to Hackathon

Copy your frontend URL:
```
https://your-frontend-url
```

Paste into hackathon submission form.

---

## 🔄 Auto-Deployment

Railway automatically deploys when you push to GitHub:

1. Make code changes
2. Commit: `git commit -m "Update"`
3. Push: `git push origin main`
4. Railway auto-builds and deploys
5. New version live in 2-5 minutes

---

## 📊 Monitor Your Deployment

### View Logs
1. Click service
2. Go to **"Logs"** tab
3. See real-time logs

### Check Status
1. Click service
2. See **"Status"** indicator
3. Green = running, Red = error

### View Metrics
1. Click service
2. Go to **"Metrics"** tab
3. See CPU, memory, network usage

---

## 🚨 Troubleshooting

### Build Failed
**Error:** `Models not found`
**Solution:** Ensure models are committed to Git
```bash
git add Code/backend/models/
git commit -m "Add models"
git push
```

### Service Won't Start
**Error:** `Container exited with code 1`
**Solution:** Check logs for error details
1. Click service
2. Go to "Logs"
3. Look for error message

### Frontend Can't Connect
**Error:** `Connection refused`
**Solution:** Update BACKEND_URL variable
1. Get backend public URL from Railway
2. Update frontend BACKEND_URL variable
3. Redeploy

### Out of Memory
**Error:** `OOMKilled`
**Solution:** Upgrade to paid plan or optimize models

---

## 💰 Pricing

### Free Tier
- 5GB/month bandwidth
- Limited compute
- Good for demo/testing

### Paid Tier
- $5/month minimum
- Unlimited bandwidth
- Better performance
- Recommended for production

---

## 🎯 Your Submission Link

Once deployed, your link will be:

```
https://aquasmart-frontend-production.up.railway.app
```

(Your actual URL will be different)

**This is what you submit to the hackathon!**

---

## ✅ Deployment Checklist

- [ ] Railway account created
- [ ] GitHub repo connected
- [ ] docker-compose.yml detected
- [ ] Backend service running
- [ ] Frontend service running
- [ ] Environment variables set
- [ ] Frontend URL copied
- [ ] Backend URL copied
- [ ] Health check passes
- [ ] Dashboard loads
- [ ] API responds

---

## 🎉 Done!

Your AquaSmart is now live on the internet!

**Share your link:**
```
https://your-frontend-url
```

**Good luck with your hackathon! 🚀🌱**

---

## 📞 Need Help?

- Railway Docs: https://docs.railway.app
- Railway Support: https://railway.app/support
- Check logs for error details
- Restart service if needed

---

## 🔗 Quick Links

- **Railway Dashboard:** https://railway.app/dashboard
- **Your Project:** https://railway.app/project/[project-id]
- **Documentation:** https://docs.railway.app
- **Community:** https://discord.gg/railway

Good luck! 🌱
