
# YouTube Downloader API

A powerful REST API for downloading YouTube videos with multiple format options and comprehensive metadata extraction. Built with Flask and yt-dlp.

## 🌟 Features

- 🎥 **Multiple Video Formats**: Support for MP4 from 144p to 1080p
- 🎵 **Audio Only Downloads**: MP3 with various bitrates (128kbps - 320kbps)
- 📊 **Rich Metadata**: Extract video information including title, views, duration, thumbnails
- 🔗 **Direct Download Links**: Get temporary download URLs that expire in 6 hours
- 📱 **Video Preview Pages**: Watch videos before downloading with embedded player
- 🌐 **REST API**: All endpoints use GET requests for easy integration
- 🧪 **Built-in Testing Interface**: Interactive web interface for testing all endpoints

## 🚀 Quick Start

### Option 1: Deploy on Replit (Recommended)
1. **Fork this Repl** or create a new one
2. **Click the Deploy button** in your Replit workspace
3. **Choose your deployment type**:
   - **Autoscale Deployment**: Best for APIs with variable traffic
   - **Reserved VM**: Best for consistent traffic or background tasks
4. **Configure and deploy** - Replit handles everything automatically!

### Option 2: Deploy on Railway.com
1. Fork this repository
2. Connect your GitHub account to Railway
3. Create a new project and select your forked repository
4. Railway will automatically detect the configuration from `railway.json`
5. Add environment variable: `SESSION_SECRET=your-random-secret-key`
6. Deploy and your API will be live!

### Option 3: Deploy on Vercel.com (Serverless)
1. Fork this repository
2. Connect your GitHub account to Vercel
3. Import your forked repository
4. Vercel will automatically use the configuration from `vercel.json`
5. Add environment variable: `SESSION_SECRET=your-random-secret-key`
6. Deploy and your serverless API will be live!

**✅ Serverless Optimized:** This application includes a specialized serverless version in the `/api` directory that's optimized for Vercel deployment. The serverless version provides download links instead of direct file streams for better performance and reliability.

**📁 File Structure for Serverless:**
```
/api/index.py          # Serverless Flask application
/api/requirements.txt  # Python dependencies for serverless
/vercel.json          # Vercel deployment configuration
```

### Local Development
```bash
# Clone the repository
git clone <your-repo-url>
cd youtube-downloader-api

# Install dependencies
pip install flask yt-dlp gunicorn werkzeug

# Run the application
python main.py
```

The API will be available at `http://localhost:5000`

## 📋 API Endpoints

### 1. Get Video Information
```http
GET /api/video-info?url=YOUTUBE_URL
```
Returns comprehensive video metadata and available formats.

**Example:**
```bash
curl "https://your-domain.com/api/video-info?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "title": "Rick Astley - Never Gonna Give You Up",
    "channel": "Rick Astley",
    "duration": 213,
    "view_count": 1500000000,
    "thumbnail": "https://...",
    "formats": {
      "video": [...],
      "audio": {...}
    }
  }
}
```

### 2. Get Download Link (Serverless Compatible)
```http
GET /api/download-link?url=YOUTUBE_URL&quality=720p&audio_only=false
```
Returns a direct download URL optimized for serverless environments.

**Parameters:**
- `url` (required): YouTube video URL
- `quality` (optional): 144p, 240p, 360p, 480p, 720p, 1080p (default: 720p)
- `audio_only` (optional): true/false (default: false)

**Examples:**
```bash
# Get 720p video download link
curl "https://your-domain.com/api/download-link?url=VIDEO_URL&quality=720p"

# Get audio-only download link
curl "https://your-domain.com/api/download-link?url=VIDEO_URL&audio_only=true"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "download_url": "https://...",
    "filename": "video.mp4",
    "format": "720p mp4",
    "quality": "720p",
    "size": 15728640
  }
}
```

### 3. Get Download Link
```http
GET /api/download-link?url=YOUTUBE_URL&quality=720p&audio_only=false
```
Returns a temporary download URL (expires in 6 hours).

**Response:**
```json
{
  "success": true,
  "download_url": "https://direct.youtube.url/...",
  "filename": "video_title.mp4",
  "filesize": 15728640,
  "expires_in": "6 hours"
}
```

### 4. Create Preview Link
```http
GET /api/create-preview-link?url=YOUTUBE_URL
```
Creates a preview page with embedded video player and download options.

