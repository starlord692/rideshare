#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "⏳ Waiting for MySQL database to be ready..."

# Use a simple python script to check if the database port is open
# Railway provides MYSQLHOST, MYSQLPORT etc.
DB_HOST=${MYSQLHOST:-db}
DB_PORT=${MYSQLPORT:-3306}

while ! python -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(1); s.connect(('$DB_HOST', $DB_PORT)); s.close()" 2>/dev/null; do
  echo "Database ($DB_HOST:$DB_PORT) is unavailable - sleeping"
  sleep 2
done

echo "✅ MySQL database is up and running!"

echo "📦 Running migrations..."
python manage.py migrate --noinput

echo "📂 Collecting static files..."
python manage.py collectstatic --noinput

echo "🚀 Starting application..."
exec "$@"
