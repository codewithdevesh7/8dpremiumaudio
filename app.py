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
    # YouTube URL se 11 digit ki Video ID nikalne ke liye
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

    # Fast Piped API instances jo IP block nahi karte
    instances = [
        f"https://pipedapi.kavin.rocks/streams/{video_id}",
        f"https://api.piped.privacydev.net/streams/{video_id}",
        f"https://pipedapi.tokhmi.xyz/streams/{video_id}"
    ]

    for api_url in instances:
        try:
            res = requests.get(api_url, timeout=7)
            if res.status_code == 200:
                data = res.json()
                audio_streams = data.get('audioStreams', [])
                if audio_streams:
                    # Best quality audio stream select karein
                    audio_url = audio_streams[-1].get('url')
                    response = redirect(audio_url)
                    response.headers['Access-Control-Allow-Origin'] = '*'
                    return response
        except Exception:
            continue

    return jsonify({"error": "YouTube audio extract nahi ho paya, doosra link try karein"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
