# Base image with Python 3.12
FROM python:3.12

# Add a non-root user for better security
RUN useradd -m flaskuser

# Install MySQL client using the default-mysql-client package
RUN apt-get update && apt-get install -y default-mysql-client && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt /app/requirements.txt

# Install dependencies from the requirements file
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the entire application code to the container
COPY . /app

# Set the PYTHONPATH to include /app
ENV PYTHONPATH=/app

# Set appropriate permissions for the app directory
RUN chown -R flaskuser:flaskuser /app

# Switch to the non-root user
USER flaskuser

# Expose the Flask app's port
EXPOSE 5001

# Command to run the Flask application
ENTRYPOINT ["python3", "app.py"]
