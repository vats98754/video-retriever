#!/usr/bin/env python3
"""
Optimized Video Retriever with TF-IDF Search
"""

import os
import json
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from download_audio import download_audio, get_youtube_id
from simple_transcript_extractor import SimpleTranscriptExtractor

class VideoRetriever:
    def __init__(self, model="base"):
        print("🚀 Loading models...")
        self.transcriber = SimpleTranscriptExtractor(model)
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        print("✅ Ready")
    
    def chunk_segments(self, segments, chunk_size=6):
        """Combine segments into optimal chunks for search"""
        chunks = []
        for i in range(0, len(segments), chunk_size):
            chunk_segments = segments[i:i+chunk_size]
            
            text = " ".join(s['text'] for s in chunk_segments)
            start = chunk_segments[0]['start']
            end = chunk_segments[-1]['end']
            speakers = list(set(s.get('speaker', 'Speaker 1') for s in chunk_segments))
            
            chunks.append({
                'text': text,
                'start': start,
                'end': end,
                'speakers': speakers,
                'duration': end - start
            })
        
        return chunks
    
    def vectorize_chunks(self, chunks):
        """Create TF-IDF vectors for chunks"""
        texts = [chunk['text'] for chunk in chunks]
        vectors = self.vectorizer.fit_transform(texts)
        
        for i, chunk in enumerate(chunks):
            chunk['vector'] = vectors[i]
        
        return chunks
    
    def search(self, chunks, query, top_k=5):
        """Search using TF-IDF cosine similarity"""
        query_vec = self.vectorizer.transform([query])
        
        scores = []
        for chunk in chunks:
            score = cosine_similarity(query_vec, chunk['vector'])[0][0]
            scores.append((score, chunk))
        
        return sorted(scores, key=lambda x: x[0], reverse=True)[:top_k]
    
    def format_results(self, results, query, video_id=None, base_url=None):
        """Format and display results with YouTube timestamps"""
        print(f"\\n🎯 Top {len(results)} results for: '{query}'")
        print("-" * 60)
        
        formatted = []
        for i, (score, chunk) in enumerate(results, 1):
            start_min, start_sec = divmod(int(chunk['start']), 60)
            end_min, end_sec = divmod(int(chunk['end']), 60)
            timestamp = f"{start_min:02d}:{start_sec:02d}-{end_min:02d}:{end_sec:02d}"
            
            # Create YouTube URL with timestamp
            youtube_url = None
            if base_url:
                youtube_url = f"{base_url}&t={int(chunk['start'])}s"
            elif video_id:
                youtube_url = f"https://youtu.be/{video_id}?t={int(chunk['start'])}s"
            
            result = {
                'rank': i,
                'score': float(score),
                'timestamp': timestamp,
                'start': chunk['start'],
                'end': chunk['end'],
                'duration': chunk['duration'],
                'speakers': chunk['speakers'],
                'text': chunk['text'][:300] + "..." if len(chunk['text']) > 300 else chunk['text'],
                'youtube_url': youtube_url
            }
            
            print(f"{i}. [{timestamp}] ({score:.3f}) {', '.join(chunk['speakers'])}")
            if youtube_url:
                print(f"   🔗 {youtube_url}")
            print(f"   {result['text']}")
            print()
            
            formatted.append(result)
        
        return formatted
    
    def save_data(self, video_id, chunks, results=None, query=None, base_url=None):
        """Save processed data with better organization"""
        # Create organized directory structure
        video_dir = f"data/{video_id}"
        os.makedirs(f"{video_dir}/vectors", exist_ok=True)
        os.makedirs(f"{video_dir}/searches", exist_ok=True)
        
        # Save vectors (without scipy sparse matrices)
        vector_data = []
        for chunk in chunks:
            chunk_copy = chunk.copy()
            if 'vector' in chunk_copy:
                del chunk_copy['vector']  # Remove sparse matrix
            vector_data.append(chunk_copy)
        
        vector_file = f"{video_dir}/vectors/chunks.json"
        with open(vector_file, 'w') as f:
            json.dump({
                'video_id': video_id,
                'base_url': base_url,
                'chunk_count': len(vector_data),
                'chunks': vector_data
            }, f, indent=2)
        
        # Save search results if provided
        if results and query:
            search_file = f"{video_dir}/searches/{query.replace(' ', '_')}.json"
            with open(search_file, 'w') as f:
                json.dump({
                    'query': query,
                    'video_id': video_id,
                    'base_url': base_url,
                    'timestamp': datetime.now().isoformat(),
                    'results': results
                }, f, indent=2)
            return vector_file, search_file
        
        return vector_file
    
    def search_video(self, url_or_id, query, top_k=5, chunk_size=6):
        """
        Complete end-to-end pipeline: URL/ID + Query → Timestamped YouTube URLs
        
        Args:
            url_or_id: YouTube URL or video ID
            query: Search query string
            top_k: Number of results to return
            chunk_size: Segments per chunk
            
        Returns:
            List of results with timestamped YouTube URLs
        """
        print(f"🎬 Processing: {url_or_id}")
        print(f"🔍 Query: '{query}'")
        
        # Extract video ID
        if url_or_id.startswith('http'):
            video_id = get_youtube_id(url_or_id)
            youtube_url = url_or_id
        else:
            video_id = url_or_id
            youtube_url = f"https://youtu.be/{video_id}"
        
        print(f"📺 Video ID: {video_id}")
        
        # Check if transcript exists
        transcript_file = f"data/{video_id}/transcripts/{video_id}.json"
        
        if not os.path.exists(transcript_file):
            print("📥 Transcript not found. Starting full pipeline...")
            
            # 1. Download audio (if needed)
            audio_file = f"data/{video_id}/audio/{video_id}.mp3"
            if not os.path.exists(audio_file):
                print("🎵 Downloading audio...")
                audio_path = download_audio(youtube_url, video_id=video_id)
                if not audio_path:
                    print("❌ Failed to download audio")
                    return None
            else:
                print(f"📁 Using existing audio: {audio_file}")
                audio_path = audio_file
            
            # 2. Generate transcript
            print("📝 Generating transcript...")
            segments, transcript_files = self.transcriber.extract_transcript(
                audio_path, youtube_url, video_id=video_id
            )
            print(f"✅ Generated transcript with {len(segments)} segments")
        else:
            print(f"📁 Using existing transcript: {transcript_file}")
            # Load existing transcript
            with open(transcript_file) as f:
                data = json.load(f)
            segments = data['segments']
        
        # 3. Create chunks and search
        print(f"🔍 Searching with chunks of {chunk_size} segments...")
        chunks = self.chunk_segments(segments, chunk_size)
        vectorized_chunks = self.vectorize_chunks(chunks)
        
        # 4. Perform search
        search_results = self.search(vectorized_chunks, query, top_k)
        results = self.format_results(search_results, query, video_id=video_id)
        
        # 5. Save results
        self.save_data(video_id, vectorized_chunks, results, query, youtube_url)
        
        print(f"\\n🎉 Search completed! Found {len(results)} timestamped results")
        return results

def main():
    import argparse
    parser = argparse.ArgumentParser(description="End-to-end YouTube video search with timestamped results")
    parser.add_argument("url_or_id", help="YouTube URL or video ID")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results to return (default: 5)")
    parser.add_argument("--chunk-size", type=int, default=6, help="Segments per chunk (default: 6)")
    parser.add_argument("--model", default="base", help="Whisper model size (default: base)")
    
    args = parser.parse_args()
    
    try:
        retriever = VideoRetriever(args.model)
        results = retriever.search_video(args.url_or_id, args.query, args.top_k, args.chunk_size)
        
        if results:
            print(f"\\n✅ SUCCESS: Found {len(results)} timestamped results!")
            print("\\n📋 SUMMARY:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['youtube_url']} - {result['text'][:50]}...")
        else:
            print("❌ No results found or processing failed")
            
    except KeyboardInterrupt:
        print("\\n⚠️  Process interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
