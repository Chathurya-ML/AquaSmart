# Dockerfile for Streamlit Frontend - Railway Deployment
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY dashboard.py .
COPY pages/ ./pages/

# Create .streamlit config directory
RUN mkdir -p .streamlit

# Streamlit config for Railway
RUN echo "[server]\nheadless = true\nenableXsrfProtection = false\n[client]\nshowErrorDetails = true" > .streamlit/config.toml

# Expose port
EXPOSE 8501

# Run Streamlit on Railway's PORT
CMD ["streamlit", "run", "dashboard.py", "--server.address=0.0.0.0", "--server.port=${PORT:-8501}"]
