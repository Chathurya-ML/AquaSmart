# Railway Deployment Guide - Both Services

## Quick Setup (5 minutes)

### Step 1: Create Backend Service
1. Go to [Railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub"
3. Select your AquaSmart repository
4. Railway will auto-detect `Code/backend/Dockerfile`
5. Set environment variables:
   - `GROQ_API_KEY`: Your Groq API key
   - `HUGGINGFACE_API_KEY`: Your HuggingFace API key (optional)
   - `APP_ENV`: `production`
   - `USE_AWS`: `false`
   - `FALLBACK_ENABLED`: `true`

### Step 2: Create Frontend Service
1. In the same Railway project, click "New Service"
2. Select "GitHub Repo" → Choose your AquaSmart repo again
3. In the service settings:
   - Set **Root Directory** to `Code/frontend`
   - Railway will auto-detect `Code/frontend/Dockerfile`
4. Set environment variables:
   - `BACKEND_URL`: `https://<backend-service-url>` (get this from backend service)

### Step 3: Link Services
1. Get backend service URL from Railway dashboard
2. Update frontend `BACKEND_URL` with backend service URL
3. Both services will communicate via this URL

## Environment Variables

### Backend Service
```
GROQ_API_KEY=your_groq_key
HUGGINGFACE_API_KEY=your_huggingface_key (optional)
APP_ENV=production
USE_AWS=false
FALLBACK_ENABLED=true
LSTM_MODEL_PATH=models/soil_forecast_model.pt
RL_MODEL_PATH=models/proactive_irrigation_policy.zip
SENSOR_DATA_PATH=data/sensor_readings.csv
DECISION_DB_PATH=data/irrigation_decisions.db
```

### Frontend Service
```
BACKEND_URL=https://your-backend-service.railway.app
```

## Deployment Structure

```
AquaSmart/
├── Code/
│   ├── backend/
│   │   ├── Dockerfile          ← Backend service
│   │   ├── requirements.txt
│   │   ├── app.py
│   │   └── ... (other backend files)
│   └── frontend/
│       ├── Dockerfile          ← Frontend service
│       ├── requirements.txt
│       ├── dashboard.py
│       └── ... (other frontend files)
├── railway.json                ← Railway config
└── docker-compose.yml          ← Local development only
```

## Accessing Your Application

- **Backend API**: `https://<backend-service>.railway.app`
- **Frontend Dashboard**: `https://<frontend-service>.railway.app`
- **API Docs**: `https://<backend-service>.railway.app/docs`

## Troubleshooting

### Backend fails to start
- Check `GROQ_API_KEY` is set correctly
- Verify all required environment variables are present
- Check logs in Railway dashboard

### Frontend can't connect to backend
- Ensure `BACKEND_URL` is set to the correct backend service URL
- Check that backend service is running and healthy
- Verify network connectivity between services

### Build fails
- Ensure `Code/backend/requirements.txt` and `Code/frontend/requirements.txt` exist
- Check that all Python dependencies are compatible with Python 3.11
- Verify Dockerfiles are in correct locations

## Local Testing Before Deployment

```bash
# Test backend
cd Code/backend
docker build -t aquasmart-backend .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key aquasmart-backend

# Test frontend
cd Code/frontend
docker build -t aquasmart-frontend .
docker run -p 8501:8501 -e BACKEND_URL=http://localhost:8000 aquasmart-frontend
```

## Next Steps

1. Deploy backend service first
2. Get backend service URL
3. Deploy frontend service with backend URL
4. Test both services are communicating
5. Share the frontend URL for your hackathon submission
