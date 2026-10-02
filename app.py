import os
from flask import Flask, request, redirect, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "8D Spatial Audio API",
        "developer": "codewithdevesh"
    })

@app.route('/stream')
def stream_audio():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "Missing URL parameter"}), 400

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        # YouTube data-center blocks ko bypass karne ke liye mobile clients:
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'web']
            }
        },
        'http_headers': {
            'User-Agent': 'com.google.android.youtube/19.09.37 (Linux; U; Android 14; en_US) gzip'
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            audio_url = info.get('url')

        if not audio_url:
            return jsonify({"error": "Stream URL could not be extracted"}), 500

        response = redirect(audio_url)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    except Exception as e:
        print(f"Extraction error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
