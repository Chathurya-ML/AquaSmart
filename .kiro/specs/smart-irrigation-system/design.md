# Smart Irrigation System - Design Document

## System Architecture

The AI-Powered Smart Irrigation & Water Optimization System combines multiple components to deliver intelligent irrigation recommendations:

### Core Components

1. **Data Ingestion Layer**
   - Soil moisture sensors (via IoT devices)
   - Weather data integration (external APIs)
   - Data validation and preprocessing

2. **ML Prediction Layer**
   - LSTM model for soil moisture forecasting
   - Crop water requirement estimation
   - Stress probability computation

3. **Decision Engine**
   - Rule-based FAO-56 irrigation logic
   - Weather-aware decision optimization
   - Threshold-based irrigation triggers

4. **Notification Layer**
   - SMS/WhatsApp alerts via Twilio
   - Real-time weather risk alerts
   - Multilingual message generation

5. **Frontend Dashboard**
   - Streamlit-based UI
   - Real-time soil and weather insights
   - AI-generated explanations
   - Language selection and voice I/O

6. **Backend API**
   - FastAPI for REST endpoints
   - Model inference and decision generation
   - Data storage and retrieval

## Key Algorithms

### FAO-56 Irrigation Logic
- **Field Capacity**: 30%
- **Management Allowed Depletion (MAD)**: 40%
- **Irrigation Threshold**: 24% (Field Capacity - MAD)
- **Decision**: Irrigate when soil moisture < 24%

### LSTM Forecasting
- Predicts soil moisture trends 7 days ahead
- Trained on historical sensor data
- Normalized input/output for stability

### LLM Explanation Layer
- Converts technical metrics to farmer-friendly language
- Provides context-aware recommendations
- Supports multiple languages

## Data Flow

```
Sensors → Data Ingestion → LSTM Forecast → Rule-Based Decision → Alerts
                                                    ↓
                                            LLM Explanation
                                                    ↓
                                            Dashboard Display
```

## Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit
- **ML Models**: PyTorch (LSTM), Scikit-learn
- **Notifications**: Twilio
- **LLM**: Groq API (llama-3.3-70b-versatile)
- **Deployment**: Docker, Docker Compose
- **Cloud**: AWS (optional)

## Performance Targets

- Irrigation decision generation: < 10 seconds
- Alert delivery: < 60 seconds
- System uptime: ≥ 95%
- Model inference latency: < 1 second

## Security Considerations

- API authentication and authorization
- Data encryption at rest and in transit
- Role-based access control
- Secure credential management via .env
