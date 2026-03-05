"""
Unit and property-based tests for LSTM forecasting module.

Tests the LSTM model loading, feature extraction, and forecasting functions
to ensure proper functionality and error handling.

Requirements: 1.1, 1.3, 1.4, 1.5, 10.1
"""

import pytest
import torch
from hypothesis import given, strategies as st, settings
from lstm_model import load_lstm_model, forecast_soil_moisture, extract_features, get_model


# ============================================================================
# Unit Tests
# ============================================================================

def test_load_lstm_model_success():
    """Test successful loading of LSTM model."""
    model = load_lstm_model("Code/backend/models/soil_forecast_model.pt")
    
    assert model is not None
    assert isinstance(model, torch.nn.Module)
    # Verify model is in eval mode
    assert not model.training


def test_load_lstm_model_file_not_found():
    """Test LSTM model loading with non-existent file."""
    with pytest.raises(FileNotFoundError) as exc_info:
        load_lstm_model("Code/backend/models/nonexistent_model.pt")
    
    assert "not found" in str(exc_info.value).lower()


def test_extract_features_valid_sequence():
    """Test feature extraction with valid sensor data."""
    past_sequence = [
        {
            'timestamp': '2024-01-15T10:00:00',
            'season': 1,
            'hour': 10,
            'temperature': 25.0,
            'humidity': 60.0,
            'wind': 3.5,
            'rain': 0.0,
            'irrigation': 5.0,
            'soil_moisture': 45.0,
            'forecast_temp_6h': 26.0,
            'forecast_rain_6h': 2.0
        }
        for _ in range(24)
    ]
    
    features = extract_features(past_sequence)
    
    assert len(features) == 24
    assert len(features[0]) == 6  # Model uses 6 features
    assert features[0][0] == 25.0  # temperature
    assert features[0][1] == 60.0  # humidity
    assert features[0][2] == 3.5   # wind


def test_forecast_soil_moisture_valid_input():
    """Test soil moisture forecasting with valid input."""
    # Load model first
    load_lstm_model("Code/backend/models/soil_forecast_model.pt")
    
    past_sequence = [
        {
            'timestamp': '2024-01-15T10:00:00',
            'season': 1,
            'hour': i % 24,
            'temperature': 25.0,
            'humidity': 60.0,
            'wind': 3.5,
            'rain': 0.0,
            'irrigation': 5.0,
            'soil_moisture': 45.0,
            'forecast_temp_6h': 26.0,
            'forecast_rain_6h': 2.0
        }
        for i in range(24)
    ]
    
    forecast = forecast_soil_moisture(past_sequence)
    
    assert isinstance(forecast, float)
    # Forecast should be a reasonable moisture value
    assert -100 <= forecast <= 200  # Allow some margin for model output


def test_forecast_soil_moisture_insufficient_sequence():
    """Test forecasting with insufficient data points."""
    # Load model first
    load_lstm_model("Code/backend/models/soil_forecast_model.pt")
    
    past_sequence = [
        {
            'timestamp': '2024-01-15T10:00:00',
            'season': 1,
            'hour': 10,
            'temperature': 25.0,
            'humidity': 60.0,
            'wind': 3.5,
            'rain': 0.0,
            'irrigation': 5.0,
            'soil_moisture': 45.0,
            'forecast_temp_6h': 26.0,
            'forecast_rain_6h': 2.0
        }
        for _ in range(10)  # Only 10 data points
    ]
    
    with pytest.raises(ValueError) as exc_info:
        forecast_soil_moisture(past_sequence)
    
    assert "at least 24 data points" in str(exc_info.value).lower()


def test_forecast_soil_moisture_model_not_loaded():
    """Test forecasting when model is not loaded."""
    # Reset the global model to None
    import lstm_model
    lstm_model._lstm_model = None
    
    past_sequence = [
        {
            'timestamp': '2024-01-15T10:00:00',
            'season': 1,
            'hour': 10,
            'temperature': 25.0,
            'humidity': 60.0,
            'wind': 3.5,
            'rain': 0.0,
            'irrigation': 5.0,
            'soil_moisture': 45.0,
            'forecast_temp_6h': 26.0,
            'forecast_rain_6h': 2.0
        }
        for _ in range(24)
    ]
    
    with pytest.raises(ValueError) as exc_info:
        forecast_soil_moisture(past_sequence)
    
    assert "not loaded" in str(exc_info.value).lower()
    
    # Reload model for other tests
    load_lstm_model("Code/backend/models/soil_forecast_model.pt")


