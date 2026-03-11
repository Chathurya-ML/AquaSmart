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
    
    The API automatically loads data from CSV and makes decision.
    Frontend just needs to provide the language preference.
    
    Requirements: 11.1, 11.5
    """
    try:
        # Call API endpoint that auto-loads CSV data
        response = requests.get(
            f"{API_URL}/irrigation_decision_auto",
            params={"language": language},
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            # Return data and a mock current object for display
            current = {
                'soil_moisture': data.get('forecasted_moisture', 0),
                'temperature': 0,
                'humidity': 0,
                'forecast_temp_6h': 0,
                'forecast_rain_6h': 0
            }
            return data, current
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
    
    # Navigation
    st.subheader("Navigation")
    page = st.radio(
        "Select Page",
        ["Dashboard", "History"],
        label_visibility="collapsed"
    )
    
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
        st.stop()

# Dashboard page content
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
    st.subheader(f"Recommended: {data['irrigation_amount']:.0f} Liters")
    
    # Visual gauge for moisture levels
    st.progress(
        min(1.0, current['soil_moisture'] / 100),
        text=f"Current: {current['soil_moisture']:.1f}%"
    )
    
    # FAO-56 thresholds
    st.caption(f"🎯 Field Capacity: 30% | Irrigation Threshold: 24% | Current: {current['soil_moisture']:.1f}% | Forecast: {data['forecasted_moisture']:.1f}%")

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
