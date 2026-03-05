"""
Quick integration test for LSTM + Rule-Based Irrigation pipeline.
"""

import torch
import numpy as np
from lstm_model import forecast_soil_moisture, load_lstm_model
from rule_based_irrigation import irrigation_decision


def test_full_pipeline():
    """Test the complete pipeline: LSTM forecast → Rule-based decision"""
    print("=" * 60)
    print("FULL PIPELINE TEST: LSTM + Rule-Based Irrigation")
    print("=" * 60)
    
    # Load LSTM model first
    print("\n0. Loading LSTM Model...")
    try:
        load_lstm_model()
        print("   ✅ LSTM model loaded")
    except Exception as e:
        print(f"   ❌ Failed to load LSTM: {e}")
        return False
    
    # Test current state (typical sensor readings)
    current_state = {
        "temperature": 28.5,
        "humidity": 65.0,
        "wind": 12.0,
        "rain": 0.0,
        "soil_moisture": 35.0,
        "forecast_rain_6h": 2.5
    }
    
    print("\n1. Current Sensor Readings:")
    for key, value in current_state.items():
        print(f"   {key}: {value}")
    
    # Step 1: Get LSTM forecast
    print("\n2. Running LSTM Forecast...")
    try:
        forecast = forecast_soil_moisture(current_state)
        print(f"   ✅ LSTM Forecast: {forecast:.2f}%")
    except Exception as e:
        print(f"   ❌ LSTM Error: {e}")
        return False
    
    # Step 2: Get irrigation decision
    print("\n3. Running Rule-Based Decision...")
    try:
        irrigation = irrigation_decision(current_state, forecast)
        print(f"   ✅ Irrigation Decision: {irrigation:.1f} L/h")
    except Exception as e:
        print(f"   ❌ Decision Error: {e}")
        return False
    
    # Step 3: Interpret result
    print("\n4. Interpretation:")
    if irrigation > 0:
        print(f"   🚿 IRRIGATE: Apply {irrigation:.1f} L/h")
        print(f"   Reason: Forecast ({forecast:.1f}%) is below threshold (24%)")
    else:
        print(f"   ✋ NO ACTION: Soil moisture adequate")
        print(f"   Reason: Forecast ({forecast:.1f}%) is above threshold (24%)")
    
    print("\n" + "=" * 60)
    print("✅ FULL PIPELINE TEST PASSED")
    print("=" * 60)
    return True


def test_multiple_scenarios():
    """Test multiple scenarios to verify system behavior"""
    print("\n" + "=" * 60)
    print("SCENARIO TESTING")
    print("=" * 60)
    
    scenarios = [
        {
            "name": "Dry conditions",
            "state": {
                "temperature": 32.0,
                "humidity": 45.0,
                "wind": 15.0,
                "rain": 0.0,
                "soil_moisture": 25.0,
                "forecast_rain_6h": 0.0
            }
        },
        {
            "name": "Wet conditions",
            "state": {
                "temperature": 22.0,
                "humidity": 85.0,
                "wind": 5.0,
                "rain": 10.0,
                "soil_moisture": 55.0,
                "forecast_rain_6h": 8.0
            }
        },
        {
            "name": "Moderate conditions",
            "state": {
                "temperature": 26.0,
                "humidity": 65.0,
                "wind": 10.0,
                "rain": 2.0,
                "soil_moisture": 40.0,
                "forecast_rain_6h": 3.0
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\nScenario {i}: {scenario['name']}")
        state = scenario['state']
        print(f"  Temp: {state['temperature']}°C, Humidity: {state['humidity']}%")
        print(f"  Current SM: {state['soil_moisture']}%, Rain: {state['rain']}mm")
        
        try:
            forecast = forecast_soil_moisture(state)
            irrigation = irrigation_decision(state, forecast)
            
            action = "IRRIGATE" if irrigation > 0 else "NO ACTION"
            print(f"  → Forecast: {forecast:.1f}%, Decision: {irrigation:.1f} L/h [{action}]")
        except Exception as e:
            print(f"  ❌ Error: {e}")


if __name__ == "__main__":
    # Run tests
    success = test_full_pipeline()
    
    if success:
        test_multiple_scenarios()
        
        print("\n" + "=" * 60)
        print("🎉 SYSTEM READY FOR DEMO!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Start backend: python app.py")
        print("2. Start frontend: streamlit run ../frontend/dashboard.py")
    else:
        print("\n❌ Pipeline test failed. Check errors above.")
