from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from yt_dlp import YoutubeDL

app = FastAPI()

html_content = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>يلا ميوزك - Yalla Music</title>
    <style>
        body { font-family: sans-serif; background-color: #121212; color: white; text-align: center; padding: 50px; }
        .container { max-width: 600px; margin: auto; background: #1e1e1e; padding: 30px; border-radius: 15px; }
        h1 { color: #f1c40f; }
        input { width: 80%; padding: 12px; margin-bottom: 20px; border-radius: 5px; border: none; }
        button { background-color: #f1c40f; border: none; padding: 12px 25px; border-radius: 5px; cursor: pointer; font-weight: bold; }
        #result { margin-top: 30px; }
        a { color: #f1c40f; text-decoration: none; display: block; margin-top: 15px; background: #333; padding: 10px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 يلا ميوزك - Yalla Music</h1>
        <input type="text" id="videoUrl" placeholder="ضع رابط الفيديو هنا...">
        <br>
        <button onclick="getDownloadLink()">استخراج رابط التحميل</button>
        <div id="result"></div>
    </div>
    <script>
        async function getDownloadLink() {
            const url = document.getElementById('videoUrl').value;
            const resultDiv = document.getElementById('result');
            if(!url) return;
            resultDiv.innerHTML = "جاري المحاولة بطريقة متقدمة... ⏳";
            try {
                const response = await fetch(`/download?url=${encodeURIComponent(url)}`);
                const data = await response.json();
                if(data.download_url) {
                    resultDiv.innerHTML = `<h3>${data.title}</h3><a href="${data.download_url}" target="_blank">تحميل مباشر (MP3/Audio) 📥</a>`;
                } else {
                    resultDiv.innerHTML = "فشل الاستخراج. جرب رابطاً آخر أو انتظر دقيقة.";
                }
            } catch (error) { resultDiv.innerHTML = "خطأ في السيرفر."; }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return html_content

@app.get("/download")
def download_music(url: str):
    try:
        # خيارات متقدمة لتجاوز الحظر
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'source_address': '0.0.0.0', # لإجبار استخدام IPv4
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # نختار الرابط المباشر
            return {
                "title": info.get('title'),
                "download_url": info.get('url'),
                "thumbnail": info.get('thumbnail')
            }
    except Exception as e:
        print(f"Error: {e}") # سيظهر لك في Logs الخاصة بـ Railway
        return {"error": str(e)}
