"""
Data Storage Layer for Smart Irrigation System.

This module provides functions for storing and retrieving data.
Uses AWS integration layer with automatic fallback to local storage.

Requirements: 7.1, 7.2, 7.5, 8.1, 8.2, 15.1, 15.2, 15.3, 15.4, 15.5
"""

import sqlite3
import pandas as pd
import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Import AWS integration layer
try:
    from aws_integration import (
        store_decision_aws,
        log_model_prediction_aws,
        write_sensor_data,
        get_aws_status
    )
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    print("AWS integration not available, using local storage only")


# Default paths for local storage
#SENSOR_DATA_PATH = os.getenv('SENSOR_DATA_PATH', 'Code/backend/data/sensor_readings.csv')
SENSOR_DATA_PATH = os.getenv('SENSOR_DATA_PATH', 'data/sensor_readings.csv')

DECISION_DB_PATH = os.getenv('DECISION_DB_PATH', 'Code/backend/data/irrigation_decisions.db')
MODEL_RESULTS_PATH = 'Code/backend/data/model_results'


# ============================================
# Sensor Data Storage
# ============================================

def load_sensor_data(start_time: Optional[datetime] = None, 
                     end_time: Optional[datetime] = None) -> pd.DataFrame:
    """
    Load sensor data from local CSV file.
    
    In production with AWS Timestream enabled, this would query Timestream.
    
    Args:
        start_time: Start of time range (optional)
        end_time: End of time range (optional)
    
    Returns:
        DataFrame with sensor readings
    
    Requirements: 7.1, 7.2
    """
    try:
        df = pd.read_csv(SENSOR_DATA_PATH)
        
        # Convert timestamp to datetime if needed
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Filter by time range if specified
        if start_time is not None:
            df = df[df['timestamp'] >= start_time]
        if end_time is not None:
            df = df[df['timestamp'] <= end_time]
        
        return df
    
    except FileNotFoundError:
        # Return empty DataFrame with expected schema
        return pd.DataFrame(columns=[
            'timestamp', 'season', 'hour', 'temperature', 'humidity',
            'wind', 'rain', 'irrigation', 'soil_moisture',
            'forecast_temp_6h', 'forecast_rain_6h'
        ])


def append_sensor_data(new_reading: Dict[str, Any]) -> bool:
    """
    Append a new sensor reading to the CSV file.
    
    This simulates receiving new sensor data 6 hours later.
    Used to update the CSV with irrigation decision results.
    
    Args:
        new_reading: Dictionary with sensor reading data
    
    Returns:
        True if successful, False otherwise
    
    Requirements: 7.1, 7.2
    """
    try:
        # Load existing data
        df = load_sensor_data()
        
        # Create new row as DataFrame
        new_row = pd.DataFrame([new_reading])
        
        # Append to existing data
        df = pd.concat([df, new_row], ignore_index=True)
        
        # Save back to CSV
        df.to_csv(SENSOR_DATA_PATH, index=False)
        
        print(f"Sensor data updated: {new_reading.get('timestamp')}")
        return True
    
    except Exception as e:
        print(f"Failed to append sensor data: {str(e)}")
        return False


# ============================================
# Decision Storage
# ============================================

def init_decision_db():
    """
    Initialize local SQLite database for irrigation decisions.
    
    In production with AWS RDS enabled, this would initialize PostgreSQL.
    
    Requirements: 8.1
    """
    os.makedirs(os.path.dirname(DECISION_DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DECISION_DB_PATH)
    cursor = conn.cursor()
    
    # Create decisions table
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


def store_decision(decision_data: Dict[str, Any]) -> bool:
    """
    Store irrigation decision using AWS (with fallback to local SQLite).
    
    Args:
        decision_data: Dictionary with decision information
    
    Returns:
        True if successful, False otherwise
    
    Requirements: 8.1, 8.2
    """
    if AWS_AVAILABLE:
        success, message = store_decision_aws(decision_data)
        print(f"Storage: {message}")
        return success
    
    # Fallback to local SQLite
    try:
        init_decision_db()
        
        conn = sqlite3.connect(DECISION_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO irrigation_decisions 
            (decision_id, farmer_id, timestamp, current_moisture, 
             forecasted_moisture, irrigation_amount, alerts, explanation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            decision_data.get('decision_id', str(int(time.time()))),
            decision_data.get('farmer_id', 'default'),
            decision_data.get('timestamp', datetime.now().isoformat()),
            decision_data.get('current_moisture'),
            decision_data.get('forecasted_moisture'),
            decision_data.get('irrigation_amount'),
            json.dumps(decision_data.get('alerts', [])),
            decision_data.get('explanation', '')
        ))
        
        conn.commit()
        conn.close()
        
        return True
    
    except Exception as e:
        print(f"Failed to store decision: {str(e)}")
        return False


def get_decision_history(limit: int = 50, farmer_id: str = 'default') -> List[Dict[str, Any]]:
    """
    Retrieve historical irrigation decisions.
    
    Args:
        limit: Maximum number of records to return
        farmer_id: Filter by farmer ID (default: 'default')
    
    Returns:
        List of historical decisions with explanations
    
    Requirements: 15.1, 15.2
    """
    try:
        init_decision_db()
        
        conn = sqlite3.connect(DECISION_DB_PATH)
        cursor = conn.cursor()
        
        # Query decisions ordered by timestamp (newest first)
        cursor.execute("""
            SELECT decision_id, farmer_id, timestamp, current_moisture,
                   forecasted_moisture, irrigation_amount, alerts, explanation
            FROM irrigation_decisions
            WHERE farmer_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (farmer_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        history = []
        for row in rows:
            history.append({
                'decision_id': row[0],
                'farmer_id': row[1],
                'timestamp': row[2],
                'current_moisture': row[3],
                'forecasted_moisture': row[4],
                'irrigation_amount': row[5],
                'alerts': json.loads(row[6]) if row[6] else [],
                'explanation': row[7]
            })
        
        return history
    
    except Exception as e:
        print(f"Failed to retrieve decision history: {str(e)}")
        return []


# ============================================
# Model Results Logging
# ============================================

def log_model_prediction(model_type: str, prediction_data: Dict[str, Any], 
                         max_retries: int = 3) -> bool:
    """
    Log model prediction using AWS S3 (with fallback to local Parquet).
    
    Args:
        model_type: Type of model ('lstm' or 'rl')
        prediction_data: Dictionary with prediction information
        max_retries: Maximum retry attempts (for AWS in production)
    
    Returns:
        True if successful, False otherwise
    
    Requirements: 15.1, 15.2, 15.3, 15.4, 15.5
    """
    if AWS_AVAILABLE:
        success, message = log_model_prediction_aws(model_type, prediction_data)
        print(f"Model logging: {message}")
        return success
    
    # Fallback to local Parquet
    try:
        date = datetime.now()
        path = Path(MODEL_RESULTS_PATH) / model_type / f"year={date.year}" / \
               f"month={date.month:02d}" / f"day={date.day:02d}"
        path.mkdir(parents=True, exist_ok=True)
        
        df = pd.DataFrame([prediction_data])
        file_path = path / f"predictions_{date.strftime('%H%M%S')}.parquet"
        df.to_parquet(file_path, engine='pyarrow', index=False)
        
        return True
    
    except Exception as e:
        print(f"Failed to log model prediction: {str(e)}")
        return False
