# Root Dockerfile for Railway - Runs both backend and frontend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
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

# Expose both ports
EXPOSE 8000 8501

# Run both services
CMD ["sh", "-c", "cd /app/backend && uvicorn app:app --host 0.0.0.0 --port $PORT & cd /app/frontend && streamlit run dashboard.py --server.address=0.0.0.0 --server.port=8501 --server.headless=true"]

