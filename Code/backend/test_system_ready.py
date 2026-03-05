"""
Quick system readiness check.
Tests that all components can be loaded and are functional.
"""

import torch
import os


def test_lstm_model():
    """Test LSTM model can be loaded"""
    print("1. Testing LSTM Model...")
    try:
        from lstm_model import load_lstm_model
        model = load_lstm_model()
        print("   ✅ LSTM model loaded successfully")
        print(f"   Model type: {type(model).__name__}")
        return True
    except Exception as e:
        print(f"   ❌ LSTM Error: {e}")
        return False


def test_rule_based():
    """Test rule-based irrigation module"""
    print("\n2. Testing Rule-Based Irrigation...")
    try:
        from rule_based_irrigation import irrigation_decision
        
        # Test with sample data
        state = {
            "soil_moisture": 35,
            "rain": 0,
            "temperature": 25,
            "humidity": 60
        }
        forecast = 22.0  # Low forecast
        
        irrigation = irrigation_decision(state, forecast)
        print(f"   ✅ Rule-based module working")
        print(f"   Test: Forecast {forecast}% → {irrigation:.1f} L/h")
        return True
    except Exception as e:
        print(f"   ❌ Rule-based Error: {e}")
        return False


def test_models_exist():
    """Check that model files exist"""
    print("\n3. Checking Model Files...")
    
    models_dir = "models"
    lstm_file = os.path.join(models_dir, "soil_forecast_model.pt")
    rl_file = os.path.join(models_dir, "proactive_irrigation_policy.zip")
    
    lstm_exists = os.path.exists(lstm_file)
    rl_exists = os.path.exists(rl_file)
    
    if lstm_exists:
        size = os.path.getsize(lstm_file) / 1024
        print(f"   ✅ LSTM model: {size:.1f} KB")
    else:
        print(f"   ❌ LSTM model not found")
    
    if rl_exists:
        size = os.path.getsize(rl_file) / 1024
        print(f"   ℹ️  RL model: {size:.1f} KB (not needed with rule-based)")
    
    return lstm_exists


def test_data_exists():
    """Check that training data exists"""
    print("\n4. Checking Training Data...")
    
    data_file = "data/sensor_readings.csv"
    
    if os.path.exists(data_file):
        size = os.path.getsize(data_file) / 1024
        print(f"   ✅ Training data: {size:.1f} KB")
        
        # Count rows
        with open(data_file, 'r') as f:
            rows = sum(1 for line in f) - 1  # Subtract header
        print(f"   Data points: {rows}")
        return True
    else:
        print(f"   ❌ Training data not found")
        return False


def test_imports():
    """Test that all required modules can be imported"""
    print("\n5. Testing Module Imports...")
    
    modules = [
        "lstm_model",
        "rule_based_irrigation",
        "alerts",
        "llm_explainer",
        "storage",
        "weather_ingestion",
        "notifications",
        "translation_tts"
    ]
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except Exception as e:
            print(f"   ❌ {module}: {e}")
            all_ok = False
    
    return all_ok


if __name__ == "__main__":
    print("=" * 60)
    print("SYSTEM READINESS CHECK")
    print("=" * 60)
    print()
    
    results = []
    results.append(("LSTM Model", test_lstm_model()))
    results.append(("Rule-Based", test_rule_based()))
    results.append(("Model Files", test_models_exist()))
    results.append(("Training Data", test_data_exists()))
    results.append(("Module Imports", test_imports()))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:20s} {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 SYSTEM READY FOR DEMO!")
        print("=" * 60)
        print("\nTo start the system:")
        print("1. Backend:  python app.py")
        print("2. Frontend: streamlit run ../frontend/dashboard.py")
    else:
        print("⚠️  SOME CHECKS FAILED")
        print("=" * 60)
        print("Review errors above and fix before demo.")
