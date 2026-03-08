"""
LLM Explanation Generator for Smart Irrigation System.

This module generates human-readable explanations of irrigation decisions
using Groq API (Llama 3.1 70B) with fallback to rule-based explanations.

The LLM also validates RL model decisions and can override them if they
seem illogical based on the metrics.

Supports:
- Groq API (Llama 3.1 70B) - recommended, free, fast
- HuggingFace Inference API (Llama models) - alternative
- Rule-based fallback - no API required

Requirements: 4.1, 4.2
"""

from typing import Dict, Any, Optional, Tuple
import os
import requests
import json

def get_groq_api_key() -> Optional[str]:
    """Get Groq API key from environment variables (Railway or .env)."""
    return os.getenv('GROQ_API_KEY', '') or None


def get_hf_api_key() -> Optional[str]:
    """Get HuggingFace API key from environment variables (Railway or .env)."""
    return os.getenv('HUGGINGFACE_API_KEY', '') or None


def create_prompt(forecast: float, irrigation_amount: float,
                  current_state: Dict[str, Any]) -> str:
    """
    Create a prompt template for the LLM with all metrics.

    Args:
        forecast: Forecasted soil moisture percentage
        irrigation_amount: Recommended irrigation amount in L/h
        current_state: Dictionary with current conditions

    Returns:
        Formatted prompt string

    Requirements: 4.1
    """
    current_moisture = current_state.get('soil_moisture', 0.0)
    rainfall = current_state.get('rain', 0.0)
    temperature = current_state.get('temperature', 0.0)
    humidity = current_state.get('humidity', 0.0)

    # Determine if irrigation should be done
    should_irrigate = "YES" if irrigation_amount > 0 else "NO"

    # Calculate threshold (24% with MAD=0.4, FC=30%, WP=15%)
    threshold = 24.0

    prompt = f"""You are an expert agricultural advisor explaining irrigation decisions to farmers. Use clear, practical language that farmers can understand and act on.

SYSTEM CONTEXT:
Our smart irrigation system uses:
1. LSTM AI model to forecast soil moisture 6 hours ahead
2. FAO-56 irrigation scheduling method (scientifically validated)
3. Management Allowed Depletion (MAD) = 40%
4. Irrigation threshold = {threshold}% soil moisture
5. Target range = 40-60% (optimal for most crops)

CURRENT SITUATION:
- Current Soil Moisture: {current_moisture:.1f}%
- AI Forecast (6h ahead): {forecast:.1f}%
- Temperature: {temperature:.1f}°C
- Humidity: {humidity:.1f}%
- Expected Rainfall: {rainfall:.1f} mm

DECISION MADE:
- Irrigate: {should_irrigate}
- Water Amount: {irrigation_amount:.1f} L/h

YOUR TASK:
Explain this decision in a way that:
1. Starts with a clear action statement (irrigate or don't irrigate)
2. States the specific water amount if irrigation is needed
3. Explains WHY using the metrics above (forecast, current moisture, weather)
4. Mentions the FAO-56 threshold ({threshold}%) and how it relates to the forecast
5. Gives practical advice the farmer can understand
6. Keeps it concise (4-6 sentences maximum)

IMPORTANT:
- Always reference specific numbers from the metrics
- Explain how the AI forecast influenced the decision
- Mention if rainfall reduces irrigation need
- Be encouraging and supportive in tone
- Use simple language, avoid jargon

Write your explanation now:"""

    return prompt




def create_validation_prompt(forecast: float, irrigation_amount: float, 
                            current_state: Dict[str, Any]) -> str:
    """
    Create a prompt for LLM to validate RL model decision.
    
    Args:
        forecast: Forecasted soil moisture percentage
        irrigation_amount: RL model's recommended irrigation amount
        current_state: Dictionary with current conditions
    
    Returns:
        Validation prompt string
    """
    current_moisture = current_state.get('soil_moisture', 0.0)
    rainfall = current_state.get('rain', 0.0)
    temperature = current_state.get('temperature', 0.0)
    humidity = current_state.get('humidity', 0.0)
    
    prompt = f"""You are an agricultural expert validating an irrigation decision.

Current Metrics:
- Soil Moisture: {current_moisture:.1f}% (target: 40-60%)
- Forecast (6h): {forecast:.1f}%
- Temperature: {temperature:.1f}°C
- Humidity: {humidity:.1f}%
- Expected Rainfall: {rainfall:.1f}mm
- RL Model Decision: {irrigation_amount:.1f} L/h

Analyze this decision:
1. Is the RL decision logical given the metrics?
2. If soil is below 40% or forecast is below 40%, irrigation MUST be recommended.
3. If rainfall > 5mm is expected, reduce irrigation.
4. If forecast > 70%, no irrigation is needed.

Respond with ONLY valid JSON (no markdown):
{{"valid": true/false, "reason": "brief explanation", "suggested_amount": number}}

If valid=false, suggest a corrected irrigation amount."""
    
    return prompt


