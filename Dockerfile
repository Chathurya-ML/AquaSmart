# Root Dockerfile for Railway - Runs both backend and frontend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY Code/backend/requirements.txt ./backend_requirements.txt
RUN pip install --no-cache-dir -r backend_requirements.txt

# Copy frontend requirements and install
COPY Code/frontend/requirements.txt ./frontend_requirements.txt
RUN pip install --no-cache-dir -r frontend_requirements.txt

# Copy backend code
COPY Code/backend/ ./backend/

# Copy frontend code
COPY Code/frontend/ ./frontend/

# Create data and models directories
RUN mkdir -p backend/data backend/models

# Create supervisor config to run both services
RUN mkdir -p /etc/supervisor/conf.d

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose both ports
EXPOSE 8000 8501

# Run supervisor to manage both services
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