def test_forecast_with_extreme_weather_values():
    """Test forecasting with extreme but valid weather values."""
    load_lstm_model("Code/backend/models/soil_forecast_model.pt")
    
    past_sequence = [
        {
            'timestamp': '2024-01-15T10:00:00',
            'season': 3,  # Winter
            'hour': i % 24,
            'temperature': -40.0,  # Extreme cold
            'humidity': 95.0,  # High humidity
            'wind': 45.0,  # Strong wind
            'rain': 150.0,  # Heavy rain
            'irrigation': 0.0,
            'soil_moisture': 90.0,  # Very wet
            'forecast_temp_6h': -35.0,
            'forecast_rain_6h': 100.0
        }
        for i in range(24)
    ]
    
    forecast = forecast_soil_moisture(past_sequence)
    
    # Should complete without error
    assert isinstance(forecast, float)


# ============================================================================
# Edge Case Unit Tests (Task 3.4)
# ============================================================================

def test_minimum_sequence_length():
    """
    Test with minimum sequence length (exactly 24 data points).
    
    Requirements: 1.4, 1.5
    """
    load_lstm_model("Code/backend/models/soil_forecast_model.pt")
    
    # Create exactly 24 data points
    past_sequence = [
        {
            'timestamp': f'2024-01-15T{i:02d}:00:00',
            'season': 1,
            'hour': i,
            'temperature': 22.0,
            'humidity': 55.0,
            'wind': 3.0,
            'rain': 0.0,
            'irrigation': 5.0,
            'soil_moisture': 50.0,
            'forecast_temp_6h': 23.0,
            'forecast_rain_6h': 1.0
        }
        for i in range(24)
    ]
    
    # Should successfully forecast with exactly 24 data points
    forecast = forecast_soil_moisture(past_sequence)
    
    assert isinstance(forecast, float)
    assert not (forecast != forecast), "Forecast should not be NaN"


def test_extreme_hot_weather():
    """
    Test with extreme hot weather conditions.
    
    Requirements: 1.4, 1.5
    """
    load_lstm_model("Code/backend/models/soil_forecast_model.pt")
    
    past_sequence = [
        {
            'timestamp': f'2024-07-15T{i % 24:02d}:00:00',
            'season': 2,  # Summer
            'hour': i % 24,
            'temperature': 55.0,  # Extreme heat
            'humidity': 10.0,  # Very dry
            'wind': 0.5,  # Light wind
            'rain': 0.0,  # No rain
            'irrigation': 20.0,  # Heavy irrigation needed
            'soil_moisture': 15.0,  # Very dry soil
            'forecast_temp_6h': 58.0,
            'forecast_rain_6h': 0.0
        }
        for i in range(24)
    ]
    
    forecast = forecast_soil_moisture(past_sequence)
    
    assert isinstance(forecast, float)
    assert not (forecast != forecast), "Forecast should not be NaN"


def test_extreme_cold_weather():
    """
    Test with extreme cold weather conditions.
    
    Requirements: 1.4, 1.5
    """
    load_lstm_model("Code/backend/models/soil_forecast_model.pt")
    
    past_sequence = [
        {
            'timestamp': f'2024-01-15T{i % 24:02d}:00:00',
            'season': 3,  # Winter
            'hour': i % 24,
            'temperature': -45.0,  # Extreme cold
            'humidity': 100.0,  # Maximum humidity
            'wind': 50.0,  # Maximum wind
            'rain': 0.0,  # No rain (frozen)
            'irrigation': 0.0,  # No irrigation
            'soil_moisture': 80.0,  # Frozen moisture
            'forecast_temp_6h': -48.0,
            'forecast_rain_6h': 0.0
        }
        for i in range(24)
    ]
    
    forecast = forecast_soil_moisture(past_sequence)
    
    assert isinstance(forecast, float)
    assert not (forecast != forecast), "Forecast should not be NaN"


def test_extreme_rainfall():
    """
    Test with extreme rainfall conditions.
    
    Requirements: 1.4, 1.5
    """
    load_lstm_model("Code/backend/models/soil_forecast_model.pt")
    
    past_sequence = [
        {
            'timestamp': f'2024-06-15T{i % 24:02d}:00:00',
            'season': 2,  # Summer
            'hour': i % 24,
            'temperature': 25.0,
            'humidity': 100.0,  # Maximum humidity
            'wind': 30.0,  # Strong wind
            'rain': 200.0,  # Extreme rainfall
            'irrigation': 0.0,  # No irrigation needed
            'soil_moisture': 95.0,  # Saturated soil
            'forecast_temp_6h': 24.0,
            'forecast_rain_6h': 180.0
        }
        for i in range(24)
    ]
    
    forecast = forecast_soil_moisture(past_sequence)
    
    assert isinstance(forecast, float)
    assert not (forecast != forecast), "Forecast should not be NaN"


