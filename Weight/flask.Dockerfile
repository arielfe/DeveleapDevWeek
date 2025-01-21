FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y netcat-traditional && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY app/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ .

# Set environment variables
ENV FLASK_APP=app.py
ENV DB_HOST=mysql_weight
ENV DB_USER=nati
ENV DB_PASSWORD=bashisthebest
ENV DB_NAME=weight
ENV DB_PORT=3306
ENV FLASK_DEBUG=1

# Create input directory
RUN mkdir -p /app/in

# Entrypoint script to wait for MySQL and start the application
CMD bash -c "echo 'Waiting for MySQL...' && \
    while ! nc -z mysql_weight 3306; do \
        echo 'MySQL not ready - sleeping 5s' && \
        sleep 5; \
    done && \
    echo 'MySQL is up - starting app' && \
    flask run --host=0.0.0.0 --port=5000 --reload"