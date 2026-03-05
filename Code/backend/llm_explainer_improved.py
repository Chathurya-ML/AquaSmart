"""
IMPROVED LLM Explanation Generator for Smart Irrigation System.

This module generates better human-readable explanations of irrigation decisions
using Groq API (Llama 3.1 70B) with improved prompts for rule-based FAO-56 method.

Requirements: 4.1, 4.2
"""

from typing import Dict, Any, Optional, Tuple
import os
import requests
import json


def get_groq_api_key() -> Optional[str]:
    """Get Groq API key from environment."""
    return os.getenv('GROQ_API_KEY', '') or None


def create_improved_prompt(forecast: float, irrigation_amount: float, 
                          current_state: Dict[str, Any]) -> str:
    """
    Create an improved prompt template for the LLM with FAO-56 context.
    
    Args:
        forecast: Forecasted soil moisture percentage
        irrigation_amount: Recommended irrigation amount in L/h
        current_state: Dictionary with current conditions
    
    Returns:
        Formatted prompt string
    """
    current_moisture = current_state.get('soil_moisture', 0.0)
    rainfall = current_state.get('rain', 0.0)
    temperature = current_state.get('temperature', 0.0)
    humidity = current_state.get('humidity', 0.0)
    
    # Determine if irrigation should be done
    should_irrigate = "YES" if irrigation_amount > 0 else "NO"
    
    # Calculate threshold (24% with MAD=0.4, FC=30%, WP=15%)
    threshold = 24.0
    field_capacity = 30.0
    
    prompt = f"""You are an expert agricultural advisor explaining irrigation decisions to farmers. Use clear, practical language.

SYSTEM CONTEXT:
Our smart irrigation system uses:
• LSTM AI model - forecasts soil moisture 6 hours ahead
• FAO-56 method - scientifically validated irrigation scheduling
• Irrigation threshold: {threshold}% (when soil needs water)
• Target range: 40-60% (optimal for crop health)
• Field capacity: {field_capacity}% (maximum water soil can hold)

CURRENT SITUATION:
• Current Soil Moisture: {current_moisture:.1f}%
• AI Forecast (6h ahead): {forecast:.1f}%
• Temperature: {temperature:.1f}°C
• Humidity: {humidity:.1f}%
• Expected Rainfall: {rainfall:.1f} mm

DECISION:
• Irrigate: {should_irrigate}
• Water Amount: {irrigation_amount:.1f} L/h

YOUR TASK:
Write a clear, farmer-friendly explanation that:
1. Starts with the action: "Irrigate now" or "No irrigation needed"
2. States water amount if irrigating
3. Explains WHY based on:
   - The AI forecast ({forecast:.1f}%) vs threshold ({threshold}%)
   - Current conditions (moisture, weather)
   - How FAO-56 method determined this
4. Gives practical advice
5. Keeps it 4-6 sentences, encouraging tone
6. Let the user know if there is any extreme weather condition like flooding like 100mm rain.


FEW-SHOT EXAMPLES:

Example 1 - Low moisture, needs irrigation:
Input: Current 35%, Forecast 22%, Temp 28°C, Rain 0mm, Decision: Irrigate 40 L/h
Output: "Irrigate now with 40 L/h. Our AI forecasts your soil moisture will drop to 22% in the next 6 hours, which is below the 24% threshold where crops start to stress. The FAO-56 method calculates you need 40 L/h to bring moisture back to the optimal 30% level. With no rainfall expected and temperature at 28°C, your crops will benefit from this irrigation to maintain healthy growth."

Example 2 - Adequate moisture, no irrigation:
Input: Current 55%, Forecast 50%, Temp 25°C, Rain 0mm, Decision: No irrigation
Output: "No irrigation needed right now. Our AI forecasts your soil moisture will remain at 50% over the next 6 hours, which is well above the 24% threshold and in the optimal range for crop health. Your current moisture level of 55% is excellent. The FAO-56 analysis confirms your crops have sufficient water, so you can save resources while maintaining healthy growth."

Example 3 - Low moisture with rainfall:
Input: Current 35%, Forecast 22%, Temp 26°C, Rain 15mm, Decision: Irrigate 25 L/h
Output: "Irrigate now with 25 L/h. While our AI forecasts soil moisture dropping to 22% (below the 24% threshold), we've reduced the irrigation amount because 15mm of rainfall is expected. The FAO-56 method calculated 40 L/h would be needed, but with the incoming rain, 25 L/h will be sufficient to reach the optimal 30% level. This smart adjustment saves water while ensuring your crops stay healthy."

Example 4 - Hot day, high evaporation:
Input: Current 30%, Forecast 20%, Temp 35°C, Rain 0mm, Decision: Irrigate 50 L/h
Output: "Irrigate now with 50 L/h. Our AI forecasts a significant drop to 20% soil moisture in the next 6 hours, well below the 24% stress threshold. The high temperature of 35°C is causing rapid evaporation, which is why the FAO-56 method recommends 50 L/h to restore moisture to 30%. Acting now will prevent crop stress and maintain optimal growing conditions despite the heat."

Example 5 - Good moisture with light rain:
Input: Current 48%, Forecast 52%, Temp 22°C, Rain 5mm, Decision: No irrigation
Output: "No irrigation needed right now. Great news - our AI forecasts your soil moisture will actually increase to 52% thanks to the expected 5mm of rainfall. Your current 48% is already in the optimal range, and the incoming rain will boost it further. The FAO-56 analysis confirms your crops are well-hydrated, so you can skip irrigation and let nature do the work."

Now write your explanation for the current situation:"""
    
    return prompt


