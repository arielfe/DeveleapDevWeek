FROM python:3.10-alpine

# Set the working directory in the container
WORKDIR /app

# Install flask and docker

RUN pip install flask && apk add docker

# Copy the rest of the application code
COPY listenok.py /app/

# Command to run the Flask app
ENTRYPOINT ["python", "listenok.py"]

