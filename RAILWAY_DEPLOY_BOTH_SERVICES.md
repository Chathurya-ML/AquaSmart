# Railway Deployment - Both Services Together

## How It Works

Your project now uses **supervisor** to run both backend and frontend in a single Railway container:

- **Root Dockerfile**: Installs both backend and frontend dependencies
- **supervisord.conf**: Manages both services (backend on 8000, frontend on 8501)
- **docker-compose.yml**: Available for local development

## Deployment Steps

### 1. Connect to Railway
```bash
npm install -g railway
railway login
```

### 2. Deploy to Railway
```bash
railway up
```

Or via Railway Dashboard:
1. Go to [Railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub"
3. Select your AquaSmart repository
4. Railway will auto-detect the root `Dockerfile`

### 3. Set Environment Variables in Railway Dashboard

**Backend Variables:**
```
GROQ_API_KEY=your_groq_api_key
HUGGINGFACE_API_KEY=your_huggingface_key (optional)
APP_ENV=production
USE_AWS=false
FALLBACK_ENABLED=true
```

**Frontend Variables:**
```
BACKEND_URL=http://localhost:8000
```

### 4. Access Your Application

Once deployed, Railway will provide URLs:
- **Frontend**: `https://your-project.railway.app:8501`
- **Backend API**: `https://your-project.railway.app:8000`
- **API Docs**: `https://your-project.railway.app:8000/docs`

## Architecture

```
Railway Container
├── Backend (uvicorn on port 8000)
│   ├── FastAPI app
│   ├── LSTM model
│   ├── RL model
│   └── Rule-based irrigation
│
├── Frontend (Streamlit on port 8501)
│   ├── Dashboard
│   └── Connects to backend via http://localhost:8000
│
└── Supervisor (manages both services)
```

## Local Testing

### Test with docker-compose (local development)
```bash
docker-compose up
```

Access:
- Frontend: http://localhost:8501
- Backend: http://localhost:8000

### Test with root Dockerfile (simulates Railway)
```bash
docker build -t aquasmart .
docker run -p 8000:8000 -p 8501:8501 \
  -e GROQ_API_KEY=your_key \
  aquasmart
```

## Troubleshooting

### Services not starting
- Check Railway logs: `railway logs`
- Verify environment variables are set
- Ensure `supervisord.conf` is in root directory

### Frontend can't connect to backend
- Backend URL should be `http://localhost:8000` (internal to container)
- Check backend is healthy: `https://your-project.railway.app:8000/health`

### Build fails
- Ensure both `Code/backend/requirements.txt` and `Code/frontend/requirements.txt` exist
- Check Dockerfile paths are correct
- Verify all Python dependencies are compatible

## File Structure

```
AquaSmart/
├── Dockerfile                    ← Root (Railway uses this)
├── supervisord.conf              ← Manages both services
├── docker-compose.yml            ← Local development
├── Code/
│   ├── backend/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app.py
│   │   └── ... (other files)
│   └── frontend/
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── dashboard.py
│       └── ... (other files)
```

## Next Steps

1. Push to GitHub (already done ✓)
2. Deploy to Railway
3. Set environment variables
4. Test both services
5. Share the frontend URL for your hackathon submission

## Support

For Railway issues: https://docs.railway.app
For Docker issues: https://docs.docker.com
