from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
from disease_api import SymptomAnalyzer
import time

app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')

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
