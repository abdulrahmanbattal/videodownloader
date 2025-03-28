from flask import Flask, request, jsonify
from googleapiclient.discovery import build
import yt_dlp
import os

app = Flask(__name__)

# استخدام مفتاح API الخاص بك
YOUTUBE_API_KEY = 'AIzaSyCoGcU17wqXryWrheUHZc6om-3zj84_8YU'
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')

    try:
        # استخراج معرف الفيديو من الرابط
        video_id = url.split('v=')[1]
        if '&' in video_id:
            video_id = video_id.split('&')[0]

        # استخدام YouTube API للتحقق من الفيديو
        request = youtube.videos().list(part='snippet', id=video_id)
        response = request.execute()

        if not response['items']:
            return jsonify({'success': False, 'error': 'الفيديو غير موجود'})

        # تحميل الفيديو باستخدام yt-dlp
        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',  # حفظ الفيديو في مجلد downloads
            'format': 'best',  # اختيار أفضل جودة
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            download_link = f"/downloads/{os.path.basename(file_path)}"

        return jsonify({'success': True, 'download_link': download_link})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# توفير الملفات المحملة للتنزيل
@app.route('/downloads/<filename>')
def serve_file(filename):
    return app.send_file(f'downloads/{filename}', as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(debug=True, host='0.0.0.0', port=5000)