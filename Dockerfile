FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source files
COPY . .

# Create directories for models and cache
RUN mkdir -p /app/checkpoints/hf_cache

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV HF_HUB_CACHE=/app/checkpoints/hf_cache
ENV GRADIO_SERVER_NAME=0.0.0.0

# Expose port for Cloud Run (dynamic port binding)
EXPOSE $PORT

# Start the Gradio app
# Note: Cloud Run will inject PORT environment variable
CMD ["python", "app_vc.py"]
