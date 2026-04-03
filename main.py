from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from yt_dlp import YoutubeDL

app = FastAPI()

# واجهة الموقع (HTML + CSS)
html_content = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>يلا ميوزك - Yalla Music</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #121212; color: white; text-align: center; padding: 50px; }
        .container { max-width: 600 : margin: auto; background: #1e1e1e; padding: 30px; border-radius: 15px; box-shadow: 0 0 20px rgba(0,0,0,0.5); }
        h1 { color: #f1c40f; }
        input { width: 80%; padding: 12px; border-radius: 5px; border: none; margin-bottom: 20px; font-size: 16px; }
        button { background-color: #f1c40f; color: black; border: none; padding: 12px 25px; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 16px; }
        button:hover { background-color: #d4ac0d; }
        #result { margin-top: 30px; }
        img { max-width: 100%; border-radius: 10px; margin-top: 10px; }
        a { color: #f1c40f; text-decoration: none; font-weight: bold; display: block; margin-top: 15px; background: #333; padding: 10px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 يلا ميوزك - Yalla Music</h1>
        <p>حمل موسيقاك المفضلة بسهولة</p>
        <input type="text" id="videoUrl" placeholder="ضع رابط الفيديو هنا (يوتيوب، تيك توك...)">
        <br>
        <button onclick="getDownloadLink()">استخراج رابط التحميل</button>
        
        <div id="result"></div>
    </div>

    <script>
        async function getDownloadLink() {
            const url = document.getElementById('videoUrl').value;
            const resultDiv = document.getElementById('result');
            if(!url) { alert("يرجى وضع رابط!"); return; }
            
            resultDiv.innerHTML = "جاري المعالجة... انتظر قليلاً ⏳";
            
            try {
                const response = await fetch(`/download?url=${encodeURIComponent(url)}`);
                const data = await response.json();
                
                if(data.download_url) {
                    resultDiv.innerHTML = `
                        <h3>${data.title}</h3>
                        <img src="${data.thumbnail}" alt="thumbnail">
                        <a href="${data.download_url}" target="_blank">اضغط هنا للتحميل المباشر 📥</a>
                    `;
                } else {
                    resultDiv.innerHTML = "عذراً، تعذر استخراج الرابط. تأكد من الرابط وحاول مجدداً.";
                }
            } catch (error) {
                resultDiv.innerHTML = "حدث خطأ في الاتصال بالسيرفر.";
            }
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
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get('title'),
                "download_url": info.get('url'),
                "thumbnail": info.get('thumbnail')
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
