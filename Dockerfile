# Official Python image use karein
FROM python:3.9-slim

# Server par FFmpeg install karein
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Working directory set karein
WORKDIR /app

# Requirements copy karein aur install karein
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Baki ka sara code copy karein
COPY . .

# Render ke liye port open karein
EXPOSE 10000

# API ko run karne ki command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]