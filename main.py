from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import yt_dlp

app = FastAPI()

# الواجهة كما هي (يمكنك الإبقاء عليها)
@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/download")
def download_music(url: str):
    try:
        # هذه الإعدادات هي الأقوى لتجاوز حظر المواقع
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            # محاكاة متصفح موبايل أندرويد
            'user_agent': 'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36',
            'http_headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
            }
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # جلب الرابط المباشر
            video_url = info.get('url')
            if not video_url:
                # محاولة ثانية بأسلوب مختلف إذا فشل الأول
                formats = info.get('formats', [])
                video_url = formats[-1].get('url')

            return {
                "title": info.get('title'),
                "download_url": video_url,
                "thumbnail": info.get('thumbnail')
            }
    except Exception as e:
        return {"error": str(e)}
