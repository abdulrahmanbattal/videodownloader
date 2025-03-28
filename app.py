from flask import Flask, request, jsonify, send_file
import yt_dlp
import os
import logging
import urllib.parse

# إعداد التسجيل (Logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    logger.info("Serving index.html")
    return app.send_static_file('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    logger.info(f"Received download request for URL: {url}")

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
            # استخدام username وpassword لإنستغرام
            'username': os.getenv('INSTAGRAM_USERNAME'),
            'password': os.getenv('INSTAGRAM_PASSWORD'),
            # استخدام ملف تعريف الارتباط ليوتيوب
            'cookiefile': 'cookies.txt',
            # إعدادات إضافية لتحسين التعامل مع يوتيوب
            'noplaylist': True,  # تحميل الفيديو الفردي فقط
            'ignoreerrors': True,  # تجاهل الأخطاء البسيطة
        }

        logger.info("Starting video download with yt-dlp")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                logger.error("Failed to extract video info")
                return jsonify({'success': False, 'error': 'فشل في استخراج معلومات الفيديو'}), 500
            file_path = ydl.prepare_filename(info)
            logger.info(f"File path after download: {file_path}")
            # التأكد من أن الملف موجود
            if not os.path.exists(file_path):
                logger.error(f"File not found after download: {file_path}")
                return jsonify({'success': False, 'error': 'فشل في تحميل الفيديو: الملف غير موجود'}), 500
            download_link = f"/downloads/{urllib.parse.quote(os.path.basename(file_path))}"
            logger.info(f"Video downloaded successfully. Download link: {download_link}")

        return jsonify({'success': True, 'download_link': download_link})

    except Exception as e:
        logger.error(f"Error downloading video: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

# توفير الملفات المحملة للتنزيل
@app.route('/downloads/<path:filename>')
def serve_file(filename):
    try:
        # فك تشفير اسم الملف للتعامل مع المسافات والأحرف الخاصة
        filename = urllib.parse.unquote(filename)
        file_path = os.path.join('downloads', filename)
        logger.info(f"Serving file: {file_path}")

        # التحقق من وجود الملف
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return jsonify({'success': False, 'error': f'الملف {filename} غير موجود'}), 404

        return send_file(file_path, as_attachment=True)

    except Exception as e:
        logger.error(f"Error serving file {filename}: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads', mode=0o777)  # إنشاء المجلد بأذونات كاملة
    # التأكد من أذونات ملف cookies.txt
    if os.path.exists('cookies.txt'):
        os.chmod('cookies.txt', 0o666)  # إعطاء أذونات قراءة وكتابة
    app.run(debug=True, host='0.0.0.0', port=5000)