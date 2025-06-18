# Dockerfile for FastAPI application

FROM python:3.11-slim

# Create working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Default development command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]