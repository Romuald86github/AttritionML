# Stage 1: Build the Flask application
FROM python:3.9-slim as build

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY src/app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app code
COPY src/app/ /app/

# Install Gunicorn
RUN pip install gunicorn

# Stage 2: Set up Nginx with the Flask app
FROM nginx:latest

# Copy the Nginx configuration file
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the Flask app code from the build stage
COPY --from=build /app /app

# Expose the port for Nginx
EXPOSE 80

# Start Nginx and Gunicorn
CMD ["sh", "-c", "nginx -g 'daemon off;' && gunicorn --bind 0.0.0.0:5010 application:app"]
