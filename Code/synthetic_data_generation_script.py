import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# ============================
# CONFIGURATION
# ============================

START_DATE = datetime(2022, 1, 1)
YEARS = 4  # Increased to generate 10k+ rows
TIME_STEP_HOURS = 6

FIELD_CAPACITY = 70  # Increased for wider range
WILTING_POINT = 15   # Decreased for wider range
MAX_MOISTURE = 85    # Increased for wider range

# ===== TUNED PARAMETERS =====
SOIL_DECAY_RATE = 0.008
DRAINAGE_COEFF = 0.015
INFILTRATION_EFF = 0.5
NOISE_STD = 0.2



# ============================
# Seasonal Functions
# ============================

def get_season(day_of_year):
    if 150 <= day_of_year <= 250:
        return "monsoon"
    elif 60 <= day_of_year < 150:
        return "summer"
    else:
        return "winter"

def seasonal_temperature(day_of_year):
    return 28 + 10 * np.sin(2 * np.pi * day_of_year / 365)

def diurnal_variation(hour):
    return 4 * np.sin((hour - 8) * np.pi / 12)

# ============================
# Rain Model with Persistence
# ============================

# ===== Improved Rain Generator =====
class RainGenerator:
    def __init__(self):
        self.rain_memory = 0

    def generate(self, season):
        if self.rain_memory > 0:
            self.rain_memory -= 1
            return np.random.uniform(2, 15)  # Increased rainfall during events

        prob = 0.05  # Increased base probability
        if season == "monsoon":
            prob = 0.25  # Much higher during monsoon
        elif season == "summer":
            prob = 0.08  # Increased for summer
        elif season == "winter":
            prob = 0.03

        if np.random.rand() < prob:
            self.rain_memory = np.random.randint(1, 4)  # Longer rain events
            if season == "monsoon":
                return np.random.uniform(10, 30)  # Heavy monsoon rains
            else:
                return np.random.uniform(5, 15)

        return 0

# ============================
# Crop Coefficient
# ============================

def crop_coefficient(day_of_year):
    stage_day = day_of_year % 120
    if stage_day < 30:
        return 0.7
    elif stage_day < 80:
        return 1.1
    else:
        return 0.9

# ============================
# Evapotranspiration
# ============================

def evapotranspiration(temp, humidity, wind, hour, kc):
    solar_factor = max(0, np.sin((hour - 6) * np.pi / 12))
    base_et = 0.003 * temp * (1 - humidity/100) + 0.0015 * wind
    return base_et * solar_factor * kc

# ============================
# Irrigation Policy (Smarter)
# ============================

def generate_irrigation(soil_moisture):
    TARGET_LOW = 40
    TARGET_HIGH = 60

    if soil_moisture < TARGET_LOW:
        return np.random.uniform(3, 8)  # More aggressive irrigation
    elif soil_moisture > TARGET_HIGH:
        return 0
    else:
        # Probabilistic irrigation in target band
        if np.random.rand() < 0.3:
            return np.random.uniform(1, 3)
        return 0

# ============================
# Main Generator
# ============================

def generate_dataset():

    records = []
    soil_moisture = 45  # Start in middle of range
    rain_gen = RainGenerator()

    current_time = START_DATE
    end_time = START_DATE + timedelta(days=365 * YEARS)

    while current_time < end_time:

        day_of_year = current_time.timetuple().tm_yday
        hour = current_time.hour

        season = get_season(day_of_year)
        kc = crop_coefficient(day_of_year)

        temp = seasonal_temperature(day_of_year) + diurnal_variation(hour)
        humidity = np.random.uniform(30, 95)  # Wider humidity range
        wind = np.random.uniform(2, 25)  # Wider wind range

        rain = rain_gen.generate(season)
        irrigation = generate_irrigation(soil_moisture)

        # ET loss (more variable)
        et = evapotranspiration(temp, humidity, wind, hour, kc) * np.random.uniform(0.7, 1.2)

        # Gentle exponential decay
        decay_loss = SOIL_DECAY_RATE * (soil_moisture - WILTING_POINT)

        # Effective water input
        effective_input = INFILTRATION_EFF * (rain + irrigation)

        # Soft overflow drainage
        overflow = max(0, soil_moisture - FIELD_CAPACITY)
        drainage = DRAINAGE_COEFF * overflow**1.5

        #previous moisture
        previous_moisture = soil_moisture

        # Update moisture
        soil_moisture = (
            soil_moisture
            - et
            - decay_loss
            - drainage
            + effective_input
        )

        # Soft bounds with more realistic dynamics
        if soil_moisture < WILTING_POINT:
          soil_moisture = WILTING_POINT + (soil_moisture - WILTING_POINT) * 0.3
        if soil_moisture > MAX_MOISTURE:
          soil_moisture = MAX_MOISTURE - (soil_moisture - MAX_MOISTURE) * 0.3

        #Adding buffer
        soil_moisture = 0.80 * soil_moisture + 0.20 * previous_moisture

        # Small sensor noise
        soil_moisture += np.random.normal(0, NOISE_STD)

        # Forecast (next step approx)
        forecast_temp = seasonal_temperature((day_of_year + 1) % 365)
        forecast_rain = rain_gen.generate(season)

        records.append([
            current_time,
            season,
            hour,
            temp,
            humidity,
            wind,
            rain,
            irrigation,
            soil_moisture,
            forecast_temp,
            forecast_rain
        ])

        current_time += timedelta(hours=TIME_STEP_HOURS)

    columns = [
        "timestamp",
        "season",
        "hour",
        "temperature",
        "humidity",
        "wind",
        "rain",
        "irrigation",
        "soil_moisture",
        "forecast_temp_6h",
        "forecast_rain_6h"
    ]

    return pd.DataFrame(records, columns=columns)


# ============================
# Generate & Save
# ============================

if __name__ == "__main__":
    df = generate_dataset()
    # Save to backend data directory
    import os
    os.makedirs("Code/backend/data", exist_ok=True)
    df.to_csv("Code/backend/data/sensor_readings.csv", index=False)
    print("Dataset generated:", df.shape)
    print("Saved to Code/backend/data/sensor_readings.csv")