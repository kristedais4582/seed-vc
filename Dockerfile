FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source files
COPY . .

# Set environment variables
ENV PORT=8080
ENV HF_HUB_CACHE=/app/checkpoints/hf_cache

# Expose port for Gradio/Cloud Run
EXPOSE 8080

# Start the Gradio app on the correct port
CMD ["python", "app_vc.py", "--share", "False"]
