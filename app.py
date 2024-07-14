from yt_dlp import YoutubeDL
from flask import Flask, render_template, request, jsonify
from pathlib import Path
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        playlist_url = request.form['playlist_url']
        videos = get_playlist_info(playlist_url)
        if videos:
            return render_template('playlist.html', videos=videos)
        else:
            return render_template(
                'index.html',
                error="Unable to fetch playlist information. Please try again."
            )
    return render_template('index.html')


@app.route('/download', methods=['POST'])
def download():
    selected_videos = request.json['videos']
    quality = request.json['quality']
    download_videos(selected_videos, quality)
    return jsonify({
        'status': 'success',
        'message': 'Videos are being downloaded to the "downloads" folder.'
    })


def get_playlist_info(url):
    ydl_opts = {
        'ignoreerrors': True,
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        try:
            playlist_dict = ydl.extract_info(url, download=False)
            if playlist_dict and 'entries' in playlist_dict:
                videos = []
                for video in playlist_dict['entries']:
                    if video:
                        videos.append({
                            'id': video.get('id', 'Unknown'),
                            'title': video.get('title', 'Unknown Title'),
                            'url': video.get(
                                'url',
                                video.get('webpage_url', 'Unknown URL')
                            )
                        })
                return videos
            else:
                print("No playlist information found")
                return []
        except Exception as e:
            print(f"Error extracting playlist info: {str(e)}")
            return []


def download_videos(videos, quality):
    # Create a 'downloads' folder if it doesn't exist
    downloads_path = Path('downloads')
    downloads_path.mkdir(exist_ok=True)

    format_string = {
        '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
        '2k': 'bestvideo[height<=1440]+bestaudio/best[height<=1440]',
        '4k': 'bestvideo[height<=2160]+bestaudio/best[height<=2160]'
    }.get(quality, 'bestvideo+bestaudio/best')

    ydl_opts = {
        'format': format_string,
        # Save to 'downloads' folder
        'outtmpl': str(downloads_path / '%(title)s.%(ext)s'),
        'ignoreerrors': True,
        'retries': 3,
    }
    with YoutubeDL(ydl_opts) as ydl:
        for video in videos:
            try:
                ydl.download([video['url']])
            except Exception as e:
                print(f"Error downloading {video['title']}: {str(e)}")


if __name__ == '__main__':
    app.run(debug=True)
