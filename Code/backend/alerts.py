"""
Alert Generation System for Smart Irrigation System.

This module provides functions for generating alerts based on forecasted
soil moisture and expected rainfall conditions.

Requirements: 3.1, 3.2, 3.3, 3.4
"""

from datetime import datetime
from typing import List
from models_schema import Alert


def generate_alerts(forecast: float, rain: float, irrigation_amount: float = None) -> List[Alert]:
    """
    Generate alerts based on forecasted conditions and irrigation decision.
    
    Alert Rules:
    1. forecast < 30% AND irrigation_amount > 0 → "Low soil moisture" alert (WARNING)
    2. forecast > 70% → "Risk of flooding" alert (WARNING)
    3. rain > 20mm → "Heavy rainfall expected" alert (CRITICAL)
    
    Args:
        forecast: Forecasted soil moisture percentage (0-100)
        rain: Expected rainfall in millimeters
        irrigation_amount: Recommended irrigation amount (optional)
    
    Returns:
        List of Alert objects with message, severity, notify, and timestamp
    
    Requirements: 3.1, 3.2, 3.3, 3.4
    """
    alerts = []
    current_time = datetime.now()
    
    # Check for low soil moisture (forecast < 30% AND irrigation needed)
    if forecast < 30 and irrigation_amount is not None and irrigation_amount > 0:
        alerts.append(Alert(
            message="Low soil moisture — irrigation needed soon.",
            severity="WARNING",
            notify=True,
            timestamp=current_time
        ))
    
    # Check for flooding risk (forecast > 70%)
    if forecast > 70:
        alerts.append(Alert(
            message="Risk of flooding — irrigation paused.",
            severity="WARNING",
            notify=True,
            timestamp=current_time
        ))
    
    # Check for heavy rainfall (rain > 20mm)
    if rain > 20:
        alerts.append(Alert(
            message="Heavy rainfall expected — flooding alert.",
            severity="CRITICAL",
            notify=True,
            timestamp=current_time
        ))
    
    return alerts
