ARG BASE_IMAGE=python:3.13-slim-bookworm

FROM $BASE_IMAGE

# system update and package install
RUN apt-get -y update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    openssl libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

# pip & poetry
RUN python3 -m pip install --user --upgrade pip && \
    python3 -m pip install -r requirements.txt

COPY . .

# Configuration
EXPOSE 8080

CMD ["python", "main.py"]
