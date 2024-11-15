from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from collections import Counter
import re
import PyPDF2
import tempfile
import os

# Anahtar kelimeleri ve ilgili alanları tanımlayalım
keywords = {
    "web_development": [
        "javascript", "html", "css", "react", "angular", "vue", 
        "node", "php", "ruby", "rails", "django", "flask", 
        "sass", "typescript", "bootstrap", "jquery", "graphql",
        "express", "next.js", "ruby on rails", "websockets", "ajax"
    ],
    "data_science": [
        "python", "pandas", "numpy", "matplotlib", "scikit-learn", 
        "tensorflow", "data", "analysis", "machine learning", 
        "deep learning", "statistics", "data visualization", 
        "big data", "spark", "pyspark", "R", "sql", "seaborn", 
        "data mining", "data wrangling", "numpy", "azure ml"
    ],
    "mobile_development": [
        "android", "ios", "flutter", "react native", "swift", 
        "java", "kotlin", "objective-c", "xamarin", "ionic", 
        "cordova", "mobile app design", "firebase", "flutter", 
        "MVVM", "REST", "API", "user interface", "user experience"
    ],
    "devops": [
        "docker", "kubernetes", "ci", "cd", "cloud", 
        "aws", "azure", "linux", "ansible", "terraform", 
        "jenkins", "git", "gitlab", "monitoring", "logging", 
        "prometheus", "grafana", "unix", "bash scripting", 
        "serverless", "microservices", "virtualization"
    ],
    "game_development": [
        "unity", "unreal", "c#", "java", "game design", 
        "graphics", "game engine", "2D", "3D", "gamification", 
        "augmented reality", "virtual reality", "C++", 
        "game physics", "AI in games", "multiplayer", 
        "game monetization", "sprite", "game mechanics", "asset"
    ],
}


# CV'yi analiz eden fonksiyon
def process_cv(cv_text):
    cv_text = cv_text.lower()
    cv_text = re.sub(r'[^a-z\s]', '', cv_text)
    
    words = cv_text.split()
    word_counter = Counter(words)
    
    results = {category: sum(word_counter[keyword] for keyword in keywords[category]) for category in keywords}
    
    return results

# PDF dosyasını okuma fonksiyonu
def read_pdf(file_path):
    pdf_text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in range(len(reader.pages)):
            pdf_text += reader.pages[page].extract_text() or ""
    return pdf_text

# HTTP isteklerini işleyecek sınıf
class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # Anasayfa isteği
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'r', encoding='utf-8') as file:  # index.html'yi döndür
                self.wfile.write(file.read().encode('utf-8'))
        else:
            # Bulunamayan sayfa
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/upload':
            # İçeriğin uzunluğunu al
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            # Geçici bir dosya olarak dosyayı kaydet
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(post_data)
                temp_file_path = temp_file.name
            
            # PDF dosyasını oku ve analiz et
            cv_text = read_pdf(temp_file_path)
            analysis_result = process_cv(cv_text)

            # Geçici dosyayı sil
            os.remove(temp_file_path)

            # JSON formatında sonuç döndür
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(analysis_result).encode('utf-8'))

# Sunucu oluşturma ve çalıştırma
def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Sunucu çalışıyor, http://localhost:{port}/ adresini ziyaret edin...')
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Sunucu durduruluyor...")
    except Exception as e:
        print(f'Hata: {e}')
    finally:
        httpd.server_close()
        print("Sunucu kapatıldı.")
if __name__ == "__main__":
    run()
