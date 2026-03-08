# Dockerfile for FastAPI Backend - Optimized for Railway
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code only (not data or models)
COPY app.py .
COPY alerts.py .
COPY aws_integration.py .
COPY error_handling.py .
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
COPY translation_tts.py .
COPY weather_ingestion.py .

# Create data and models directories (will be mounted or created at runtime)
RUN mkdir -p data models

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Expose port
EXPOSE 8000

# Run the application with uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
