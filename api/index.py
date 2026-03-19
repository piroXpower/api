from flask import Flask, request, Response
import requests

app = Flask(__name__)

# CONFIGURATION
RAPID_KEY = "8200be2accmsh7b5a6a90b3e980cp1744f7jsnc85a9325546d"
RAPID_HOST = "youtube-media-downloader.p.rapidapi.com"

@app.route('/')
def home():
    return "Vercel Proxy is Running!"

@app.route('/stream')
def stream_proxy():
    video_id = request.args.get('id')
    if not video_id:
        return "Missing Video ID", 400

    # 1. Get the actual Google Video link from RapidAPI
    api_url = f"https://{RAPID_HOST}/v2/video/details"
    headers = {
        "x-rapidapi-key": RAPID_KEY,
        "x-rapidapi-host": RAPID_HOST
    }
    
    try:
        res = requests.get(api_url, headers=headers, params={"videoId": video_id}, timeout=10)
        data = res.json()
        
        # Get the first audio URL
        audios = data.get("audios", {}).get("items", [])
        if not audios:
            return "No Audio Found", 404
        
        target_url = audios[0].get("url")

        # 2. PIPE the data: Vercel downloads and sends it to the VPS simultaneously
        def generate():
            # Using a real Browser User-Agent to avoid blocks
            req_headers = {"User-Agent": "Mozilla/5.0"}
            with requests.get(target_url, headers=req_headers, stream=True) as r:
                for chunk in r.iter_content(chunk_size=1024*16):
                    if chunk:
                        yield chunk

        return Response(generate(), content_type='audio/mpeg')

    except Exception as e:
        return str(e), 500
      
