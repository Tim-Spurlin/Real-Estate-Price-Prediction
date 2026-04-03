"""Lightweight Flask backend for the Real Estate Dashboard."""
import os
import json
import webbrowser
import threading
from flask import Flask, send_from_directory, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__, static_folder='app', static_url_path='')

# Expose standard web traffic telemetry at /metrics
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Ames Real Estate Intelligence API', version='1.0.0')

RENTCAST_API_KEY = os.environ.get('RENTCAST_API_KEY', '')

# Model is lazy-loaded on first predict call
_model = None
_feature_cols = None

import time
from datetime import datetime

_daily_requests = 0
_last_reset_date = datetime.now().date()
_request_timestamps = []

def check_rate_limits():
    global _daily_requests, _last_reset_date, _request_timestamps
    now = time.time()
    today = datetime.now().date()
    
    if today > _last_reset_date:
        _daily_requests = 0
        _last_reset_date = today
        
    if _daily_requests >= 50:
        return "Daily limit of 50 API requests reached. Please try again tomorrow."
        
    _request_timestamps = [ts for ts in _request_timestamps if now - ts <= 120]
    if len(_request_timestamps) >= 2:
        return "Rate limit exceeded: Please wait. Only 2 consecutive requests are permitted within a 2-minute period."
        
    _daily_requests += 1
    _request_timestamps.append(now)
    return None

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
        
    limit_error = check_rate_limits()
    if limit_error:
        return jsonify({'error': limit_error}), 429
    try:
        resp = req.get('https://api.rentcast.io/v1/properties',
                       params={'address': address},
                       headers={'X-Api-Key': RENTCAST_API_KEY}, timeout=10)
        
        rentcast_data = resp.json()
        if isinstance(rentcast_data, dict):
            if 'error' in rentcast_data:
                return jsonify(rentcast_data), resp.status_code
            rentcast_data = [rentcast_data]
            
        # Automatically inject ML-predicted pricing
        if _load_model():
            import numpy as np, pandas as pd
            for item in rentcast_data:
                # Map RentCast fields to our model features
                grLiv = item.get('squareFootage', 0)
                lotArea = item.get('lotSize', 0)
                yrBuilt = item.get('yearBuilt', 2000)
                fullBath = item.get('bathrooms', 2)
                beds = item.get('bedrooms', 3)
                
                row = {c: 0 for c in _feature_cols}
                row['GrLivArea'] = grLiv
                row['LotArea'] = lotArea
                row['YearBuilt'] = yrBuilt
                row['FullBath'] = fullBath
                row['BedroomAbvGr'] = beds
                
                # Standard baseline assumptions for missing features
                row['TotRmsAbvGrd'] = beds + fullBath + 1
                row['OverallQual'] = 6
                row['OverallCond'] = 5
                row['YrSold'] = 2024
                
                # Derived Phase II features
                row['TotalUsableAreaSF'] = grLiv
                row['TotalBathrooms'] = fullBath
                row['AgeAtSale'] = max(0, 2024 - yrBuilt)
                row['LivingAreaToLotRatio'] = grLiv / lotArea if lotArea > 0 else 0
                row['IsNewConstruction'] = 1 if yrBuilt == 2024 else 0
                
                df = pd.DataFrame([row])
                df.columns = df.columns.astype(str)
                log_price = _model.predict(df)[0]
                predicted_val = float(np.expm1(log_price))
                
                # Apply inflation multiplier from 2010 base to 2024
                # (Simple heuristic since the Kaggle Ames model was trained on 2006-2010 nominal dollars)
                item['ai_predicted_price'] = predicted_val * 1.6
                
        return jsonify(rentcast_data), resp.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def open_browser():
    webbrowser.open('http://127.0.0.1:5050')

if __name__ == '__main__':
    threading.Timer(1.5, open_browser).start()
    print("Dashboard live at http://127.0.0.1:5050")
    app.run(host='127.0.0.1', port=5050, debug=False)
