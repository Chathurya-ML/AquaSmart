"""
Populate history database with dummy 6-hour interval data for demo purposes.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

# Database path
DECISION_DB_PATH = 'Code/backend/data/irrigation_decisions.db'

def init_decision_db():
    """Initialize the database."""
    Path(DECISION_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DECISION_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS irrigation_decisions (
            decision_id TEXT PRIMARY KEY,
            farmer_id TEXT,
            timestamp TEXT,
            current_moisture REAL,
            forecasted_moisture REAL,
            irrigation_amount REAL,
            alerts TEXT,
            explanation TEXT
        )
    """)
    
    conn.commit()
    conn.close()


def populate_dummy_history():
    """Populate with 6-hour interval dummy data."""
    init_decision_db()
    
    conn = sqlite3.connect(DECISION_DB_PATH)
    cursor = conn.cursor()
    
    # Generate 10 decisions at 6-hour intervals (going backwards from now)
    base_time = datetime.now()
    decisions = []
    
    for i in range(10):
        # Go backwards in time
        timestamp = base_time - timedelta(hours=6*i)
        
        # Simulate realistic soil moisture progression
        current_moisture = 46.15 - (i * 0.5)  # Gradually decreases
        forecasted_moisture = current_moisture - 1.0  # Forecast is slightly lower
        
        # Determine irrigation based on threshold (24%)
        if forecasted_moisture < 24:
            # Calculate irrigation: (30% - forecast) × 0.5m × 1000 × 10
            water_deficit = (0.30 - forecasted_moisture/100) * 0.5 * 1000
            irrigation_amount = water_deficit * 10  # Convert to liters
        else:
            irrigation_amount = 0
        
        # Generate alerts
        alerts = []
        if forecasted_moisture < 20:
            alerts.append("⚠️ Critical: Soil moisture very low")
        elif forecasted_moisture < 24:
            alerts.append("⚠️ Warning: Soil moisture below threshold")
        
        # Generate explanation
        if irrigation_amount > 0:
            explanation = f"Soil moisture forecast is {forecasted_moisture:.1f}%, which is below the irrigation threshold of 24%. Recommended irrigation: {irrigation_amount:.0f} liters to bring soil back to field capacity (30%)."
        else:
            explanation = f"Soil moisture forecast is {forecasted_moisture:.1f}%, which is adequate. No irrigation needed at this time."
        
        decision = {
            'decision_id': str(int(timestamp.timestamp())),
            'farmer_id': 'default',
            'timestamp': timestamp.isoformat(),
            'current_moisture': current_moisture,
            'forecasted_moisture': forecasted_moisture,
            'irrigation_amount': irrigation_amount,
            'alerts': json.dumps(alerts),
            'explanation': explanation
        }
        
        decisions.append(decision)
        
        # Insert into database
        cursor.execute("""
            INSERT OR REPLACE INTO irrigation_decisions 
            (decision_id, farmer_id, timestamp, current_moisture, 
             forecasted_moisture, irrigation_amount, alerts, explanation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            decision['decision_id'],
            decision['farmer_id'],
            decision['timestamp'],
            decision['current_moisture'],
            decision['forecasted_moisture'],
            decision['irrigation_amount'],
            decision['alerts'],
            decision['explanation']
        ))
    
    conn.commit()
    conn.close()
    
    print(f"✓ Populated history with {len(decisions)} dummy decisions")
    print("\nSample decisions (most recent first):")
    for i, d in enumerate(decisions[:3]):
        print(f"\n{i+1}. {d['timestamp']}")
        print(f"   Current: {d['current_moisture']:.1f}% → Forecast: {d['forecasted_moisture']:.1f}%")
        print(f"   Irrigation: {d['irrigation_amount']:.0f} liters")
        print(f"   Explanation: {d['explanation']}")


if __name__ == "__main__":
    populate_dummy_history()
