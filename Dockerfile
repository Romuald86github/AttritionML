# Stage 1: Build the Flask application
FROM python:3.9-slim as build

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY src/app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app code
COPY src/app/ /app/

# Stage 2: Run the Flask app with Gunicorn
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the Flask app code from the build stage
COPY --from=build /app /app

# Expose the port for Gunicorn
EXPOSE 5010

# Start Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5010", "application:app"]