#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "⏳ Waiting for MySQL database to be ready..."

# Use a simple python script to check if the database port is open
while ! python -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(1); s.connect(('db', 3306)); s.close()" 2>/dev/null; do
  echo "Database is unavailable - sleeping"
  sleep 2
done

echo "✅ MySQL database is up and running!"

echo "📦 Running makemigrations..."
python manage.py makemigrations

echo "📦 Running migrations..."
python manage.py migrate

echo "🚀 Starting Django development server..."
exec "$@"
