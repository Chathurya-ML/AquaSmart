"""
Test the improved LLM explainer.
"""

from llm_explainer_improved import generate_explanation, create_improved_fallback


def test_scenarios():
    """Test various irrigation scenarios"""
    print("=" * 70)
    print("TESTING IMPROVED LLM EXPLAINER")
    print("=" * 70)
    
    scenarios = [
        {
            "name": "Low moisture - needs irrigation",
            "forecast": 22.0,
            "irrigation": 40.0,
            "state": {
                "soil_moisture": 35.0,
                "rain": 0.0,
                "temperature": 28.5,
                "humidity": 65.0
            }
        },
        {
            "name": "Adequate moisture - no irrigation",
            "forecast": 50.0,
            "irrigation": 0.0,
            "state": {
                "soil_moisture": 55.0,
                "rain": 0.0,
                "temperature": 25.0,
                "humidity": 70.0
            }
        },
        {
            "name": "Low moisture with rainfall",
            "forecast": 22.0,
            "irrigation": 25.0,
            "state": {
                "soil_moisture": 35.0,
                "rain": 15.0,
                "temperature": 26.0,
                "humidity": 80.0
            }
        },
        {
            "name": "Hot day - needs irrigation",
            "forecast": 20.0,
            "irrigation": 50.0,
            "state": {
                "soil_moisture": 30.0,
                "rain": 0.0,
                "temperature": 35.0,
                "humidity": 45.0
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*70}")
        print(f"SCENARIO {i}: {scenario['name']}")
        print(f"{'='*70}")
        print(f"Forecast: {scenario['forecast']}%")
        print(f"Irrigation: {scenario['irrigation']} L/h")
        print(f"Current: {scenario['state']['soil_moisture']}%")
        print(f"Rain: {scenario['state']['rain']}mm")
        print(f"Temp: {scenario['state']['temperature']}°C")
        print()
        
        # Generate explanation (will use fallback if no API key)
        try:
            explanation, amount = generate_explanation(
                scenario['forecast'],
                scenario['irrigation'],
                scenario['state']
            )
            
            print("EXPLANATION:")
            print("-" * 70)
            print(explanation)
            print("-" * 70)
            
        except Exception as e:
            print(f"Error: {e}")
    
    print(f"\n{'='*70}")
    print("TEST COMPLETE")
    print(f"{'='*70}")


if __name__ == "__main__":
    test_scenarios()
