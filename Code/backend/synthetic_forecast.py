"""
Synthetic Soil Moisture Forecasting Module.

This module provides synthetic forecasting for soil moisture when the LSTM model
is not available. It uses rule-based logic and historical patterns to generate
realistic predictions suitable for demonstration and testing.

Requirements: 1.1, 1.3
"""

import numpy as np
from typing import List, Dict, Any


def forecast_soil_moisture_synthetic(past_sequence: List[Dict[str, Any]]) -> float:
    """
    Generate a synthetic soil moisture forecast 6 hours ahead.
    
    This function uses rule-based logic to simulate LSTM predictions:
    1. Analyzes recent soil moisture trend
    2. Considers rainfall impact
    3. Accounts for temperature/evapotranspiration
    4. Adds realistic noise
    
    Args:
        past_sequence: List of dictionaries with sensor readings
                      Required fields: soil_moisture, rain, temperature, humidity
    
    Returns:
        Predicted soil moisture percentage (0-100)
    
    Requirements: 1.1, 1.3
    """
    if not past_sequence or len(past_sequence) < 1:
        return 50.0  # Default middle value
    
    try:
        # Extract current and recent values
        current_moisture = float(past_sequence[-1]['soil_moisture'])
        current_rain = float(past_sequence[-1]['rain'])
        current_temp = float(past_sequence[-1]['temperature'])
        current_humidity = float(past_sequence[-1]['humidity'])
        
        # Calculate trend from last 6 readings (if available)
        recent_readings = past_sequence[-6:] if len(past_sequence) >= 6 else past_sequence
        moisture_values = [float(r['soil_moisture']) for r in recent_readings]
        
        # Calculate moisture trend (slope)
        if len(moisture_values) > 1:
            trend = (moisture_values[-1] - moisture_values[0]) / len(moisture_values)
        else:
            trend = 0.0
        
        # Base forecast: continue current trend
        forecast = current_moisture + trend
        
        # Factor 1: Rainfall increases soil moisture
        # Each mm of rain adds approximately 0.5-1.0% to soil moisture
        rain_impact = current_rain * 0.75
        forecast += rain_impact
        
        # Factor 2: Temperature and humidity affect evapotranspiration
        # Higher temp = more evapotranspiration (moisture loss)
        # Higher humidity = less evapotranspiration
        # Baseline: 20°C, 60% humidity
        temp_factor = (current_temp - 20.0) * 0.15  # 0.15% per degree above 20°C
        humidity_factor = (current_humidity - 60.0) * 0.05  # 0.05% per % above 60%
        
        evapotranspiration = temp_factor - humidity_factor
        forecast -= evapotranspiration
        
        # Factor 3: Add realistic noise (±2%)
        noise = np.random.normal(0, 1.5)
        forecast += noise
        
        # Clamp to valid range [0, 100]
        forecast = max(0.0, min(100.0, forecast))
        
        # Debug logging
        print(f"Synthetic Forecast Debug:")
        print(f"  Current moisture: {current_moisture:.2f}%")
        print(f"  Trend: {trend:.2f}%")
        print(f"  Rain impact: +{rain_impact:.2f}%")
        print(f"  Evapotranspiration: -{evapotranspiration:.2f}%")
        print(f"  Noise: {noise:+.2f}%")
        print(f"  Final forecast: {forecast:.2f}%")
        
        return forecast
    
    except (KeyError, ValueError, TypeError) as e:
        print(f"Error in synthetic forecast: {str(e)}")
        # Fallback: return current moisture
        return float(past_sequence[-1].get('soil_moisture', 50.0))


def forecast_soil_moisture_advanced(past_sequence: List[Dict[str, Any]]) -> float:
    """
    Advanced synthetic forecast using more sophisticated patterns.
    
    This version considers:
    - Seasonal patterns
    - Irrigation history
    - Multi-day trends
    - Weather patterns
    
    Args:
        past_sequence: List of sensor readings
    
    Returns:
        Predicted soil moisture percentage (0-100)
    
    Requirements: 1.1, 1.3
    """
    if not past_sequence or len(past_sequence) < 1:
        return 50.0
    
    try:
        current_moisture = float(past_sequence[-1]['soil_moisture'])
        
        # Get historical data for pattern analysis
        if len(past_sequence) >= 24:
            # Analyze 24-hour pattern
            day_readings = past_sequence[-24:]
            moisture_24h = [float(r['soil_moisture']) for r in day_readings]
            
            # Calculate daily average and variance
            daily_avg = np.mean(moisture_24h)
            daily_std = np.std(moisture_24h)
            
            # Predict based on daily pattern
            # If currently above average, expect decrease
            # If currently below average, expect increase
            deviation = current_moisture - daily_avg
            mean_reversion = -deviation * 0.3  # 30% mean reversion
        else:
            mean_reversion = 0.0
        
        # Get recent weather impact
        recent_rain = sum(float(r.get('rain', 0)) for r in past_sequence[-6:])
        recent_temp = np.mean([float(r.get('temperature', 20)) for r in past_sequence[-6:]])
        
        # Calculate forecast
        forecast = current_moisture
        
        # Apply mean reversion
        forecast += mean_reversion
        
        # Apply weather impact
        forecast += recent_rain * 0.5  # Rain increases moisture
        forecast -= (recent_temp - 20.0) * 0.1  # Heat increases evapotranspiration
        
        # Add realistic variation
        forecast += np.random.normal(0, 1.0)
        
        # Clamp to valid range
        forecast = max(0.0, min(100.0, forecast))
        
        return forecast
    
    except Exception as e:
        print(f"Error in advanced forecast: {str(e)}")
        return float(past_sequence[-1].get('soil_moisture', 50.0))
