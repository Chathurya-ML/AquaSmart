"""
LSTM Forecasting Module for Smart Irrigation System.

This module provides functions for loading the LSTM model and performing
soil moisture forecasting based on historical sensor data.

Falls back to synthetic forecasting if LSTM model is not available.

Requirements: 1.1, 10.1
"""

import torch
import os
from typing import List, Dict, Any

# Import the model architecture so PyTorch can deserialize it
from model_architecture import SoilMoistureLSTM
from synthetic_forecast import forecast_soil_moisture_synthetic


# Global variable to store the loaded model
_lstm_model = None
_use_synthetic = False  # Flag to track if we're using synthetic forecasting


def load_lstm_model(model_path: str = None) -> torch.nn.Module:
    """
    Load the pre-trained LSTM model from disk.
    
    Args:
        model_path: Path to the model file (default: models/soil_forecast_model.pt relative to this file)
    
    Returns:
        Loaded PyTorch model in evaluation mode
    
    Raises:
        FileNotFoundError: If model file doesn't exist
        RuntimeError: If model loading fails
    
    Requirements: 10.1
    """
    global _lstm_model
    
    # If no path provided, use default path relative to this file
    if model_path is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, "models", "soil_forecast_model.pt")
    
    try:
        # Load the model with weights_only=False to support full model loading
        # We need to make SoilMoistureLSTM available in __main__ for unpickling
        import sys
        import __main__
        __main__.SoilMoistureLSTM = SoilMoistureLSTM
        
        _lstm_model = torch.load(model_path, weights_only=False)
        
        # Set model to evaluation mode
        _lstm_model.eval()
        
        return _lstm_model
    
    except FileNotFoundError as e:
        raise FileNotFoundError(f"LSTM model file not found at {model_path}") from e
    except Exception as e:
        raise RuntimeError(f"Failed to load LSTM model: {str(e)}") from e


def extract_features(past_sequence: List[Dict[str, Any]]) -> List[List[float]]:
    """
    Extract the required features from past_sequence for the LSTM model.
    
    The model was trained with 6 features (not 11 as originally specified):
    1. temperature (°C)
    2. humidity (%)
    3. wind (m/s)
    4. rain (mm)
    5. soil_moisture (%)
    6. forecast_rain_6h (mm)
    
    Args:
        past_sequence: List of dictionaries containing sensor readings
    
    Returns:
        2D list of shape (sequence_length, 6) with extracted features
    
    Requirements: 1.1, 1.4
    """
    features = []
    
    for record in past_sequence:
        # Extract the 6 features the model was trained on
        feature_vector = [
            float(record['temperature']),
            float(record['humidity']),
            float(record['wind']),
            float(record['rain']),
            float(record['soil_moisture']),
            float(record['forecast_rain_6h'])
        ]
        features.append(feature_vector)
    
    return features


def forecast_soil_moisture(past_sequence: List[Dict[str, Any]]) -> float:
    """
    Forecast soil moisture 6 hours ahead using the LSTM model.
    
    Falls back to synthetic forecasting if LSTM model is not available.
    
    This function:
    1. Tries to use LSTM model if loaded
    2. Falls back to synthetic forecasting if model unavailable
    3. Extracts 6 features from each record in past_sequence
    4. Converts the features to a PyTorch tensor
    5. Performs model inference with torch.no_grad()
    6. Returns the predicted moisture as a float
    
    Args:
        past_sequence: List of dictionaries with required features
                      (minimum 24 data points required)
                      Required features: temperature, humidity, wind, rain, 
                      soil_moisture, forecast_rain_6h
    
    Returns:
        Predicted soil moisture percentage (0-100)
    
    Raises:
        ValueError: If past_sequence is invalid
        RuntimeError: If both LSTM and synthetic forecasting fail
    
    Requirements: 1.1, 1.3
    """
    global _lstm_model, _use_synthetic
    
    # Validate input
    if not past_sequence or len(past_sequence) < 1:
        raise ValueError(f"past_sequence must contain at least 1 data point, got {len(past_sequence)}")
    
    # Try LSTM model first if loaded
    if _lstm_model is not None and not _use_synthetic:
        try:
            # Extract features from the sequence
            features = extract_features(past_sequence)
            
            # Convert to tensor: shape (batch=1, seq_len, features=6)
            tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0)
            
            # DEBUG: Log input statistics
            print(f"LSTM Input Debug:")
            print(f"  Sequence length: {len(past_sequence)}")
            print(f"  Last 3 soil moisture values: {[f[4] for f in features[-3:]]}")
            print(f"  Last 3 rainfall values: {[f[3] for f in features[-3:]]}")
            print(f"  Tensor shape: {tensor.shape}")
            print(f"  Tensor min/max: {tensor.min():.2f} / {tensor.max():.2f}")
            
            # Perform inference without gradient computation
            with torch.no_grad():
                prediction = _lstm_model(tensor)
            
            # Extract the scalar value and return as float
            predicted_moisture = float(prediction.item())
            
            print(f"  LSTM Prediction: {predicted_moisture:.2f}%")
            
            return predicted_moisture
        
        except Exception as e:
            print(f"LSTM inference failed: {str(e)}")
            print("Falling back to synthetic forecasting...")
            _use_synthetic = True
    
    # Use synthetic forecasting (fallback or primary)
    if _use_synthetic or _lstm_model is None:
        try:
            print("Using synthetic soil moisture forecast...")
            return forecast_soil_moisture_synthetic(past_sequence)
        except Exception as e:
            raise RuntimeError(f"Synthetic forecast failed: {str(e)}") from e


def get_model():
    """
    Get the currently loaded LSTM model.
    
    Returns:
        The loaded PyTorch model, or None if not loaded
    """
    return _lstm_model
