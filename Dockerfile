# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Copy existing vectorstore to volume location with correct structure
RUN mkdir -p /app/vectorstore/credit_risk_management_guidebook && \
    cp -r credit_risk_management_guidebook_vectorstore/* /app/vectorstore/credit_risk_management_guidebook/ 2>/dev/null || true

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "backend.py"]