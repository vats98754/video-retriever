# 🎥 Video Retriever - AI-Powered YouTube Search

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

**🌐 Live Web Application**: Deploy your own AI-powered video search engine!

## 🚀 Quick Deploy (Web Application)

### One-Click Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/vats98754/video-retriever)

**Get your app running in 2 minutes:**
1. Click the deploy button above
2. Connect your GitHub account  
3. Your app will be live at `https://your-app-name.onrender.com`

### Alternative Platforms
- **Railway**: [Deploy to Railway](https://railway.app) - Connect GitHub repo
- **Heroku**: Use the included `Procfile` for one-click deploy
- **Docker**: `docker-compose up` for local deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## ✨ Web Application Features

- 🎥 **Multi-Video Search**: Search across multiple YouTube videos simultaneously
- ⏰ **Timestamped Results**: Get exact timestamps for relevant moments  
- 🎤 **Speaker Detection**: Identify different speakers in conversations
- 📱 **Modern UI**: Beautiful, responsive interface with real-time updates
- 🔍 **Search History**: Keep track of your previous searches
- 🎯 **Similarity Scoring**: Results ranked by AI-powered relevance scores
- ⚙️ **Configurable**: Customize search parameters and models

## 💻 Local Development

```bash
# Clone and start the web interface
git clone https://github.com/vats98754/video-retriever.git
cd video-retriever

# Start web application (includes setup)
./start_web.sh

# Or start with custom options
./start_web.sh --port 8080 --model small --similarity-threshold 0.2
```

## 📱 Command Line Usage

**One command to get timestamped YouTube URLs:**

```bash
# Search any YouTube video - everything is handled automatically!
python video_retriever.py "https://youtu.be/VIDEO_ID" "your search query"

# Or use just the video ID
python video_retriever.py "VIDEO_ID" "your search query"
```

## ✨ Features

- **🎯 Complete End-to-End Pipeline**: URL/ID + Query → Timestamped YouTube URLs
- **📋 Smart Transcript Selection**: Automatically uses YouTube captions when available, falls back to Whisper
- **🌍 Multi-Language Support**: Supports transcripts in multiple languages with automatic fallback
- **⚡ Smart File Management**: Automatically reuses existing audio/transcripts
- **🧠 TF-IDF Semantic Search**: Fast, local search with no external dependencies
- **📁 Organized Storage**: All files stored in `data/VIDEO_ID/` structure
- **🔗 Direct YouTube Links**: Results include clickable `https://youtu.be/ID?t=123s` URLs

## 🎬 How It Works

1. **Input**: YouTube URL or video ID + search query
2. **Auto-Check**: Uses existing files if available (no re-downloading)
3. **Smart Transcript**: First tries YouTube captions, then falls back to Whisper if needed
4. **Download**: Audio via yt-dlp (only if no transcript available and Whisper needed)
5. **Transcribe**: Audio to text via Whisper (only if YouTube captions unavailable)  
6. **Search**: TF-IDF semantic search with smart chunking
## 📋 Examples

```bash
# Search for interview tips
python video_retriever.py "https://youtu.be/0siE31sqz0Q" "interview preparation"

# List available transcripts for a video
python video_retriever.py "0siE31sqz0Q" --list-transcripts

# Search with language preference
python video_retriever.py "VIDEO_ID" "search terms" --language es

# Get more results
python video_retriever.py "0siE31sqz0Q" "storytelling" --top-k 10

# Use different chunk size for different granularity
python video_retriever.py "VIDEO_ID" "search terms" --chunk-size 4
```

## 📁 File Organization

Everything is organized under `data/VIDEO_ID/`:

```
data/
├── README.md            # Structure documentation
├── .gitkeep            # Preserves directory in git
└── VIDEO_ID/           # Created automatically per video
    ├── audio/          # Downloaded MP3 files (git ignored)
    ├── transcripts/    # JSON, TXT, SRT transcripts (git ignored)
    ├── vectors/        # Processed chunks for search (git ignored)
    └── searches/       # Search results with timestamps (git ignored)
```

**Note**: Only the directory structure is tracked in git. All data files are automatically ignored to keep the repository clean.

## 🔧 Advanced Usage

```python
from video_retriever import VideoRetriever

# Initialize
retriever = VideoRetriever(model="base")

# End-to-end search
results = retriever.search_video(
    "https://youtu.be/VIDEO_ID", 
    "your query", 
    top_k=5
)

# Results include timestamped URLs
for result in results:
    print(f"🔗 {result['youtube_url']}")
    print(f"📝 {result['text']}")
```

## 🛠️ Requirements

- Python 3.8+
- yt-dlp (audio download)
- youtube-transcript-api (YouTube captions)
- OpenAI Whisper (fallback transcription)
- scikit-learn (TF-IDF search)

## 💡 Tips

- **YouTube Captions First**: System automatically uses YouTube's captions when available (much faster!)
- **Language Support**: Use `--language es` for Spanish, `--language fr` for French, etc.
- **Check Available Languages**: Use `--list-transcripts` to see what languages are available
- **Reuse Files**: The system automatically detects and reuses existing audio/transcripts
- **Chunk Size**: Use smaller chunks (3-4) for precise search, larger (8-10) for context
- **Model Size**: Use `base` for speed, `large` for accuracy (only used when Whisper fallback needed)
- **Query Tips**: Use descriptive phrases rather than single keywords

- `yt-dlp` - YouTube downloading
- `youtube-transcript-api` - YouTube captions extraction
- `openai-whisper` - Speech transcription (fallback)
- `scikit-learn` - TF-IDF vectorization
- `numpy` - Numerical operations
