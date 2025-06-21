import os
from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__, static_folder='static', template_folder='templates')

DOWNLOAD_DIR = "/tmp/downloads"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/baixar", methods=["POST"])
def baixar():
    data = request.get_json()
    url = data.get("url")
    formato = data.get("format")

    if not url or not formato:
        return jsonify({"status": "error", "message": "Parâmetros ausentes"})

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    ydl_opts = {
        "format": "bestaudio/best" if formato == "mp3" else "bestvideo+bestaudio/best",
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
        "postprocessors": [],
        "quiet": True,
        "geo_bypass": True,  # tenta ignorar bloqueios regionais
    }

    if formato == "mp3":
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    elif formato in ["mp4", "mkv"]:
        ydl_opts["merge_output_format"] = formato

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
