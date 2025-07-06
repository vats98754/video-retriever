import os
import subprocess
import json
import re
from pathlib import Path
import whisper
from datetime import timedelta
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

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
    
    def fetch_youtube_transcript(self, video_id, languages=None):
        """Try to fetch transcript from YouTube API with enhanced language support"""
        try:
            print("🔍 Checking for YouTube captions...")
            ytt_api = YouTubeTranscriptApi()
            
            # Default language preference order
            if languages is None:
                languages = ['en', 'en-US', 'en-GB', 'de', 'es', 'fr', 'it', 'pt', 'ja', 'ko', 'zh', 'ru', 'ar', 'hi']
            
            # First, try to get available transcripts to show user what's available
            try:
                transcript_list = ytt_api.list(video_id)
                available_languages = [t.language_code for t in transcript_list]
                print(f"📋 Available languages: {', '.join(available_languages)}")
                
                # Prefer manually created transcripts over auto-generated ones
                for lang in languages:
                    try:
                        transcript = transcript_list.find_manually_created_transcript([lang])
                        fetched_transcript = transcript.fetch()
                        print(f"✅ Found manual YouTube transcript: {fetched_transcript.language} (manual)")
                        break
                    except NoTranscriptFound:
                        continue
                else:
                    # Fall back to auto-generated transcripts
                    fetched_transcript = ytt_api.fetch(video_id, languages=languages)
                    print(f"✅ Found YouTube transcript: {fetched_transcript.language} ({'auto-generated' if fetched_transcript.is_generated else 'manual'})")
            
            except Exception:
                # Fallback to simple fetch if listing fails
                fetched_transcript = ytt_api.fetch(video_id, languages=languages)
                print(f"✅ Found YouTube transcript: {fetched_transcript.language} ({'auto-generated' if fetched_transcript.is_generated else 'manual'})")
            
            # Convert YouTube transcript format to match Whisper format
            segments = []
            for snippet in fetched_transcript:
                # Calculate end time from start + duration
                start_time = snippet.start
                end_time = start_time + snippet.duration
                
                # Clean up text: remove HTML tags and normalize whitespace
                text = snippet.text.strip()
                text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
                text = re.sub(r'\s+', ' ', text)    # Normalize whitespace
                
                if text:  # Only add non-empty segments
                    segments.append({
                        'text': text,
                        'start': start_time,
                        'end': end_time
                    })
            
            return segments, fetched_transcript.language
            
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            print(f"❌ No YouTube transcript available: {e}")
            return None, None
        except Exception as e:
            print(f"⚠️ Error fetching YouTube transcript: {e}")
            return None, None

    def convert_to_whisper_format(self, youtube_segments):
        """Convert YouTube transcript segments to Whisper format"""
        # YouTube transcripts don't have speaker info, so we'll assign a default speaker
        for segment in youtube_segments:
            segment['speaker'] = 'Speaker 1'
        
        return youtube_segments

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
        """Extract transcript with speaker labels - try YouTube API first, fallback to Whisper"""
        print(f"🎵 Processing: {audio_path}")
        
        # Extract video_id from audio path if not provided
        if video_id is None:
            video_id = Path(audio_path).stem
        
        # Get metadata
        metadata = {}
        if youtube_url:
            metadata = self.get_video_metadata(youtube_url)
            print(f"📺 {metadata.get('title', 'Unknown')}")
        
        # Try YouTube transcript API first
        segments = None
        transcript_source = "whisper"
        
        if video_id:
            youtube_segments, language = self.fetch_youtube_transcript(video_id)
            if youtube_segments:
                segments = self.convert_to_whisper_format(youtube_segments)
                transcript_source = f"youtube-{language}"
                print(f"✅ Using YouTube transcript ({language})")
        
        # Fallback to Whisper if YouTube transcript not available
        if segments is None:
            print("🎙️ Falling back to Whisper transcription...")
            result = self.transcribe_audio(audio_path)
            segments = self.assign_speakers(result["segments"])
            transcript_source = "whisper"
            print(f"✅ Used Whisper transcription")
        
        # Add transcript source to metadata
        metadata['transcript_source'] = transcript_source
        
        # Save files
        output_files = self.save_transcript(segments, video_id, metadata)
        
        print(f"✅ Generated {len(output_files)} files using {transcript_source}")
        return segments, output_files
    
    def list_available_transcripts(self, video_id):
        """List all available transcripts for a video"""
        try:
            ytt_api = YouTubeTranscriptApi()
            transcript_list = ytt_api.list(video_id)
            
            print(f"📋 Available transcripts for video {video_id}:")
            for transcript in transcript_list:
                transcript_type = "manual" if not transcript.is_generated else "auto-generated"
                translatable = "translatable" if transcript.is_translatable else "not translatable"
                print(f"  - {transcript.language} ({transcript.language_code}) - {transcript_type}, {translatable}")
                
            return transcript_list
            
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            print(f"❌ No transcripts available: {e}")
            return None
        except Exception as e:
            print(f"⚠️ Error listing transcripts: {e}")
            return None
