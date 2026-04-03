import os
import requests
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse, StreamingResponse
import yt_dlp

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <html>
    <body style="background:#111; color:white; text-align:center; padding-top:50px; font-family:sans-serif;">
        <h1>🎵 يلا ميوزك شغال!</h1>
        <p>انسخ الرابط وجربه في خانة الاستخراج</p>
    </body>
    </html>
    """

@app.get("/api/extract")
async def extract(url: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            # نرسل رابط البروكسي بدلاً من الرابط المباشر لتجنب 403
            return {
                "success": True,
                "title": info.get('title'),
                "download_url": f"/proxy?url={video_url}"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/proxy")
async def proxy(url: str):
    # تمرير البيانات بقطع صغيرة (Chunked) لتقليل الضغط على السيرفر
    def stream_content():
        r = requests.get(url, stream=True, timeout=10)
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            if chunk:
                yield chunk

    return StreamingResponse(stream_content(), media_type="audio/mpeg")
