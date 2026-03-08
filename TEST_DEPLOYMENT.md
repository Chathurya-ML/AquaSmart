# 🧪 Pre-Deployment Testing Guide

## Test Checklist

### 1. Backend Health Check
```bash
curl http://localhost:8000/health
```
Expected response:
```json
{"status": "healthy"}
```

### 2. API Documentation
Open in browser:
```
http://localhost:8000/docs
```
Should show Swagger UI with all endpoints

### 3. Frontend Dashboard
Open in browser:
```
http://localhost:8501
```
Should show AquaSmart dashboard with real-time data

### 4. Test Endpoints

#### Get Irrigation Decision
```bash
curl -X POST http://localhost:8000/irrigation_decision \
  -H "Content-Type: application/json" \
  -d '{
    "soil_moisture": 45,
    "temperature": 28,
    "humidity": 65,
    "rainfall": 0
  }'
```

#### Get Forecast
```bash
curl http://localhost:8000/forecast
```

#### Get Alerts
```bash
curl http://localhost:8000/alerts
```

---

## Manual Testing Steps

### Step 1: Start Backend
```bash
cd Code/backend
python app.py
```
Wait for: `Uvicorn running on http://0.0.0.0:8000`

### Step 2: Start Frontend
In a new terminal:
```bash
cd Code/frontend
streamlit run dashboard.py --server.port 8501
```
Wait for: `You can now view your Streamlit app in your browser`

### Step 3: Test in Browser
1. Open http://localhost:8501
2. Check if dashboard loads
3. Verify real-time data displays
4. Test language selector
5. Check alerts display

### Step 4: Test API
1. Open http://localhost:8000/docs
2. Try endpoints:
   - GET /health
   - GET /forecast
   - GET /alerts
   - POST /irrigation_decision

---

## Docker Testing

### Build Images
```bash
docker-compose build
```

### Start Services
```bash
docker-compose up
```

### Test Services
```bash
# Backend health
curl http://localhost:8000/health

# Frontend
Open http://localhost:8501 in browser
```

### Stop Services
```bash
docker-compose down
```

---

## Expected Results

### Backend ✅
- [ ] Health check returns 200
- [ ] API documentation loads
- [ ] Endpoints respond correctly
- [ ] Models load successfully
- [ ] No errors in logs

### Frontend ✅
- [ ] Dashboard loads
- [ ] Real-time data displays
- [ ] Charts render correctly
- [ ] Language selector works
- [ ] Alerts display properly

### Integration ✅
- [ ] Frontend connects to backend
- [ ] Data flows correctly
- [ ] No CORS errors
- [ ] All features work together

---

## Troubleshooting

### Backend Won't Start
- Check port 8000 is available
- Verify Python 3.10+ installed
- Check requirements.txt installed
- Check models exist in Code/backend/models/

### Frontend Won't Start
- Check port 8501 is available
- Verify Streamlit installed
- Check BACKEND_URL environment variable
- Check backend is running

### Connection Error
- Verify both services running
- Check BACKEND_URL is correct
- Check firewall settings
- Check network connectivity

### Model Loading Error
- Verify models exist:
  - Code/backend/models/soil_forecast_model.pt
  - Code/backend/models/proactive_irrigation_policy.zip
- Check file permissions
- Check disk space

---

## Performance Metrics

### Expected Response Times
- Health check: < 100ms
- Forecast: < 500ms
- Irrigation decision: < 1000ms
- Dashboard load: < 2000ms

### Expected Resource Usage
- Backend: ~200-300 MB RAM
- Frontend: ~150-200 MB RAM
- Total: ~400-500 MB RAM

---

## Success Criteria

✅ All endpoints respond correctly
✅ Dashboard displays real-time data
✅ No errors in logs
✅ Response times acceptable
✅ All features working
✅ Ready for Railway deployment

---

## Next Steps

If all tests pass:
1. Commit any changes
2. Push to GitHub
3. Run RAILWAY_SETUP.bat or RAILWAY_SETUP.sh
4. Deploy to Railway

If tests fail:
1. Check logs for errors
2. Verify configuration
3. Check environment variables
4. Review troubleshooting section

---

## Test Results

| Test | Status | Notes |
|------|--------|-------|
| Backend Health | ⏳ | Run: curl http://localhost:8000/health |
| API Docs | ⏳ | Open: http://localhost:8000/docs |
| Frontend | ⏳ | Open: http://localhost:8501 |
| Forecast | ⏳ | Test endpoint |
| Alerts | ⏳ | Test endpoint |
| Integration | ⏳ | Test frontend-backend connection |

---

**Good luck with testing! 🧪**