def test_boundary_values():
    """
    Test with boundary values for all features.
    
    Requirements: 1.4, 1.5
    """
    load_lstm_model("Code/backend/models/soil_forecast_model.pt")
    
    # Test with minimum boundary values
    past_sequence_min = [
        {
            'timestamp': f'2024-01-15T{i % 24:02d}:00:00',
            'season': 0,  # Minimum season
            'hour': 0,  # Minimum hour
            'temperature': -50.0,  # Minimum temperature
            'humidity': 0.0,  # Minimum humidity
            'wind': 0.0,  # Minimum wind
            'rain': 0.0,  # Minimum rain
            'irrigation': 0.0,  # Minimum irrigation
            'soil_moisture': 0.0,  # Minimum soil moisture
            'forecast_temp_6h': -50.0,
            'forecast_rain_6h': 0.0
        }
        for i in range(24)
    ]
    
    forecast_min = forecast_soil_moisture(past_sequence_min)
    assert isinstance(forecast_min, float)
    assert not (forecast_min != forecast_min), "Forecast should not be NaN"
    
    # Test with maximum boundary values
    past_sequence_max = [
        {
            'timestamp': f'2024-12-31T{i % 24:02d}:00:00',
            'season': 3,  # Maximum season
            'hour': 23,  # Maximum hour
            'temperature': 60.0,  # Maximum temperature
            'humidity': 100.0,  # Maximum humidity
            'wind': 50.0,  # Maximum wind
            'rain': 200.0,  # Maximum rain
            'irrigation': 100.0,  # Maximum irrigation
            'soil_moisture': 100.0,  # Maximum soil moisture
            'forecast_temp_6h': 60.0,
            'forecast_rain_6h': 200.0
        }
        for i in range(24)
    ]
    
    forecast_max = forecast_soil_moisture(past_sequence_max)
    assert isinstance(forecast_max, float)
    assert not (forecast_max != forecast_max), "Forecast should not be NaN"


def test_missing_required_feature():
    """
    Test error handling when a required feature is missing.
    
    Requirements: 1.4, 1.5
    """
    load_lstm_model("Code/backend/models/soil_forecast_model.pt")
    
    # Create sequence with missing 'temperature' feature
    past_sequence = [
        {
            'timestamp': f'2024-01-15T{i % 24:02d}:00:00',
            'season': 1,
            'hour': i % 24,
            # 'temperature': 25.0,  # Missing!
            'humidity': 60.0,
            'wind': 3.5,
            'rain': 0.0,
            'irrigation': 5.0,
            'soil_moisture': 45.0,
            'forecast_temp_6h': 26.0,
            'forecast_rain_6h': 2.0
        }
        for i in range(24)
    ]
    
    # Should raise an error due to missing feature
    with pytest.raises((KeyError, RuntimeError)) as exc_info:
        forecast_soil_moisture(past_sequence)
    
    # Verify error is related to missing feature
    error_message = str(exc_info.value).lower()
    assert 'temperature' in error_message or 'key' in error_message or 'missing' in error_message


def test_multiple_missing_features():
    """
    Test error handling when multiple required features are missing.
    
    Requirements: 1.4, 1.5
    """
    load_lstm_model("Code/backend/models/soil_forecast_model.pt")
    
    # Create sequence with multiple missing features
    past_sequence = [
        {
            'timestamp': f'2024-01-15T{i % 24:02d}:00:00',
            'season': 1,
            'hour': i % 24,
            # Missing: temperature, humidity, wind
            'rain': 0.0,
            'irrigation': 5.0,
            'soil_moisture': 45.0,
            'forecast_temp_6h': 26.0,
            'forecast_rain_6h': 2.0
        }
        for i in range(24)
    ]
    
    # Should raise an error due to missing features
    with pytest.raises((KeyError, RuntimeError)) as exc_info:
        forecast_soil_moisture(past_sequence)


def test_zero_values_all_features():
    """
    Test with all features set to zero (edge case for model behavior).
    
    Requirements: 1.4, 1.5
    """
    load_lstm_model("Code/backend/models/soil_forecast_model.pt")
    
    past_sequence = [
        {
            'timestamp': f'2024-01-15T{i % 24:02d}:00:00',
            'season': 0,
            'hour': 0,
            'temperature': 0.0,
            'humidity': 0.0,
            'wind': 0.0,
            'rain': 0.0,
            'irrigation': 0.0,
            'soil_moisture': 0.0,
            'forecast_temp_6h': 0.0,
            'forecast_rain_6h': 0.0
        }
        for i in range(24)
    ]
    
    forecast = forecast_soil_moisture(past_sequence)
    
    assert isinstance(forecast, float)
    assert not (forecast != forecast), "Forecast should not be NaN"


