import os
import requests
import urllib.parse
from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse, StreamingResponse
import yt_dlp

app = FastAPI()

# الواجهة كما هي
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>يلا ميوزك - Yalla Music</title>
    <style>
        body { font-family: sans-serif; background: #0b0b0b; color: white; text-align: center; padding: 40px 10px; }
        .card { background: #161616; padding: 30px; border-radius: 20px; max-width: 450px; margin: auto; border: 1px solid #333; }
        input { width: 100%; padding: 15px; border-radius: 12px; border: none; background: #222; color: white; margin-bottom: 15px; box-sizing: border-box; }
        button { background: #f1c40f; color: black; border: none; padding: 15px; width: 100%; border-radius: 12px; font-weight: bold; cursor: pointer; }
        #status { margin-top: 20px; color: #f1c40f; }
        #result-box { margin-top: 25px; display: none; padding: 20px; background: #222; border-radius: 15px; }
        .download-btn { display: block; background: #27ae60; color: white; padding: 15px; text-decoration: none; border-radius: 10px; margin-top: 15px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🎵 يلا ميوزك</h1>
        <input type="text" id="urlInput" placeholder="ضع رابط الفيديو هنا...">
        <button id="btn" onclick="processDownload()">استخراج وتحميل</button>
        <div id="status"></div>
        <div id="result-box">
            <h4 id="vTitle" style="margin-bottom:15px; color:#f1c40f;"></h4>
            <a id="dlAction" class="download-btn" href="#">اضغط هنا لبدء التنزيل 📥</a>
        </div>
    </div>
    <script>
        async function processDownload() {
            const url = document.getElementById('urlInput').value;
            const status = document.getElementById('status');
            const resBox = document.getElementById('result-box');
            if(!url) return alert("ضع الرابط!");
            status.innerText = "جاري المعالجة... ⏳";
            resBox.style.display = "none";
            try {
                const res = await fetch(`/api/extract?url=${encodeURIComponent(url)}`);
                const data = await res.json();
                if(data.success) {
                    document.getElementById('vTitle').innerText = data.title;
                    document.getElementById('dlAction').href = data.download_url;
                    status.innerText = "تم بنجاح! ✅";
                    resBox.style.display = "block";
                } else { status.innerText = "فشل: " + data.error; }
            } catch (e) { status.innerText = "خطأ في السيرفر (500)"; }
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
    ydl_opts = {'format': 'bestaudio/best', 'quiet': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'music')
            # نمرر الرابط للبروكسي
            return {
                "success": True,
                "title": title,
                "download_url": f"/proxy?url={urllib.parse.quote(info.get('url'))}&name={urllib.parse.quote(title)}"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/proxy")
async def proxy(url: str, name: str = "music"):
    # فك تشفير الرابط والاسم
    target_url = urllib.parse.unquote(url)
    target_name = urllib.parse.unquote(name)
    
    def stream_content():
        # نستخدم جلسة (Session) لسرعة الطلب وتفادي الخطأ 500
        with requests.Session() as session:
            r = session.get(target_url, stream=True, timeout=20)
            # نرفع حجم الـ Chunk لتقليل الضغط على المعالج
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    yield chunk

    headers = {
        "Content-Disposition": f'attachment; filename="{target_name}.mp3"',
        "Content-Type": "audio/mpeg"
    }
    return StreamingResponse(stream_content(), headers=headers)
