# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for OpenCV and FER
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
# We use requirements.txt which includes the full ML libraries
RUN pip install --no-cache-dir -r requirements.txt

# Create an empty emotions.db if it doesn't exist
RUN touch emotions.db

# Make port 5000 available to the world outside this container
EXPOSE 7860

# Define environment variable
ENV FLASK_APP=app.py
ENV PORT=7860

# Run app.py with gunicorn when the container launches
# Hugging Face usually expects the app to run on port 7860
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app:app"]
