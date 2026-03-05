"""
LSTM Model Architecture Definition.

This module defines the SoilMoistureLSTM class that matches the architecture
of the pre-trained model. This class must be imported before loading the model.
"""

import torch
import torch.nn as nn


class SoilMoistureLSTM(nn.Module):
    """
    LSTM neural network for soil moisture forecasting.
    
    This architecture processes time-series sensor data with 11 features
    and predicts soil moisture 6 hours ahead.
    """
    
    def __init__(self, input_size=11, hidden_size=64, num_layers=2, output_size=1):
        """
        Initialize the LSTM model.
        
        Args:
            input_size: Number of input features (default: 11)
            hidden_size: Number of hidden units in LSTM layers (default: 64)
            num_layers: Number of LSTM layers (default: 2)
            output_size: Number of output values (default: 1)
        """
        super(SoilMoistureLSTM, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # LSTM layers
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2 if num_layers > 1 else 0
        )
        
        # Fully connected output layer
        self.fc = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        """
        Forward pass through the network.
        
        Args:
            x: Input tensor of shape (batch_size, sequence_length, input_size)
        
        Returns:
            Output tensor of shape (batch_size, output_size)
        """
        # Get num_layers and hidden_size from the LSTM module
        num_layers = self.lstm.num_layers
        hidden_size = self.lstm.hidden_size
        
        # Initialize hidden state and cell state
        h0 = torch.zeros(num_layers, x.size(0), hidden_size).to(x.device)
        c0 = torch.zeros(num_layers, x.size(0), hidden_size).to(x.device)
        
        # Forward propagate LSTM
        out, _ = self.lstm(x, (h0, c0))
        
        # Get the output from the last time step
        out = out[:, -1, :]
        
        # Pass through fully connected layer
        out = self.fc(out)
        
        return out
