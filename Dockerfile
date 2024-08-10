# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY scr/app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app code
COPY src/app/application.py /app/

# Copy the static and template files
COPY src/app/static /app/static
COPY src/app/templates /app/templates

# Build the Flask app
RUN pip install gunicorn

# Nginx configuration
FROM nginx:latest

# Copy the Nginx configuration file
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the Flask app code
COPY --from=0 /app /app

# Expose the port for Nginx
EXPOSE 80

# Start Nginx and Gunicorn
CMD ["nginx", "-g", "daemon off;"] & \
    gunicorn --bind 0.0.0.0:5010 application:app

