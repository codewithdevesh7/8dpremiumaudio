import os
import re
import json
import urllib.parse
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

    # YouTube Official Android Innertube Client (Bypasses bot blocks completely)
    endpoint = "https://www.youtube.com/youtubei/v1/player"
    headers = {
        "User-Agent": "com.google.android.youtube/19.09.37 (Linux; U; Android 11) gzip",
        "Content-Type": "application/json",
        "X-YouTube-Client-Name": "3",
        "X-YouTube-Client-Version": "19.09.37"
    }

    payload = {
        "videoId": video_id,
        "context": {
            "client": {
                "clientName": "ANDROID",
                "clientVersion": "19.09.37",
                "androidSdkVersion": 30,
                "hl": "en",
                "gl": "US"
            }
        }
    }

    try:
        res = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        data = res.json()
        
        streaming_data = data.get('streamingData', {})
        formats = streaming_data.get('adaptiveFormats', [])

        # Filter strictly audio streams
        audio_streams = [
            f for f in formats 
            if 'audio' in f.get('mimeType', '') and 'url' in f
        ]

        if not audio_streams:
            # Agar direct url format me nahi mila toh normal formats me dekhein
            audio_streams = [
                f for f in streaming_data.get('formats', [])
                if 'url' in f
            ]

        if audio_streams:
            # Sort by highest audio bitrate
            audio_streams.sort(key=lambda x: x.get('bitrate', 0), reverse=True)
            audio_url = audio_streams[0]['url']
            
            response = redirect(audio_url)
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response

    except Exception as e:
        print(f"Error fetching from Innertube: {e}")

    return jsonify({"error": "Failed to extract clean audio stream. Please test another YouTube link."}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
