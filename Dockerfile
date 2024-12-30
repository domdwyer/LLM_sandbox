FROM python:3.8-slim

# Prevent Python from writing .pyc files; turn off buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install ffmpeg and other dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

# Set the working directory
WORKDIR /app

# Copy the application code
COPY . /app

# Command to run the script
ENTRYPOINT ["python", "transcribe.py"]