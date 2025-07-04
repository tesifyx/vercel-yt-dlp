import os
import logging
import yt_dlp
import tempfile
import re


class YouTubeService:

    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        logging.info(f"YouTube service initialized with temp dir: {self.temp_dir}")

    def is_valid_youtube_url(self, url):
        youtube_regex = re.compile(
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
        return youtube_regex.match(url) is not None

    def get_video_info(self, url):
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                video_info = {
                    'title': info.get('title', 'Unknown'),
                    'channel': info.get('uploader', 'Unknown'),
                    'channel_id': info.get('uploader_id', ''),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'upload_date': info.get('upload_date', ''),
                    'description': info.get('description', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'webpage_url': info.get('webpage_url', url),
                    'video_id': info.get('id', ''),
                    'formats': {
                        'video': [],
                        'audio': []
                    }
                }

                # Track (quality_label + type) combinations already added
                existing_video_formats = set()

                formats = info.get('formats', [])
                for fmt in formats:
                    url = fmt.get('url')
                    if not url or 'manifest.googlevideo.com' in url or 'm3u8' in url:
                        continue

                    vcodec = fmt.get('vcodec', 'none')
                    acodec = fmt.get('acodec', 'none')
                    height = fmt.get('height')
                    abr = fmt.get('abr')
                    ext = fmt.get('ext')

                    if vcodec != 'none' and height:
                        if ext == 'webm':
                            continue

                        quality = f"{height}p"
                        ftype = 'video_with_audio' if acodec != 'none' else 'video_only'
                        key = (quality, ftype)

                        if key in existing_video_formats:
                            continue
                        existing_video_formats.add(key)

                        video_info['formats']['video'].append({
                            'format_id': fmt.get('format_id'),
                            'url': url,
                            'ext': ext,
                            'filesize': fmt.get('filesize'),
                            'quality_label': quality,
                            'type': ftype
                        })

                    elif vcodec == 'none' and acodec != 'none':
                        audio_ext = 'm4a' if 'm4a' in ext else 'mp3'
                        quality_label = f"{abr}kbps" if abr else 'audio'
                        video_info['formats']['audio'].append({
                            'format_id': fmt.get('format_id'),
                            'url': url,
                            'ext': audio_ext,
                            'filesize': fmt.get('filesize'),
                            'quality_label': quality_label,
                            'type': 'audio_only'
                        })

                def safe_quality_int(label):
                    try:
                        return int(label.replace('p',''))
                    except:
                        return 0

                def safe_bitrate(label):
                    try:
                        return int(label.replace('kbps',''))
                    except:
                        return 0

                video_info['formats']['video'].sort(key=lambda x: safe_quality_int(x['quality_label']))
                video_info['formats']['audio'].sort(key=lambda x: safe_bitrate(x['quality_label']))

                return video_info

        except Exception as e:
            logging.error(f"Error extracting video info: {e}")
            raise Exception(f"Failed to extract video information: {str(e)}")

    def download_video(self, url, format_id=None, audio_only=False, quality='720p'):
        try:
            output_path = os.path.join(self.temp_dir, '%(title)s.%(ext)s')

            ydl_opts = {
                'outtmpl': output_path,
                'quiet': True,
                'no_warnings': True,
            }

            if audio_only:
                ydl_opts['format'] = 'bestaudio[ext=m4a]/bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            elif format_id:
                ydl_opts['format'] = format_id
            else:
                height = int(quality.replace('p', ''))
                ydl_opts['format'] = f'bestvideo[ext=mp4][height<={height}]+bestaudio[ext=m4a]/best[ext=mp4][height<={height}]'

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                base_filename = ydl.prepare_filename(info)

                if audio_only:
                    audio_file = base_filename.rsplit('.', 1)[0] + '.mp3'
                    if os.path.exists(audio_file):
                        base_filename = audio_file

                if not os.path.exists(base_filename):
                    raise Exception("Downloaded file not found")

                return {
                    'success': True,
                    'file_path': base_filename,
                    'filename': os.path.basename(base_filename),
                    'mimetype': 'audio/mpeg' if audio_only else 'video/mp4'
                }

        except Exception as e:
            logging.error(f"Error downloading video: {e}")
            return {'success': False, 'error': str(e)}
