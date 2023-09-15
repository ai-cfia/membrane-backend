# Use the official Python 3.11 image as the base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the contents of the current directory into the container at /app
COPY . .

# Install project dependencies from the requirements.txt file
RUN pip install --no-cache-dir -r requirements-production.txt

# Set environment variable for PORT
ENV PORT=5000

# Run your Flask app when the container starts
ENTRYPOINT gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 15 --forwarded-allow-ips "*" app:app
