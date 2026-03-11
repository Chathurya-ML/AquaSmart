#!/usr/bin/env python3
"""Quick benchmark test for AquaSmart API"""

import requests
import time
import json
import pandas as pd
from datetime import datetime

API_URL = "http://localhost:8000"

# Load sensor data
try:
    sensor_data = pd.read_csv('Code/backend/data/sensor_readings.csv')
    past_sequence = sensor_data.tail(24).to_dict('records')
    current = sensor_data.iloc[-1]
except Exception as e:
    print(f"Error loading data: {e}")
    exit(1)

# Prepare request
request_data = {
    "soil_moisture": float(current['soil_moisture']),
    "temperature": float(current['temperature']),
    "humidity": float(current['humidity']),
    "rain": float(current['forecast_rain_6h']),
    "forecast_temp_6h": float(current['forecast_temp_6h']),
    "forecast_rain_6h": float(current['forecast_rain_6h']),
    "past_sequence": past_sequence,
    "language": "en"
}

print("=" * 60)
print("AquaSmart Benchmark Test")
print("=" * 60)

# Test 1: API Health
print("\n[1] API Health Check...")
try:
    start = time.time()
    response = requests.get(f"{API_URL}/health", timeout=5)
    elapsed = (time.time() - start) * 1000
    print(f"✓ Health: {elapsed:.2f}ms")
except Exception as e:
    print(f"✗ Health check failed: {e}")
    exit(1)

# Test 2: Single Request
print("\n[2] Single Irrigation Decision Request...")
times = []
for i in range(3):
    try:
        start = time.time()
        response = requests.post(
            f"{API_URL}/irrigation_decision",
            json=request_data,
            timeout=120
        )
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
        print(f"  Request {i+1}: {elapsed:.2f}ms")
        
        if response.status_code == 200:
            data = response.json()
            print(f"    - Irrigation: {data['irrigation_amount']:.1f} L/h")
            print(f"    - Forecast: {data['forecasted_moisture']:.1f}%")
    except Exception as e:
        print(f"  Request {i+1} failed: {e}")

if times:
    print(f"\n  Average: {sum(times)/len(times):.2f}ms")
    print(f"  Min: {min(times):.2f}ms")
    print(f"  Max: {max(times):.2f}ms")

# Test 3: History Endpoint
print("\n[3] History Endpoint...")
try:
    start = time.time()
    response = requests.get(f"{API_URL}/history", params={"limit": 50}, timeout=10)
    elapsed = (time.time() - start) * 1000
    print(f"✓ History: {elapsed:.2f}ms")
    if response.status_code == 200:
        history = response.json()
        if isinstance(history, dict) and 'history' in history:
            print(f"  Records: {len(history['history'])}")
except Exception as e:
    print(f"✗ History failed: {e}")

print("\n" + "=" * 60)
print("Benchmark Complete")
print("=" * 60)