def generate_explanation_groq(forecast: float, irrigation_amount: float, 
                              current_state: Dict[str, Any]) -> str:
    """
    Generate improved explanation using Groq API.
    
    Args:
        forecast: Forecasted soil moisture percentage
        irrigation_amount: Recommended irrigation amount in L/h
        current_state: Dictionary with current conditions
    
    Returns:
        Human-readable explanation string
    
    Raises:
        RuntimeError: If API call fails
    """
    api_key = get_groq_api_key()
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set in environment")
    
    prompt = create_improved_prompt(forecast, irrigation_amount, current_state)
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": os.getenv('GROQ_MODEL', 'llama-3.1-70b-versatile'),
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful agricultural advisor. Provide clear, practical, encouraging explanations for farmers. Always reference specific numbers and explain the science simply."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 400
            },
            timeout=15
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"Groq API error: {response.status_code} - {response.text}")
        
        result = response.json()
        explanation = result['choices'][0]['message']['content'].strip()
        
        return explanation
    
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Groq API request failed: {str(e)}") from e


def create_improved_fallback(forecast: float, irrigation_amount: float, 
                             current_state: Dict[str, Any]) -> str:
    """
    Create an improved rule-based explanation as fallback.
    
    Args:
        forecast: Forecasted soil moisture percentage
        irrigation_amount: Recommended irrigation amount in L/h
        current_state: Dictionary with current conditions
    
    Returns:
        Improved explanation string
    """
    current_moisture = current_state.get('soil_moisture', 0.0)
    rainfall = current_state.get('rain', 0.0)
    temperature = current_state.get('temperature', 0.0)
    humidity = current_state.get('humidity', 0.0)
    
    threshold = 24.0
    field_capacity = 30.0
    
    # Build explanation based on decision
    if irrigation_amount > 0:
        # IRRIGATE
        action = f"🚿 **Irrigate now with {irrigation_amount:.1f} L/h**"
        
        # Explain why
        reasons = []
        
        # Forecast analysis
        if forecast < threshold:
            deficit = field_capacity - forecast
            reasons.append(
                f"Our AI forecasts your soil moisture will drop to {forecast:.1f}% in the next 6 hours, "
                f"which is below the {threshold}% threshold where crops begin to stress."
            )
        
        # FAO-56 calculation
        reasons.append(
            f"Using the FAO-56 method, we calculated {irrigation_amount:.1f} L/h will bring "
            f"your soil back to the optimal {field_capacity}% level."
        )
        
        # Weather context
        weather_parts = []
        if rainfall > 5:
            weather_parts.append(f"{rainfall:.1f}mm rainfall expected (irrigation reduced accordingly)")
        elif rainfall > 0:
            weather_parts.append(f"{rainfall:.1f}mm light rainfall expected")
        else:
            weather_parts.append("no rainfall expected")
        
        if temperature > 30:
            weather_parts.append(f"high temperature ({temperature:.1f}°C) increases water loss")
        elif temperature < 20:
            weather_parts.append(f"moderate temperature ({temperature:.1f}°C)")
        else:
            weather_parts.append(f"temperature at {temperature:.1f}°C")
        
        reasons.append(f"With {weather_parts[0]} and {weather_parts[1]}, this irrigation will maintain healthy crop growth.")
        
        explanation = f"{action}\n\n" + " ".join(reasons)
    
    else:
        # NO IRRIGATION
        action = f"✋ **No irrigation needed right now**"
        
        reasons = []
        
        # Explain why no irrigation
        if forecast >= threshold:
            reasons.append(
                f"Our AI forecasts your soil moisture will be {forecast:.1f}% in 6 hours, "
                f"which is above the {threshold}% threshold."
            )
        
        if current_moisture > 50:
            reasons.append(f"Your current soil moisture ({current_moisture:.1f}%) is already in the optimal range.")
        else:
            reasons.append(f"Your soil moisture ({current_moisture:.1f}%) is adequate for now.")
        
        # Weather context
        if rainfall > 5:
            reasons.append(f"Plus, {rainfall:.1f}mm of rainfall is expected, which will help maintain moisture levels.")
        elif rainfall > 0:
            reasons.append(f"Light rainfall ({rainfall:.1f}mm) is also expected.")
        
        reasons.append("Your crops have sufficient water for healthy growth. We'll continue monitoring and alert you if irrigation becomes necessary.")
        
        explanation = f"{action}\n\n" + " ".join(reasons)
    
    return explanation


def generate_explanation(forecast: float, irrigation_amount: float, 
                        current_state: Dict[str, Any]) -> Tuple[str, float]:
    """
    Generate improved explanation for irrigation decision.
    
    Args:
        forecast: Forecasted soil moisture percentage (0-100)
        irrigation_amount: Recommended irrigation amount in L/h
        current_state: Dictionary containing sensor readings
    
    Returns:
        Tuple of (explanation_text, irrigation_amount)
    
    Requirements: 4.1, 4.2
    """
    # Validate inputs
    required_fields = ['soil_moisture', 'rain', 'temperature', 'humidity']
    missing_fields = [field for field in required_fields if field not in current_state]
    if missing_fields:
        raise ValueError(f"current_state missing required fields: {missing_fields}")
    
    # Try Groq API first
    if get_groq_api_key():
        try:
            print("Generating improved explanation using Groq API...")
            explanation = generate_explanation_groq(forecast, irrigation_amount, current_state)
            return explanation, irrigation_amount
        except Exception as e:
            print(f"Groq API failed: {str(e)}. Using improved fallback...")
    
    # Fallback to improved rule-based explanation
    print("Using improved rule-based explanation")
    explanation = create_improved_fallback(forecast, irrigation_amount, current_state)
    return explanation, irrigation_amount
