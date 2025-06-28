# Data Directory Structure
# 
# This directory will contain organized data for each processed video:
#
# data/
# ├── .gitkeep                    # Preserves this directory in git
# └── VIDEO_ID/                   # Created automatically for each video
#     ├── audio/                  # Downloaded MP3 files
#     ├── transcripts/            # JSON, TXT, SRT transcript files
#     ├── vectors/                # Processed chunks for search
#     └── searches/               # Search results with timestamps
#
# All content files are ignored by git but directory structure is preserved.
