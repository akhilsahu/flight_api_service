# Use a stable Python base
FROM python:3.11-slim

# Install system dependencies
# We removed libgconf-2-4 and added chromium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    libglib2.0-0 \
    libnss3 \
    libfontconfig1 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    python3-tk \
    python3-dev \
    xvfb \
    chromium \
    chromium-driver \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Tell SeleniumBase to use the system-installed Chromium
ENV SB_CHROME_BINARY=/usr/bin/chromium
ENV SB_CHROMEDRIVER_BINARY=/usr/bin/chromedriver

# Copy the rest of your code
COPY . .

ENV PYTHONUNBUFFERED=1