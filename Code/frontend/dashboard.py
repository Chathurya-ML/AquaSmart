"""
Streamlit Dashboard for Smart Irrigation System.

This dashboard provides a user-friendly interface for viewing irrigation
recommendations, forecasts, and system status.

Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 5.1, 5.2
"""

import streamlit as st
import requests
import base64
from datetime import datetime
import pandas as pd

# ============================================
# Configuration
# ============================================

import os

API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Supported languages
LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi',
    'es': 'Spanish',
    'pt': 'Portuguese',
    'fr': 'French',
    'de': 'German'
}

# ============================================
# Page Configuration
# ============================================

st.set_page_config(
    page_title="Smart Irrigation System - Prototype",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# Helper Functions
# ============================================

def fetch_irrigation_data(language='en'):
    """
    Fetch irrigation decision from the API.
    
    Requirements: 11.1, 11.5
    """
    try:
        # Load sample sensor data
        try:
            sensor_data = pd.read_csv('Code/backend/data/sensor_readings.csv')
        except FileNotFoundError:
            # Try alternative paths
            try:
                sensor_data = pd.read_csv('../backend/data/sensor_readings.csv')
            except FileNotFoundError:
                sensor_data = pd.read_csv('./data/sensor_readings.csv')
        
        # Get last 24 hours of data for past_sequence
        past_sequence = sensor_data.tail(24).to_dict('records')
        
        # Get current readings from the most recent data point
        current = sensor_data.iloc[-1]
        
        # Prepare request
        request_data = {
            "soil_moisture": float(current['soil_moisture']),
            "temperature": float(current['temperature']),
            "humidity": float(current['humidity']),
            "rain": float(current['forecast_rain_6h']),
            "forecast_temp_6h": float(current['forecast_temp_6h']),
            "forecast_rain_6h": float(current['forecast_rain_6h']),
            "past_sequence": past_sequence,
            "language": language
        }
        
        # Call API
        response = requests.post(
            f"{API_URL}/irrigation_decision",
            json=request_data,
            timeout=120  # Increased from 30 to 120 seconds for first LLM load
        )
        
        if response.status_code == 200:
            return response.json(), current
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None, None
    
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None, None


def check_api_health():
    """Check if the API is running."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


# ============================================
# Sidebar
# ============================================

with st.sidebar:
    st.title("🌱 Smart Irrigation")
    st.markdown("---")
    
    # Language selection
    st.subheader("Language / भाषा")
    selected_language = st.selectbox(
        "Select Language",
        options=list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x],
        key='language'
    )
    
    st.markdown("---")
    
    # Refresh button
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    
    st.markdown("---")
    
    # System status
    st.subheader("System Status")
    api_healthy = check_api_health()
    
    if api_healthy:
        st.success("✓ API Online")
    else:
        st.error("✗ API Offline")
        st.info("Start the backend: `uvicorn app:app --reload`")

# ============================================
# Main Dashboard
# ============================================

st.title("Smart Irrigation System - Prototype")
st.markdown("ML-powered irrigation decisions with forecasting and alerts")

# Check API health
if not check_api_health():
    st.error("⚠️ Backend API is not running. Please start the FastAPI server.")
    st.code("cd Code/backend && uvicorn app:app --reload", language="bash")
    st.stop()

# Fetch data once on page load or when language changes
if 'data' not in st.session_state or st.session_state.get('last_language') != selected_language:
    with st.spinner("Fetching irrigation data..."):
        data, current = fetch_irrigation_data(selected_language)
        st.session_state.data = data
        st.session_state.current = current
        st.session_state.last_language = selected_language

data = st.session_state.get('data')
current = st.session_state.get('current')

if data is None or current is None:
    st.error("Failed to fetch data. Please check the API and try again.")
    st.stop()

# ============================================
# Current Readings Section
# ============================================

st.header("📊 Current Conditions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Current Soil Moisture",
        f"{current['soil_moisture']:.1f}%",
        help="Current soil moisture level"
    )

with col2:
    forecast_delta = data['forecasted_moisture'] - current['soil_moisture']
    st.metric(
        "Forecast (6h ahead)",
        f"{data['forecasted_moisture']:.1f}%",
        delta=f"{forecast_delta:+.1f}%",
        help="Predicted soil moisture in 6 hours"
    )

with col3:
    st.metric(
        "Temperature",
        f"{current['temperature']:.1f}°C",
        help="Current temperature"
    )

with col4:
    st.metric(
        "Humidity",
        f"{current['humidity']:.1f}%",
        help="Current humidity level"
    )

st.markdown("---")

# ============================================
# Irrigation Recommendation Section
# ============================================

st.header("💧 Irrigation Recommendation")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"Recommended: {data['irrigation_amount']:.1f} L/h")
    
    # Visual gauge for moisture levels
    st.progress(
        min(1.0, current['soil_moisture'] / 100),
        text=f"Current: {current['soil_moisture']:.1f}%"
    )
    
    st.caption(f"🎯 Target: 40-60% | Current: {current['soil_moisture']:.1f}% | Forecast: {data['forecasted_moisture']:.1f}%")

with col2:
    # Active alerts
    if data['alerts']:
        st.warning("⚠️ Active Alerts")
        for alert in data['alerts']:
            st.write(f"• {alert}")
    else:
        st.success("✓ No Alerts")

st.markdown("---")

# ============================================
# Decision Explanation Section
# ============================================

st.header("🤖 Decision Explanation")

# Display explanation
st.info(data['llm_explanation'])

# Audio playback
if data.get('audio_base64'):
    try:
        audio_bytes = base64.b64decode(data['audio_base64'])
        st.audio(audio_bytes, format='audio/mp3')
    except Exception as e:
        st.warning(f"Audio playback unavailable: {str(e)}")

# Timestamp
st.caption(f"Decision generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption(f"Next update: {data.get('next_run', '6 hours later')}")

st.markdown("---")

# ============================================
# System Information Section
# ============================================

with st.expander("ℹ️ System Information"):
    st.markdown("""
    ### About This System
    
    This Smart Irrigation System uses machine learning to optimize water usage:
    
    - **LSTM Model**: Forecasts soil moisture 6 hours ahead
    - **RL Model**: Determines optimal irrigation amounts
    - **Alert System**: Warns about critical conditions
    - **Multi-language**: Supports multiple languages with audio
    
    ### Prototype vs Production
    
    **Current (Prototype)**:
    - Local data and models
    - Single fetch on page load
    - Open-source LLM (DistilGPT-2)
    
    **Production (Commented)**:
    - AWS Timestream, RDS, S3
    - Auto-refresh every 6 hours
    - Amazon Bedrock for LLM
    - Twilio notifications
    """)

# ============================================
# Footer
# ============================================

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Smart Irrigation System v1.0 | Prototype | "
    "<a href='http://localhost:8000/docs' target='_blank'>API Docs</a>"
    "</div>",
    unsafe_allow_html=True
)
