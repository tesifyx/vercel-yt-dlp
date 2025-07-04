import os
import logging
from flask import Flask, jsonify, request, render_template, send_file, abort
from werkzeug.middleware.proxy_fix import ProxyFix
from youtube_service import YouTubeService
from urllib.parse import urlparse
import tempfile
import threading
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "youtube-downloader-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize YouTube service
youtube_service = YouTubeService()

# Store for temporary download files
temp_files = {}

def cleanup_temp_file(file_path, delay=300):
    """Clean up temporary file after delay (5 minutes)"""
    def cleanup():
        time.sleep(delay)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logging.info(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logging.error(f"Error cleaning up temp file {file_path}: {e}")
    
    thread = threading.Thread(target=cleanup)
    thread.daemon = True
    thread.start()

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
                'error': 'Missing required parameter: url',
                'success': False
            }), 400
        
        url = url.strip()
        
        # Validate URL
        if not youtube_service.is_valid_youtube_url(url):
            return jsonify({
                'error': 'Invalid YouTube URL',
                'success': False
            }), 400
        
        # Get video information
        video_info = youtube_service.get_video_info(url)
        
        return jsonify({
            'success': True,
            'data': video_info
        })
        
    except Exception as e:
        logging.error(f"Error getting video info: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/download')
def download_video():
    """Download video or audio in specified format"""
    try:
        url = request.args.get('url')
        if not url:
            return jsonify({
                'error': 'Missing required parameter: url',
                'success': False
            }), 400
        
        url = url.strip()
        format_id = request.args.get('format_id')
        audio_only = request.args.get('audio_only', 'false').lower() == 'true'
        quality = request.args.get('quality', '720p')
        
        # Validate URL
        if not youtube_service.is_valid_youtube_url(url):
            return jsonify({
                'error': 'Invalid YouTube URL',
                'success': False
            }), 400
        
        # Download the video/audio
        download_result = youtube_service.download_video(
            url, 
            format_id=format_id, 
            audio_only=audio_only, 
            quality=quality
        )
        
        if not download_result['success']:
            return jsonify(download_result), 500
        
        file_path = download_result['file_path']
        filename = download_result['filename']
        
        # Schedule cleanup
        cleanup_temp_file(file_path)
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype=download_result.get('mimetype', 'application/octet-stream')
        )
        
    except Exception as e:
        logging.error(f"Error downloading video: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/download-link')
def get_download_link():
    """Get temporary download link for video/audio"""
    try:
        url = request.args.get('url')
        if not url:
            return jsonify({
                'error': 'Missing required parameter: url',
                'success': False
            }), 400
        
        url = url.strip()
        format_id = request.args.get('format_id')
        audio_only = request.args.get('audio_only', 'false').lower() == 'true'
        quality = request.args.get('quality', '720p')
        
        # Validate URL
        if not youtube_service.is_valid_youtube_url(url):
            return jsonify({
                'error': 'Invalid YouTube URL',
                'success': False
            }), 400
        
        # Get direct download URL
        download_url = youtube_service.get_download_url(
            url, 
            format_id=format_id, 
            audio_only=audio_only, 
            quality=quality
        )
        
        return jsonify({
            'success': True,
            'download_url': download_url['url'],
            'filename': download_url['filename'],
            'filesize': download_url.get('filesize'),
            'expires_in': '6 hours'
        })
        
    except Exception as e:
        logging.error(f"Error getting download link: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/video/<video_id>')
def video_preview(video_id):
    """Video preview page with download options"""
    try:
        # Construct YouTube URL from video ID
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Get video information
        video_info = youtube_service.get_video_info(url)
        
        return render_template('video_preview.html', video=video_info, video_id=video_id)
        
    except Exception as e:
        logging.error(f"Error loading video preview: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/api/create-preview-link')
def create_preview_link():
    """Create a preview link for YouTube video"""
    try:
        url = request.args.get('url')
        if not url:
            return jsonify({
                'error': 'Missing required parameter: url',
                'success': False
            }), 400
        
        url = url.strip()
        
        # Validate URL
        if not youtube_service.is_valid_youtube_url(url):
            return jsonify({
                'error': 'Invalid YouTube URL',
                'success': False
            }), 400
        
        # Extract video ID from URL
        import re
        video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
        if not video_id_match:
            return jsonify({
                'error': 'Could not extract video ID from URL',
                'success': False
            }), 400
        
        video_id = video_id_match.group(1)
        
        # Create preview URL
        preview_url = request.url_root + f'video/{video_id}'
        
        return jsonify({
            'success': True,
            'preview_url': preview_url,
            'video_id': video_id,
            'original_url': url
        })
        
    except Exception as e:
        logging.error(f"Error creating preview link: {e}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'YouTube Downloader API',
        'version': '1.0.0'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'success': False
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'success': False
    }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