def validate_rl_decision(forecast: float, irrigation_amount: float, 
                        current_state: Dict[str, Any]) -> Tuple[bool, float, str]:
    """
    Use LLM to validate RL model decision and suggest corrections if needed.
    
    Args:
        forecast: Forecasted soil moisture
        irrigation_amount: RL model's recommendation
        current_state: Current conditions
    
    Returns:
        Tuple of (is_valid, corrected_amount, reason)
    """
    api_key = get_groq_api_key()
    if not api_key:
        # No API, return original decision as valid
        return True, irrigation_amount, "No LLM validation available"
    
    prompt = create_validation_prompt(forecast, irrigation_amount, current_state)
    
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
                        "content": "You are a validation expert. Respond with ONLY valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 200
            },
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"Validation API error: {response.status_code}")
            return True, irrigation_amount, "Validation API failed"
        
        result = response.json()
        response_text = result['choices'][0]['message']['content'].strip()
        
        # Parse JSON response
        validation = json.loads(response_text)
        
        is_valid = validation.get('valid', True)
        reason = validation.get('reason', 'No reason provided')
        suggested = validation.get('suggested_amount', irrigation_amount)
        
        if not is_valid:
            print(f"LLM VALIDATION: Decision invalid. Reason: {reason}. Correcting to {suggested:.1f} L/h")
            return False, float(suggested), reason
        
        return True, irrigation_amount, reason
    
    except Exception as e:
        print(f"LLM validation failed: {str(e)}")
        return True, irrigation_amount, f"Validation error: {str(e)}"


