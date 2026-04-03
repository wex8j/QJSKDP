import os
import requests
import urllib.parse
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
import yt_dlp

app = FastAPI()

# واجهة مستخدم محسنة مع "نظام كشف أخطاء"
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>يلا ميوزك - النسخة المستقرة</title>
    <style>
        body { font-family: sans-serif; background: #0b0b0b; color: white; text-align: center; padding: 30px 10px; }
        .card { background: #1a1a1a; padding: 25px; border-radius: 15px; max-width: 450px; margin: auto; border: 2px solid #333; }
        h1 { color: #f1c40f; }
        input { width: 100%; padding: 15px; border-radius: 10px; border: none; background: #222; color: white; margin-bottom: 15px; box-sizing: border-box; }
        #btn { background: #f1c40f; color: black; border: none; padding: 15px; width: 100%; border-radius: 10px; font-weight: bold; cursor: pointer; font-size: 18px; }
        #btn:disabled { background: #555; cursor: not-allowed; }
        #status { margin: 20px 0; color: #aaa; font-size: 14px; }
        #result-box { display: none; background: #222; padding: 20px; border-radius: 15px; border: 2px solid #27ae60; margin-top: 20px; }
        .thumb { width: 100%; border-radius: 10px; margin-bottom: 15px; }
        .download-btn { display: block; background: #27ae60; color: white; padding: 15px; text-decoration: none; border-radius: 10px; font-weight: bold; font-size: 18px; }
        .error-msg { color: #e74c3c; background: #321; padding: 10px; border-radius: 10px; margin-top: 10px; display: none; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🎵 يلا ميوزك</h1>
        <p>إذا اختفت النتيجة، يرجى تحديث الصفحة</p>
        <input type="text" id="urlInput" placeholder="ضع رابط الفيديو هنا...">
        <button id="btn" onclick="startWork()">ابدأ الاستخراج الآن</button>
        
        <div id="status">جاهز للعمل...</div>
        <div id="errorBox" class="error-msg"></div>

        <div id="result-box">
            <img id="vThumb" class="thumb" src="">
            <h3 id="vTitle" style="color:#f1c40f; margin-bottom:15px;"></h3>
            <a id="dlAction" class="download-btn" href="#">تحميل بصيغة MP3 📥</a>
        </div>
    </div>

    <script>
        async function startWork() {
            const url = document.getElementById('urlInput').value;
            const btn = document.getElementById('btn');
            const status = document.getElementById('status');
            const resBox = document.getElementById('result-box');
            const errorBox = document.getElementById('errorBox');

            if(!url) return alert("الرجاء وضع رابط!");

            // تحضير الواجهة
            btn.disabled = true;
            status.innerText = "جاري الاتصال بالسيرفر وتجاوز حظر يوتيوب... ⏳";
            resBox.style.display = "none";
            errorBox.style.display = "none";

            try {
                const response = await fetch(`/api/extract?url=${encodeURIComponent(url)}`);
                const data = await response.json();

                if (data.success) {
                    document.getElementById('vTitle').innerText = data.title;
                    document.getElementById('vThumb').src = data.thumbnail;
                    document.getElementById('dlAction').href = data.download_url;
                    
                    status.innerText = "اكتمل بنجاح! ✅";
                    resBox.style.display = "block"; // إظهار النتيجة بقوة
                } else {
                    status.innerText = "فشل الاستخراج";
                    errorBox.innerText = "خطأ السيرفر: " + data.error;
                    errorBox.style.display = "block";
                }
            } catch (err) {
                status.innerText = "خطأ في الشبكة";
                errorBox.innerText = "تعذر الاتصال بالسيرفر. تأكد أن Railway شغال.";
                errorBox.style.display = "block";
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
        'nocheckcertificate': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'music_file')
            # تجهيز رابط البروكسي مع اسم الملف
            safe_name = urllib.parse.quote(title)
            return {
                "success": True,
                "title": title,
                "thumbnail": info.get('thumbnail'),
                "download_url": f"/proxy?url={info.get('url')}&name={safe_name}"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/proxy")
async def proxy(url: str, name: str = "music"):
    def stream_content():
        headers = {'User-Agent': 'Mozilla/5.0'}
        with requests.get(url, stream=True, headers=headers) as r:
            for chunk in r.iter_content(chunk_size=1024 * 512):
                yield chunk

    decoded_name = urllib.parse.unquote(name)
    headers = {"Content-Disposition": f'attachment; filename="{decoded_name}.mp3"'}
    return StreamingResponse(stream_content(), media_type="audio/mpeg", headers=headers)
