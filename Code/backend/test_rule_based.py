"""
Test script for rule-based irrigation decision module.
"""

from rule_based_irrigation import irrigation_amount, irrigation_decision


def test_basic_calculation():
    """Test the basic FAO-56 calculation"""
    print("=" * 60)
    print("TEST 1: Basic FAO-56 Calculation")
    print("=" * 60)
    
    # Test case from your example
    sm_forecast = 0.22  # 22% volumetric
    fc = 0.30           # 30% field capacity
    wp = 0.15           # 15% wilting point
    root_depth = 0.5    # 50cm root zone
    
    water_needed = irrigation_amount(sm_forecast, fc, wp, root_depth)
    print(f"Forecast: {sm_forecast*100:.0f}% volumetric")
    print(f"Field capacity: {fc*100:.0f}%")
    print(f"Wilting point: {wp*100:.0f}%")
    print(f"Root depth: {root_depth}m")
    print(f"Irrigation needed: {water_needed:.1f} mm")
    print()


def test_irrigation_decision():
    """Test the irrigation_decision function with various scenarios"""
    print("=" * 60)
    print("TEST 2: Irrigation Decision Scenarios")
    print("=" * 60)
    
    scenarios = [
        {
            "name": "Low moisture, no rain",
            "state": {"soil_moisture": 35, "rain": 0, "temperature": 25, "humidity": 60},
            "forecast": 22
        },
        {
            "name": "Adequate moisture",
            "state": {"soil_moisture": 50, "rain": 0, "temperature": 25, "humidity": 60},
            "forecast": 50
        },
        {
            "name": "Low moisture, heavy rain expected",
            "state": {"soil_moisture": 35, "rain": 15, "temperature": 25, "humidity": 80},
            "forecast": 22
        },
        {
            "name": "Moderate moisture, light rain",
            "state": {"soil_moisture": 40, "rain": 5, "temperature": 22, "humidity": 70},
            "forecast": 38
        }
    ]
    
    for scenario in scenarios:
        print(f"\nScenario: {scenario['name']}")
        print(f"  Current: {scenario['state']['soil_moisture']}%")
        print(f"  Forecast: {scenario['forecast']}%")
        print(f"  Rain: {scenario['state']['rain']}mm")
        
        irrigation = irrigation_decision(scenario['state'], scenario['forecast'])
        print(f"  → Decision: {irrigation:.1f} L/h")
        print()


def test_threshold_behavior():
    """Test behavior around the irrigation threshold"""
    print("=" * 60)
    print("TEST 3: Threshold Behavior")
    print("=" * 60)
    
    # With MAD=0.4, FC=0.30, WP=0.15:
    # Available water = 0.30 - 0.15 = 0.15
    # Threshold = 0.30 - (0.4 × 0.15) = 0.30 - 0.06 = 0.24 (24%)
    
    print("Threshold should be at 24% (with MAD=0.4, FC=30%, WP=15%)")
    print()
    
    test_forecasts = [20, 23, 24, 25, 26, 30]
    state = {"soil_moisture": 40, "rain": 0, "temperature": 25, "humidity": 60}
    
    for forecast in test_forecasts:
        irrigation = irrigation_decision(state, forecast)
        status = "IRRIGATE" if irrigation > 0 else "NO ACTION"
        print(f"Forecast: {forecast}% → {irrigation:.1f} L/h [{status}]")


if __name__ == "__main__":
    test_basic_calculation()
    test_irrigation_decision()
    test_threshold_behavior()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETE")
    print("=" * 60)