**Response:**
```json
{
  "success": true,
  "preview_url": "https://your-domain.com/video/dQw4w9WgXcQ",
  "video_id": "dQw4w9WgXcQ",
  "original_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

## 🧪 Testing Interface

Visit your deployed app's homepage to access the built-in testing interface:

- **Quick Test Buttons**: Instantly test common scenarios
- **Custom Testing Form**: Configure your own test parameters
- **Response Viewer**: Pretty-printed JSON with copy functionality
- **Performance Metrics**: Track response times and test history

## 📱 Video Preview Pages

Visit `/video/{VIDEO_ID}` to access a preview page where users can:
- Watch the YouTube video with embedded player
- See video metadata (title, channel, views, likes, duration)
- Choose from multiple download options
- Get direct download links

Example: `https://your-domain.com/video/dQw4w9WgXcQ`

## 🔧 Configuration

### Environment Variables
- `SESSION_SECRET`: Set a random secret key for session management

### Deployment Files Included
- `railway.json`: Railway.com deployment configuration
- `vercel.json`: Vercel.com serverless configuration  
- `Procfile`: Heroku/Railway process configuration
- `runtime.txt`: Python version specification
- `.replit`: Replit workspace configuration

## 📊 Response Format

All API responses follow this consistent structure:

```json
{
  "success": boolean,
  "data": object | null,
  "error": string | null
}
```

### HTTP Status Codes
- `200`: Success
- `400`: Bad Request (invalid URL, missing parameters)
- `404`: Not Found (invalid endpoint)
- `500`: Internal Server Error (processing failed)

## ⚡ Performance & Limitations

### Rate Limiting
- **No built-in rate limiting**: Implement your own if needed for production
- Consider using a reverse proxy like Cloudflare for additional protection

### File Management
- **Automatic cleanup**: Temporary files are cleaned up after 5 minutes
- **Download links**: Expire after 6 hours for security
- **Storage**: Temporary files use system temp directory

### Platform Considerations
- **Replit**: Best overall experience with integrated deployment
- **Railway**: Great for production apps with consistent traffic
- **Vercel**: Good for light usage, may timeout on large files
- **Local**: Perfect for development and testing

## 🛠️ Technical Stack

- **Backend**: Python Flask
- **Video Processing**: yt-dlp (youtube-dl fork)
- **Frontend**: Bootstrap 5 (dark theme), Vanilla JavaScript
- **Web Server**: Gunicorn (production) / Flask dev server (development)

## 📈 Usage Examples

### cURL Examples
```bash
# Get video information
curl "https://your-api.com/api/video-info?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Download 1080p video
curl -L "https://your-api.com/api/download?url=VIDEO_URL&quality=1080p" -o video.mp4

# Get download link for audio
curl "https://your-api.com/api/download-link?url=VIDEO_URL&audio_only=true"

# Create preview page
curl "https://your-api.com/api/create-preview-link?url=VIDEO_URL"
```

### JavaScript/Fetch Examples
```javascript
// Get video info
const response = await fetch('/api/video-info?url=' + encodeURIComponent(videoUrl));
const data = await response.json();

// Create download link
const downloadResponse = await fetch(`/api/download-link?url=${encodeURIComponent(videoUrl)}&quality=720p`);
const downloadData = await downloadResponse.json();
```

### Python Examples
```python
import requests

# Get video information
response = requests.get('https://your-api.com/api/video-info', {
    'params': {'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'}
})
data = response.json()

# Download file
download_response = requests.get('https://your-api.com/api/download', {
    'params': {'url': video_url, 'quality': '720p'}
})
with open('video.mp4', 'wb') as f:
    f.write(download_response.content)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly using the built-in test interface
5. Submit a pull request

## 📝 License

MIT License - feel free to use this project for personal or commercial purposes.

## 🆘 Support

- **Issues**: Create an issue in the GitHub repository
- **Documentation**: Visit the deployed app homepage for interactive documentation
- **Community**: Check Replit community forums for deployment help

## 🔗 Links

- **Live Demo**: [Your deployed app URL]
- **Replit Deployment Docs**: https://docs.replit.com/cloud-services/deployments
- **Railway Docs**: https://docs.railway.app
- **Vercel Docs**: https://vercel.com/docs

---

**Made with ❤️ using Replit**