def test_varying_sequence_lengths():
    """
    Test with various valid sequence lengths (24, 48, 72, 168 hours).
    
    Requirements: 1.4, 1.5
    """
    load_lstm_model("Code/backend/models/soil_forecast_model.pt")
    
    for seq_length in [24, 48, 72, 168]:
        past_sequence = [
            {
                'timestamp': f'2024-01-15T{i % 24:02d}:00:00',
                'season': 1,
                'hour': i % 24,
                'temperature': 25.0,
                'humidity': 60.0,
                'wind': 3.5,
                'rain': 0.0,
                'irrigation': 5.0,
                'soil_moisture': 45.0,
                'forecast_temp_6h': 26.0,
                'forecast_rain_6h': 2.0
            }
            for i in range(seq_length)
        ]
        
        forecast = forecast_soil_moisture(past_sequence)
        
        assert isinstance(forecast, float), f"Failed for sequence length {seq_length}"
        assert not (forecast != forecast), f"Forecast is NaN for sequence length {seq_length}"


def test_get_model():
    """Test getting the loaded model."""
    load_lstm_model("Code/backend/models/soil_forecast_model.pt")
    model = get_model()
    
    assert model is not None
    assert isinstance(model, torch.nn.Module)


# ============================================================================
# Property-Based Tests
# ============================================================================

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
    past_sequence=st.lists(
        valid_sensor_reading_dict(),
        min_size=24,
        max_size=168  # Up to 1 week of hourly data
    )
)
def test_property_lstm_forecast_generation(past_sequence):
    """
    Property 1: LSTM Forecast Generation
    
    For any valid historical sensor sequence containing at least 24 data points
    with all 11 required features, the LSTM model should successfully generate
    a soil moisture forecast.
    
    Validates: Requirements 1.1
    """
    # Ensure model is loaded
    load_lstm_model("Code/backend/models/soil_forecast_model.pt")
    
    # The forecast should complete without raising an exception
    try:
        forecast = forecast_soil_moisture(past_sequence)
        
        # Verify we got a result
        assert forecast is not None, "Forecast returned None"
        assert isinstance(forecast, float), f"Forecast must be float, got {type(forecast)}"
        
    except Exception as e:
        pytest.fail(f"LSTM forecast generation failed with valid input: {str(e)}")


@settings(max_examples=100)
@given(
    past_sequence=st.lists(
        valid_sensor_reading_dict(),
        min_size=24,
        max_size=168
    )
)
def test_property_lstm_output_bounds(past_sequence):
    """
    Property 2: LSTM Output Bounds
    
    **Validates: Requirements 1.3**
    
    For any valid input sequence, the LSTM model's predicted soil moisture value
    should be a floating-point number between 0 and 100 (inclusive).
    """
    # Ensure model is loaded
    load_lstm_model("Code/backend/models/soil_forecast_model.pt")
    
    forecast = forecast_soil_moisture(past_sequence)
    
    # Verify the forecast is a float
    assert isinstance(forecast, float), f"Forecast must be float, got {type(forecast)}"
    
    # Verify the forecast is not NaN or infinite
    assert not (forecast != forecast), "Forecast is NaN"  # Check for NaN
    assert forecast != float('inf') and forecast != float('-inf'), "Forecast is infinite"
    
    # Verify the forecast is within the valid bounds [0, 100]
    assert 0 <= forecast <= 100, (
        f"LSTM output {forecast} is outside valid bounds [0, 100]. "
        f"Soil moisture percentage must be between 0 and 100 inclusive."
    )


@settings(max_examples=100)
@given(
    sequence_length=st.integers(min_value=0, max_value=23)
)
def test_property_lstm_rejects_insufficient_sequence(sequence_length):
    """
    Property 3 (partial): LSTM Input Validation - Insufficient Sequence
    
    For any input sequence with fewer than 24 data points, the system should
    reject the forecast request with a descriptive validation error.
    
    Validates: Requirements 1.4, 1.5
    """
    # Ensure model is loaded
    load_lstm_model("Code/backend/models/soil_forecast_model.pt")
    
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
    
    # The forecast should be rejected with a ValueError
    with pytest.raises(ValueError) as exc_info:
        forecast_soil_moisture(past_sequence)
    
    # Verify the error message is descriptive
    error_message = str(exc_info.value).lower()
    assert "24" in error_message or "data points" in error_message or "sequence" in error_message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
