import os
from flask import Flask, request, redirect, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

# Ye route add karne se browser me 'Not Found' nahi aayega
@app.route('/')
def home():
    return jsonify({"status": "live", "message": "8D Audio Backend is running successfully!"})

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

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            audio_url = info.get('url')

        return redirect(audio_url)
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
