# Use the official Python 3.10 image as the base image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy the contents of the current directory into the container at /app
COPY . /app

# Install project dependencies from the requirements.txt file
RUN pip install -r requirements.txt

# Expose the port on which your Flask app will run
EXPOSE 5000

# Run your Flask app when the container starts
CMD ["python", "app.py"]
