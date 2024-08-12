FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY src/app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Gunicorn
RUN pip install gunicorn

# Copy the Flask app code
COPY src/app/ /app/

# Copy the Nginx configuration file
COPY nginx.conf /etc/nginx/nginx.conf

# Expose the port for Nginx
EXPOSE 80

# Start Gunicorn and Nginx using a supervisor-like approach
CMD ["sh", "-c", "/usr/local/bin/gunicorn --bind 0.0.0.0:5010 application:app & nginx -g 'daemon off;'"]