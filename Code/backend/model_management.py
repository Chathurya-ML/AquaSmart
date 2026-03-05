"""
Model Management Module for Smart Irrigation System.

This module provides functions for loading, validating, and managing
ML models (LSTM and RL) with checksum validation and hot-reload support.

Requirements: 10.1, 10.2, 10.3, 10.4, 10.5
"""

import os
import hashlib
import time
from typing import Optional, Dict, Tuple
from pathlib import Path
import torch
from stable_baselines3 import PPO

# Import model loading functions
from lstm_model import load_lstm_model, get_model as get_lstm_model
from rl_model import load_rl_model, get_model as get_rl_model

# Model file paths
LSTM_MODEL_PATH = os.getenv('LSTM_MODEL_PATH', './models/soil_forecast_model.pt')
RL_MODEL_PATH = os.getenv('RL_MODEL_PATH', './models/proactive_irrigation_policy.zip')

# Model metadata
_model_checksums: Dict[str, str] = {}
_model_load_times: Dict[str, float] = {}
_models_loaded: bool = False


def calculate_checksum(file_path: str) -> str:
    """
    Calculate SHA256 checksum of a file.
    
    Args:
        file_path: Path to the file
    
    Returns:
        Hexadecimal checksum string
    
    Requirements: 10.5
    """
    sha256_hash = hashlib.sha256()
    
    with open(file_path, 'rb') as f:
        # Read file in chunks to handle large files
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    return sha256_hash.hexdigest()


def validate_model_file(file_path: str, model_type: str) -> bool:
    """
    Validate that a model file exists and has correct format.
    
    Args:
        file_path: Path to the model file
        model_type: Type of model ('lstm' or 'rl')
    
    Returns:
        True if valid, False otherwise
    
    Requirements: 10.3, 10.5
    """
    # Check file exists
    if not os.path.exists(file_path):
        print(f"Model file not found: {file_path}")
        return False
    
    # Check file is not empty
    if os.path.getsize(file_path) == 0:
        print(f"Model file is empty: {file_path}")
        return False
    
    # Check file extension
    if model_type == 'lstm':
        if not file_path.endswith('.pt'):
            print(f"Invalid LSTM model file extension: {file_path}")
            return False
    elif model_type == 'rl':
        if not file_path.endswith('.zip'):
            print(f"Invalid RL model file extension: {file_path}")
            return False
    
    return True


def load_models_with_validation() -> Tuple[bool, str]:
    """
    Load both LSTM and RL models with validation.
    
    This function:
    1. Validates model files exist and have correct format
    2. Calculates checksums for integrity validation
    3. Loads both models
    4. Prevents application startup if models fail to load
    
    Returns:
        Tuple of (success: bool, error_message: str)
    
    Requirements: 10.1, 10.2, 10.3, 10.5
    """
    global _models_loaded, _model_checksums, _model_load_times
    
    try:
        # Validate LSTM model file
        if not validate_model_file(LSTM_MODEL_PATH, 'lstm'):
            return False, f"LSTM model validation failed: {LSTM_MODEL_PATH}"
        
        # Validate RL model file
        if not validate_model_file(RL_MODEL_PATH, 'rl'):
            return False, f"RL model validation failed: {RL_MODEL_PATH}"
        
        # Calculate checksums for integrity validation
        print("Calculating model checksums...")
        lstm_checksum = calculate_checksum(LSTM_MODEL_PATH)
        rl_checksum = calculate_checksum(RL_MODEL_PATH)
        
        _model_checksums['lstm'] = lstm_checksum
        _model_checksums['rl'] = rl_checksum
        
        print(f"LSTM model checksum: {lstm_checksum[:16]}...")
        print(f"RL model checksum: {rl_checksum[:16]}...")
        
        # Load LSTM model
        print(f"Loading LSTM model from {LSTM_MODEL_PATH}...")
        start_time = time.time()
        lstm_model = load_lstm_model(LSTM_MODEL_PATH)
        lstm_load_time = time.time() - start_time
        _model_load_times['lstm'] = lstm_load_time
        print(f"LSTM model loaded successfully in {lstm_load_time:.2f}s")
        
        # Load RL model
        print(f"Loading RL model from {RL_MODEL_PATH}...")
        start_time = time.time()
        rl_model = load_rl_model(RL_MODEL_PATH)
        rl_load_time = time.time() - start_time
        _model_load_times['rl'] = rl_load_time
        print(f"RL model loaded successfully in {rl_load_time:.2f}s")
        
        _models_loaded = True
        return True, "Models loaded successfully"
    
    except FileNotFoundError as e:
        error_msg = f"Model file not found: {str(e)}"
        print(error_msg)
        return False, error_msg
    
    except Exception as e:
        error_msg = f"Model loading failed: {str(e)}"
        print(error_msg)
        return False, error_msg


