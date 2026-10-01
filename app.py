import os
from flask import Flask, request, Response
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)  # Cross-Origin access allow karega Netlify ke liye

@app.route('/stream')
def stream_audio():
    video_url = request.args.get('url')
    if not video_url:
        return "Missing URL parameter", 400

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        audio_url = info.get('url')

    # Redirect direct high-speed audio stream
    from flask import redirect
    return redirect(audio_url)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
