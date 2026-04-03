from fastapi import FastAPI, HTTPException
from yt_dlp import YoutubeDL

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to Yalla Music API"}

@app.get("/download")
def download_music(url: str):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get('title'),
                "download_url": info.get('url'),
                "thumbnail": info.get('thumbnail'),
                "duration": info.get('duration')
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
