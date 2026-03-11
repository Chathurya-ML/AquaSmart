"""
Create a realistic working CSV with recent data for app.py to run on.
Data is based on patterns from the LSTM training data (2022 winter data).
Includes future weather forecasts for irrigation decisions.
"""

import pandas as pd
from datetime import datetime, timedelta
import numpy as np

# Read the main CSV to understand data patterns
df_main = pd.read_csv('Code/backend/data/sensor_readings.csv')

# Get statistics from the main CSV to create realistic data
temp_mean = df_main['temperature'].mean()
temp_std = df_main['temperature'].std()
humidity_mean = df_main['humidity'].mean()
humidity_std = df_main['humidity'].std()
wind_mean = df_main['wind'].mean()
wind_std = df_main['wind'].std()
soil_moisture_mean = df_main['soil_moisture'].mean()
soil_moisture_std = df_main['soil_moisture'].std()

print(f"Data statistics from main CSV:")
print(f"  Temperature: {temp_mean:.1f}°C ± {temp_std:.1f}")
print(f"  Humidity: {humidity_mean:.1f}% ± {humidity_std:.1f}")
print(f"  Wind: {wind_mean:.1f} m/s ± {wind_std:.1f}")
print(f"  Soil Moisture: {soil_moisture_mean:.1f}% ± {soil_moisture_std:.1f}")

# Create realistic data for the last 5 days (20 data points at 6-hour intervals)
np.random.seed(42)
data = []

# Start from 5 days ago
start_date = datetime.now() - timedelta(days=5)
start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

for i in range(20):
    timestamp = start_date + timedelta(hours=6*i)
    hour = timestamp.hour
    
    # Determine season (winter for realistic data)
    season = 'winter'
    
    # Generate realistic values based on hour of day and random variation
    # Temperature varies by hour (cooler at night, warmer during day)
    hour_factor = np.sin((hour - 6) * np.pi / 12)  # Peak at 12:00
    temperature = temp_mean + hour_factor * 5 + np.random.normal(0, temp_std * 0.3)
    
    # Humidity inversely correlated with temperature
    humidity = humidity_mean - hour_factor * 10 + np.random.normal(0, humidity_std * 0.3)
    humidity = np.clip(humidity, 20, 95)
    
    # Wind speed
    wind = max(0, wind_mean + np.random.normal(0, wind_std * 0.5))
    
    # Rain (mostly 0, occasional rain)
    rain = 0.0 if np.random.random() > 0.15 else np.random.uniform(2, 8)
    
    # Soil moisture (gradually decreases, then increases with irrigation/rain)
    if i == 0:
        soil_moisture = soil_moisture_mean + np.random.normal(0, soil_moisture_std * 0.2)
    else:
        # Decrease due to evapotranspiration, increase with rain/irrigation
        soil_moisture = data[i-1]['soil_moisture'] - 0.5 + rain * 0.3
        soil_moisture = np.clip(soil_moisture, 20, 50)
    
    # Irrigation (will be updated by app.py)
    irrigation = 0.0
    
    # Future forecasts (6 hours ahead)
    forecast_temp_6h = temperature + np.random.normal(0, 2)
    forecast_rain_6h = 0.0 if np.random.random() > 0.1 else np.random.uniform(1, 5)
    
    data.append({
        'timestamp': timestamp.isoformat(),
        'season': season,
        'hour': hour,
        'temperature': temperature,
        'humidity': humidity,
        'wind': wind,
        'rain': rain,
        'irrigation': irrigation,
        'soil_moisture': soil_moisture,
        'forecast_temp_6h': forecast_temp_6h,
        'forecast_rain_6h': forecast_rain_6h
    })

# Create DataFrame
df_working = pd.DataFrame(data)

# Save to working CSV
output_path = 'Code/backend/data/working_sensor_data.csv'
df_working.to_csv(output_path, index=False)

print(f"\n✓ Created realistic working CSV: {output_path}")
print(f"  Records: {len(df_working)}")
print(f"  Date range: {df_working['timestamp'].iloc[0]} to {df_working['timestamp'].iloc[-1]}")
print(f"\nSample data (first 3 rows):")
print(df_working.head(3).to_string())
print(f"\nLatest data (last 3 rows):")
print(df_working.tail(3).to_string())
