FROM python:3.8-slim

WORKDIR /app

# install git, ssh, curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    openssh-client \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# install docker compose
RUN curl -SL "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-linux-x86_64" \
    -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose

COPY Builder.py /app/

ENTRYPOINT ["python3", "Builder.py"]