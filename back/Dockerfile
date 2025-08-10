FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Create directory for celery beat
RUN mkdir -p /var/run/celery

# Command to run will be provided by docker-compose
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]