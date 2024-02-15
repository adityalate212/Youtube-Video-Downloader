from flask import Flask, render_template, request, send_file, redirect
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pytube import YouTube
import ssl

# Disable SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context

app = Flask(__name__)

# Set up API key
api_key = 'AIzaSyDAnjJeKSCQob3Xg2O22h6kCwFBoTv5A70'  # Replace with your YouTube API key
youtube = build('youtube', 'v3', developerKey=api_key)

@app.route('/', methods=['GET', 'POST'])
def index():
    videos = []

    if request.method == 'POST':
        keyword = request.form.get('keyword')

        try:
            # Search for videos with the specified keyword
            search_response = youtube.search().list(
                q=keyword,
                type='video',
                part='id',
                maxResults=10  # Display the top 10 videos
            ).execute()

            video_ids = []
            for search_result in search_response.get('items', []):
                video_ids.append(search_result['id']['videoId'])

            for video_id in video_ids:
                video_url = f'https://www.youtube.com/watch?v={video_id}'
                yt = YouTube(video_url)

                # Get video information
                title = yt.title
                description = yt.description
                views = yt.views
                duration = yt.length
                thumbnail_url = yt.thumbnail_url

                videos.append({
                    'title': title,
                    'description': description,
                    'views': views,
                    'duration': duration,
                    'thumbnail_url': thumbnail_url,
                    'video_id': video_id
                })

        except HttpError as e:
            return f'An error occurred: {e}'

    return render_template('index.html', videos=videos)

@app.route('/download/<video_id>', methods=['GET'])
def download(video_id):
    try:
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        yt = YouTube(video_url)
        video_stream = yt.streams.get_highest_resolution()
        video_stream.download(output_path='downloads/')
        file_path = f'downloads/{yt.title}.mp4'
        # Redirect to the thank_you page after successful download
        return redirect('/thank_you')
    except Exception as e:
        return f'An error occurred: {e}'

@app.route('/thank_you', methods=['GET'])
def thank_you():
    return render_template('thank_you.html')

if __name__ == '__main__':
    app.run(debug=True)