def generate_explanation_groq(forecast: float, irrigation_amount: float, 
                              current_state: Dict[str, Any]) -> str:
    """
    Generate explanation using Groq API (Llama 3.1 70B).
    
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
    
    prompt = create_prompt(forecast, irrigation_amount, current_state)
    
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
                        "content": "You are a helpful agricultural advisor. Provide clear, practical explanations for farmers."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 300
            },
            timeout=10
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"Groq API error: {response.status_code} - {response.text}")
        
        result = response.json()
        explanation = result['choices'][0]['message']['content'].strip()
        
        return explanation
    
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Groq API request failed: {str(e)}") from e


def generate_explanation_huggingface(forecast: float, irrigation_amount: float, 
                                     current_state: Dict[str, Any]) -> str:
    """
    Generate explanation using HuggingFace Inference API.
    
    Args:
        forecast: Forecasted soil moisture percentage
        irrigation_amount: Recommended irrigation amount in L/h
        current_state: Dictionary with current conditions
    
    Returns:
        Human-readable explanation string
    
    Raises:
        RuntimeError: If API call fails
    """
    api_key = get_hf_api_key()
    if not api_key:
        raise RuntimeError("HUGGINGFACE_API_KEY not set in environment")
    
    prompt = create_prompt(forecast, irrigation_amount, current_state)
    
    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/meta-llama/Llama-2-7b-chat-hf",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "inputs": prompt,
                "parameters": {
                    "max_length": 300,
                    "temperature": 0.7
                }
            },
            timeout=10
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"HuggingFace API error: {response.status_code} - {response.text}")
        
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            explanation = result[0].get('generated_text', '').strip()
        else:
            explanation = str(result).strip()
        
        return explanation
    
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"HuggingFace API request failed: {str(e)}") from e


def generate_explanation(forecast: float, irrigation_amount: float, 
                        current_state: Dict[str, Any]) -> Tuple[str, float]:
    """
    Generate explanation and validate/correct RL decision using LLM.
    
    This function orchestrates the flow:
    1. Validates RL model decision using LLM
    2. Corrects irrigation amount if needed
    3. Generates explanation for the (possibly corrected) decision
    
    Args:
        forecast: Forecasted soil moisture percentage (0-100)
        irrigation_amount: RL model's recommended irrigation amount in L/h
        current_state: Dictionary containing:
            - soil_moisture: Current soil moisture percentage
            - rain: Expected rainfall in mm
            - temperature: Current temperature in Celsius
            - humidity: Current humidity percentage
    
    Returns:
        Tuple of (explanation_text, corrected_irrigation_amount)
    
    Raises:
        ValueError: If required fields are missing from current_state
    
    Requirements: 4.1, 4.2
    """
    # Validate inputs
    required_fields = ['soil_moisture', 'rain', 'temperature', 'humidity']
    missing_fields = [field for field in required_fields if field not in current_state]
    if missing_fields:
        raise ValueError(f"current_state missing required fields: {missing_fields}")
    
    # Step 1: Validate RL decision using LLM
    is_valid, corrected_amount, validation_reason = validate_rl_decision(
        forecast, irrigation_amount, current_state
    )
    
    # Use corrected amount if validation failed
    final_irrigation_amount = corrected_amount if not is_valid else irrigation_amount
    
    # Step 2: Try Groq first (recommended)
    if get_groq_api_key():
        try:
            print("Generating explanation using Groq API...")
            explanation = generate_explanation_groq(forecast, final_irrigation_amount, current_state)
            return explanation, final_irrigation_amount
        except Exception as e:
            print(f"Groq API failed: {str(e)}. Trying HuggingFace...")
    
    # Step 3: Try HuggingFace second
    if get_hf_api_key():
        try:
            print("Generating explanation using HuggingFace API...")
            explanation = generate_explanation_huggingface(forecast, final_irrigation_amount, current_state)
            return explanation, final_irrigation_amount
        except Exception as e:
            print(f"HuggingFace API failed: {str(e)}. Using fallback...")
    
    # Step 4: Fallback to rule-based explanation
    print("Using rule-based explanation (no API available)")
    explanation = create_fallback_explanation(forecast, final_irrigation_amount, current_state)
    return explanation, final_irrigation_amount


def create_fallback_explanation(forecast: float, irrigation_amount: float, 
                                current_state: Dict[str, Any]) -> str:
    """
    Create a simple rule-based explanation as fallback.
    
    Args:
        forecast: Forecasted soil moisture percentage
        irrigation_amount: Recommended irrigation amount in L/h
        current_state: Dictionary with current conditions
    
    Returns:
        Simple explanation string
    """
    current_moisture = current_state.get('soil_moisture', 0.0)
    rainfall = current_state.get('rain', 0.0)
    temperature = current_state.get('temperature', 0.0)
    humidity = current_state.get('humidity', 0.0)
    
    # Determine irrigation decision based on irrigation_amount
    if irrigation_amount > 0:
        decision = "YES, irrigate"
        action = f"Apply {irrigation_amount:.1f} L/h"
    else:
        decision = "NO, do not irrigate"
        action = "No irrigation needed at this time"
    
    # Build detailed reasoning considering all factors
    reasons = []
    
    # Soil moisture analysis
    if current_moisture < 30:
        reasons.append(f"soil is critically dry ({current_moisture:.1f}%)")
    elif current_moisture < 40:
        reasons.append(f"soil moisture is below target minimum ({current_moisture:.1f}%)")
    elif current_moisture > 70:
        reasons.append(f"soil is already wet ({current_moisture:.1f}%)")
    else:
        reasons.append(f"soil moisture is in good range ({current_moisture:.1f}%)")
    
    # Forecast analysis
    if forecast < 40:
        reasons.append(f"forecast shows soil will drop to {forecast:.1f}% (below target)")
    elif forecast > 70:
        reasons.append(f"forecast shows soil will reach {forecast:.1f}% (above target)")
    else:
        reasons.append(f"forecast shows soil will be {forecast:.1f}% (in target range)")
    
    # Rainfall analysis
    if rainfall > 5:
        reasons.append(f"significant rainfall ({rainfall:.1f}mm) expected - reduces irrigation need")
    elif rainfall > 0:
        reasons.append(f"some rainfall ({rainfall:.1f}mm) expected")
    else:
        reasons.append("no rainfall expected")
    
    # Temperature analysis
    if temperature > 35:
        reasons.append(f"high temperature ({temperature:.1f}°C) increases evaporation")
    elif temperature < 15:
        reasons.append(f"low temperature ({temperature:.1f}°C) reduces evaporation")
    else:
        reasons.append(f"moderate temperature ({temperature:.1f}°C)")
    
    explanation = (
        f"**Irrigation Decision: {decision}**\n\n"
        f"{action}.\n\n"
        f"**Why:** "
        f"{reasons[0].capitalize()}. "
        f"{reasons[1].capitalize()}. "
        f"{reasons[2].capitalize()}. "
        f"{reasons[3].capitalize()}."
    )
    
    return explanation
