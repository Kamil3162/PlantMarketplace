# products/Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/app

WORKDIR $APP_HOME

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Kopiuj base.txt z katalogu products
COPY products/requirements.txt .
RUN pip install --no-cache-dir -r base.txt

# Kopiuj cały projekt
COPY . .

# Ponieważ uruchamiamy serwer Django z katalogu products
CMD ["python", "products/product_manage.py", "runserver", "0.0.0.0:8002"]