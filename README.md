# YouTube Video Transcript Extractor & Semantic Search

**End-to-end YouTube video processing with timestamped semantic search.**

## 🚀 Quick Start

**One command to get timestamped YouTube URLs:**

```bash
# Install dependencies
pip install -r requirements.txt

# Search any YouTube video - everything is handled automatically!
python video_retriever.py "https://youtu.be/VIDEO_ID" "your search query"

# Or use just the video ID
python video_retriever.py "VIDEO_ID" "your search query"
```

## ✨ Features

- **🎯 Complete End-to-End Pipeline**: URL/ID + Query → Timestamped YouTube URLs
- **⚡ Smart File Management**: Automatically reuses existing audio/transcripts
- **🧠 TF-IDF Semantic Search**: Fast, local search with no external dependencies
- **📁 Organized Storage**: All files stored in `data/VIDEO_ID/` structure
- **🔗 Direct YouTube Links**: Results include clickable `https://youtu.be/ID?t=123s` URLs

## 🎬 How It Works

1. **Input**: YouTube URL or video ID + search query
2. **Auto-Check**: Uses existing files if available (no re-downloading)
3. **Download**: Audio via yt-dlp (if needed)
4. **Transcribe**: Audio to text via Whisper (if needed)  
5. **Search**: TF-IDF semantic search with smart chunking
## 📋 Examples

```bash
# Search for interview tips
python video_retriever.py "https://youtu.be/0siE31sqz0Q" "interview preparation"

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
- OpenAI Whisper (transcription)
- scikit-learn (TF-IDF search)

## 💡 Tips

- **Reuse Files**: The system automatically detects and reuses existing audio/transcripts
- **Chunk Size**: Use smaller chunks (3-4) for precise search, larger (8-10) for context
- **Model Size**: Use `base` for speed, `large` for accuracy
- **Query Tips**: Use descriptive phrases rather than single keywords

- `yt-dlp` - YouTube downloading
- `openai-whisper` - Speech transcription
- `scikit-learn` - TF-IDF vectorization
- `numpy` - Numerical operations
