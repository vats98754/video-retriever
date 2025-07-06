#!/bin/bash

# Video Retriever Web Interface Launcher
# Usage: ./start_web.sh [options]
# Options:
#   --host HOST                  Host to bind to (default: 0.0.0.0)
#   --port PORT                  Port to bind to (default: 5000)
#   --debug                      Enable debug mode (default: enabled)
#   --no-debug                   Disable debug mode
#   --model MODEL                Default Whisper model (default: base)
#   --similarity-threshold NUM   Default similarity threshold 0.0-1.0 (default: 0.1)
#   --min-results NUM            Default minimum results per video (default: 1)
#   --secret-key KEY             Flask secret key (optional)
#   --help, -h                   Show help and exit

# Function to show usage
show_usage() {
    echo "🚀 Video Retriever Web Interface Launcher"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Server Options:"
    echo "  --host HOST                  Host to bind to (default: 0.0.0.0)"
    echo "  --port PORT                  Port to bind to (default: 5000)"
    echo "  --debug                      Enable debug mode (default: enabled)"
    echo "  --no-debug                   Disable debug mode"
    echo "  --secret-key KEY             Flask secret key (optional)"
    echo ""
    echo "Default Search Options:"
    echo "  --model MODEL                Default Whisper model (default: base)"
    echo "                               Options: tiny, base, small, medium, large"
    echo "  --similarity-threshold NUM   Default similarity threshold 0.0-1.0 (default: 0.1)"
    echo "  --min-results NUM            Default minimum results per video (default: 1)"
    echo ""
    echo "Other Options:"
    echo "  --help, -h                   Show this help and exit"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Start with default settings"
    echo "  $0 --port 8080                       # Start on port 8080"
    echo "  $0 --host localhost --no-debug       # Start on localhost only, no debug"
    echo "  $0 --model small --min-results 3     # Use small model, min 3 results"
    echo ""
}

# Check for help flag
for arg in "$@"; do
    if [[ "$arg" == "--help" ]] || [[ "$arg" == "-h" ]]; then
        show_usage
        exit 0
    fi
done

echo "🚀 Starting Video Retriever Web Interface..."

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade requirements
echo "📋 Installing requirements..."
pip install -r requirements.txt

# Check if yt-dlp is installed
if ! command -v yt-dlp &> /dev/null; then
    echo "⚠️  Warning: yt-dlp not found in PATH. Installing via pip..."
    pip install yt-dlp
fi

echo "🌐 Starting web server..."
echo "📱 Open your browser to: http://localhost:5000"
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

# Extract port from arguments if provided for the browser message
PORT=5000
HOST="0.0.0.0"

# Parse arguments to extract port and host for display
i=1
while [ $i -le $# ]; do
    case "${!i}" in
        --port)
            ((i++))
            PORT="${!i}"
            ;;
        --port=*)
            PORT="${!i#*=}"
            ;;
        --host)
            ((i++))
            HOST="${!i}"
            ;;
        --host=*)
            HOST="${!i#*=}"
            ;;
    esac
    ((i++))
done

# Update browser message with actual port and host
if [[ "$HOST" == "0.0.0.0" ]]; then
    echo "📱 Open your browser to: http://localhost:$PORT"
    # Try to get network IP (macOS compatible)
    NETWORK_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')
    if [[ -n "$NETWORK_IP" ]]; then
        echo "🌍 Or access from network: http://$NETWORK_IP:$PORT"
    fi
else
    echo "📱 Open your browser to: http://$HOST:$PORT"
fi

echo ""
echo "🛠️  Starting with arguments: $@"
echo ""

# Start the Flask application with all passed arguments
python app.py "$@"
