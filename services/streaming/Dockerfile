# ══════════════════════════════════════════════════════════════
# STREAMING SERVICE - Dockerfile
# ══════════════════════════════════════════════════════════════

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py .
COPY routes/ ./routes/

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
