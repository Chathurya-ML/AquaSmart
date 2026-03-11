"""
Rule-Based Irrigation Decision Module using FAO-56 Method.

This module provides a simple, reliable irrigation scheduling approach based on
soil water balance and Management Allowed Depletion (MAD) principles.

This is a faster alternative to RL training for hackathon demos.

Requirements: 2.1, 10.2
"""

from typing import Dict, Any


def irrigation_amount(
    sm_forecast: float,
    field_capacity: float = 0.30,
    wilting_point: float = 0.15,
    root_depth: float = 0.5,
    MAD: float = 0.4
) -> float:
    """
    Calculate irrigation amount using FAO-56 soil water balance method.
    
    The method works as follows:
    1. Calculate available water = field_capacity - wilting_point
    2. Calculate threshold = field_capacity - (MAD × available_water)
    3. If forecast < threshold: irrigate to bring soil back to field capacity
    4. Otherwise: no irrigation needed
    
    Args:
        sm_forecast: Forecasted soil moisture (volumetric, 0.0-1.0)
        field_capacity: Maximum water soil can hold (volumetric, default 0.30)
        wilting_point: Minimum water for plant survival (volumetric, default 0.15)
        root_depth: Effective root zone depth in meters (default 0.5m)
        MAD: Management Allowed Depletion fraction (default 0.4 = 40%)
    
    Returns:
        Irrigation amount in millimeters (mm)
        
    Example:
        >>> irrigation_amount(0.22, fc=0.30, wp=0.15, root_depth=0.5)
        40.0  # Need 40mm of water (= 400,000 liters for 1 hectare)
    """
    # Calculate available water capacity
    available_water = field_capacity - wilting_point
    
    # Calculate irrigation threshold (when to start irrigating)
    threshold = field_capacity - (MAD * available_water)
    
    # If forecast is below threshold, calculate irrigation needed
    if sm_forecast < threshold:
        # Water deficit in volumetric terms
        water_deficit = field_capacity - sm_forecast
        
        # Convert to depth (mm): deficit × root_depth × 1000
        irrigation_mm = water_deficit * root_depth * 1000
        
        return irrigation_mm
    else:
        # Soil moisture is adequate, no irrigation needed
        return 0.0


def irrigation_decision(current_state: Dict[str, Any], forecast: float) -> float:
    """
    Determine optimal irrigation amount using rule-based FAO-56 method.
    
    This function:
    1. Converts soil moisture from percentage to volumetric (÷ 100)
    2. Applies FAO-56 irrigation scheduling logic
    3. Adjusts for expected rainfall
    4. Converts from mm to liters/hour for system compatibility
    
    Args:
        current_state: Dictionary containing:
            - soil_moisture: Current soil moisture percentage (0-100)
            - rain: Expected rainfall in mm (optional)
            - temperature: Current temperature in Celsius (not used in calculation)
            - humidity: Current humidity percentage (not used in calculation)
        forecast: Predicted soil moisture percentage from LSTM (0-100)
    
    Returns:
        Irrigation amount in Liters (total water needed, not per hour)
        
    Notes:
        - Calculates total liters needed for 1 hectare field
        - 1mm of water over 1 hectare = 10,000 liters
        - Rainfall reduces irrigation proportionally
        - Field capacity = 30% volumetric (typical for loam soil)
        - Wilting point = 15% volumetric (typical for loam soil)
        - Root depth = 0.5m (typical for vegetables/crops)
        - MAD = 40% (conservative, suitable for most crops)
    
    Requirements: 2.1, 10.2
    """
    # Convert forecast from percentage to volumetric (0-100 -> 0.0-1.0)
    sm_forecast_volumetric = forecast / 100.0
    
    # Get expected rainfall (default to 0 if not provided)
    rainfall = float(current_state.get('rain', 0.0))
    
    # Calculate base irrigation amount using FAO-56 method
    # Using typical soil parameters for loam soil
    irrigation_mm = irrigation_amount(
        sm_forecast=sm_forecast_volumetric,
        field_capacity=0.30,   # 30% volumetric water content
        wilting_point=0.15,    # 15% volumetric water content
        root_depth=0.5,        # 50cm root zone
        MAD=0.4                # 40% depletion allowed
    )
    
    # Adjust for expected rainfall
    # Subtract rainfall from irrigation need (can't go negative)
    net_irrigation_mm = max(0.0, irrigation_mm - rainfall)
    
    # Convert mm to Liters (for 1 hectare field)
    # 1mm of water over 1 hectare = 10,000 liters
    # For typical field size, we calculate total liters needed
    # Assuming 1 hectare (10,000 m²) field
    field_area_m2 = 10000  # 1 hectare
    irrigation_liters = net_irrigation_mm * field_area_m2 / 1000  # mm to liters
    
    # Log decision for debugging
    if irrigation_mm > 0:
        print(f"Rule-based decision: Forecast={forecast:.1f}%, Need={irrigation_mm:.1f}mm, "
              f"Rainfall={rainfall:.1f}mm, Net irrigation={irrigation_liters:.0f} Liters")
    else:
        print(f"Rule-based decision: Forecast={forecast:.1f}% is adequate. No irrigation needed.")
    
    return irrigation_liters


def load_model(model_path: str = None):
    """
    Dummy function for compatibility with RL model interface.
    Rule-based approach doesn't need model loading.
    
    Args:
        model_path: Ignored (for interface compatibility)
    
    Returns:
        None (no model to load)
    """
    print("Rule-based irrigation: No model loading required")
    return None


def get_model():
    """
    Dummy function for compatibility with RL model interface.
    
    Returns:
        None (no model exists)
    """
    return None
