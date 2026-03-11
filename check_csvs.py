import pandas as pd

print("=== Main CSV ===")
df_main = pd.read_csv('Code/backend/data/sensor_readings.csv')
print(f'Rows: {len(df_main)}')
print(f'Date range: {df_main["timestamp"].min()} to {df_main["timestamp"].max()}')

print("\n=== Working CSV ===")
df_working = pd.read_csv('Code/backend/data/working_sensor_data.csv')
print(f'Rows: {len(df_working)}')
if len(df_working) > 0:
    print(f'Date range: {df_working["timestamp"].min()} to {df_working["timestamp"].max()}')
else:
    print('Empty!')
