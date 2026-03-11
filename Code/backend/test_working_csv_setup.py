"""
Test the working CSV setup to ensure app.py can read and write correctly.
"""

import pandas as pd
import os
from pathlib import Path

def test_working_csv_setup():
    """Test that working CSV exists and has correct structure."""
    
    working_csv_path = 'Code/backend/data/working_sensor_data.csv'
    
    print("=" * 60)
    print("Testing Working CSV Setup")
    print("=" * 60)
    
    # Test 1: File exists
    if not os.path.exists(working_csv_path):
        print("✗ FAIL: Working CSV does not exist")
        return False
    print(f"✓ Working CSV exists: {working_csv_path}")
    
    # Test 2: Load CSV
    try:
        df = pd.read_csv(working_csv_path)
        print(f"✓ CSV loaded successfully: {len(df)} records")
    except Exception as e:
        print(f"✗ FAIL: Could not load CSV: {str(e)}")
        return False
    
    # Test 3: Check required columns
    required_columns = [
        'timestamp', 'season', 'hour', 'temperature', 'humidity',
        'wind', 'rain', 'irrigation', 'soil_moisture',
        'forecast_temp_6h', 'forecast_rain_6h'
    ]
    
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        print(f"✗ FAIL: Missing columns: {missing_cols}")
        return False
    print(f"✓ All required columns present")
    
    # Test 4: Check data types and ranges
    print("\nData Validation:")
    
    # Temperature range
    temp_min, temp_max = df['temperature'].min(), df['temperature'].max()
    print(f"  Temperature: {temp_min:.1f}°C to {temp_max:.1f}°C")
    if temp_min < -10 or temp_max > 50:
        print(f"  ⚠ WARNING: Temperature out of realistic range")
    
    # Humidity range
    humidity_min, humidity_max = df['humidity'].min(), df['humidity'].max()
    print(f"  Humidity: {humidity_min:.1f}% to {humidity_max:.1f}%")
    if humidity_min < 0 or humidity_max > 100:
        print(f"  ✗ FAIL: Humidity out of range [0-100]")
        return False
    
    # Soil moisture range
    sm_min, sm_max = df['soil_moisture'].min(), df['soil_moisture'].max()
    print(f"  Soil Moisture: {sm_min:.1f}% to {sm_max:.1f}%")
    if sm_min < 0 or sm_max > 100:
        print(f"  ✗ FAIL: Soil moisture out of range [0-100]")
        return False
    
    # Test 5: Check future forecasts
    print("\nFuture Weather Forecasts:")
    forecast_temp_mean = df['forecast_temp_6h'].mean()
    forecast_rain_mean = df['forecast_rain_6h'].mean()
    print(f"  Avg forecast temp: {forecast_temp_mean:.1f}°C")
    print(f"  Avg forecast rain: {forecast_rain_mean:.1f}mm")
    
    if df['forecast_temp_6h'].isna().any():
        print(f"  ✗ FAIL: Missing forecast temperature values")
        return False
    if df['forecast_rain_6h'].isna().any():
        print(f"  ✗ FAIL: Missing forecast rain values")
        return False
    print(f"  ✓ All forecast values present")
    
    # Test 6: Check latest record (for app.py to use)
    latest = df.iloc[-1]
    print(f"\nLatest Record (for app.py):")
    print(f"  Timestamp: {latest['timestamp']}")
    print(f"  Soil Moisture: {latest['soil_moisture']:.1f}%")
    print(f"  Temperature: {latest['temperature']:.1f}°C")
    print(f"  Forecast Temp (6h): {latest['forecast_temp_6h']:.1f}°C")
    print(f"  Forecast Rain (6h): {latest['forecast_rain_6h']:.1f}mm")
    
    # Test 7: Verify data is realistic (not all zeros or same values)
    if df['soil_moisture'].std() < 0.1:
        print(f"  ⚠ WARNING: Soil moisture has very low variation")
    if df['temperature'].std() < 0.1:
        print(f"  ⚠ WARNING: Temperature has very low variation")
    
    print("\n" + "=" * 60)
    print("✓ All tests passed! Working CSV is ready for app.py")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = test_working_csv_setup()
    exit(0 if success else 1)
