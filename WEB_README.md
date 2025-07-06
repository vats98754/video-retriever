# Video Retriever Web Interface

A modern, beautiful web interface for searching across multiple YouTube videos using AI-powered transcript analysis.

## Features

- 🎥 **Multi-Video Search**: Search across multiple YouTube videos simultaneously
- ⏰ **Timestamped Results**: Get exact timestamps for relevant moments
- 🎤 **Speaker Detection**: Identify different speakers in conversations
- 📱 **Modern UI**: Beautiful, responsive interface with real-time updates
- 🔍 **Search History**: Keep track of your previous searches
- 🎯 **Relevance Scoring**: Results ranked by AI-powered relevance scores
- ⚙️ **Configurable**: Customize server settings and default search parameters

## Quick Start

### Option 1: Using the Launcher Script (Recommended)
```bash
# Basic start with default settings
./start_web.sh

# With custom options (see Configuration section below)
./start_web.sh --port 8080 --model small --similarity-threshold 0.2
```

### Option 2: Direct Python Execution
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start with default settings
python app.py

# Or with custom options
python app.py --port 8080 --model large --no-debug
```

## Configuration Options

The web interface supports various command-line options to customize both server behavior and default search parameters:

### Server Options
- `--host HOST` - Host to bind to (default: 0.0.0.0)
- `--port PORT` - Port to bind to (default: 5000) 
- `--debug` - Enable debug mode (default: enabled)
- `--no-debug` - Disable debug mode
- `--secret-key KEY` - Flask secret key (optional)

### Default Search Parameters
- `--model MODEL` - Default Whisper model: tiny, base, small, medium, large (default: base)
- `--similarity-threshold NUM` - Default similarity threshold 0.0-1.0 (default: 0.1)
- `--min-results NUM` - Default minimum results per video (default: 1)

### Examples
```bash
# Development mode on custom port
./start_web.sh --port 8080 --debug

# Production mode with high accuracy
./start_web.sh --host 127.0.0.1 --no-debug --model large --similarity-threshold 0.3

# Fast mode with smaller model
./start_web.sh --model tiny --similarity-threshold 0.05

# Network accessible server
./start_web.sh --host 0.0.0.0 --port 5000 --no-debug

# See all options
./start_web.sh --help

# View example configurations
./examples.sh
```

### Option 3: Manual Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the web server
python app.py
```

## Usage

1. **Open your browser** to `http://localhost:5000`

2. **Add YouTube videos**: 
   - Paste YouTube URLs (e.g., `https://youtu.be/dQw4w9WgXcQ`)
   - Or use video IDs directly (e.g., `dQw4w9WgXcQ`)
   - Click "Add Another Video" for multiple videos

3. **Enter your search query**:
   - Ask natural language questions
   - Examples: "machine learning tips", "interview advice", "python examples"

4. **Get timestamped results**:
   - See relevant moments with exact timestamps
   - Click "Watch at [timestamp]" to jump to that moment on YouTube
   - View speaker information and relevance scores

## How It Works

1. **Audio Extraction**: Downloads audio from YouTube videos using `yt-dlp`
2. **Transcript Generation**: 
   - First tries to fetch official YouTube captions
   - Falls back to Whisper AI transcription if needed
3. **Content Chunking**: Breaks transcripts into searchable segments
4. **AI Search**: Uses TF-IDF vectorization and cosine similarity for relevant matching
5. **Speaker Detection**: Identifies different speakers in conversations
6. **Timestamped Results**: Returns exact moments with YouTube links

## API Endpoints

### Search Videos
- **POST** `/api/search`
- **Body**: 
  ```json
  {
    "video_urls": ["https://youtu.be/VIDEO_ID"],
    "query": "your search query",
    "session_id": "optional-session-id",
    "top_k": 5
  }
  ```

### Get Session History
- **GET** `/api/session/{session_id}/history`

### Get Video Info
- **GET** `/api/video/{video_id}/info`

## Real-time Updates

The interface uses WebSocket connections for real-time progress updates:
- Video processing status
- Download and transcription progress
- Error notifications

## Data Storage

All processed data is stored in the `data/` directory:
```
data/
├── {video_id}/
│   ├── audio/
│   │   └── {video_id}.mp3
│   ├── transcripts/
│   │   ├── {video_id}.json
│   │   ├── {video_id}.txt
│   │   └── {video_id}.srt
│   ├── vectors/
│   │   └── chunks.json
│   └── searches/
│       └── {query}.json
```

## Requirements

- Python 3.8+
- `yt-dlp` for video downloading
- Whisper AI for transcription
- Flask for web interface
- Modern web browser

## Troubleshooting

### Common Issues

1. **"yt-dlp not found"**: Install with `pip install yt-dlp`
2. **Port 5000 already in use**: Change the port in `app.py`
3. **Slow transcription**: Use a smaller Whisper model (change `model="base"` to `model="tiny"`)
4. **Memory issues**: Process fewer videos at once or use `model="tiny"`

### Performance Tips

- Use official YouTube captions when available (faster than Whisper)
- Process popular videos first (more likely to have captions)
- Adjust `chunk_size` for different granularity of results
- Use smaller Whisper models for faster processing

## Advanced Configuration

Edit `app.py` to customize:
- Whisper model size: `model="base"` (options: tiny, base, small, medium, large)
- Default result count: `top_k=5`
- Server port: `port=5000`
- Host binding: `host='0.0.0.0'`
