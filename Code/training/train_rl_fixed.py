import gymnasium as gym
import numpy as np
import torch
import pandas as pd
from stable_baselines3 import PPO
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

class IrrigationEnv(gym.Env):
    """
    Irrigation environment for RL training.
    
    Action space: 0-100 L/h (continuous)
    Observation space: [current_soil_moisture, forecast_soil_moisture, rain, temperature, humidity]
    Target range: 40-60% soil moisture
    """
    
    def __init__(self, dataset, lstm_model, seq_length=24, target_low=40, target_high=60):
        super().__init__()
        self.dataset = dataset
        self.lstm_model = lstm_model
        self.seq_length = seq_length
        self.index = seq_length
        self.target_low = target_low
        self.target_high = target_high

        # Action space: irrigation amount (0–100 L/h)
        self.action_space = gym.spaces.Box(low=0, high=100, shape=(1,), dtype=np.float32)

        # Observation space: [current soil moisture, forecasted soil moisture, rain, temp, humidity]
        self.observation_space = gym.spaces.Box(low=0, high=100, shape=(5,), dtype=np.float32)

        self.soil_moisture = 50

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.index = self.seq_length
        self.soil_moisture = self.dataset.iloc[self.index]["soil_moisture"]
        return self._get_obs(), {}

    def _get_obs(self):
        row = self.dataset.iloc[self.index]

        # Forecast soil moisture using LSTM
        past_seq = self.dataset.iloc[self.index-self.seq_length:self.index][
            ["temperature","humidity","wind","rain","soil_moisture","forecast_rain_6h"]
        ].values
        past_seq = torch.tensor(past_seq, dtype=torch.float32).unsqueeze(0)
        with torch.no_grad():
            forecast = self.lstm_model(past_seq).item()

        return np.array([
            self.soil_moisture,
            forecast,              # proactive foresight
            row["forecast_rain_6h"],
            row["temperature"],
            row["humidity"]
        ], dtype=np.float32)

    def step(self, action):
        irrigation = action[0]
        row = self.dataset.iloc[self.index]

        # Realistic soil moisture dynamics
        # Irrigation effect: 1 L/h increases moisture by ~0.8%
        # Rain effect: 1mm increases moisture by ~0.5%
        # Temperature effect: higher temp increases ET loss
        # Wind effect: higher wind increases ET loss
        
        self.soil_moisture += 0.008 * irrigation  # 1 L/h -> 0.8% increase
        self.soil_moisture += 0.5 * row["rain"]   # 1mm rain -> 0.5% increase
        self.soil_moisture -= 0.08 * row["temperature"]  # ET loss
        self.soil_moisture -= 0.02 * row["wind"]  # Wind-driven ET
        self.soil_moisture -= 0.01 * (100 - row["humidity"])  # Humidity effect

        # Clamp to realistic bounds
        self.soil_moisture = np.clip(self.soil_moisture, 15, 85)

        # Continuous reward function: encourage staying in target band
        in_target = self.target_low <= self.soil_moisture <= self.target_high
        
        # Base reward for being in target band
        if in_target:
            reward = 1.0
        else:
            # Penalty based on distance from target band
            if self.soil_moisture < self.target_low:
                distance = self.target_low - self.soil_moisture
                reward = -0.5 - 0.1 * distance
            else:  # above target
                distance = self.soil_moisture - self.target_high
                reward = -0.5 - 0.1 * distance
        
        # Penalty for excessive irrigation (water waste)
        reward -= 0.001 * irrigation
        
        # Bonus for efficient irrigation (small amounts when needed)
        if in_target and irrigation < 20:
            reward += 0.1

        self.index += 1
        done = self.index >= len(self.dataset) - 1
        obs = self._get_obs() if not done else np.zeros(5, dtype=np.float32)

        return obs, reward, done, False, {}

# ============================
# Load LSTM model and dataset
# ============================
print("Loading LSTM model...")
lstm_model = torch.load("backend/models/soil_forecast_model.pt", weights_only=False)
lstm_model.eval()
print("LSTM model loaded successfully")

print("Loading dataset...")
df = pd.read_csv("backend/data/sensor_readings.csv")
print(f"Dataset shape: {df.shape}")

# ============================
# Training
# ============================
print("Creating environment...")
env = IrrigationEnv(df, lstm_model, seq_length=24, target_low=40, target_high=60)

print("Training RL model with PPO...")
print("This may take a few minutes...")
model = PPO(
    "MlpPolicy", 
    env, 
    verbose=1, 
    learning_rate=3e-4, 
    n_steps=2048,
    batch_size=64,
    n_epochs=10,
    gamma=0.99,
    gae_lambda=0.95
)

# Train for 50k timesteps (reduced for faster training)
model.learn(total_timesteps=50000)

# ============================
# Save model to correct location
# ============================
os.makedirs("backend/models", exist_ok=True)
model.save("backend/models/proactive_irrigation_policy")
print("Model saved to backend/models/proactive_irrigation_policy.zip")

# ============================
# Quick validation
# ============================
print("\nValidating trained model...")
obs = env.reset()
total_reward = 0
for _ in range(100):
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, done, _ = env.step(action)
    total_reward += reward
    if done:
        break

print(f"Validation episode reward: {total_reward:.2f}")
print("RL training complete!")
