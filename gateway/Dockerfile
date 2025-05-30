# Dockerfile
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy requirements file
COPY req.txt .
RUN pip install --no-cache-dir -r req.txt

# Copy project
COPY . .

# Expose the correct port
EXPOSE 8010

# Run on port 8010
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8010", "--reload"]