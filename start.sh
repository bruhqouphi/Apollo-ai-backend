#!/usr/bin/env bash
# Production startup script for Render.com

# Exit on error
set -o errexit

echo "Starting Apollo AI Backend..."

# Create necessary directories if they don't exist
mkdir -p uploads exports static logs

# Set proper permissions
chmod 755 uploads exports static logs

# Start the application with Gunicorn
exec gunicorn app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:${PORT:-8000} \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --timeout 120 \
    --keepalive 2 \
    --max-requests 1000 \
    --max-requests-jitter 50
