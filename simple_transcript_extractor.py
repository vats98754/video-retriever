import os
import subprocess
import json
from pathlib import Path
import whisper
from datetime import timedelta

class SimpleTranscriptExtractor:
    def __init__(self, model_size="base"):
        """Initialize with Whisper model"""
        print(f"Loading Whisper model: {model_size}")
        self.whisper_model = whisper.load_model(model_size)
        print("✅ Whisper model loaded")
    
    def get_video_metadata(self, youtube_url):
        """Extract video metadata using yt-dlp"""
        try:
            result = subprocess.run([
                'yt-dlp', '--print', 'title', '--print', 'uploader', youtube_url
            ], capture_output=True, text=True, check=True)
            
            lines = result.stdout.strip().split('\n')
            return {
                'title': lines[0] if lines else '',
                'uploader': lines[1] if len(lines) > 1 else ''
            }
        except subprocess.CalledProcessError:
            return {'title': '', 'uploader': ''}
    
    def format_timestamp(self, seconds):
        """Convert seconds to HH:MM:SS format"""
        return str(timedelta(seconds=int(seconds)))
    
    def format_srt_timestamp(self, seconds):
        """Format timestamp for SRT files"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def transcribe_audio(self, audio_path):
        """Transcribe audio using Whisper"""
        print("🎙️  Transcribing audio...")
        result = self.whisper_model.transcribe(audio_path, verbose=False)
        print(f"✅ Found {len(result['segments'])} segments")
        return result
    
    def assign_speakers(self, segments):
        """Assign speakers based on conversational patterns"""
        current_speaker = 0
        switch_words = ["so", "well", "yeah", "now", "but", "and", "actually"]
        
        for i, segment in enumerate(segments):
            text = segment['text'].lower().strip()
            
            # Switch speaker on conversational cues
            if i > 0 and any(text.startswith(word) for word in switch_words):
                current_speaker = (current_speaker + 1) % 2
            
            segment['speaker'] = f"Speaker {current_speaker + 1}"
        
        return segments
    
    def save_transcript(self, segments, video_id, metadata):
        """Save transcript in multiple formats in organized structure"""
        transcript_folder = f"data/{video_id}/transcripts"
        os.makedirs(transcript_folder, exist_ok=True)
        
        # JSON format
        json_path = f"{transcript_folder}/{video_id}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                "metadata": metadata,
                "segments": segments,
                "total_duration": segments[-1]["end"] if segments else 0
            }, f, indent=2, ensure_ascii=False)
        
        # Text format
        txt_path = f"{transcript_folder}/{video_id}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"Video: {metadata.get('title', 'Unknown')}\n")
            f.write(f"Uploader: {metadata.get('uploader', 'Unknown')}\n")
            f.write("=" * 60 + "\n\n")
            
            for segment in segments:
                timestamp = self.format_timestamp(segment["start"])
                speaker = segment.get('speaker', 'Speaker 1')
                text = segment['text'].strip()
                f.write(f"[{timestamp}] {speaker}: {text}\n")
        
        # SRT format
        srt_path = f"{transcript_folder}/{video_id}.srt"
        with open(srt_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments, 1):
                start_time = self.format_srt_timestamp(segment["start"])
                end_time = self.format_srt_timestamp(segment["end"])
                speaker = segment.get('speaker', 'Speaker 1')
                text = segment['text'].strip()
                
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{speaker}: {text}\n\n")
        
        return [json_path, txt_path, srt_path]
    
    def extract_transcript(self, audio_path, youtube_url=None, video_id=None):
        """Extract transcript with speaker labels"""
        print(f"🎵 Processing: {audio_path}")
        
        # Extract video_id from audio path if not provided
        if video_id is None:
            video_id = Path(audio_path).stem
        
        # Get metadata
        metadata = {}
        if youtube_url:
            metadata = self.get_video_metadata(youtube_url)
            print(f"📺 {metadata.get('title', 'Unknown')}")
        
        # Transcribe and assign speakers
        result = self.transcribe_audio(audio_path)
        segments = self.assign_speakers(result["segments"])
        
        # Save files
        output_files = self.save_transcript(segments, video_id, metadata)
        
        print(f"✅ Generated {len(output_files)} files")
        return segments, output_files