def check_models_loaded() -> bool:
    """
    Check if both models are loaded and ready.
    
    Returns:
        True if both models loaded, False otherwise
    
    Requirements: 10.3
    """
    return _models_loaded and get_lstm_model() is not None and get_rl_model() is not None


def get_model_status() -> Dict[str, any]:
    """
    Get status information about loaded models.
    
    Returns:
        Dictionary with model status information
    
    Requirements: 10.1, 10.2
    """
    return {
        'models_loaded': _models_loaded,
        'lstm_loaded': get_lstm_model() is not None,
        'rl_loaded': get_rl_model() is not None,
        'lstm_checksum': _model_checksums.get('lstm', 'N/A'),
        'rl_checksum': _model_checksums.get('rl', 'N/A'),
        'lstm_load_time': _model_load_times.get('lstm', 0),
        'rl_load_time': _model_load_times.get('rl', 0)
    }


def detect_model_changes() -> Dict[str, bool]:
    """
    Detect if model files have changed (for hot-reload).
    
    Compares current file checksums with stored checksums to detect changes.
    
    Returns:
        Dictionary indicating which models have changed
    
    Requirements: 10.4
    """
    changes = {
        'lstm_changed': False,
        'rl_changed': False
    }
    
    try:
        # Check LSTM model
        if os.path.exists(LSTM_MODEL_PATH):
            current_lstm_checksum = calculate_checksum(LSTM_MODEL_PATH)
            if 'lstm' in _model_checksums:
                changes['lstm_changed'] = current_lstm_checksum != _model_checksums['lstm']
        
        # Check RL model
        if os.path.exists(RL_MODEL_PATH):
            current_rl_checksum = calculate_checksum(RL_MODEL_PATH)
            if 'rl' in _model_checksums:
                changes['rl_changed'] = current_rl_checksum != _model_checksums['rl']
    
    except Exception as e:
        print(f"Error detecting model changes: {str(e)}")
    
    return changes


def hot_reload_models() -> Tuple[bool, str]:
    """
    Hot-reload models if files have changed.
    
    This function:
    1. Detects if model files have changed
    2. Reloads changed models without restarting the application
    3. Updates checksums and load times
    
    Returns:
        Tuple of (success: bool, message: str)
    
    Requirements: 10.4
    """
    global _model_checksums, _model_load_times
    
    changes = detect_model_changes()
    
    if not changes['lstm_changed'] and not changes['rl_changed']:
        return True, "No model changes detected"
    
    messages = []
    
    try:
        # Reload LSTM model if changed
        if changes['lstm_changed']:
            print("LSTM model file changed. Reloading...")
            start_time = time.time()
            load_lstm_model(LSTM_MODEL_PATH)
            load_time = time.time() - start_time
            
            _model_checksums['lstm'] = calculate_checksum(LSTM_MODEL_PATH)
            _model_load_times['lstm'] = load_time
            
            messages.append(f"LSTM model reloaded in {load_time:.2f}s")
        
        # Reload RL model if changed
        if changes['rl_changed']:
            print("RL model file changed. Reloading...")
            start_time = time.time()
            load_rl_model(RL_MODEL_PATH)
            load_time = time.time() - start_time
            
            _model_checksums['rl'] = calculate_checksum(RL_MODEL_PATH)
            _model_load_times['rl'] = load_time
            
            messages.append(f"RL model reloaded in {load_time:.2f}s")
        
        return True, "; ".join(messages)
    
    except Exception as e:
        error_msg = f"Hot reload failed: {str(e)}"
        print(error_msg)
        return False, error_msg


def verify_model_integrity() -> Tuple[bool, str]:
    """
    Verify model file integrity using checksums.
    
    Recalculates checksums and compares with stored values to detect corruption.
    
    Returns:
        Tuple of (valid: bool, message: str)
    
    Requirements: 10.5
    """
    try:
        # Verify LSTM model
        if os.path.exists(LSTM_MODEL_PATH):
            current_lstm_checksum = calculate_checksum(LSTM_MODEL_PATH)
            if 'lstm' in _model_checksums:
                if current_lstm_checksum != _model_checksums['lstm']:
                    return False, "LSTM model file has been modified or corrupted"
        else:
            return False, "LSTM model file not found"
        
        # Verify RL model
        if os.path.exists(RL_MODEL_PATH):
            current_rl_checksum = calculate_checksum(RL_MODEL_PATH)
            if 'rl' in _model_checksums:
                if current_rl_checksum != _model_checksums['rl']:
                    return False, "RL model file has been modified or corrupted"
        else:
            return False, "RL model file not found"
        
        return True, "Model integrity verified"
    
    except Exception as e:
        return False, f"Integrity check failed: {str(e)}"
