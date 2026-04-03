import pandas as pd
import numpy as np

from src.features_domain import generate_domain_features
from src.features_dfs import generate_dfs_features
from src.features_poly import generate_poly_features
from src.features_macro import generate_macro_features
from src.features_geo import generate_geo_features
from src.feature_selection import select_features

def preprocess_data(train_path="data/train.csv", test_path="data/test.csv"):
    train_raw = pd.read_csv(train_path)
    test_raw = pd.read_csv(test_path)
    
    y_train = np.log1p(train_raw["SalePrice"])
    test_ids = test_raw["Id"]
    len_train = len(train_raw)
    
    df = pd.concat([train_raw.drop(["SalePrice", "Id"], axis=1), test_raw.drop(["Id"], axis=1)]).reset_index(drop=True)
    
    print("Executing Pillar I: Domain Engineering...")
    df = generate_domain_features(df)
    
    print("Executing Pillar V: Geospatial Vectorization...")
    df = generate_geo_features(df)
    
    print("Executing Pillar IV: Macroeconomic Time-Series...")
    df = generate_macro_features(df)
    
    print("Executing Pillar II: Deep Feature Synthesis (DFS)...")
    df = generate_dfs_features(df)
    
    print("Encoding matrices and applying One-Hot Dummies...")
    df = pd.get_dummies(df, drop_first=True)
    
    print("Executing Pillar III: Polynomial Interactions...")
    df = generate_poly_features(df)
    
    # Global Fallback Guard
    df = df.fillna(0)
    # Ensure all column names are strings to prevent XGBoost JSON dump errors
    df.columns = df.columns.astype(str)
    
    X_train = df[:len_train]
    X_test = df[len_train:]
    
    # Apply Boruta dynamically
    selected_cols = select_features(X_train, y_train)
    X_train_filtered = X_train[selected_cols]
    X_test_filtered = X_test[selected_cols]
    
    return X_train_filtered, y_train, X_test_filtered, test_ids
