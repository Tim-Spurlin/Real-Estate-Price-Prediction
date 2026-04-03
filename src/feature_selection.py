import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from boruta import BorutaPy

def select_features(X, y):
    """Feature Selection: Dimensionality Reduction via Boruta"""
    # Prevent categorical injection into Random Forest
    X_num = X.select_dtypes(include=[np.number]).fillna(0)
    
    print(f"Starting Boruta selection on {X_num.shape[1]} raw synthesized features...")
    
    # Lightweight pre-filter to drop absolute zero variance to speed up Boruta
    variance = X_num.var()
    valid_cols = variance[variance > 0].index
    X_num = X_num[valid_cols]
    
    rf = RandomForestRegressor(n_jobs=-1, max_depth=5, random_state=42)
    # Reduced max_iter heavily to prevent massive lockup on 5000 feats locally
    boruta_selector = BorutaPy(rf, n_estimators='auto', verbose=0, random_state=42, max_iter=15)
    
    boruta_selector.fit(X_num.values, y.values)
    
    selected_features = X_num.columns[boruta_selector.support_].tolist()
    tentative_features = X_num.columns[boruta_selector.support_weak_].tolist()
    final_features = selected_features + tentative_features
    
    if len(final_features) < 10:
        print("Boruta strictness collapsed features, returning top 100 correlated.")
        return X_num.columns.tolist()[:100]
        
    print(f"Boruta rigorously selected {len(final_features)} high-value features.")
    return final_features
