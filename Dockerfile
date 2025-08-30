# Use a lightweight Python base image
FROM python:3.13-slim

# Install system dependencies (only tesseract-ocr)
RUN apt-get update && \
    apt-get install -y tesseract-ocr && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port
EXPOSE 5000

# Run the app using Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
