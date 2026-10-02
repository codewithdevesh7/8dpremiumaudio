import os
import re
import requests
from flask import Flask, request, redirect, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "8D Spatial Audio API",
        "developer": "codewithdevesh"
    })

def extract_video_id(url):
    pattern = r'(?:v=|\/|youtu\.be\/)([0-9A-Za-z_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

@app.route('/stream')
def stream_audio():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "Missing URL parameter"}), 400

    video_id = extract_video_id(video_url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    # Cobalt API ke public instances jo bot block bypass karte hain
    cobalt_instances = [
        "https://api.cobalt.tools",
        "https://cobalt-api.kwiatekm.tokyo",
        "https://co.wuk.sh"
    ]

    clean_yt_url = f"https://www.youtube.com/watch?v={video_id}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    payload = {
        "url": clean_yt_url,
        "downloadMode": "audio",
        "audioFormat": "mp3"
    }

    for base_url in cobalt_instances:
        try:
            res = requests.post(f"{base_url}/", json=payload, headers=headers, timeout=8)
            if res.status_code == 200:
                data = res.json()
                stream_url = data.get('url')
                if stream_url:
                    response = redirect(stream_url)
                    response.headers['Access-Control-Allow-Origin'] = '*'
                    return response
        except Exception:
            continue

    # Fallback to Invidious if Cobalt is busy
    try:
        inv_res = requests.get(f"https://invidious.nerdvpn.de/api/v1/videos/{video_id}", timeout=6)
        if inv_res.status_code == 200:
            inv_data = inv_res.json()
            format_streams = inv_data.get('adaptiveFormats', [])
            audio_streams = [f for f in format_streams if 'audio' in f.get('type', '')]
            if audio_streams:
                audio_url = audio_streams[-1].get('url')
                response = redirect(audio_url)
                response.headers['Access-Control-Allow-Origin'] = '*'
                return response
    except Exception:
        pass

    return jsonify({"error": "Unable to extract audio stream at this moment. Please retry."}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
