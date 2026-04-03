import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
import yt_dlp

app = FastAPI()

# واجهة مستخدم محسنة وتمنع الاختفاء المفاجئ
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
        h1 { color: #f1c40f; margin-bottom: 10px; font-size: 28px; }
        p { color: #888; font-size: 14px; margin-bottom: 25px; }
        input { width: 100%; padding: 15px; border-radius: 12px; border: 2px solid #333; background: #222; color: white; margin-bottom: 15px; box-sizing: border-box; font-size: 16px; outline: none; }
        input:focus { border-color: #f1c40f; }
        button { background: #f1c40f; color: black; border: none; padding: 15px; width: 100%; border-radius: 12px; font-weight: bold; cursor: pointer; font-size: 17px; transition: 0.3s; }
        button:hover { background: #d4ac0d; transform: scale(1.02); }
        #status { margin-top: 20px; color: #f1c40f; font-weight: bold; min-height: 24px; }
        #result-box { margin-top: 25px; display: none; padding: 20px; background: #222; border-radius: 15px; border: 1px dashed #444; }
        .download-btn { display: block; background: #27ae60; color: white; padding: 15px; text-decoration: none; border-radius: 10px; margin-top: 15px; font-weight: bold; font-size: 18px; }
        .download-btn:hover { background: #219150; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🎵 يلا ميوزك</h1>
        <p>تطبيق تحميل الموسيقى الخاص بك</p>
        
        <input type="text" id="urlInput" placeholder="ضع رابط الفيديو هنا (يوتيوب، تيك توك...)">
        <button id="btn" onclick="processDownload()">استخراج الرابط</button>
        
        <div id="status"></div>
        
        <div id="result-box">
            <h4 id="videoTitle" style="margin:0; font-size:15px; color:#ddd;"></h4>
            <a id="dlAction" class="download-btn" href="#">اضغط هنا لبدء التنزيل 📥</a>
        </div>
    </div>

    <script>
        async function processDownload() {
            const url = document.getElementById('urlInput').value;
            const status = document.getElementById('status');
            const resultBox = document.getElementById('result-box');
            const btn = document.getElementById('btn');

            if(!url) return alert("يرجى وضع الرابط أولاً!");

            // تغيير حالة الزر والنص
            btn.disabled = true;
            status.innerText = "جاري جلب البيانات من السيرفر... ⏳";
            resultBox.style.display = "none";

            try {
                const res = await fetch(`/api/extract?url=${encodeURIComponent(url)}`);
                const data = await res.json();
                
                if(data.success) {
                    document.getElementById('videoTitle').innerText = data.title;
                    document.getElementById('dlAction').href = data.download_url;
                    
                    status.innerText = "تم استخراج الرابط بنجاح! ✅";
                    resultBox.style.display = "block";
                } else {
                    status.innerText = "⚠️ فشل الاستخراج، تأكد من الرابط.";
                    alert("خطأ: " + data.error);
                }
            } catch (e) {
                status.innerText = "❌ حدث خطأ في السيرفر.";
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
        'noplaylist': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            # نستخدم مسار البروكسي لتجنب الـ 403
            return {
                "success": True,
                "title": info.get('title'),
                "download_url": f"/proxy?url={video_url}"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/proxy")
async def proxy(url: str):
    def stream_content():
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, stream=True, headers=headers)
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            yield chunk

    # إجبار المتصفح على التحميل كملف MP3
    headers = {"Content-Disposition": 'attachment; filename="yalla-music.mp3"'}
    return StreamingResponse(stream_content(), media_type="audio/mpeg", headers=headers)
