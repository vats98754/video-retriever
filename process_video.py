import sys
import os
from download_audio import download_audio, get_youtube_id
from simple_transcript_extractor import SimpleTranscriptExtractor

def process_youtube_video(youtube_url):
    """Download audio and extract transcript from YouTube video"""
    
    print(f"Processing YouTube video: {youtube_url}")
    print("=" * 60)
    
    # Step 1: Download audio using yt-dlp
    print("Step 1: Downloading audio...")
    audio_path = download_audio(youtube_url)
    
    if not audio_path or not os.path.exists(audio_path):
        print("Failed to download audio")
        return None
    
    print(f"Audio downloaded successfully: {audio_path}")
    
    # Step 2: Extract transcript and align with speakers (i.e. speaker diarization)
    print("\nStep 2: Extracting transcript with speaker diarization...")
    try:
        extractor = SimpleTranscriptExtractor()
        segments, output_files = extractor.extract_transcript(audio_path, youtube_url)
        
        print("Transcript extracted successfully!")
        print(f"Generated {len(segments)} transcript segments")
        print(f"Output files: {', '.join(output_files)}")
        
        return {
            'audio_path': audio_path,
            'segments': segments,
            'output_files': output_files
        }
        
    except Exception as e:
        print(f"Error extracting transcript: {e}")
        print("You may need to install additional dependencies or set up authentication")
        return None

def main():
    """Main entry point"""
    if len(sys.argv) != 2:
        print("Usage: python process_video.py <youtube_url>")
        print("Example: python process_video.py https://youtu.be/AUUZuzVHKdo")
        sys.exit(1)
    
    youtube_url = sys.argv[1]
    result = process_youtube_video(youtube_url)
    
    if result:
        print("Processing completed successfully!")
        print(f"Summary:")
        print(f"- Audio file: {result['audio_path']}")
        print(f"- Transcript segments: {len(result['segments'])}")
        print(f"- Output files: {len(result['output_files'])}")
    else:
        print("Processing failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
