"""
History Page for Smart Irrigation System.

Simple page displaying past irrigation decisions.
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os

API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="History - Smart Irrigation System",
    page_icon="📜",
    layout="wide"
)

# Sidebar
with st.sidebar:
    st.title("🌱 Smart Irrigation")
    st.markdown("---")
    
    page = st.radio(
        "Select Page",
        ["Dashboard", "History"],
        label_visibility="collapsed",
        index=1
    )
    
    if page == "Dashboard":
        st.switch_page("dashboard.py")
    
    st.markdown("---")
    
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

# Main content
st.title("📜 Decision History")

try:
    response = requests.get(f"{API_URL}/history", params={"limit": 50}, timeout=10)
    
    if response.status_code == 200:
        history = response.json()
        if isinstance(history, dict) and 'history' in history:
            history = history['history']
        
        if history:
            # Create simple table
            data = []
            for decision in history:
                data.append({
                    'Time': decision.get('timestamp', 'N/A'),
                    'Soil Moisture': f"{decision.get('current_moisture', 0):.1f}%",
                    'Forecast': f"{decision.get('forecasted_moisture', 0):.1f}%",
                    'Irrigation (L/h)': f"{decision.get('irrigation_amount', 0):.1f}",
                    'Alerts': len(decision.get('alerts', []))
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Simple expandable explanations
            st.markdown("---")
            st.subheader("💬 Explanations")
            
            for idx, decision in enumerate(reversed(history)):
                with st.expander(f"{decision.get('timestamp', 'N/A')} - {decision.get('current_moisture', 0):.1f}%"):
                    st.write(decision.get('explanation', 'No explanation available'))
        else:
            st.info("No history available yet.")
    else:
        st.error("Failed to fetch history")
        
except Exception as e:
    st.error(f"Error: {str(e)}")
