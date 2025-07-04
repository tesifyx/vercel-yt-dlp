# YouTube Downloader API

## Overview

This is a Flask-based REST API for downloading YouTube videos and extracting video metadata. The application provides a web interface for testing the API and supports multiple video/audio formats with quality options. Built with Python Flask, it uses yt-dlp for YouTube video processing and provides both programmatic API access and a user-friendly web interface.

## System Architecture

### Backend Architecture
- **Framework**: Flask with Python 3.x
- **Video Processing**: yt-dlp library for YouTube video extraction and download
- **Web Server**: Flask development server (suitable for development/testing)
- **Template Engine**: Jinja2 (Flask's default templating engine)
- **Static File Serving**: Flask's built-in static file handler

### Frontend Architecture
- **UI Framework**: Bootstrap 5 (dark theme) with Font Awesome icons
- **JavaScript**: Vanilla ES6+ for interactive functionality
- **Styling**: Custom CSS with Bootstrap theme overrides
- **Layout**: Responsive design with Bootstrap grid system

## Key Components

### Core Application Files
- **app.py**: Main Flask application with route definitions and request handling
- **main.py**: Application entry point for running the Flask server
- **youtube_service.py**: Service layer handling YouTube URL validation and video processing
- **templates/**: HTML templates using Jinja2 templating
- **static/**: Client-side JavaScript and CSS assets

### API Endpoints
- **GET /**: Main page with API documentation and testing interface
- **POST /api/video-info**: Extract video metadata and available formats
- **POST /api/download**: Download video in specified format and quality

### Service Layer
- **YouTubeService**: Encapsulates yt-dlp functionality for video processing
- URL validation using regex patterns
- Temporary file management for downloads
- Format extraction and quality options

## Data Flow

1. **Client Request**: User submits YouTube URL via web interface or API call
2. **URL Validation**: Service validates YouTube URL format
3. **Video Processing**: yt-dlp extracts video information and available formats
4. **Response Generation**: API returns metadata or initiates download
5. **File Management**: Temporary files are created for downloads and cleaned up automatically
6. **Client Response**: JSON data or file download sent to client

## External Dependencies

### Python Packages
- **Flask**: Web framework for API and routing
- **yt-dlp**: YouTube video extraction and download library
- **Werkzeug**: WSGI utilities (ProxyFix middleware)

### Frontend Dependencies (CDN)
- **Bootstrap 5**: CSS framework for responsive UI
- **Font Awesome 6**: Icon library for UI elements

### System Dependencies
- **Python 3.x**: Runtime environment
- **ffmpeg**: Required by yt-dlp for video/audio processing (implicit dependency)

## Deployment Strategy

### Current Setup
- Development server configuration using Flask's built-in server
- Host: 0.0.0.0 (accepts connections from any IP)
- Port: 5000
- Debug mode enabled for development

### File Management
- Temporary directory creation for download files
- Automatic cleanup of temporary files after 5 minutes
- Thread-based cleanup to avoid blocking main application

### Configuration
- Environment-based secret key configuration
- ProxyFix middleware for reverse proxy compatibility
- Configurable logging levels

## User Preferences

Preferred communication style: Simple, everyday language.

## Deployment Configuration

### Supported Platforms
- **Railway.com**: Uses `railway.json` configuration with Nixpacks builder and automatic health checks
- **Vercel.com**: Uses `vercel.json` configuration for serverless deployment
- **Local Development**: Standard Flask development server on port 5000

### Deployment Files
- `Procfile`: Railway/Heroku deployment configuration
- `vercel.json`: Vercel serverless configuration 
- `railway.json`: Railway platform-specific settings
- `runtime.txt`: Python version specification
- `README.md`: Comprehensive deployment and usage documentation

### API Changes
- All endpoints converted from POST to GET requests for better caching and simpler integration
- URL parameters used instead of JSON request bodies
- Maintained backward compatibility in response formats

## Recent Changes

### July 04, 2025 - Serverless Migration & Optimization
- ✅ Migrated from Replit Agent to standard Replit environment
- ✅ Created serverless-compatible Flask application in `/api/index.py`
- ✅ Updated Vercel configuration for proper serverless deployment
- ✅ Removed threading-based file cleanup for serverless compatibility
- ✅ Enhanced `/api/download-link` endpoint for serverless environments
- ✅ Updated index page to reflect serverless deployment benefits
- ✅ Modified README with improved Vercel deployment instructions
- ✅ Added serverless mode indicators throughout documentation

### July 02, 2025 - Major Update: GET API & Deployment Ready
- ✅ Converted all API endpoints from POST to GET requests
- ✅ Updated frontend JavaScript to use GET requests with URL parameters
- ✅ Created deployment configurations for Railway.com and Vercel.com
- ✅ Added comprehensive README with deployment instructions
- ✅ Enhanced video preview functionality with embedded YouTube player
- ✅ Implemented preview link generation for better user experience

### API Endpoint Updates
- `GET /api/video-info?url=VIDEO_URL` - Get video metadata and formats
- `GET /api/download?url=VIDEO_URL&quality=720p&audio_only=false` - Direct download
- `GET /api/download-link?url=VIDEO_URL&quality=720p&audio_only=false` - Get download URL
- `GET /api/create-preview-link?url=VIDEO_URL` - Create preview page
- `GET /video/{VIDEO_ID}` - Video preview page with embedded player

## Changelog

Changelog:
- July 02, 2025. Initial setup
- July 02, 2025. Converted to GET APIs and added deployment configurations