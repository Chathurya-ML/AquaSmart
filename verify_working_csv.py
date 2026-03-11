import pandas as pd

# Check working CSV
df = pd.read_csv('Code/backend/data/working_sensor_data.csv')
print(f'Working CSV rows: {len(df)}')
print(f'Date range: {df["timestamp"].min()} to {df["timestamp"].max()}')

# Check for 2026 data
has_2026 = df['timestamp'].astype(str).str.contains('2026').any()
print(f'Has 2026 data: {has_2026}')

if has_2026:
    print('\nRemoving 2026 data...')
    df_clean = df[~df['timestamp'].astype(str).str.contains('2026')].copy()
    df_clean.to_csv('Code/backend/data/working_sensor_data.csv', index=False)
    print(f'✓ Cleaned! New row count: {len(df_clean)}')
else:
    print('✓ No 2026 data found')
