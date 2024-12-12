from flask import Flask, request, render_template, redirect, url_for, g
import pandas as pd
from disease_api import SymptomAnalyzer
import time
import gc
from prometheus_client import Counter, generate_latest, Histogram

# 定義指標
http_requests_total = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'status'])
http_request_duration = Histogram('http_request_duration_seconds', 'HTTP Request Duration', ['method', 'endpoint'])
error_requests_total = Counter('error_requests_total', 'Total Error HTTP Requests', ['method', 'endpoint', 'status'])

# 定義 Flask 應用
app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')

@app.before_request
def start_timer():
    g.start_time = time.time()

@app.after_request
def track_request(response):
    # 計算請求持續時間
    duration = time.time() - g.start_time

    # 記錄請求數據
    http_requests_total.labels(request.method, request.path, response.status_code).inc()
    http_request_duration.labels(request.method, request.path).observe(duration)

    # 如果是錯誤請求，記錄到 error_requests_total
    if 400 <= response.status_code < 600:
        error_requests_total.labels(request.method, request.path, response.status_code).inc()

    return response

@app.route('/metrics')
def metrics():
    # 暴露所有指標數據
    return generate_latest(), 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/disease', methods=['POST'])
def disease():
    # 模擬一個正常請求的處理
    return {"result": "example disease"}, 200

@app.route('/error')
def error():
    # 模擬一個錯誤請求
    return {"error": "This is a simulated error!"}, 500
    
analyzer = SymptomAnalyzer()
analyzer.load_diseases('disease_data.csv')

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_symptom':
            symptom = request.form.get('symptom')
            if not symptom.strip():
                error_message = "請填寫症狀。"
                return render_template('index2.html', symptoms=analyzer.selected_symptoms, error=error_message, result=None)
            analyzer.add_symptom(symptom)
        elif action == 'analyze':
            if not analyzer.selected_symptoms:
                error_message = "尚未添加任何症狀，請輸入至少一個症狀！"
                return render_template('index2.html', symptoms=analyzer.selected_symptoms, error=error_message, result=None)
            result = analyzer.analyze_possible_diseases()
            if not result.get("matched_diseases"):  # 如果沒有匹配的疾病
                analyzer.reset_symptoms()
                error_message = "查無結果，請嘗試輸入其他症狀。"
                return render_template(
                'index2.html',
                symptoms=[],
                result=None,
                error=error_message
            )
            top_departments = result.get("recommended_departments", [])[:3]
            return render_template(
                'index2.html',
                symptoms=analyzer.selected_symptoms,
                result=result,
                top_departments=top_departments,
                error=None
            )
        elif action == 'reset':
            analyzer.reset_symptoms()
    return render_template('index2.html', symptoms=analyzer.selected_symptoms, result=None, error=None)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
