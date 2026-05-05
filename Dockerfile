FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    gcc \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Make entrypoint script executable and fix line endings (just in case)
RUN dos2unix entrypoint.sh && chmod +x entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["sh", "-c", "python manage.py migrate --fake-initial && python manage.py collectstatic --noinput && daphne -b 0.0.0.0 -p ${PORT:-8000} rideshare_backend.asgi:application"]
