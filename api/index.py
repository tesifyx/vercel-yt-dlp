import os
import logging
import re
import tempfile
from urllib.parse import urlparse
from flask import Flask, jsonify, request, render_template

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create Flask app with proper template and static folder paths
app = Flask(__name__, 
    template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates'),
    static_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')
)
app.secret_key = os.environ.get("SESSION_SECRET", "youtube-downloader-secret-key")

# Simple YouTube service for serverless environment
class YouTubeService:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        logging.info(f"YouTube service initialized with temp dir: {self.temp_dir}")
    
    def is_valid_youtube_url(self, url):
        youtube_regex = re.compile(
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        return bool(youtube_regex.match(url))
    
    def get_video_info(self, url):
        try:
            import yt_dlp
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise Exception("Could not extract video information")
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'channel': info.get('uploader', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'description': info.get('description', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'formats': info.get('formats', [])
                }
        except Exception as e:
            logging.error(f"Error extracting video info: {e}")
            raise

# Initialize YouTube service
youtube_service = YouTubeService()

@app.route('/')
def index():
    """Main page with API documentation and testing interface"""
    return render_template('index.html')

@app.route('/api/video-info')
def get_video_info():
    """Get detailed video information including available formats"""
    try:
        url = request.args.get('url')
        if not url:
            return jsonify({
                'success': False,
                'error': 'URL parameter is required'
            }), 400
        
        if not youtube_service.is_valid_youtube_url(url):
            return jsonify({
                'success': False,
                'error': 'Invalid YouTube URL'
            }), 400
        
        video_info = youtube_service.get_video_info(url)
        return jsonify({
            'success': True,
            'data': video_info
        })
    
    except Exception as e:
        logging.error(f"Error getting video info: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/download-link')
def get_download_link():
    """Get temporary download link for video/audio"""
    try:
        url = request.args.get('url')
        quality = request.args.get('quality', '720p')
        audio_only = request.args.get('audio_only', 'false').lower() == 'true'
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'URL parameter is required'
            }), 400
        
        if not youtube_service.is_valid_youtube_url(url):
            return jsonify({
                'success': False,
                'error': 'Invalid YouTube URL'
            }), 400
        
        # Get video info to extract direct download URLs
        video_info = youtube_service.get_video_info(url)
        
        # Find the best format based on quality preference
        best_format = None
        if audio_only:
            # Find best audio format
            for fmt in video_info.get('formats', []):
                if fmt.get('vcodec') == 'none' and fmt.get('acodec') != 'none':
                    if not best_format or (fmt.get('abr', 0) > best_format.get('abr', 0)):
                        best_format = fmt
        else:
            # Find best video format matching quality
            target_height = int(quality.replace('p', ''))
            for fmt in video_info.get('formats', []):
                if (fmt.get('height') == target_height and 
                    fmt.get('vcodec') != 'none' and 
                    fmt.get('acodec') != 'none'):
                    best_format = fmt
                    break
            
            # If no exact match, find closest
            if not best_format:
                for fmt in video_info.get('formats', []):
                    if (fmt.get('height') and 
                        fmt.get('vcodec') != 'none' and 
                        fmt.get('acodec') != 'none'):
                        if not best_format or abs(fmt.get('height') - target_height) < abs(best_format.get('height') - target_height):
                            best_format = fmt
        
        if not best_format:
            return jsonify({
                'success': False,
                'error': 'No suitable format found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'download_url': best_format.get('url'),
                'filename': f"{video_info.get('title', 'video')}.{best_format.get('ext', 'mp4')}",
                'format': best_format.get('format'),
                'quality': f"{best_format.get('height', 'unknown')}p" if not audio_only else f"{best_format.get('abr', 'unknown')}kbps",
                'size': best_format.get('filesize', 'unknown')
            }
        })
        
    except Exception as e:
        logging.error(f"Error getting download link: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/video/<video_id>')
def video_preview(video_id):
    """Video preview page with download options"""
    try:
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        video_info = youtube_service.get_video_info(youtube_url)
        return render_template('video_preview.html', video_info=video_info, video_id=video_id)
    except Exception as e:
        logging.error(f"Error in video preview: {str(e)}")
        return render_template('error.html', error=str(e)), 500

@app.route('/api/create-preview-link')
def create_preview_link():
    """Create a preview link for YouTube video"""
    try:
        url = request.args.get('url')
        if not url:
            return jsonify({
                'success': False,
                'error': 'URL parameter is required'
            }), 400
        
        if not youtube_service.is_valid_youtube_url(url):
            return jsonify({
                'success': False,
                'error': 'Invalid YouTube URL'
            }), 400
        
        # Extract video ID from URL
        parsed_url = urlparse(url)
        if 'youtube.com' in parsed_url.netloc:
            video_id = parsed_url.query.split('v=')[1].split('&')[0]
        elif 'youtu.be' in parsed_url.netloc:
            video_id = parsed_url.path[1:]
        else:
            return jsonify({
                'success': False,
                'error': 'Could not extract video ID from URL'
            }), 400
        
        preview_url = f"{request.host_url}video/{video_id}"
        
        return jsonify({
            'success': True,
            'data': {
                'preview_url': preview_url,
                'video_id': video_id
            }
        })
        
    except Exception as e:
        logging.error(f"Error creating preview link: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'YouTube Downloader API',
        'mode': 'serverless'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

# For local development
if __name__ == '__main__':
    app.run(debug=True)