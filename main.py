import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
import yt_dlp

app = FastAPI()

# واجهة المستخدم الاحترافية لـ "يلا ميوزك"
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>يلا ميوزك | Yalla Music</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #0f0f0f; color: #ffffff; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .card { background: #1a1a1a; padding: 2rem; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); width: 90%; max-width: 500px; text-align: center; border: 1px solid #333; }
        h1 { color: #ff0000; font-size: 2.5rem; margin-bottom: 0.5rem; }
        p { color: #aaa; margin-bottom: 2rem; }
        input { width: 100%; padding: 15px; border-radius: 10px; border: 2px solid #333; background: #111; color: #fff; box-sizing: border-box; margin-bottom: 1rem; font-size: 1rem; }
        input:focus { border-color: #ff0000; outline: none; }
        button { background: #ff0000; color: #fff; border: none; padding: 15px 30px; border-radius: 10px; cursor: pointer; font-weight: bold; width: 100%; font-size: 1.1rem; transition: 0.3s; }
        button:hover { background: #cc0000; transform: translateY(-2px); }
        #loader { display: none; margin-top: 20px; color: #f1c40f; }
        #result { margin-top: 25px; display: none; padding: 15px; background: #222; border-radius: 10px; }
        .thumb { width: 100%; border-radius: 10px; margin-bottom: 10px; }
        .download-btn { background: #27ae60; text-decoration: none; color: white; padding: 10px; display: block; border-radius: 8px; margin-top: 10px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🎵 يلا ميوزك</h1>
        <p>حمل الموسيقى والفيديوهات بضغطة زر</p>
        <input type="text" id="urlInput" placeholder="صق رابط الفيديو هنا...">
        <button onclick="startDownload()">استخراج الرابط</button>
        
        <div id="loader">جاري الفحص وتخطى الحظر... ⏳</div>
        
        <div id="result">
            <img id="thumb" class="thumb" src="" alt="thumbnail">
            <h3 id="title" style="font-size: 1rem;"></h3>
            <a id="link" class="download-btn" href="#" target="_blank">تحميل الآن 📥</a>
        </div>
    </div>

    <script>
        async function startDownload() {
            const url = document.getElementById('urlInput').value;
            const loader = document.getElementById('loader');
            const result = document.getElementById('result');
            
            if(!url) return alert("الرجاء وضع رابط!");

            loader.style.display = "block";
            result.style.display = "none";

            try {
                const response = await fetch(`/api/extract?url=${encodeURIComponent(url)}`);
                const data = await response.json();
                
                loader.style.display = "none";
                if(data.success) {
                    document.getElementById('thumb').src = data.thumbnail;
                    document.getElementById('title').innerText = data.title;
                    document.getElementById('link').href = data.download_url;
                    result.style.display = "block";
                } else {
                    alert("فشل الاستخراج: " + (data.error || "حاول مرة أخرى"));
                }
            } catch (e) {
                loader.style.display = "none";
                alert("خطأ في السيرفر!");
            }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_TEMPLATE

@app.get("/api/extract")
async def extract(url: str):
    # خيارات متقدمة جداً لتجاوز حظر يوتيوب
    ydl_opts = {
        'format': 'bestaudio/best/best',
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        # 'cookiefile': 'cookies.txt', # فعل هذا السطر بعد رفع ملف cookies.txt
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'http_headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "success": True,
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "download_url": info.get('url')
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
