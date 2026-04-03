import os
import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
import yt_dlp

app = FastAPI()

# الواجهة (كما هي)
@app.get("/", response_class=HTMLResponse)
async def index():
    return open("index.html", "r", encoding="utf-8").read() if os.path.exists("index.html") else "Yalla Music is Running!"

@app.get("/api/extract")
async def extract(url: str, request: Request):
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        # 'cookiefile': 'cookies.txt', # استخدمه إذا استمر الحظر
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            
            # بدلاً من إعطاء الرابط المباشر، نعطيه رابط من سيرفرنا نحن
            # لكي يقوم سيرفرنا بجلب البيانات وتمريرها لك
            proxy_url = f"{request.base_url}proxy?url={video_url}"
            
            return {
                "success": True,
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "download_url": proxy_url # الرابط الجديد عبر سيرفرك
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

# هذه الوظيفة هي التي تحل مشكلة الـ 403
@app.get("/proxy")
async def proxy(url: str):
    def stream_video():
        with requests.get(url, stream=True) as r:
            for chunk in r.iter_content(chunk_size=1024*1024):
                yield chunk
    
    return StreamingResponse(stream_video(), media_type="audio/mpeg")
