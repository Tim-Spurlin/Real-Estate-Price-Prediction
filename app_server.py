"""Lightweight Flask backend for the Real Estate Dashboard."""
import os
import json
import webbrowser
import threading
from flask import Flask, send_from_directory, request, jsonify

app = Flask(__name__, static_folder='app', static_url_path='')

RENTCAST_API_KEY = os.environ.get('RENTCAST_API_KEY', '2e1b3dd1d84947b4b5faeee561a60e87')

# Model is lazy-loaded on first predict call
_model = None
_feature_cols = None

def _load_model():
    global _model, _feature_cols
    if _model is not None:
        return True
    try:
        import joblib
        _model = joblib.load('models/stacking_model.pkl')
        _feature_cols = joblib.load('models/feature_columns.pkl')
        return True
    except Exception:
        return False

@app.route('/')
def index():
    return send_from_directory('app', 'index.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    if not _load_model():
        return jsonify({'error': 'Model not trained yet. Run: python quick_train.py'}), 500
    import numpy as np, pandas as pd
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data.'}), 400
    row = {c: 0 for c in _feature_cols}
    for k in data:
        if k in row:
            row[k] = float(data[k])
    df = pd.DataFrame([row])
    df.columns = df.columns.astype(str)
    price = float(np.expm1(_model.predict(df)[0]))
    return jsonify({'predicted_price': round(price, 2), 'features_used': len(_feature_cols),
                    'model': 'Stacking Regressor'})

@app.route('/api/lookup', methods=['POST'])
def lookup():
    import requests as req
    data = request.get_json()
    address = data.get('address', '')
    if not RENTCAST_API_KEY:
        return jsonify({
            'error': 'No RentCast API key configured.',
            'help': 'Set RENTCAST_API_KEY env var. Get a free key at https://www.rentcast.io/api'
        }), 400
    try:
        resp = req.get('https://api.rentcast.io/v1/properties',
                       params={'address': address},
                       headers={'X-Api-Key': RENTCAST_API_KEY}, timeout=10)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def open_browser():
    webbrowser.open('http://127.0.0.1:5050')

if __name__ == '__main__':
    threading.Timer(1.5, open_browser).start()
    print("Dashboard live at http://127.0.0.1:5050")
    app.run(host='127.0.0.1', port=5050, debug=False)
