# Railway Deployment - Separate Backend & Frontend Services

## Overview
Deploy backend and frontend as **two separate Railway services** with independent URLs.

## Deployment Steps

### Step 1: Deploy Backend Service

1. Go to [Railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub"
3. Select your AquaSmart repository
4. In the service settings:
   - Set **Root Directory** to `Code/backend`
   - Railway will auto-detect `Code/backend/Dockerfile`
5. Set environment variables:
   ```
   GROQ_API_KEY=your_groq_api_key
   HUGGINGFACE_API_KEY=your_huggingface_key (optional)
   APP_ENV=production
   USE_AWS=false
   FALLBACK_ENABLED=true
   ```
6. Deploy and get the backend URL (e.g., `https://aquasmart-backend.railway.app`)

### Step 2: Deploy Frontend Service

1. In the same Railway project, click "New Service"
2. Select "GitHub Repo" → Choose your AquaSmart repo
3. In the service settings:
   - Set **Root Directory** to `Code/frontend`
   - Railway will auto-detect `Code/frontend/Dockerfile`
4. Set environment variables:
   ```
   BACKEND_URL=https://aquasmart-backend.railway.app
   ```
   (Replace with your actual backend URL from Step 1)
5. Deploy and get the frontend URL (e.g., `https://aquasmart-frontend.railway.app`)

## Your URLs

After deployment, you'll have:

- **Backend API**: `https://aquasmart-backend.railway.app`
- **API Documentation**: `https://aquasmart-backend.railway.app/docs`
- **Frontend Dashboard**: `https://aquasmart-frontend.railway.app`

## Architecture

```
Railway Project
├── Backend Service (Code/backend)
│   ├── Port: $PORT (Railway assigns dynamically)
│   ├── Dockerfile: Code/backend/Dockerfile
│   └── URL: https://aquasmart-backend.railway.app
│
└── Frontend Service (Code/frontend)
    ├── Port: $PORT (Railway assigns dynamically)
    ├── Dockerfile: Code/frontend/Dockerfile
    ├── Connects to: Backend URL via BACKEND_URL env var
    └── URL: https://aquasmart-frontend.railway.app
```

## How It Works

- **Backend Dockerfile**: Uses `CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port $PORT"]`
  - Railway sets `$PORT` environment variable
  - Backend runs on Railway's assigned port
  
- **Frontend Dockerfile**: Uses `CMD ["sh", "-c", "streamlit run dashboard.py --server.address=0.0.0.0 --server.port=$PORT"]`
  - Railway sets `$PORT` environment variable
  - Frontend runs on Railway's assigned port
  - Connects to backend via `BACKEND_URL` environment variable

## Troubleshooting

### Backend fails to start
- Check `GROQ_API_KEY` is set correctly
- Verify all required environment variables are present
- Check Railway logs for errors

### Frontend can't connect to backend
- Ensure `BACKEND_URL` is set to the correct backend service URL
- Check that backend service is running and healthy
- Verify the URL format: `https://your-backend-service.railway.app`

### Build fails
- Ensure `Code/backend/requirements.txt` and `Code/frontend/requirements.txt` exist
- Check that all Python dependencies are compatible with Python 3.11
- Verify Dockerfiles are in correct locations

## Local Testing

### Test backend locally
```bash
cd Code/backend
docker build -t aquasmart-backend .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key aquasmart-backend
```

### Test frontend locally
```bash
cd Code/frontend
docker build -t aquasmart-frontend .
docker run -p 8501:8501 -e BACKEND_URL=http://localhost:8000 aquasmart-frontend
```

## Next Steps

1. Deploy backend service first
2. Get backend URL
3. Deploy frontend service with backend URL
4. Test both services are communicating
5. Share the frontend URL for your hackathon submission

## Support

- Railway Docs: https://docs.railway.app
- Docker Docs: https://docs.docker.com
