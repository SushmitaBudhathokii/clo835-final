# Use an official Python base image for smaller size & less setup hassle
FROM python:3.9-slim

# Set working directory inside container
WORKDIR /app

# Install required system packages for MySQL client and ping
RUN apt-get update -y && \
    apt-get install -y default-mysql-client iputils-ping && \
    rm -rf /var/lib/apt/lists/*

# Copy application code
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Expose port 81 (per CLO835 require
EXPOSE 81

# Environment variable for background image URL (will be overridden by ConfigMap in K8s)
ENV BG_IMAGE_URL=/static/background.jpg

# Run Flask app
CMD ["python", "app.py"]