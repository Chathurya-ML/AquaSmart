# 🚀 Deployment Guide - Smart Irrigation System

## Quick Start for Hackathon Demo

### Prerequisites
- Docker Desktop installed
- 8GB RAM minimum
- Ports 8000 and 8501 available

### Windows Users

1. **Double-click `start.bat`** or run in Command Prompt:
```cmd
start.bat
```

2. Wait for services to start (~30 seconds)

3. Open your browser:
   - Dashboard: http://localhost:8501
   - API: http://localhost:8000/docs

### Linux/Mac Users

1. **Make script executable and run:**
```bash
chmod +x start.sh
./start.sh
```

2. Wait for services to start (~30 seconds)

3. Open your browser:
   - Dashboard: http://localhost:8501
   - API: http://localhost:8000/docs

## Manual Docker Setup

If the scripts don't work, use these commands:

```bash
# Build containers
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Local Development (Without Docker)

### Backend

```bash
cd Code/backend

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd Code/frontend

# Run dashboard
streamlit run dashboard.py --server.port 8501
```

## Troubleshooting

### Port Already in Use

**Windows:**
```cmd
netstat -ano | findstr :8000
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
lsof -ti:8000 | xargs kill -9
lsof -ti:8501 | xargs kill -9
```

### Docker Issues

```bash
# Clean up Docker
docker-compose down -v
docker system prune -a

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

### Models Not Loading

Ensure model files exist:
- `Code/backend/models/soil_forecast_model.pt`
- `Code/backend/models/proactive_irrigation_policy.zip`

### API Connection Error

1. Check backend is running: http://localhost:8000/health
2. Check Docker logs: `docker-compose logs backend`
3. Verify network: `docker network ls`

## Demo Walkthrough

### 1. Access Dashboard
Open http://localhost:8501

### 2. View Current Conditions
- Current soil moisture
- Temperature and humidity
- 6-hour forecast

### 3. Check Irrigation Recommendation
- Recommended irrigation amount
- Visual moisture gauge
- Active alerts

### 4. Listen to Explanation
- Read AI-generated explanation
- Play audio version
- Try different languages

### 5. Test Language Support
- Select language from sidebar
- Click "Refresh Data"
- Hear explanation in selected language

### 6. Explore API
Open http://localhost:8000/docs
- Try the `/irrigation_decision` endpoint
- Check `/health` status
- View request/response schemas

## Performance Tips

### For Hackathon Demo

1. **Pre-load models**: Start services 2 minutes before demo
2. **Test connection**: Visit dashboard before presenting
3. **Prepare fallback**: Have screenshots ready
4. **Monitor logs**: Keep terminal with logs visible

### Resource Usage

- Backend: ~2GB RAM
- Frontend: ~500MB RAM
- Total: ~3GB RAM with models loaded

## Production Deployment (Future)

### AWS Setup

1. **Uncomment AWS code** in:
   - `storage.py` (Timestream, RDS, S3)
   - `llm_explainer.py` (Bedrock)
   - `notifications.py` (Twilio)
   - `weather_ingestion.py` (Lambda)

2. **Configure environment variables**:
```bash
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
RDS_HOST=your-rds-endpoint
S3_BUCKET=your-bucket
TWILIO_ACCOUNT_SID=your_sid
```

3. **Deploy to ECS/EKS**:
```bash
# Build for production
docker build -t irrigation-backend:prod ./Code/backend
docker build -t irrigation-frontend:prod ./Code/frontend

# Push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin
docker push your-ecr-repo/irrigation-backend:prod
docker push your-ecr-repo/irrigation-frontend:prod
```

## Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Check models loaded
curl http://localhost:8000/health | jq '.models_loaded'
```

### Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

## Stopping the System

```bash
# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop and remove everything
docker-compose down -v --rmi all
```

## Support

For issues during hackathon:
1. Check logs: `docker-compose logs`
2. Restart services: `docker-compose restart`
3. Rebuild: `docker-compose up --build`

---

**Good luck with your hackathon! 🌱**
