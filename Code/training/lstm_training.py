import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import os

# ============================
# Load Dataset
# ============================
df = pd.read_csv("synthetic_irrigation_data_natural.csv")

# Features (inputs) - match backend expectations: temperature, humidity, wind, rain, soil_moisture, forecast_rain_6h
# NOTE: Do NOT include "irrigation" in features
features = ["temperature", "humidity", "wind", "rain", "soil_moisture", "forecast_rain_6h"]
target = "soil_moisture"

data = df[features].values

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
X, y = create_sequences(data_scaled, SEQ_LEN)

# Train-validation-test split
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, shuffle=False)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, shuffle=False)

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
class SoilMoistureLSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers=2):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])  # last hidden state
        return out

model = SoilMoistureLSTM(input_size=len(features), hidden_size=64)

# Loss + Optimizer
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# ============================
# Training Loop with Validation
# ============================
EPOCHS = 100
best_val_loss = float('inf')
patience = 10
patience_counter = 0

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
        print(f"Epoch {epoch}, Train Loss: {loss.item():.6f}, Val Loss: {val_loss.item():.6f}")

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
os.makedirs("Code/backend/models", exist_ok=True)
torch.save(model, "Code/backend/models/soil_forecast_model.pt")
print("Model saved to Code/backend/models/soil_forecast_model.pt")

# ============================
# Evaluation
# ============================
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
for i in range(5):
    print(f"Predicted: {test_preds_rescaled[i]:.2f}%, Actual: {y_test_rescaled[i]:.2f}%")

print(f"\nTest RMSE: {np.sqrt(np.mean((test_preds_rescaled - y_test_rescaled)**2)):.4f}%")