# Dockerfile
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy requirements file
COPY gateway/req.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj microservices_provider z root
COPY microservices_provider /app/microservices_provider
RUN pip install -e /app/microservices_provider

# Copy project
COPY gateway/ /app/

# Expose the correct port
EXPOSE 8010

# Run on port 8010
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8010", "--reload"]