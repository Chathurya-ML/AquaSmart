# 🐳 Docker Deployment Guide - AquaSmart

Complete guide to build and run AquaSmart using Docker.

---

## 📋 Prerequisites

1. **Docker Desktop** installed
   - Windows: [Download Docker Desktop](https://www.docker.com/products/docker-desktop)
   - Verify: `docker --version` and `docker-compose --version`

2. **Trained Models** in place
   - `Code/backend/models/soil_forecast_model.pt` ✅
   - `Code/backend/data/sensor_readings.csv` ✅

3. **Environment Variables** (optional)
   - Copy `.env.example` to `.env`
   - Add your API keys (Groq, OpenWeather, etc.)

---

## 🚀 Quick Start (3 Commands)

### Option 1: Using Docker Compose (Recommended)

```bash
# 1. Build images
docker-compose build

# 2. Start services
docker-compose up -d

# 3. Check status
docker-compose ps
```

**Access the app:**
- Frontend: http://localhost:8501
- Backend API: http://localhost:5000

### Option 2: Manual Docker Build

```bash
# Build backend
cd Code/backend
docker build -t aquasmart-backend .

# Build frontend
cd ../frontend
docker build -t aquasmart-frontend .

# Run backend
docker run -d -p 5000:5000 --name backend aquasmart-backend

# Run frontend
docker run -d -p 8501:8501 --name frontend aquasmart-frontend
```

---

## 📦 What Gets Built

### Backend Image
- **Base:** Python 3.10-slim
- **Size:** ~800MB
- **Includes:**
  - Flask API
  - LSTM model
  - Rule-based irrigation
  - LLM explainer
  - All dependencies

### Frontend Image
- **Base:** Python 3.10-slim
- **Size:** ~600MB
- **Includes:**
  - Streamlit dashboard
  - UI components
  - All dependencies

---

## 🔧 Detailed Commands

### Build Images

```bash
# Build both services
docker-compose build

# Build only backend
docker-compose build backend

# Build only frontend
docker-compose build frontend

# Force rebuild (no cache)
docker-compose build --no-cache
```

### Start Services

```bash
# Start in background
docker-compose up -d

# Start with logs visible
docker-compose up

# Start only backend
docker-compose up -d backend

# Start only frontend
docker-compose up -d frontend
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop but keep containers
docker-compose stop
```

### View Logs

```bash
# All services
docker-compose logs

# Follow logs (live)
docker-compose logs -f

# Backend only
docker-compose logs backend

# Last 100 lines
docker-compose logs --tail=100
```

### Check Status

```bash
# List running containers
docker-compose ps

# Check health
docker-compose ps backend

# Detailed info
docker inspect aquasmart-backend
```

---

## 🌍 Environment Variables

Create a `.env` file in the root directory:

```bash
# API Keys (Optional but recommended)
GROQ_API_KEY=your_groq_api_key_here
HUGGINGFACE_API_KEY=your_hf_key_here
OPENWEATHER_API_KEY=your_weather_key_here

# AWS (Optional - for cloud storage)
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=us-east-1
S3_BUCKET_NAME=aquasmart-data

# Flask
FLASK_ENV=production
```

**Without API keys:** System will use fallback rule-based explanations (still works!)

---

## 📂 Volume Mounts

Docker Compose mounts these directories:

```yaml
volumes:
  - ./Code/backend/data:/app/data      # Training data
  - ./Code/backend/models:/app/models  # LSTM & RL models
```

**Why?** So your trained models persist even if containers are recreated.

---

## 🔍 Troubleshooting

### Backend won't start

```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Models missing - ensure models/ directory has .pt files
# 2. Port 5000 in use - change port in docker-compose.yml
# 3. Dependencies failed - rebuild with --no-cache
```

### Frontend can't connect to backend

```bash
# Check backend is running
docker-compose ps backend

# Check network
docker network inspect aquasmart-network

# Restart both services
docker-compose restart
```

### Models not found

```bash
# Verify models exist
ls Code/backend/models/

# Should see:
# - soil_forecast_model.pt
# - proactive_irrigation_policy.zip (optional)

# If missing, train models first (see TRAINING_PIPELINE.md)
```

### Port already in use

```bash
# Find what's using port 5000
netstat -ano | findstr :5000

# Change port in docker-compose.yml:
ports:
  - "5001:5000"  # Use 5001 instead
```

---

## 🧪 Testing the Deployment

### 1. Health Check

```bash
# Backend health
curl http://localhost:5000/health

# Should return: {"status": "healthy"}
```

### 2. API Test

```bash
# Test irrigation decision endpoint
curl -X POST http://localhost:5000/api/decision \
  -H "Content-Type: application/json" \
  -d '{
    "soil_moisture": 35,
    "temperature": 28,
    "humidity": 65,
    "rain": 0,
    "wind": 10,
    "forecast_rain_6h": 0
  }'
```

### 3. Frontend Test

Open browser: http://localhost:8501

Should see the AquaSmart dashboard.

---

## 📊 Resource Usage

### Expected Resource Consumption

```
Backend:
- CPU: 10-20% (idle), 50-80% (processing)
- RAM: 500MB-1GB
- Disk: 800MB (image) + models

Frontend:
- CPU: 5-10%
- RAM: 200-400MB
- Disk: 600MB (image)

Total: ~2GB RAM, ~2GB disk
```

### Optimize for Low Resources

Edit `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          memory: 512M
```

---

## 🚢 Production Deployment

### For Cloud Deployment (AWS, Azure, GCP)

1. **Push images to registry:**

```bash
# Tag images
docker tag aquasmart-backend:latest your-registry/aquasmart-backend:v1.0
docker tag aquasmart-frontend:latest your-registry/aquasmart-frontend:v1.0

# Push to registry
docker push your-registry/aquasmart-backend:v1.0
docker push your-registry/aquasmart-frontend:v1.0
```

2. **Use production docker-compose:**

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    image: your-registry/aquasmart-backend:v1.0
    environment:
      - FLASK_ENV=production
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure

  frontend:
    image: your-registry/aquasmart-frontend:v1.0
    deploy:
      replicas: 2
```

3. **Deploy:**

```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🔐 Security Best Practices

1. **Don't commit .env file**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Use secrets for production**
   ```yaml
   services:
     backend:
       secrets:
         - groq_api_key
   
   secrets:
     groq_api_key:
       external: true
   ```

3. **Run as non-root user**
   Add to Dockerfile:
   ```dockerfile
   RUN useradd -m appuser
   USER appuser
   ```

4. **Scan images for vulnerabilities**
   ```bash
   docker scan aquasmart-backend
   ```

---

## 📝 Common Commands Cheat Sheet

```bash
# Build
docker-compose build                    # Build all
docker-compose build --no-cache         # Clean build

# Start/Stop
docker-compose up -d                    # Start background
docker-compose down                     # Stop all
docker-compose restart                  # Restart all

# Logs
docker-compose logs -f                  # Follow logs
docker-compose logs backend --tail=50   # Last 50 lines

# Status
docker-compose ps                       # List containers
docker-compose top                      # Show processes

# Clean Up
docker-compose down -v                  # Remove volumes
docker system prune -a                  # Clean everything
docker volume prune                     # Remove unused volumes

# Execute Commands
docker-compose exec backend bash        # Shell into backend
docker-compose exec backend python test_system_ready.py
```

---

## 🎯 Hackathon Demo Setup

For quick demo setup:

```bash
# 1. One-time build
docker-compose build

# 2. Start for demo
docker-compose up -d

# 3. Open browser
start http://localhost:8501

# 4. After demo
docker-compose down
```

**Demo tip:** Start containers 2-3 minutes before presenting to ensure everything is loaded.

---

## 🐛 Debug Mode

Run with debug logging:

```bash
# Edit docker-compose.yml, add:
environment:
  - FLASK_DEBUG=1
  - LOG_LEVEL=DEBUG

# Restart
docker-compose up
```

---

## 📦 Backup & Restore

### Backup Models

```bash
# Create backup
docker run --rm -v aquasmart_backend-models:/data -v $(pwd):/backup \
  alpine tar czf /backup/models-backup.tar.gz -C /data .
```

### Restore Models

```bash
# Restore from backup
docker run --rm -v aquasmart_backend-models:/data -v $(pwd):/backup \
  alpine tar xzf /backup/models-backup.tar.gz -C /data
```

---

## ✅ Verification Checklist

Before demo:
- [ ] Docker Desktop running
- [ ] Images built successfully
- [ ] Containers running (`docker-compose ps`)
- [ ] Backend health check passes
- [ ] Frontend accessible at localhost:8501
- [ ] API responds to test requests
- [ ] Models loaded (check logs)
- [ ] .env file configured (if using APIs)

---

## 🎉 You're Ready!

Your AquaSmart system is now containerized and ready to deploy anywhere Docker runs!

**Quick Start:**
```bash
docker-compose up -d
```

**Access:**
- Frontend: http://localhost:8501
- Backend: http://localhost:5000

**Stop:**
```bash
docker-compose down
```

Good luck with your hackathon! 🚀
