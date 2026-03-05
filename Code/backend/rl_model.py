"""
RL Decision Module for Smart Irrigation System.

This module provides functions for loading the RL model (PPO) and making
irrigation decisions based on current conditions and forecasts.

Requirements: 2.1, 10.2
"""

import numpy as np
import os
from typing import Dict, Any
from stable_baselines3 import PPO


# Global variable to store the loaded model
_rl_model = None


def load_rl_model(model_path: str = None) -> PPO:
    """
    Load the pre-trained RL model (PPO) from disk.
    
    Args:
        model_path: Path to the model file (default: models/proactive_irrigation_policy.zip)
    
    Returns:
        Loaded PPO model ready for inference
    
    Raises:
        FileNotFoundError: If model file doesn't exist
        RuntimeError: If model loading fails
    
    Requirements: 10.2
    """
    global _rl_model
    
    # If no path provided, use default path relative to this file
    if model_path is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, "models", "proactive_irrigation_policy.zip")
    
    try:
        # Load the PPO model using Stable-Baselines3
        _rl_model = PPO.load(model_path)
        
        return _rl_model
    
    except FileNotFoundError as e:
        raise FileNotFoundError(f"RL model file not found at {model_path}") from e
    except Exception as e:
        raise RuntimeError(f"Failed to load RL model: {str(e)}") from e


def irrigation_decision(current_state: Dict[str, Any], forecast: float) -> float:
    """
    Determine optimal irrigation amount using the RL model.
    
    This function:
    1. Constructs a 5-dimensional state array from current_state and forecast
    2. Uses rl_model.predict() with deterministic=True for inference
    3. Applies safety thresholds and rainfall adjustments
    4. Returns the irrigation amount as a float
    
    State dimensions:
    1. Current soil moisture (%)
    2. Forecasted soil moisture (%)
    3. Expected rainfall (mm)
    4. Current temperature (°C)
    5. Current humidity (%)
    
    Safety thresholds:
    - If current moisture < 40% OR forecast < 40%: Force minimum irrigation (50 L/h)
    - If forecast > 70%: Force zero irrigation
    - If rainfall > 5mm expected: Reduce irrigation by 50%
    - If rainfall > 10mm expected: Reduce irrigation by 75%
    
    Args:
        current_state: Dictionary containing:
            - soil_moisture: Current soil moisture percentage (0-100)
            - rain: Expected rainfall in mm
            - temperature: Current temperature in Celsius
            - humidity: Current humidity percentage (0-100)
        forecast: Predicted soil moisture from LSTM (0-100)
    
    Returns:
        Irrigation amount in liters/hour (non-negative float)
    
    Raises:
        ValueError: If current_state is invalid or model not loaded
        RuntimeError: If model inference fails
    
    Requirements: 2.1, 10.2
    """
    global _rl_model
    
    # Validate model is loaded
    if _rl_model is None:
        raise ValueError("RL model not loaded. Call load_rl_model() first.")
    
    # Validate current_state has required fields
    required_fields = ['soil_moisture', 'rain', 'temperature', 'humidity']
    missing_fields = [field for field in required_fields if field not in current_state]
    if missing_fields:
        raise ValueError(f"current_state missing required fields: {missing_fields}")
    
    try:
        current_moisture = float(current_state['soil_moisture'])
        rainfall = float(current_state['rain'])
        
        # Apply safety thresholds first
        # If current moisture is below target minimum (40%), force irrigation
        if current_moisture < 40:
            print(f"SAFETY: Current moisture {current_moisture:.1f}% is below target minimum (40%). Forcing irrigation (50 L/h)")
            return 50.0
        
        # If forecast is below target minimum (40%), force irrigation
        if forecast < 40:
            print(f"SAFETY: Forecast {forecast:.1f}% is below target minimum (40%). Forcing irrigation (50 L/h)")
            return 50.0
        
        # If forecast is very high (above 70%), no irrigation needed
        if forecast > 70:
            print(f"SAFETY: Forecast {forecast:.1f}% is above target maximum (70%). No irrigation needed")
            return 0.0
        
        # Construct 5-dimensional state array and normalize to [0, 1]
        # This matches the normalization in the training environment
        obs = np.array([
            current_moisture / 100.0,                    # current moisture: 0-100 -> 0-1
            float(forecast) / 100.0,                     # forecast: 0-100 -> 0-1
            np.clip(rainfall, 0, 50) / 50.0,           # rain: 0-50 -> 0-1 (capped at 50mm)
            np.clip((float(current_state['temperature']) + 10) / 60.0, 0, 1),  # temp: -10 to 50°C -> 0-1
            float(current_state['humidity']) / 100.0    # humidity: 0-100 -> 0-1
        ], dtype=np.float32)
        
        # Use RL model to predict irrigation amount with deterministic=True
        action, _ = _rl_model.predict(obs, deterministic=True)
        
        # Extract the irrigation amount
        # action is a numpy array, so we need to extract the scalar value
        irrigation_normalized = float(action[0]) if isinstance(action, np.ndarray) else float(action)
        
        # Scale from RL output [0, 1] to practical range (0-100 liters/hour)
        irrigation_amount = max(0.0, irrigation_normalized * 100.0)
        
        # Adjust irrigation based on expected rainfall
        # More rainfall = less irrigation needed
        if rainfall > 10:
            # Heavy rainfall expected: reduce irrigation by 75%
            irrigation_amount *= 0.25
            print(f"RAINFALL ADJUSTMENT: Heavy rainfall ({rainfall:.1f}mm) expected. Reducing irrigation by 75%")
        elif rainfall > 5:
            # Moderate rainfall expected: reduce irrigation by 50%
            irrigation_amount *= 0.5
            print(f"RAINFALL ADJUSTMENT: Moderate rainfall ({rainfall:.1f}mm) expected. Reducing irrigation by 50%")
        elif rainfall > 0:
            # Light rainfall expected: reduce irrigation by 25%
            irrigation_amount *= 0.75
            print(f"RAINFALL ADJUSTMENT: Light rainfall ({rainfall:.1f}mm) expected. Reducing irrigation by 25%")
        
        print(f"RL Model output: {irrigation_normalized:.3f} -> Scaled to {irrigation_amount:.1f} L/h")
        
        return irrigation_amount
    
    except Exception as e:
        raise RuntimeError(f"RL inference failed: {str(e)}") from e


def get_model():
    """
    Get the currently loaded RL model.
    
    Returns:
        The loaded PPO model, or None if not loaded
    """
    return _rl_model
