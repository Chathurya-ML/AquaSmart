import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import os
import sys

# Add backend to path so we can import model architecture
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from model_architecture import SoilMoistureLSTM

# ============================
# Load Dataset
# ============================
print("Loading dataset...")
df = pd.read_csv("../backend/data/sensor_readings.csv")
print(f"Dataset shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")

# Features (inputs) - match backend expectations: temperature, humidity, wind, rain, soil_moisture, forecast_rain_6h
# NOTE: Do NOT include "irrigation" in features
features = ["temperature", "humidity", "wind", "rain", "soil_moisture", "forecast_rain_6h"]
target = "soil_moisture"

data = df[features].values
print(f"Data shape: {data.shape}")
print(f"Features: {features}")

# Scale data
scaler = MinMaxScaler()
data_scaled = scaler.fit_transform(data)

# ============================
# Sequence Creation
# ============================
def create_sequences(data, seq_length=24):
    xs, ys = [], []
    for i in range(len(data) - seq_length):
        x = data[i:(i+seq_length)]       # past seq_length timesteps
        y = data[i+seq_length, 4]        # soil_moisture target at next step (index 4 in features)
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)

SEQ_LEN = 24  # past 24 timesteps (~144 hours = 6 days)
print(f"Creating sequences with length {SEQ_LEN}...")
X, y = create_sequences(data_scaled, SEQ_LEN)
print(f"Sequences created: X shape {X.shape}, y shape {y.shape}")

# Train-validation-test split
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, shuffle=False)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, shuffle=False)

print(f"Train set: {X_train.shape}")
print(f"Val set: {X_val.shape}")
print(f"Test set: {X_test.shape}")

# Convert to tensors
X_train = torch.tensor(X_train, dtype=torch.float32)
y_train = torch.tensor(y_train, dtype=torch.float32)
X_val = torch.tensor(X_val, dtype=torch.float32)
y_val = torch.tensor(y_val, dtype=torch.float32)
X_test = torch.tensor(X_test, dtype=torch.float32)
y_test = torch.tensor(y_test, dtype=torch.float32)

# ============================
# LSTM Model
# ============================
print("Creating LSTM model...")
model = SoilMoistureLSTM(input_size=len(features), hidden_size=64, num_layers=2, output_size=1)
print(f"Model created with input_size={len(features)}")

# Loss + Optimizer
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# ============================
# Training Loop with Validation
# ============================
EPOCHS = 50
best_val_loss = float('inf')
patience = 10
patience_counter = 0

print(f"Starting training for {EPOCHS} epochs...")
for epoch in range(EPOCHS):
    # Training phase
    model.train()
    optimizer.zero_grad()
    output = model(X_train)
    loss = criterion(output.squeeze(), y_train)
    loss.backward()
    optimizer.step()

    # Validation phase
    model.eval()
    with torch.no_grad():
        val_output = model(X_val)
        val_loss = criterion(val_output.squeeze(), y_val)

    if epoch % 5 == 0:
        print(f"Epoch {epoch:3d}, Train Loss: {loss.item():.6f}, Val Loss: {val_loss.item():.6f}")

    # Early stopping
    if val_loss.item() < best_val_loss:
        best_val_loss = val_loss.item()
        patience_counter = 0
    else:
        patience_counter += 1
        if patience_counter >= patience:
            print(f"Early stopping at epoch {epoch}")
            break

# ============================
# Save the trained LSTM model to correct location
# ============================
os.makedirs("backend/models", exist_ok=True)
torch.save(model, "backend/models/soil_forecast_model.pt")
print("Model saved to backend/models/soil_forecast_model.pt")

# ============================
# Evaluation
# ============================
print("\nEvaluating on test set...")
model.eval()
with torch.no_grad():
    test_preds = model(X_test).squeeze().numpy()

# Inverse scale predictions - only for soil_moisture column (index 4)
soil_index = 4  # soil_moisture is at index 4 in features list
dummy_data = np.zeros((len(y_test), len(features)))
dummy_data[:, soil_index] = y_test.numpy()
y_test_rescaled = scaler.inverse_transform(dummy_data)[:, soil_index]

dummy_preds = np.zeros((len(test_preds), len(features)))
dummy_preds[:, soil_index] = test_preds
test_preds_rescaled = scaler.inverse_transform(dummy_preds)[:, soil_index]

print("\nSample predictions vs actual:")
for i in range(min(5, len(test_preds_rescaled))):
    print(f"  Predicted: {test_preds_rescaled[i]:.2f}%, Actual: {y_test_rescaled[i]:.2f}%")

rmse = np.sqrt(np.mean((test_preds_rescaled - y_test_rescaled)**2))
print(f"\nTest RMSE: {rmse:.4f}%")
print(f"Test predictions range: {test_preds_rescaled.min():.2f}% - {test_preds_rescaled.max():.2f}%")
print(f"Test actual range: {y_test_rescaled.min():.2f}% - {y_test_rescaled.max():.2f}%")
