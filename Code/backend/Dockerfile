# Dockerfile for FastAPI Backend - Railway Deployment
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY alerts.py .
COPY aws_integration.py .
COPY error_handling.py .
COPY generate_models_runtime.py .
COPY llm_explainer.py .
COPY llm_explainer_improved.py .
COPY lstm_model.py .
COPY model_architecture.py .
COPY model_management.py .
COPY models_schema.py .
COPY notifications.py .
COPY rl_model.py .
COPY rule_based_irrigation.py .
COPY storage.py .
COPY synthetic_forecast.py .
COPY translation_tts.py .
COPY weather_ingestion.py .
COPY data/ ./data/


# Create data and models directories
RUN mkdir -p data models

# Copy model files if they exist
#COPY models/ ./models/ 2>/dev/null || true
# Expose port
EXPOSE 8000

# Run the application
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}
