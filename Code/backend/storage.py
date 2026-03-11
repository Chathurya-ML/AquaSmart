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
# Use working CSV for app.py computation and updates
SENSOR_DATA_PATH = os.getenv('SENSOR_DATA_PATH', 'Code/backend/data/working_sensor_data.csv')

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
        
        # Validate CSV integrity - check for malformed rows
        expected_columns = [
            'timestamp', 'season', 'hour', 'temperature', 'humidity',
            'wind', 'rain', 'irrigation', 'soil_moisture',
            'forecast_temp_6h', 'forecast_rain_6h'
        ]
        
        missing_cols = [col for col in expected_columns if col not in df.columns]
        if missing_cols:
            print(f"Warning: Missing columns in CSV: {missing_cols}")
        
        # Convert timestamp to datetime if needed
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            # Remove rows with invalid timestamps
            invalid_rows = df[df['timestamp'].isna()].index.tolist()
            if invalid_rows:
                print(f"Warning: Removing {len(invalid_rows)} rows with invalid timestamps")
                df = df.dropna(subset=['timestamp'])
        
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
        # Validate required fields
        required_fields = [
            'timestamp', 'season', 'hour', 'temperature', 'humidity',
            'wind', 'rain', 'irrigation', 'soil_moisture',
            'forecast_temp_6h', 'forecast_rain_6h'
        ]
        
        missing_fields = [f for f in required_fields if f not in new_reading]
        if missing_fields:
            print(f"Warning: Missing fields in new reading: {missing_fields}")
            # Add default values for missing fields
            for field in missing_fields:
                if field == 'season':
                    new_reading[field] = 'winter'
                elif field == 'hour':
                    new_reading[field] = 0
                else:
                    new_reading[field] = 0.0
        
        # Validate data types and ranges
        try:
            # Ensure numeric fields are floats
            numeric_fields = [
                'temperature', 'humidity', 'wind', 'rain', 'irrigation',
                'soil_moisture', 'forecast_temp_6h', 'forecast_rain_6h', 'hour'
            ]
            for field in numeric_fields:
                if field in new_reading:
                    new_reading[field] = float(new_reading[field])
            
            # Validate ranges
            if new_reading.get('soil_moisture', 0) < 0 or new_reading.get('soil_moisture', 0) > 100:
                print(f"Warning: Soil moisture {new_reading['soil_moisture']} out of range [0-100]")
            
            if new_reading.get('humidity', 0) < 0 or new_reading.get('humidity', 0) > 100:
                print(f"Warning: Humidity {new_reading['humidity']} out of range [0-100]")
        
        except ValueError as e:
            print(f"Error: Invalid data type in new reading: {str(e)}")
            return False
        
        # Load existing data
        df = load_sensor_data()
        
        # Create new row as DataFrame
        new_row = pd.DataFrame([new_reading])
        
        # Append to existing data
        df = pd.concat([df, new_row], ignore_index=True)
        
        # Save back to CSV with proper formatting
        df.to_csv(SENSOR_DATA_PATH, index=False, quoting=1)  # quoting=1 ensures proper CSV format
        
        print(f"Sensor data updated: {new_reading.get('timestamp')} | Irrigation: {new_reading.get('irrigation', 0):.2f} L/h")
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
        
        # If no history, populate with sample data for demo
        if len(history) == 0:
            print("No history found. Populating with sample data for demo...")
            _populate_sample_history()
            # Recursively call to get the sample data
            return get_decision_history(limit, farmer_id)
        
        return history
    
    except Exception as e:
        print(f"Failed to retrieve decision history: {str(e)}")
        return []


def _populate_sample_history():
    """
    Populate database with sample irrigation decisions for demo purposes.
    Only called if database is empty.
    """
    try:
        from datetime import datetime, timedelta
        
        init_decision_db()
        conn = sqlite3.connect(DECISION_DB_PATH)
        cursor = conn.cursor()
        
        # Create 5 sample decisions at 6-hour intervals
        base_time = datetime.now() - timedelta(hours=24)
        
        sample_decisions = [
            {
                'decision_id': str(int(base_time.timestamp())),
                'farmer_id': 'default',
                'timestamp': base_time.isoformat(),
                'current_moisture': 28.5,
                'forecasted_moisture': 26.2,
                'irrigation_amount': 150.0,
                'alerts': json.dumps(['Soil moisture below threshold']),
                'explanation': 'Soil moisture is declining. Irrigation recommended to maintain optimal levels.'
            },
            {
                'decision_id': str(int((base_time + timedelta(hours=6)).timestamp())),
                'farmer_id': 'default',
                'timestamp': (base_time + timedelta(hours=6)).isoformat(),
                'current_moisture': 26.2,
                'forecasted_moisture': 24.8,
                'irrigation_amount': 180.0,
                'alerts': json.dumps(['Critical: Soil moisture critical']),
                'explanation': 'Soil moisture approaching critical threshold. Immediate irrigation required.'
            },
            {
                'decision_id': str(int((base_time + timedelta(hours=12)).timestamp())),
                'farmer_id': 'default',
                'timestamp': (base_time + timedelta(hours=12)).isoformat(),
                'current_moisture': 32.1,
                'forecasted_moisture': 30.5,
                'irrigation_amount': 0.0,
                'alerts': json.dumps([]),
                'explanation': 'Soil moisture is adequate. No irrigation needed at this time.'
            },
            {
                'decision_id': str(int((base_time + timedelta(hours=18)).timestamp())),
                'farmer_id': 'default',
                'timestamp': (base_time + timedelta(hours=18)).isoformat(),
                'current_moisture': 30.5,
                'forecasted_moisture': 28.9,
                'irrigation_amount': 120.0,
                'alerts': json.dumps(['Rainfall expected']),
                'explanation': 'Rainfall expected in 6 hours. Light irrigation to prepare soil.'
            },
            {
                'decision_id': str(int((base_time + timedelta(hours=24)).timestamp())),
                'farmer_id': 'default',
                'timestamp': (base_time + timedelta(hours=24)).isoformat(),
                'current_moisture': 35.2,
                'forecasted_moisture': 33.8,
                'irrigation_amount': 0.0,
                'alerts': json.dumps([]),
                'explanation': 'Recent rainfall has increased soil moisture. No irrigation needed.'
            }
        ]
        
        for decision in sample_decisions:
            cursor.execute("""
                INSERT INTO irrigation_decisions 
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
        print(f"✓ Populated database with {len(sample_decisions)} sample decisions")
        
    except Exception as e:
        print(f"Failed to populate sample history: {str(e)}")


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
