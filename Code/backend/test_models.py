"""
Unit tests for Pydantic models validation.

Tests the IrrigationRequest, IrrigationResponse, and SensorReading models
to ensure proper validation of fields and ranges.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from models_schema import IrrigationRequest, IrrigationResponse, SensorReading


def test_sensor_reading_valid():
    """Test SensorReading with valid data."""
    reading = SensorReading(
        timestamp=datetime.now(),
        season=1,
        hour=12,
        temperature=25.5,
        humidity=60.0,
        wind=3.5,
        rain=0.0,
        irrigation=5.0,
        soil_moisture=45.0,
        forecast_temp_6h=26.0,
        forecast_rain_6h=2.0
    )
    assert reading.season == 1
    assert reading.hour == 12
    assert reading.soil_moisture == 45.0


def test_sensor_reading_invalid_season():
    """Test SensorReading rejects invalid season."""
    with pytest.raises(ValidationError) as exc_info:
        SensorReading(
            timestamp=datetime.now(),
            season=5,  # Invalid: must be 0-3
            hour=12,
            temperature=25.5,
            humidity=60.0,
            wind=3.5,
            rain=0.0,
            irrigation=5.0,
            soil_moisture=45.0,
            forecast_temp_6h=26.0,
            forecast_rain_6h=2.0
        )
    assert "season" in str(exc_info.value)


def test_sensor_reading_invalid_hour():
    """Test SensorReading rejects invalid hour."""
    with pytest.raises(ValidationError) as exc_info:
        SensorReading(
            timestamp=datetime.now(),
            season=1,
            hour=25,  # Invalid: must be 0-23
            temperature=25.5,
            humidity=60.0,
            wind=3.5,
            rain=0.0,
            irrigation=5.0,
            soil_moisture=45.0,
            forecast_temp_6h=26.0,
            forecast_rain_6h=2.0
        )
    assert "hour" in str(exc_info.value)


def test_irrigation_request_valid():
    """Test IrrigationRequest with valid data."""
    past_sequence = [
        {
            'timestamp': '2024-01-15T10:00:00',
            'season': 0,
            'hour': 10,
            'temperature': 20.0,
            'humidity': 55.0,
            'wind': 2.5,
            'rain': 0.0,
            'irrigation': 3.0,
            'soil_moisture': 50.0,
            'forecast_temp_6h': 22.0,
            'forecast_rain_6h': 0.0
        }
        for _ in range(24)
    ]
    
    request = IrrigationRequest(
        soil_moisture=50.0,
        temperature=25.0,
        humidity=60.0,
        rain=5.0,
        forecast_temp_6h=26.0,
        forecast_rain_6h=2.0,
        past_sequence=past_sequence,
        language="en"
    )
    
    assert request.soil_moisture == 50.0
    assert request.language == "en"
    assert len(request.past_sequence) == 24


def test_irrigation_request_invalid_soil_moisture():
    """Test IrrigationRequest rejects invalid soil moisture."""
    past_sequence = [
        {
            'timestamp': '2024-01-15T10:00:00',
            'season': 0,
            'hour': 10,
            'temperature': 20.0,
            'humidity': 55.0,
            'wind': 2.5,
            'rain': 0.0,
            'irrigation': 3.0,
            'soil_moisture': 50.0,
            'forecast_temp_6h': 22.0,
            'forecast_rain_6h': 0.0
        }
        for _ in range(24)
    ]
    
    with pytest.raises(ValidationError) as exc_info:
        IrrigationRequest(
            soil_moisture=150.0,  # Invalid: must be 0-100
            temperature=25.0,
            humidity=60.0,
            rain=5.0,
            forecast_temp_6h=26.0,
            forecast_rain_6h=2.0,
            past_sequence=past_sequence,
            language="en"
        )
    assert "soil_moisture" in str(exc_info.value)


def test_irrigation_request_insufficient_sequence():
    """Test IrrigationRequest rejects sequence with < 24 data points."""
    past_sequence = [
        {
            'timestamp': '2024-01-15T10:00:00',
            'season': 0,
            'hour': 10,
            'temperature': 20.0,
            'humidity': 55.0,
            'wind': 2.5,
            'rain': 0.0,
            'irrigation': 3.0,
            'soil_moisture': 50.0,
            'forecast_temp_6h': 22.0,
            'forecast_rain_6h': 0.0
        }
        for _ in range(10)  # Only 10 data points
    ]
    
    with pytest.raises(ValidationError) as exc_info:
        IrrigationRequest(
            soil_moisture=50.0,
            temperature=25.0,
            humidity=60.0,
            rain=5.0,
            forecast_temp_6h=26.0,
            forecast_rain_6h=2.0,
            past_sequence=past_sequence,
            language="en"
        )
    assert "past_sequence" in str(exc_info.value)


def test_irrigation_request_missing_features():
    """Test IrrigationRequest rejects sequence with missing features."""
    past_sequence = [
        {
            'timestamp': '2024-01-15T10:00:00',
            'season': 0,
            'hour': 10,
            'temperature': 20.0,
            # Missing: humidity, wind, rain, irrigation, soil_moisture, forecast_temp_6h, forecast_rain_6h
        }
        for _ in range(24)
    ]
    
    with pytest.raises(ValidationError) as exc_info:
        IrrigationRequest(
            soil_moisture=50.0,
            temperature=25.0,
            humidity=60.0,
            rain=5.0,
            forecast_temp_6h=26.0,
            forecast_rain_6h=2.0,
            past_sequence=past_sequence,
            language="en"
        )
    assert "missing required features" in str(exc_info.value).lower()


def test_irrigation_response_valid():
    """Test IrrigationResponse with valid data."""
    response = IrrigationResponse(
        forecasted_moisture=55.0,
        irrigation_amount=10.5,
        alerts=["Low soil moisture — irrigation needed soon."],
        llm_explanation="The system recommends 10.5mm irrigation.",
        audio_base64="YXVkaW9kYXRh",
        next_run="6 hours later"
    )
    
    assert response.forecasted_moisture == 55.0
    assert response.irrigation_amount == 10.5
    assert len(response.alerts) == 1
    assert response.next_run == "6 hours later"


def test_irrigation_response_empty_alerts():
    """Test IrrigationResponse with no alerts."""
    response = IrrigationResponse(
        forecasted_moisture=55.0,
        irrigation_amount=10.5,
        alerts=[],
        llm_explanation="The system recommends 10.5mm irrigation.",
        audio_base64="YXVkaW9kYXRh"
    )
    
    assert len(response.alerts) == 0
    assert response.next_run == "6 hours later"  # Default value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# ============================================================================
# Property-Based Tests
# ============================================================================

from hypothesis import given, strategies as st
from hypothesis import settings


# Strategy for generating valid sensor reading dictionaries
def valid_sensor_reading_dict():
    """Generate a valid sensor reading dictionary with all 11 features."""
    return st.fixed_dictionaries({
        'timestamp': st.datetimes().map(lambda dt: dt.isoformat()),
        'season': st.integers(min_value=0, max_value=3),
        'hour': st.integers(min_value=0, max_value=23),
        'temperature': st.floats(min_value=-50, max_value=60, allow_nan=False, allow_infinity=False),
        'humidity': st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False),
        'wind': st.floats(min_value=0, max_value=50, allow_nan=False, allow_infinity=False),
        'rain': st.floats(min_value=0, max_value=200, allow_nan=False, allow_infinity=False),
        'irrigation': st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False),
        'soil_moisture': st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False),
        'forecast_temp_6h': st.floats(min_value=-50, max_value=60, allow_nan=False, allow_infinity=False),
        'forecast_rain_6h': st.floats(min_value=0, max_value=200, allow_nan=False, allow_infinity=False),
    })


@settings(max_examples=100)
@given(
    missing_feature=st.sampled_from([
        'timestamp', 'season', 'hour', 'temperature', 'humidity',
        'wind', 'rain', 'irrigation', 'soil_moisture',
        'forecast_temp_6h', 'forecast_rain_6h'
    ])
)
def test_property_lstm_input_validation_missing_features(missing_feature):
    """
    Property 3: LSTM Input Validation
    
    For any input sequence missing one or more of the 11 required features,
    the system should reject the forecast request with a descriptive validation error.
    
    Validates: Requirements 1.4, 1.5
    """
    # Generate a sequence with one feature missing
    past_sequence = []
    for _ in range(24):
        reading = {
            'timestamp': '2024-01-15T10:00:00',
            'season': 0,
            'hour': 10,
            'temperature': 20.0,
            'humidity': 55.0,
            'wind': 2.5,
            'rain': 0.0,
            'irrigation': 3.0,
            'soil_moisture': 50.0,
            'forecast_temp_6h': 22.0,
            'forecast_rain_6h': 0.0
        }
        # Remove the selected feature
        del reading[missing_feature]
        past_sequence.append(reading)
    
    # The request should be rejected with a validation error
    with pytest.raises(ValidationError) as exc_info:
        IrrigationRequest(
            soil_moisture=50.0,
            temperature=25.0,
            humidity=60.0,
            rain=5.0,
            forecast_temp_6h=26.0,
            forecast_rain_6h=2.0,
            past_sequence=past_sequence,
            language="en"
        )
    
    # Verify the error message mentions missing features
    error_message = str(exc_info.value).lower()
    assert "missing required features" in error_message or missing_feature in error_message


@settings(max_examples=100)
@given(
    soil_moisture=st.one_of(
        st.floats(min_value=-1000, max_value=-0.01),
        st.floats(min_value=100.01, max_value=1000)
    ).filter(lambda x: not (x != x)),  # Filter out NaN
    temperature=st.one_of(
        st.floats(min_value=-1000, max_value=-50.01),
        st.floats(min_value=60.01, max_value=1000)
    ).filter(lambda x: not (x != x)),
    humidity=st.one_of(
        st.floats(min_value=-1000, max_value=-0.01),
        st.floats(min_value=100.01, max_value=1000)
    ).filter(lambda x: not (x != x)),
)
def test_property_lstm_input_validation_invalid_ranges(soil_moisture, temperature, humidity):
    """
    Property 3: LSTM Input Validation
    
    For any input containing values outside valid ranges, the system should
    reject the forecast request with a descriptive validation error.
    
    Validates: Requirements 1.4, 1.5
    """
    # Generate a valid sequence
    past_sequence = [
        {
            'timestamp': '2024-01-15T10:00:00',
            'season': 0,
            'hour': 10,
            'temperature': 20.0,
            'humidity': 55.0,
            'wind': 2.5,
            'rain': 0.0,
            'irrigation': 3.0,
            'soil_moisture': 50.0,
            'forecast_temp_6h': 22.0,
            'forecast_rain_6h': 0.0
        }
        for _ in range(24)
    ]
    
    # The request should be rejected with a validation error
    with pytest.raises(ValidationError):
        IrrigationRequest(
            soil_moisture=soil_moisture,
            temperature=temperature,
            humidity=humidity,
            rain=5.0,
            forecast_temp_6h=26.0,
            forecast_rain_6h=2.0,
            past_sequence=past_sequence,
            language="en"
        )


@settings(max_examples=100)
@given(
    sequence_length=st.integers(min_value=0, max_value=23)
)
def test_property_lstm_input_validation_insufficient_sequence(sequence_length):
    """
    Property 3: LSTM Input Validation
    
    For any input sequence with fewer than 24 data points, the system should
    reject the forecast request with a descriptive validation error.
    
    Validates: Requirements 1.4, 1.5
    """
    # Generate a sequence with insufficient length
    past_sequence = [
        {
            'timestamp': '2024-01-15T10:00:00',
            'season': 0,
            'hour': 10,
            'temperature': 20.0,
            'humidity': 55.0,
            'wind': 2.5,
            'rain': 0.0,
            'irrigation': 3.0,
            'soil_moisture': 50.0,
            'forecast_temp_6h': 22.0,
            'forecast_rain_6h': 0.0
        }
        for _ in range(sequence_length)
    ]
    
    # The request should be rejected with a validation error
    with pytest.raises(ValidationError) as exc_info:
        IrrigationRequest(
            soil_moisture=50.0,
            temperature=25.0,
            humidity=60.0,
            rain=5.0,
            forecast_temp_6h=26.0,
            forecast_rain_6h=2.0,
            past_sequence=past_sequence,
            language="en"
        )
    
    # Verify the error is about sequence length
    error_message = str(exc_info.value).lower()
    assert "past_sequence" in error_message or "length" in error_message or "24" in error_message


@settings(max_examples=100)
@given(
    forecasted_moisture=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False),
    irrigation_amount=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False),
    alerts=st.lists(st.text(min_size=1, max_size=100), max_size=5),
    llm_explanation=st.text(min_size=1, max_size=500),
    audio_base64=st.text(min_size=1, max_size=1000),
    next_run=st.text(min_size=1, max_size=50)
)
def test_property_complete_response_structure(
    forecasted_moisture, 
    irrigation_amount, 
    alerts, 
    llm_explanation, 
    audio_base64, 
    next_run
):
    """
    Property 17: Complete Response Structure
    
    For any valid irrigation request, the API response should include all required fields:
    forecasted_moisture, irrigation_amount, alerts, llm_explanation, audio_base64, and next_run.
    
    Validates: Requirements 6.3
    """
    # Create a response with all required fields
    response = IrrigationResponse(
        forecasted_moisture=forecasted_moisture,
        irrigation_amount=irrigation_amount,
        alerts=alerts,
        llm_explanation=llm_explanation,
        audio_base64=audio_base64,
        next_run=next_run
    )
    
    # Verify all required fields are present
    assert hasattr(response, 'forecasted_moisture'), "Response missing 'forecasted_moisture' field"
    assert hasattr(response, 'irrigation_amount'), "Response missing 'irrigation_amount' field"
    assert hasattr(response, 'alerts'), "Response missing 'alerts' field"
    assert hasattr(response, 'llm_explanation'), "Response missing 'llm_explanation' field"
    assert hasattr(response, 'audio_base64'), "Response missing 'audio_base64' field"
    assert hasattr(response, 'next_run'), "Response missing 'next_run' field"
    
    # Verify field values match input
    assert response.forecasted_moisture == forecasted_moisture
    assert response.irrigation_amount == irrigation_amount
    assert response.alerts == alerts
    assert response.llm_explanation == llm_explanation
    assert response.audio_base64 == audio_base64
    assert response.next_run == next_run
    
    # Verify field types
    assert isinstance(response.forecasted_moisture, float)
    assert isinstance(response.irrigation_amount, float)
    assert isinstance(response.alerts, list)
    assert isinstance(response.llm_explanation, str)
    assert isinstance(response.audio_base64, str)
    assert isinstance(response.next_run, str)
