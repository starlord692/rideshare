#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "⏳ Waiting for MySQL database to be ready..."

# Wait for MySQL to be ready
if [ -n "$MYSQL_URL" ]; then
  echo "🔗 Parsing MYSQL_URL..."
  # Example: mysql://user:pass@host:port/db
  # Extract host and port using python
  DB_HOST=$(python -c "from urllib.parse import urlparse; url = '$MYSQL_URL'; print(urlparse(url).hostname)")
  DB_PORT=$(python -c "from urllib.parse import urlparse; url = '$MYSQL_URL'; print(urlparse(url).port or 3306)")
else
  DB_HOST=${MYSQLHOST:-db}
  DB_PORT=${MYSQLPORT:-3306}
fi

while ! python -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(1); s.connect(('$DB_HOST', $DB_PORT)); s.close()" 2>/dev/null; do
  echo "Database ($DB_HOST:$DB_PORT) is unavailable - sleeping"
  sleep 2
done

echo "✅ MySQL database is up and running!"

exec "$@"
