# Dockerfile
FROM python:3.12-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y \
  libpq-dev gcc curl && \
  rm -rf /var/lib/apt/lists/*

WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .