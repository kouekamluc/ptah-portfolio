# Multi-stage Dockerfile for Ptah Kouekam's Engineering & Software Portfolio
FROM python:3.13-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=portfolio_site.settings.production \
    PORT=8000

WORKDIR /app

# Install system dependencies (for Pillow and PostgreSQL client)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . /app/

# Collect static files for WhiteNoise
RUN python manage.py collectstatic --noinput

# Expose server port
EXPOSE 8000

# Start Gunicorn WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60", "portfolio_site.wsgi:application"]
