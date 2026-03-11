"""
Create a working CSV with the latest recent records for app.py to use.
This CSV will be used for computation and updated with new values.
"""

import pandas as pd
from pathlib import Path

# Paths
MAIN_CSV = 'Code/backend/data/sensor_readings.csv'
WORKING_CSV = 'Code/backend/data/working_sensor_data.csv'

def create_working_csv(num_records=100):
    """
    Create a working CSV with the latest records from the main CSV.
    
    Args:
        num_records: Number of recent records to include (default: 100)
    """
    try:
        # Read the main CSV
        df = pd.read_csv(MAIN_CSV)
        
        # Get the latest records
        working_df = df.tail(num_records).copy()
        
        # Save to working CSV
        working_df.to_csv(WORKING_CSV, index=False)
        
        print(f"✓ Created working CSV: {WORKING_CSV}")
        print(f"  Records: {len(working_df)}")
        print(f"  Date range: {working_df['timestamp'].iloc[0]} to {working_df['timestamp'].iloc[-1]}")
        print(f"  File size: {Path(WORKING_CSV).stat().st_size} bytes")
        
        return True
    
    except Exception as e:
        print(f"✗ Error creating working CSV: {str(e)}")
        return False


if __name__ == "__main__":
    create_working_csv(num_records=100)
