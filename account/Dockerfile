FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Skopiuj requirements z account/
COPY account/requirements/base.txt .
RUN pip install --upgrade pip && \
    pip install -r base.txt

# Skopiuj microservices_provider z root
COPY microservices_provider /app/microservices_provider
RUN pip install -e /app/microservices_provider

# Skopiuj tylko kod account (nie wszystkie foldery)
COPY account/ /app/

RUN mkdir -p /app/logs