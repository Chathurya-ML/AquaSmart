"""
FastAPI Backend for Smart Irrigation System.

This module provides the main API endpoints for irrigation decisions
and system health monitoring.

Requirements: 6.1, 6.3, 10.1, 10.2, 10.3, 12.1, 12.2
"""

# Load environment variables FIRST before any other imports
import os
from pathlib import Path

# Note: Railway injects environment variables directly
# .env is only used for local development
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent / '.env'
    load_dotenv(env_path)
except ImportError:
    pass  # dotenv not available in production

import time
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import data models
from models_schema import IrrigationRequest, IrrigationResponse

# Import core modules
from lstm_model import forecast_soil_moisture
from rule_based_irrigation import irrigation_decision  # Using rule-based FAO-56 method
from alerts import generate_alerts
from llm_explainer_improved import generate_explanation  # Improved LLM explanations
from translation_tts import translate_and_generate_audio
from storage import store_decision, log_model_prediction, append_sensor_data
from notifications import send_alert
from model_management import load_models_with_validation, check_models_loaded, get_model_status


# ============================================
# Application Lifecycle Management
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown.
    
    Startup: Load and validate models
    Shutdown: Cleanup resources
    
    Requirements: 10.1, 10.2, 10.3
    """
    # Startup: Load models
    print("=" * 60)
    print("Smart Irrigation System - Starting Up")
    print("=" * 60)
    
    success, message = load_models_with_validation()
    
    if not success:
        print(f"FATAL ERROR: {message}")
        print("Application cannot start without models.")
        raise RuntimeError(message)
    
    print(f"✓ {message}")
    print("=" * 60)
    print("Application ready to serve requests")
    print("=" * 60)
    
    yield
    
    # Shutdown: Cleanup
    print("Shutting down...")


# ============================================
# FastAPI Application
# ============================================

app = FastAPI(
    title="Smart Irrigation System API",
    description="ML-powered irrigation decision system with forecasting and alerts",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# API Endpoints
# ============================================

@app.post("/irrigation_decision", response_model=IrrigationResponse)
async def make_irrigation_decision(request: IrrigationRequest):
    """
    Make irrigation decision based on current conditions and forecast.
    
    This endpoint orchestrates the complete decision pipeline:
    1. Fetch historical data (from request)
    2. LSTM forecast
    3. RL decision
    4. Alert generation
    5. LLM explanation
    6. Translation and TTS
    7. Data logging
    8. Critical alert notifications
    
    Requirements: 6.1, 6.3, 1.1, 2.1, 3.1, 4.1, 8.1, 15.1, 15.2
    """
    start_time = time.time()
    
    try:
        # Step 1: LSTM Forecast
        forecast_start = time.time()
        forecasted_moisture = forecast_soil_moisture(request.past_sequence)
        forecast_time = (time.time() - forecast_start) * 1000  # ms
        
        # Step 2: RL Decision
        rl_start = time.time()
        current_state = {
            'soil_moisture': request.soil_moisture,
            'rain': request.rain,
            'temperature': request.temperature,
            'humidity': request.humidity
        }
        irrigation_amount = irrigation_decision(current_state, forecasted_moisture)
        rl_time = (time.time() - rl_start) * 1000  # ms
        
        # Step 3: Generate Alerts
        alert_objects = generate_alerts(forecasted_moisture, request.rain, irrigation_amount)
        alert_messages = [alert.message for alert in alert_objects]
        
        # Step 4: LLM Explanation (with validation and correction)
        explanation, corrected_irrigation_amount = generate_explanation(
            forecasted_moisture,
            irrigation_amount,
            current_state
        )
        
        # Use corrected amount if LLM changed it
        if corrected_irrigation_amount != irrigation_amount:
            print(f"LLM corrected irrigation: {irrigation_amount:.1f} L/h → {corrected_irrigation_amount:.1f} L/h")
            irrigation_amount = corrected_irrigation_amount
        
        # Step 5: Translation and TTS
        translated_explanation, audio_base64 = translate_and_generate_audio(
            explanation,
            request.language
        )
        
        # Step 6: Log LSTM prediction to storage
        log_model_prediction('lstm', {
            'timestamp': datetime.now().isoformat(),
            'farmer_id': 'default',
            'input_features': {
                'sequence_length': len(request.past_sequence),
                'current_moisture': request.soil_moisture
            },
            'predicted_value': forecasted_moisture,
            'inference_time_ms': forecast_time
        })
        
        # Step 7: Log RL decision to storage
        log_model_prediction('rl', {
            'timestamp': datetime.now().isoformat(),
            'farmer_id': 'default',
            'input_features': current_state,
            'predicted_value': irrigation_amount,
            'inference_time_ms': rl_time
        })
        
        # Step 8: Store decision in database
        store_decision({
            'decision_id': str(int(time.time())),
            'farmer_id': 'default',
            'timestamp': datetime.now().isoformat(),
            'current_moisture': request.soil_moisture,
            'forecasted_moisture': forecasted_moisture,
            'irrigation_amount': irrigation_amount,
            'alerts': alert_messages,
            'explanation': translated_explanation
        })
        
        # Step 9: Update CSV with new sensor reading (simulating 6-hour cycle)
        # This creates the next data point for the next 6-hour cycle
        from datetime import timedelta
        
        # Calculate next timestamp (6 hours later)
        next_timestamp = datetime.now() + timedelta(hours=6)
        
        # Create new sensor reading with forecasted values
        # In production, this would come from actual sensors
        new_reading = {
            'timestamp': next_timestamp.isoformat(),
            'season': 'winter',  # Would be calculated from date
            'hour': next_timestamp.hour,
            'temperature': request.forecast_temp_6h,  # Use forecasted temp
            'humidity': request.humidity,  # Assume similar humidity
            'wind': 10.0,  # Default value
            'rain': request.rain,  # Use forecasted rain
            'irrigation': irrigation_amount,  # Store the irrigation decision
            'soil_moisture': forecasted_moisture,  # Use forecasted moisture
            'forecast_temp_6h': request.forecast_temp_6h,  # Placeholder
            'forecast_rain_6h': request.forecast_rain_6h  # Placeholder
        }
        
        append_sensor_data(new_reading)
        
        # Step 10: Send critical alerts via notification service
        for alert in alert_objects:
            if alert.notify:
                send_alert(
                    farmer_phone='+1234567890',  # Default for prototype
                    message=alert.message,
                    language=request.language
                )
        
        # Calculate total response time
        response_time = (time.time() - start_time) * 1000
        print(f"Request processed in {response_time:.2f}ms")
        
        # Return response
        return IrrigationResponse(
            forecasted_moisture=forecasted_moisture,
            irrigation_amount=irrigation_amount,
            alerts=alert_messages,
            llm_explanation=translated_explanation,
            audio_base64=audio_base64,
            next_run="6 hours later"
        )
    
    except ValueError as e:
        # Validation errors (422)
        raise HTTPException(status_code=422, detail=str(e))
    
    except Exception as e:
        # Internal server errors (500)
        print(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred while processing irrigation decision"
        )


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring system status.
    
    Returns status of:
    - Models loaded
    - Database connection (commented for prototype)
    - Timestamp
    
    Requirements: 12.1, 12.2
    """
    start_time = time.time()
    
    # Check models loaded
    models_loaded = check_models_loaded()
    model_status = get_model_status()
    
    # Database connection check (commented for prototype)
    # database_connected = check_database_connection()
    database_connected = True  # Prototype: always true
    
    # Calculate response time
    response_time = (time.time() - start_time) * 1000
    
    # Ensure response within 2 seconds
    if response_time > 2000:
        print(f"WARNING: Health check took {response_time:.2f}ms (> 2000ms)")
    
    status = "healthy" if models_loaded and database_connected else "unhealthy"
    
    return {
        "status": status,
        "models_loaded": models_loaded,
        "lstm_loaded": model_status['lstm_loaded'],
        "rl_loaded": model_status['rl_loaded'],
        "database_connected": database_connected,
        "timestamp": datetime.now().isoformat(),
        "response_time_ms": response_time
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Smart Irrigation System API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


# ============================================
# Run Server
# ============================================

if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.environ.get("PORT", 8000))  # Railway sets PORT
    uvicorn.run(app, host="0.0.0.0", port=port)

