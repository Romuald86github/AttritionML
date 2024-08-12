# Stage 1: Build the Flask application
FROM python:3.9-slim as build

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY src/app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app code
COPY src/app/ /app/

# Stage 2: Set up Nginx with the Flask app
FROM nginx:latest

# Install Gunicorn
RUN apt-get update && apt-get install -y python3-pip
RUN pip3 install gunicorn

# Copy the Nginx configuration file
COPY nginx.conf /etc/nginx/nginx.conf

# Copy the Flask app code from the build stage
COPY --from=build /app /app

# Expose the port for Nginx
EXPOSE 80

# Start Gunicorn and Nginx using a supervisor-like approach
CMD ["sh", "-c", "/usr/local/bin/gunicorn --bind 0.0.0.0:5010 application:app & nginx -g 'daemon off;'"]