# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Create a virtual environment and set environment variables
RUN python -m venv /app/venv
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy the requirements file and install dependencies
COPY src/app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app code and other necessary files
COPY src/app/application.py /app/
COPY src/app/static /app/static
COPY src/app/templates /app/templates

# Expose the port for Gunicorn
EXPOSE 5010

# Start Gunicorn with specified number of workers and port
CMD ["gunicorn", "application:app", "-b", "0.0.0.0:5010", "-w", "4"]
