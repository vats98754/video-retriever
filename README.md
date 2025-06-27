# YouTube Video Transcript Extractor

Downloads audio from YouTube videos and extracts transcripts with speaker labels.

## Features

- Fast audio download using `yt-dlp`
- Accurate transcription with OpenAI Whisper
- Automatic speaker detection (Speaker 1, Speaker 2)
- Multiple output formats (JSON, TXT, SRT)
- Streamlined processing pipeline

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Process a video
python process_video.py https://youtu.be/VIDEO_ID
```

## Usage

**Complete workflow:**
```bash
python process_video.py https://youtu.be/AUUZuzVHKdo
```

**Individual components:**
```bash
# Download audio only
python download_audio.py

# Extract transcript from audio
python simple_transcript_extractor.py audio/file.mp3 --youtube-url https://youtu.be/VIDEO_ID
```

## Output

Generates three files in `transcripts/` directory using YouTube video ID:
- `VIDEO_ID.json` - Machine-readable with metadata
- `VIDEO_ID.txt` - Human-readable with timestamps
- `VIDEO_ID.srt` - Standard subtitle format

Example output:
```
[0:00:00] Speaker 1: What are the tools that we can put in the hands of people
[0:00:04] Speaker 1: that will give them that sense of empowerment?
```

## Configuration

Choose Whisper model size for speed vs accuracy:
```bash
python simple_transcript_extractor.py audio.mp3 --model tiny    # Fast
python simple_transcript_extractor.py audio.mp3 --model base    # Default
python simple_transcript_extractor.py audio.mp3 --model large   # Accurate
```

## Dependencies

- `yt-dlp` - YouTube downloading
- `openai-whisper` - Speech transcription
- `torch` - PyTorch for Whisper

## File Structure

```
video-retriever/
├── download_audio.py           # Audio download
├── simple_transcript_extractor.py  # Transcript extraction
├── process_video.py           # Complete pipeline
├── requirements.txt           # Dependencies
├── README.md                  # Documentation
├── audio/                     # Downloaded audio files
│   └── VIDEO_ID.mp3
└── transcripts/              # Generated transcripts
    ├── VIDEO_ID.json
    ├── VIDEO_ID.txt
    └── VIDEO_ID.srt
```
