
import gym
import numpy as np
import torch
import pandas as pd
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import EvalCallback
import os

class IrrigationEnv(gym.Env):
    def __init__(self, dataset, lstm_model, seq_length=24, target_low=40, target_high=60, 
                 episode_length=500, curriculum_stage=0):
        super().__init__()
        self.dataset = dataset
        self.lstm_model = lstm_model
        self.seq_length = seq_length
        self.episode_length = episode_length  # Shorter episodes for better learning
        self.steps_in_episode = 0
        self.curriculum_stage = curriculum_stage  # 0=wide band, 1=medium, 2=tight
        
        # Curriculum learning: gradually tighten the target band
        if curriculum_stage == 0:
            self.target_low = 30
            self.target_high = 70
        elif curriculum_stage == 1:
            self.target_low = 35
            self.target_high = 65
        else:
            self.target_low = target_low
            self.target_high = target_high

        # Action space: irrigation amount (0–100 L/h)
        self.action_space = gym.spaces.Box(low=0, high=100, shape=(1,), dtype=np.float32)

        # Observation space: [current soil moisture, forecasted soil moisture, rain, temp, humidity]
        # All normalized to [0, 1]
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(5,), dtype=np.float32)

        self.soil_moisture = 50
        self.start_index = seq_length

    def reset(self):
        # Random start position in dataset to increase diversity
        self.start_index = np.random.randint(self.seq_length, len(self.dataset) - self.episode_length - 1)
        self.index = self.start_index
        self.steps_in_episode = 0
        self.soil_moisture = self.dataset.iloc[self.index]["soil_moisture"]
        return self._get_obs()

    def _normalize_obs(self, obs):
        """Normalize observations to [0, 1] range"""
        # soil_moisture: 0-100 -> 0-1
        # forecast: 0-100 -> 0-1
        # rain: 0-50 -> 0-1 (cap at 50mm)
        # temperature: -10 to 50 -> 0-1
        # humidity: 0-100 -> 0-1
        
        normalized = np.array([
            obs[0] / 100.0,                    # current moisture
            obs[1] / 100.0,                    # forecast
            np.clip(obs[2], 0, 50) / 50.0,    # rain (capped at 50mm)
            np.clip((obs[3] + 10) / 60.0, 0, 1),  # temperature (-10 to 50°C)
            obs[4] / 100.0                     # humidity
        ], dtype=np.float32)
        
        return normalized

    def _get_obs(self):
        row = self.dataset.iloc[self.index]

        # Forecast soil moisture using LSTM
        past_seq = self.dataset.iloc[self.index-self.seq_length:self.index][["temperature","humidity","wind","rain","soil_moisture","forecast_rain_6h"]].values
        past_seq = torch.tensor(past_seq, dtype=torch.float32).unsqueeze(0)
        with torch.no_grad():
            forecast = self.lstm_model(past_seq).item()

        obs = np.array([
            self.soil_moisture,
            forecast,
            row["forecast_rain_6h"],
            row["temperature"],
            row["humidity"]
        ], dtype=np.float32)
        
        return self._normalize_obs(obs)

    def step(self, action):
        irrigation = action[0] * 100.0  # Scale from [0,1] to [0,100]
        row = self.dataset.iloc[self.index]

        # More realistic soil moisture dynamics
        self.soil_moisture += 0.008 * irrigation  # 1 L/h -> 0.8% increase
        self.soil_moisture += 0.5 * row["rain"]   # 1mm rain -> 0.5% increase
        self.soil_moisture -= 0.08 * row["temperature"]  # ET loss
        self.soil_moisture -= 0.02 * row["wind"]  # Wind-driven ET
        self.soil_moisture -= 0.01 * (100 - row["humidity"])  # Humidity effect

        # Clamp to realistic bounds
        self.soil_moisture = np.clip(self.soil_moisture, 15, 85)

        # ===== IMPROVED REWARD SHAPING (Optimized for Fast Convergence) =====
        target_mid = (self.target_low + self.target_high) / 2
        distance = abs(self.soil_moisture - target_mid)
        
        # Base reward: smooth quadratic penalty for distance
        reward = 1.0 - 0.01 * (distance ** 2)
        
        # Gentle irrigation penalty (only excessive)
        if irrigation > 50:
            reward -= 0.0005 * (irrigation - 50)
        
        # Bonus for being in target band (strong signal for convergence)
        if self.target_low <= self.soil_moisture <= self.target_high:
            reward += 0.4  # Increased from 0.3 for faster convergence
            
            # Efficiency bonus only if in band
            if irrigation < 20:
                reward += 0.15  # Increased from 0.1
        else:
            # Penalty for being outside band
            reward -= 0.15 * distance  # Increased from 0.1

        self.index += 1
        self.steps_in_episode += 1
        
        # Episode ends after episode_length steps OR at end of dataset
        done = (self.steps_in_episode >= self.episode_length) or (self.index >= len(self.dataset) - 1)
        obs = self._get_obs() if not done else np.zeros(5)

        return obs, reward, done, {}

# ============================
# Load LSTM model and dataset
# ============================
print("Loading LSTM model...")
lstm_model = torch.load("../backend/models/soil_forecast_model.pt", weights_only=False)
lstm_model.eval()

print("Loading dataset...")
df = pd.read_csv("../backend/data/sensor_readings.csv")

# ============================
# Fast Curriculum Learning: 2 Stages (Hackathon Speed)
# ============================
print("\n" + "="*60)
print("FAST CURRICULUM LEARNING (HACKATHON MODE)")
print("="*60)

stages = [
    {"name": "Stage 1: Wide Band (30-70%)", "curriculum": 0, "timesteps": 75000},
    {"name": "Stage 2: Tight Band (40-60%)", "curriculum": 2, "timesteps": 75000}
]

model = None

for stage in stages:
    print(f"\n{stage['name']}")
    print(f"Training for {stage['timesteps']} timesteps...")
    
    # Create environment with curriculum stage
    env = IrrigationEnv(
        df, 
        lstm_model, 
        episode_length=400,  # Shorter episodes for faster feedback
        curriculum_stage=stage['curriculum']
    )
    
    if model is None:
        # First stage: create new model with aggressive hyperparameters
        model = PPO(
            "MlpPolicy",
            env,
            verbose=1,
            learning_rate=2e-3,  # Higher LR for faster convergence
            n_steps=256,  # More frequent updates
            batch_size=32,  # Smaller batches for faster updates
            n_epochs=15,  # More passes per rollout
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.2,
            ent_coef=0.02,  # Higher entropy for more exploration
            vf_coef=0.5,
            max_grad_norm=0.5
        )
    else:
        # Subsequent stages: continue training with same model
        model.set_env(env)
    
    # Train this stage
    model.learn(total_timesteps=stage['timesteps'])
    
    print(f"✓ {stage['name']} complete")

print("\n" + "="*60)
print("FAST CURRICULUM LEARNING COMPLETE")
print("="*60)
print("Total training time: ~20-30 minutes")

# ============================
# Save model to correct location
# ============================
os.makedirs("../backend/models", exist_ok=True)
model.save("../backend/models/proactive_irrigation_policy")
print("\n✓ Model saved to ../backend/models/proactive_irrigation_policy.zip")