from flask import Flask, request, jsonify
import yt_dlp
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
        # إعدادات yt-dlp مع رؤوس HTTP لمحاكاة متصفح حقيقي
        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',  # حفظ الفيديو في مجلد downloads
            'format': 'best',  # اختيار أفضل جودة
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.google.com/',
            },
            # (اختياري) استخدام ملف تعريف الارتباط إذا كنت بحاجة إلى تسجيل الدخول
            # 'cookiefile': 'cookies.txt',  # أزل التعليق إذا كنت تستخدم ملف تعريف الارتباط
            # (اختياري) استخدام بيانات تسجيل الدخول عبر متغيرات بيئية
            # 'username': os.getenv('INSTAGRAM_USERNAME'),
            # 'password': os.getenv('INSTAGRAM_PASSWORD'),
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