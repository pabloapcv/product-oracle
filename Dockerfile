FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set Python path
ENV PYTHONPATH=/app

# Create directories for outputs
RUN mkdir -p /app/reports /app/models /app/logs

# Default command (can be overridden)
CMD ["python", "-m", "src.pipeline", "--week_start", "$(date +%Y-%m-%d)"]

