# 🧪 Pre-Deployment Testing Guide

## Quick Test (2 Minutes)

### Open These URLs in Your Browser

1. **Backend Health:**
   ```
   http://localhost:8000/health
   ```
   Expected: `{"status": "healthy"}`

2. **API Documentation:**
   ```
   http://localhost:8000/docs
   ```
   Expected: Swagger UI with all endpoints

3. **Frontend Dashboard:**
   ```
   http://localhost:8501
   ```
   Expected: AquaSmart dashboard with real-time data

---

## Detailed Testing

### Test 1: Backend Health Check ✅

**Command:**
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{"status": "healthy"}
```

**What it tests:*