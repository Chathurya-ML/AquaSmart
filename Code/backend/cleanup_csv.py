"""Clean CSV by removing all non-2024 data"""
import pandas as pd

df = pd.read_csv('Code/backend/data/sensor_readings.csv')
print(f'Total rows before: {len(df)}')
print(f'Date range: {df["timestamp"].min()} to {df["timestamp"].max()}')

# Keep only 2024 data
df_2024 = df[df['timestamp'].str.startswith('2024')].copy()
print(f'2024 rows: {len(df_2024)}')

# Save cleaned CSV
df_2024.to_csv('Code/backend/data/sensor_readings.csv', index=False)
print('✓ Cleaned CSV - removed all non-2024 data')
