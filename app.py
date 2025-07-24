from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
import os
import json
import uuid
import threading
import argparse
from datetime import datetime
from video_retriever import VideoRetriever
from download_audio import get_youtube_id
import traceback

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global retriever instance and configuration
retriever = None
config = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': True,
    'default_model': 'base',
    'default_similarity_threshold': 0.1,
    'default_min_results': 1
}

class SearchSession:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.searches = []
        self.videos = {}
        self.created_at = datetime.now()

# Store active sessions
sessions = {}

def initialize_retriever():
    """Initialize the retriever with proper error handling"""
    global retriever
    if retriever is None:
        try:
            # Initialize with enhanced similarity settings
            retriever = VideoRetriever(
                model=config['default_model'],
                similarity_threshold=config['default_similarity_threshold'],
                min_results=config['default_min_results']
            )
            return True
        except Exception as e:
            print(f"Error initializing retriever: {e}")
            return False
    return True

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current default configuration"""
    return jsonify({
        'default_model': config['default_model'],
        'default_similarity_threshold': config['default_similarity_threshold'],
        'default_min_results': config['default_min_results'],
        'server_config': {
            'host': config['host'],
            'port': config['port'],
            'debug': config['debug']
        }
    })

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search_videos():
    """Handle video search requests with enhanced similarity matching"""
    try:
        data = request.json
        video_urls = data.get('video_urls', [])
        query = data.get('query', '')
        session_id = data.get('session_id')
        
        # Get all optional parameters with defaults from global config
        top_k = data.get('top_k', 5)
        similarity_threshold = data.get('similarity_threshold', config['default_similarity_threshold'])
        chunk_size = data.get('chunk_size', 6)
        whisper_model = data.get('whisper_model', config['default_model'])
        min_results = data.get('min_results', config['default_min_results'])
        preferred_language = data.get('preferred_language', None)
        
        # Validate parameters
        if not 0.0 <= similarity_threshold <= 1.0:
            return jsonify({'error': 'Similarity threshold must be between 0.0 and 1.0'}), 400
        
        if chunk_size < 1 or chunk_size > 20:
            return jsonify({'error': 'Chunk size must be between 1 and 20'}), 400
        
        if top_k < 1 or top_k > 50:
            return jsonify({'error': 'Top K must be between 1 and 50'}), 400
        
        if min_results < 0 or min_results > 10:
            return jsonify({'error': 'Min results must be between 0 and 10'}), 400
        
        if whisper_model not in ['tiny', 'base', 'small', 'medium', 'large']:
            return jsonify({'error': 'Invalid Whisper model'}), 400
        
        if not video_urls or not query:
            return jsonify({'error': 'Video URLs and query are required'}), 400
        
        # Log configuration for debugging
        print(f"🔧 Search configuration:")
        print(f"   Query: '{query}'")
        print(f"   Videos: {len(video_urls)}")
        print(f"   Top K: {top_k}")
        print(f"   Similarity threshold: {similarity_threshold}")
        print(f"   Chunk size: {chunk_size}")
        print(f"   Whisper model: {whisper_model}")
        print(f"   Min results: {min_results}")
        print(f"   Preferred language: {preferred_language}")
        
        # Update or create retriever with new configuration
        global retriever
        retriever_needs_update = (
            not retriever or 
            retriever.similarity_threshold != similarity_threshold or
            retriever.min_results != min_results
        )
        
        if retriever_needs_update:
            print(f"🔄 Updating retriever configuration...")
            retriever = VideoRetriever(
                model=whisper_model,
                similarity_threshold=similarity_threshold,
                min_results=min_results
            )
        
        # Validate video URLs/IDs
        validated_urls = []
        for url in video_urls:
            url = url.strip()
            if not url:
                continue
            if not (url.startswith('http') or len(url) == 11):  # Basic YouTube ID validation
                continue
            validated_urls.append(url)
        
        if not validated_urls:
            return jsonify({'error': 'No valid YouTube URLs or video IDs provided'}), 400
        
        # Get or create session
        if session_id not in sessions:
            sessions[session_id] = SearchSession()
        
        search_session = sessions[session_id]
        
        # Initialize retriever if needed
        if not initialize_retriever():
            return jsonify({'error': 'Failed to initialize retriever. Please check if all dependencies are installed.'}), 500
        
        # Process videos
        all_results = []
        processed_count = 0
        
        for video_url in validated_urls:
            try:
                video_id = get_youtube_id(video_url) if video_url.startswith('http') else video_url
                
                # Emit progress update
                socketio.emit('search_progress', {
                    'session_id': session_id,
                    'status': f'Processing video {processed_count + 1}/{len(validated_urls)}: {video_id}',
                    'video_id': video_id,
                    'progress': (processed_count / len(validated_urls)) * 100
                })
                
                # Search video with all parameters
                results = retriever.search_video(video_url, query, top_k, chunk_size)
                
                if results:
                    # Get video metadata if available
                    metadata = {}
                    transcript_file = f"data/{video_id}/transcripts/{video_id}.json"
                    if os.path.exists(transcript_file):
                        with open(transcript_file) as f:
                            transcript_data = json.load(f)
                            metadata = transcript_data.get('metadata', {})
                    
                    video_info = {
                        'video_id': video_id,
                        'url': video_url if video_url.startswith('http') else f"https://youtu.be/{video_id}",
                        'title': metadata.get('title', f'Video {video_id}'),
                        'uploader': metadata.get('uploader', 'Unknown'),
                        'transcript_source': metadata.get('transcript_source', 'unknown'),
                        'results': results,
                        'query': query,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    all_results.append(video_info)
                    search_session.videos[video_id] = video_info
                    
                    socketio.emit('search_progress', {
                        'session_id': session_id,
                        'status': f'✅ Found {len(results)} results in {video_id}',
                        'video_id': video_id,
                        'results_found': len(results)
                    })
                else:
                    socketio.emit('search_progress', {
                        'session_id': session_id,
                        'status': f'⚠️ No results found in {video_id}',
                        'video_id': video_id
                    })
                
                processed_count += 1
                
            except Exception as e:
                print(f"Error processing video {video_url}: {e}")
                socketio.emit('search_error', {
                    'session_id': session_id,
                    'error': f'Error processing {video_url}: {str(e)}',
                    'video_url': video_url
                })
                processed_count += 1
        
        # Save search to session
        search_result = {
            'id': str(uuid.uuid4()),
            'query': query,
            'video_count': len(validated_urls),
            'successful_videos': len(all_results),
            'results': all_results,
            'timestamp': datetime.now().isoformat()
        }
        
        search_session.searches.append(search_result)
        
        # Final progress update
        socketio.emit('search_complete', {
            'session_id': session_id,
            'status': f'✅ Search complete! Processed {processed_count} videos, found results in {len(all_results)} videos',
            'total_results': sum(len(video.get('results', [])) for video in all_results)
        })
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'search_id': search_result['id'],
            'results': all_results,
            'processed_count': processed_count,
            'successful_count': len(all_results)
        })
        
    except Exception as e:
        print(f"Search error: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@app.route('/api/session/<session_id>/history')
def get_session_history(session_id):
    """Get search history for a session"""
    if session_id in sessions:
        search_session = sessions[session_id]
        return jsonify({
            'session_id': session_id,
            'searches': search_session.searches,
            'videos': list(search_session.videos.keys())
        })
    return jsonify({'error': 'Session not found'}), 404

@app.route('/api/video/<video_id>/info')
def get_video_info(video_id):
    """Get detailed video information"""
    try:
        transcript_file = f"data/{video_id}/transcripts/{video_id}.json"
        if os.path.exists(transcript_file):
            with open(transcript_file) as f:
                data = json.load(f)
            return jsonify(data)
        return jsonify({'error': 'Video not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/similarity/stats')
def get_similarity_stats():
    """Get current similarity configuration and statistics"""
    global retriever
    if retriever:
        return jsonify({
            'similarity_threshold': retriever.similarity_threshold,
            'min_results': retriever.min_results,
            'vectorizer_features': retriever.vectorizer.max_features,
            'ngram_range': getattr(retriever.vectorizer, 'ngram_range', (1, 1))
        })
    return jsonify({'error': 'Retriever not initialized'}), 500

@app.route('/api/similarity/configure', methods=['POST'])
def configure_similarity():
    """Configure similarity threshold and other search parameters"""
    try:
        data = request.json
        similarity_threshold = data.get('similarity_threshold')
        min_results = data.get('min_results')
        
        global retriever
        if not retriever:
            return jsonify({'error': 'Retriever not initialized'}), 500
        
        if similarity_threshold is not None:
            if not 0.0 <= similarity_threshold <= 1.0:
                return jsonify({'error': 'Similarity threshold must be between 0.0 and 1.0'}), 400
            retriever.similarity_threshold = similarity_threshold
        
        if min_results is not None:
            if min_results < 0:
                return jsonify({'error': 'Min results must be non-negative'}), 400
            retriever.min_results = min_results
        
        return jsonify({
            'success': True,
            'similarity_threshold': retriever.similarity_threshold,
            'min_results': retriever.min_results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('connected', {'status': 'Connected to Video Retriever'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

@socketio.on('initialize_session')
def handle_initialize_session():
    """Initialize a new search session"""
    session_id = str(uuid.uuid4())
    sessions[session_id] = SearchSession()
    emit('session_initialized', {'session_id': session_id})

def parse_arguments():
    """Parse command-line arguments for web server configuration"""
    parser = argparse.ArgumentParser(description="Video Retriever Web Interface")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind to (default: 5000)")
    parser.add_argument("--debug", action="store_true", default=True, help="Enable debug mode (default: True)")
    parser.add_argument("--no-debug", action="store_true", help="Disable debug mode")
    parser.add_argument("--model", default="base", help="Default Whisper model (default: base)")
    parser.add_argument("--similarity-threshold", type=float, default=0.1, 
                       help="Default similarity threshold (0.0-1.0, default: 0.1)")
    parser.add_argument("--min-results", type=int, default=1, 
                       help="Default minimum results per video (default: 1)")
    parser.add_argument("--secret-key", help="Flask secret key (optional)")
    parser.add_argument("--test-config", action="store_true", help="Test configuration and exit")
    
    return parser.parse_args()

if __name__ == '__main__':
    # Parse command-line arguments
    args = parse_arguments()
    
    # Update global config with command-line arguments and environment variables
    config.update({
        'host': os.environ.get('HOST', args.host),
        'port': int(os.environ.get('PORT', args.port)),
        'debug': (args.debug and not args.no_debug) and not os.environ.get('PRODUCTION'),
        'default_model': os.environ.get('DEFAULT_MODEL', args.model),
        'default_similarity_threshold': float(os.environ.get('DEFAULT_SIMILARITY_THRESHOLD', args.similarity_threshold)),
        'default_min_results': int(os.environ.get('DEFAULT_MIN_RESULTS', args.min_results))
    })
    
    # Validate similarity threshold
    if not 0.0 <= config['default_similarity_threshold'] <= 1.0:
        print("❌ Error: Similarity threshold must be between 0.0 and 1.0")
        exit(1)
    
    # Set secret key if provided or use environment variable
    if args.secret_key:
        app.config['SECRET_KEY'] = args.secret_key
    elif os.environ.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    else:
        # Generate a random secret key for production
        import secrets
        app.config['SECRET_KEY'] = secrets.token_hex(32)
    
    # Test configuration mode - print config and exit
    if args.test_config:
        print("🧪 Configuration Test Mode")
        print(f"📊 Host: {config['host']}")
        print(f"📊 Port: {config['port']}")
        print(f"📊 Debug: {config['debug']}")
        print(f"📊 Default Model: {config['default_model']}")
        print(f"📊 Default Similarity Threshold: {config['default_similarity_threshold']}")
        print(f"📊 Default Min Results: {config['default_min_results']}")
        print("✅ Configuration is valid")
        exit(0)
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Initialize retriever on startup
    print("🚀 Initializing Video Retriever...")
    print(f"📊 Default Model: {config['default_model']}")
    print(f"🎯 Default Similarity Threshold: {config['default_similarity_threshold']}")
    print(f"📈 Default Min Results: {config['default_min_results']}")
    
    if initialize_retriever():
        print("✅ Retriever initialized successfully")
    else:
        print("⚠️  Warning: Retriever initialization failed")
    
    print("🌐 Starting web server...")
    print(f"🔗 Server will be available at: http://{config['host']}:{config['port']}")
    if config['host'] == '0.0.0.0':
        print(f"🌍 Local access: http://localhost:{config['port']}")
    print(f"🔍 Debug mode: {'enabled' if config['debug'] else 'disabled'}")
    
    socketio.run(app, debug=config['debug'], host=config['host'], port=config['port'])
