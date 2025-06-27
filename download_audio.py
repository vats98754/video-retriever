import os
import subprocess
import re

def get_youtube_id(url):
    match = re.search(r"(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{11})", url)
    return match.group(1) if match else "output"

def download_audio(youtube_url, output_path=None, audio_folder='audio'):
    if output_path is None:
        output_path = get_youtube_id(youtube_url) + '.mp3'
    os.makedirs(audio_folder, exist_ok=True)
    
    # Extract filename without extension for yt-dlp template
    filename_without_ext = os.path.splitext(output_path)[0]
    
    # Use yt-dlp to download and convert to mp3
    output_template = os.path.join(audio_folder, f"{filename_without_ext}.%(ext)s")
    
    # Run yt-dlp as a subprocess in terminal
    try:
        subprocess.run([
            'yt-dlp', 
            '-x', 
            '--audio-format', 'mp3',
            '--output', output_template,
            youtube_url
        ], check=True)
        
        final_path = os.path.join(audio_folder, output_path)
        print(f"[✔] Audio downloaded to {final_path}")
        return final_path
        
    except subprocess.CalledProcessError as e:
        print(f"[✗] Error downloading audio: {e}")
        return None

if __name__ == "__main__":
    youtube_url = input("Please enter the YouTube video URL: ")
    download_audio(youtube_url)