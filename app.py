import os
import requests
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
# Sabhi origins (Netlify, localhost, etc.) ke liye CORS allow
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
        'noplaylist': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            audio_url = info.get('url')

        if not audio_url:
            return jsonify({"error": "Stream URL nahi mili"}), 500

        # Direct stream proxy
        req = requests.get(audio_url, stream=True, headers={'User-Agent': 'Mozilla/5.0'})
        response = Response(
            req.iter_content(chunk_size=1024 * 128),
            content_type=req.headers.get('Content-Type', 'audio/webm'),
            status=req.status_code
        )
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
