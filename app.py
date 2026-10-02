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

    # 1. Piped Active Public Endpoints
    piped_mirrors = [
        f"https://pipedapi.drgns.space/streams/{video_id}",
        f"https://piped-api.garudalinux.org/streams/{video_id}",
        f"https://api.piped.projectsegfau.lt/streams/{video_id}",
        f"https://pipedapi.leptons.xyz/streams/{video_id}"
    ]

    for api in piped_mirrors:
        try:
            r = requests.get(api, timeout=6)
            if r.status_code == 200:
                data = r.json()
                audio_streams = data.get('audioStreams', [])
                if audio_streams:
                    stream_url = audio_streams[-1].get('url')
                    if stream_url:
                        res = redirect(stream_url)
                        res.headers['Access-Control-Allow-Origin'] = '*'
                        return res
        except Exception:
            continue

    # 2. Invidious Fallback Mirrors
    invidious_mirrors = [
        f"https://inv.nadeko.net/api/v1/videos/{video_id}",
        f"https://invidious.jing.rocks/api/v1/videos/{video_id}",
        f"https://vid.priv.au/api/v1/videos/{video_id}"
    ]

    for api in invidious_mirrors:
        try:
            r = requests.get(api, timeout=6)
            if r.status_code == 200:
                data = r.json()
                formats = data.get('adaptiveFormats', [])
                audio_streams = [f for f in formats if 'audio' in f.get('type', '')]
                if audio_streams:
                    audio_url = audio_streams[-1].get('url')
                    if audio_url:
                        res = redirect(audio_url)
                        res.headers['Access-Control-Allow-Origin'] = '*'
                        return res
        except Exception:
            continue

    return jsonify({"error": "Stream extraction failed across all mirrors. Please try another song."}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
