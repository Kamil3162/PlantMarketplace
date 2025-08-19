FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY inventory/requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY microservices_provider /app/microservices_provider
RUN pip install -e /app/microservices_provider

COPY aws /app/aws
RUN pip install -e /app/aws

COPY inventory/ /app/

RUN mkdir -p /app/logs