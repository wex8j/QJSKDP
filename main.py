import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
import yt_dlp

app = FastAPI()

# واجهة الموقع المتكاملة
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>يلا ميوزك - Yalla Music</title>
    <style>
        body { font-family: sans-serif; background: #0b0b0b; color: white; text-align: center; padding: 50px 20px; }
        .card { background: #161616; padding: 30px; border-radius: 20px; max-width: 500px; margin: auto; border: 1px solid #333; }
        h1 { color: #f1c40f; margin-bottom: 20px; }
        input { width: 100%; padding: 15px; border-radius: 10px; border: none; background: #222; color: white; margin-bottom: 20px; box-sizing: border-box; }
        button { background: #f1c40f; color: black; border: none; padding: 15px; width: 100%; border-radius: 10px; font-weight: bold; cursor: pointer; }
        #status { margin-top: 20px; color: #aaa; }
        #result { margin-top: 20px; display: none; }
        .download-btn { display: block; background: #27ae60; color: white; padding: 15px; text-decoration: none; border-radius: 10px; margin-top: 10px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🎵 يلا ميوزك</h1>
        <input type="text" id="urlInput" placeholder="ضع رابط الفيديو هنا...">
        <button onclick="extract()">استخراج الرابط</button>
        <div id="status"></div>
        <div id="result">
            <h3 id="title"></h3>
            <a id="dlLink" class="download-btn" href="">تحميل الآن 📥</a>
        </div>
    </div>

    <script>
        async function extract() {
            const url = document.getElementById('urlInput').value;
            const status = document.getElementById('status');
            const result = document.getElementById('result');
            if(!url) return alert("ضع الرابط أولاً!");

            status.innerText = "جاري التحضير... انتظر ثواني ⏳";
            result.style.display = "none";

            try {
                const res = await fetch(`/api/extract?url=${encodeURIComponent(url)}`);
                const data = await res.json();
                status.innerText = "";
                if(data.success) {
                    document.getElementById('title').innerText = data.title;
                    document.getElementById('dlLink').href = data.download_url;
                    result.style.display = "block";
                } else {
                    status.innerText = "فشل: " + data.error;
                }
            } catch (e) { status.innerText = "خطأ في الاتصال بالسيرفر"; }
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
            video_url = info.get('url')
            # نربط الزر بمسار البروكسي لنتجنب حظر يوتيوب 403
            return {
                "success": True,
                "title": info.get('title'),
                "download_url": f"/proxy?url={video_url}&title={info.get('title')}"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/proxy")
async def proxy(url: str, title: str = "music"):
    def stream_content():
        # نستخدم Headers تجعل يوتيوب يظن أننا متصفح عادي
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, stream=True, headers=headers)
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            yield chunk

    # نجعل المتصفح يحمل الملف بدلاً من تشغيله
    content_disposition = f'attachment; filename="{title}.mp3"'
    return StreamingResponse(stream_content(), media_type="audio/mpeg", headers={"Content-Disposition": content_disposition})
