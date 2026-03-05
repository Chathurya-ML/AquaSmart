"""
Pydantic models for Smart Irrigation System API.

This module defines the data models for request/response validation
and internal data structures used throughout the system.
"""

from datetime import datetime
from typing import List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class SensorReading(BaseModel):
    """
    Model representing a single sensor reading with all 11 required features.
    
    Requirements: 1.4
    """
    timestamp: datetime = Field(..., description="Timestamp of the reading")
    season: int = Field(..., ge=0, le=3, description="Season (0=Spring, 1=Summer, 2=Fall, 3=Winter)")
    hour: int = Field(..., ge=0, le=23, description="Hour of day (0-23)")
    temperature: float = Field(..., ge=-50, le=60, description="Temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Humidity percentage")
    wind: float = Field(..., ge=0, description="Wind speed in m/s")
    rain: float = Field(..., ge=0, description="Rainfall in mm")
    irrigation: float = Field(..., ge=0, description="Irrigation amount in mm")
    soil_moisture: float = Field(..., ge=0, le=100, description="Soil moisture percentage")
    forecast_temp_6h: float = Field(..., ge=-50, le=60, description="Forecasted temperature 6h ahead in Celsius")
    forecast_rain_6h: float = Field(..., ge=0, description="Forecasted rainfall 6h ahead in mm")


class IrrigationRequest(BaseModel):
    """
    Request model for irrigation decision endpoint.
    
    Contains current sensor readings and historical data sequence.
    Requirements: 6.2, 1.4
    """
    soil_moisture: float = Field(
        ..., 
        ge=0, 
        le=100, 
        description="Current soil moisture percentage"
    )
    temperature: float = Field(
        ..., 
        ge=-50, 
        le=60, 
        description="Current temperature in Celsius"
    )
    humidity: float = Field(
        ..., 
        ge=0, 
        le=100, 
        description="Current humidity percentage"
    )
    rain: float = Field(
        ..., 
        ge=0, 
        description="Expected rainfall in mm"
    )
    forecast_temp_6h: float = Field(
        ..., 
        ge=-50, 
        le=60, 
        description="Forecasted temperature 6h ahead in Celsius"
    )
    forecast_rain_6h: float = Field(
        ..., 
        ge=0, 
        description="Forecasted rainfall 6h ahead in mm"
    )
    past_sequence: List[Dict[str, Any]] = Field(
        ..., 
        min_length=24, 
        description="Historical data with 11 features (minimum 24 data points)"
    )
    language: str = Field(
        default="en", 
        description="ISO language code for explanation translation"
    )
    
    @field_validator('past_sequence')
    @classmethod
    def validate_sequence(cls, v):
        """
        Validate that each record in past_sequence contains all 11 required features.
        
        Requirements: 1.4, 1.5
        """
        required_features = [
            'timestamp', 'season', 'hour', 'temperature', 'humidity',
            'wind', 'rain', 'irrigation', 'soil_moisture',
            'forecast_temp_6h', 'forecast_rain_6h'
        ]
        
        for idx, record in enumerate(v):
            missing = set(required_features) - set(record.keys())
            if missing:
                raise ValueError(
                    f"Record at index {idx} is missing required features: {missing}"
                )
        
        return v


class Alert(BaseModel):
    """
    Model representing an alert with severity and notification flag.
    
    Requirements: 3.1, 3.2, 3.3, 3.4
    """
    message: str = Field(..., description="Alert message text")
    severity: str = Field(..., description="Alert severity level (WARNING, CRITICAL)")
    notify: bool = Field(..., description="Whether to send notification via Twilio")
    timestamp: datetime = Field(default_factory=datetime.now, description="Alert generation timestamp")


class IrrigationResponse(BaseModel):
    """
    Response model for irrigation decision endpoint.
    
    Contains forecast, decision, alerts, and explanation with audio.
    Requirements: 6.3
    """
    forecasted_moisture: float = Field(
        ..., 
        description="Predicted soil moisture percentage in 6 hours"
    )
    irrigation_amount: float = Field(
        ..., 
        description="Recommended irrigation amount in mm"
    )
    alerts: List[str] = Field(
        default_factory=list, 
        description="List of active alert messages"
    )
    llm_explanation: str = Field(
        ..., 
        description="Human-readable explanation of the decision"
    )
    audio_base64: str = Field(
        ..., 
        description="Base64-encoded audio explanation"
    )
    next_run: str = Field(
        default="6 hours later", 
        description="Next scheduled run time"
    )


class ModelPrediction(BaseModel):
    """
    Model for logging ML model predictions and decisions.
    
    Used for storing results to S3/local storage for analysis and retraining.
    Requirements: 15.1, 15.2
    """
    timestamp: datetime = Field(default_factory=datetime.now, description="Prediction timestamp")
    farmer_id: str = Field(..., description="Unique farmer identifier")
    input_features: Dict[str, Any] = Field(..., description="Input features used for prediction")
    predicted_value: float = Field(..., description="Model output value")
    inference_time_ms: float = Field(..., description="Inference time in milliseconds")
    model_version: str = Field(default="1.0.0", description="Model version identifier")
