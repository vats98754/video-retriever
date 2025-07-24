#!/bin/bash

# Production startup script for Video Retriever
echo "🚀 Starting Video Retriever in Production Mode..."

# Set production environment
export PRODUCTION=1
export PYTHONUNBUFFERED=1

# Create data directory
mkdir -p data

# Get port from environment or default to 5000
PORT=${PORT:-5000}
HOST=${HOST:-0.0.0.0}

echo "🌐 Starting server on $HOST:$PORT"

# Use gunicorn for production deployment
if command -v gunicorn &> /dev/null; then
    echo "🔧 Using Gunicorn for production server..."
    exec gunicorn --worker-class eventlet \
                  --workers 1 \
                  --bind $HOST:$PORT \
                  --timeout 300 \
                  --keep-alive 2 \
                  --max-requests 1000 \
                  --max-requests-jitter 50 \
                  --log-level info \
                  app:app
else
    echo "🔧 Using Flask development server..."
    exec python app.py --host $HOST --port $PORT --no-debug
fi
