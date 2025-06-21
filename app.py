import os
from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__, static_folder='static', template_folder='templates')

# Caminho do ffmpeg (confirme que essa pasta existe e está junto do executável)
FFMPEG_PATH = r"C:\Biblioteca\Noctune\noctune-backend\ffmpeg\bin\ffmpeg.exe"

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route("/selecionar_pasta")
def selecionar_pasta():
    # Removido tkinter porque não funciona em servidor remoto
    return jsonify({"caminho": ""})

@app.route("/baixar", methods=["POST"])
def baixar():
    data = request.get_json()
    url = data.get("url")
    formato = data.get("format")
    pasta = data.get("folder")

    if not url or not pasta or not formato:
        return jsonify({"status": "error", "message": "Parâmetros incompletos"})

    ydl_opts = {
        "format": "bestaudio/best" if formato == "mp3" else "bestvideo+bestaudio/best",
        "outtmpl": os.path.join(pasta, "%(title)s.%(ext)s"),
        "postprocessors": [],
        "ffmpeg_location": os.path.dirname(FFMPEG_PATH),
        "quiet": True,
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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

