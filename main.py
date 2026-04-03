import os
import requests
import urllib.parse
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
import yt_dlp

app = FastAPI()

# واجهة مستخدم احترافية تظهر تفاصيل الأغنية
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>يلا ميوزك - Yalla Music</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #0b0b0b; color: white; text-align: center; padding: 40px 10px; }
        .card { background: #161616; padding: 30px; border-radius: 20px; max-width: 450px; margin: auto; border: 1px solid #333; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        h1 { color: #f1c40f; margin-bottom: 20px; }
        input { width: 100%; padding: 15px; border-radius: 12px; border: 2px solid #333; background: #222; color: white; margin-bottom: 15px; box-sizing: border-box; font-size: 16px; outline: none; }
        input:focus { border-color: #f1c40f; }
        button { background: #f1c40f; color: black; border: none; padding: 15px; width: 100%; border-radius: 12px; font-weight: bold; cursor: pointer; font-size: 17px; }
        #status { margin-top: 20px; color: #f1c40f; }
        #result-box { margin-top: 25px; display: none; padding: 20px; background: #222; border-radius: 15px; }
        .thumb { width: 100%; border-radius: 10px; margin-bottom: 10px; border: 1px solid #444; }
        .download-btn { display: block; background: #27ae60; color: white; padding: 15px; text-decoration: none; border-radius: 10px; margin-top: 15px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🎵 يلا ميوزك</h1>
        <input type="text" id="urlInput" placeholder="صق رابط الفيديو هنا...">
        <button id="btn" onclick="processDownload()">استخراج وتحميل</button>
        <div id="status"></div>
        <div id="result-box" id="resBox">
            <img id="vThumb" class="thumb" src="" alt="">
            <h4 id="vTitle" style="margin:10px 0; color:#f1c40f;"></h4>
            <a id="dlAction" class="download-btn" href="#">تحميل ملف الـ MP3 الآن 📥</a>
        </div>
    </div>

    <script>
        async function processDownload() {
            const url = document.getElementById('urlInput').value;
            const status = document.getElementById('status');
            const resBox = document.getElementById('result-box');
            const btn = document.getElementById('btn');

            if(!url) return alert("يرجى وضع الرابط!");

            btn.disabled = true;
            status.innerText = "جاري استخراج اسم الأغنية والروابط... ⏳";
            resBox.style.display = "none";

            try {
                const res = await fetch(`/api/extract?url=${encodeURIComponent(url)}`);
                const data = await res.json();
                
                if(data.success) {
                    document.getElementById('vTitle').innerText = data.title;
                    document.getElementById('vThumb').src = data.thumbnail;
                    document.getElementById('dlAction').href = data.download_url;
                    
                    status.innerText = "تم بنجاح! جاهز للتحميل ✅";
                    resBox.style.display = "block";
                } else {
                    status.innerText = "⚠️ فشل الاستخراج، جرب رابطاً آخر.";
                }
            } catch (e) {
                status.innerText = "❌ خطأ في السيرفر.";
            } finally {
                btn.disabled = false;
            }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_CONTENT

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
            title = info.get('title', 'music')
            # نرسل اسم الأغنية في الرابط لكي يستخدمه البروكسي عند التحميل
            safe_title = urllib.parse.quote(title)
            return {
                "success": True,
                "title": title,
                "thumbnail": info.get('thumbnail'),
                "download_url": f"/proxy?url={info.get('url')}&name={safe_title}"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/proxy")
async def proxy(url: str, name: str = "music"):
    def stream_content():
        headers = {'User-Agent': 'Mozilla/5.0'}
        with requests.get(url, stream=True, headers=headers) as r:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                yield chunk

    # فك تشفير الاسم وتعيينه كاسم للملف المحمل
    decoded_name = urllib.parse.unquote(name)
    headers = {
        "Content-Disposition": f'attachment; filename="{decoded_name}.mp3"'
    }
    return StreamingResponse(stream_content(), media_type="audio/mpeg", headers=headers)
