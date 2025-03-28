from flask import Flask, request, jsonify
from pytube import YouTube
import os

app = Flask(__name__)

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')

    try:
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        file_path = stream.download(output_path='downloads')
        download_link = f"/downloads/{os.path.basename(file_path)}"
        return jsonify({'success': True, 'download_link': download_link})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# تشغيل الخادم المدمج فقط إذا تم تشغيل الملف مباشرة (محليًا)
if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(debug=True, host='0.0.0.0', port=5000)