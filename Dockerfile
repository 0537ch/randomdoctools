FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ghostscript \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PORT=5000

# Command to run the application
CMD ["python", "app.py"]
