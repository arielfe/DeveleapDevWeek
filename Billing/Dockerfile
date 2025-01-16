# Base image with Python 3.12
FROM python:3.12

# Add a non-root user for better security
RUN useradd -m flaskuser

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt /app/requirements.txt

# Install dependencies from the requirements file
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the entire application code to the container
COPY . /app

# Set appropriate permissions for the app directory
RUN chown -R flaskuser:flaskuser /app

# Switch to the non-root user
USER flaskuser

# Expose the Flask app's port
EXPOSE 5000

# Set ENTRYPOINT to execute the application
ENTRYPOINT ["python3", "app.py"]
