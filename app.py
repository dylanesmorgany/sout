from flask import Flask, send_from_directory, jsonify
from pathlib import Path
import json

app = Flask(__name__, static_url_path='')
LOG_FILE = Path('logs.json')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/manage')
def manage():
    return send_from_directory('.', 'manage.html')

@app.route('/logs')
def logs():
    if LOG_FILE.exists():
        data = json.loads(LOG_FILE.read_text())
    else:
        data = []
    return jsonify(data)

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
