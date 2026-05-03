FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Cloud Run uses PORT env variable (default 8080)
ENV PORT=8080
ENV ENVIRONMENT=production
EXPOSE 8080

# Run with uvicorn — Cloud Run injects $PORT
CMD exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 2
