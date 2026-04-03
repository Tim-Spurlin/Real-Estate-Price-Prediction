"""Save the trained stacking model to disk for the Flask server."""
import os
import joblib
import numpy as np
from src.preprocessing import preprocess_data
from src.train import train_and_submit

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import RobustScaler
from sklearn.linear_model import Lasso, Ridge
from sklearn.ensemble import StackingRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor

def save_model():
    print("Training model for deployment...")
    X_train, y_train, X_test, test_ids = preprocess_data()
    print(f"Feature matrix: {X_train.shape}")

    lasso = make_pipeline(RobustScaler(), Lasso(alpha=0.005, random_state=42))
    ridge = make_pipeline(RobustScaler(), Ridge(alpha=20.0, random_state=42))
    xgb = XGBRegressor(learning_rate=0.01, n_estimators=1000, max_depth=4,
                        min_child_weight=1, gamma=0.05, subsample=0.8,
                        colsample_bytree=0.2, objective='reg:squarederror',
                        nthread=-1, seed=42, random_state=42)
    lgbm = LGBMRegressor(objective='regression', num_leaves=6,
                          learning_rate=0.03, n_estimators=800,
                          feature_fraction=0.25, min_data_in_leaf=10,
                          verbose=-1, random_state=42)
    catb = CatBoostRegressor(iterations=900, learning_rate=0.03, depth=5,
                              l2_leaf_reg=10, eval_metric='RMSE',
                              random_seed=42, logging_level='Silent')
    gbr = GradientBoostingRegressor(n_estimators=1000, learning_rate=0.05,
                                     max_depth=4, max_features='sqrt',
                                     min_samples_leaf=15, min_samples_split=10,
                                     loss='huber', random_state=42)

    estimators = [('lasso', lasso), ('ridge', ridge), ('xgb', xgb),
                  ('lgbm', lgbm), ('catb', catb), ('gbr', gbr)]
    stack = StackingRegressor(estimators=estimators,
                               final_estimator=make_pipeline(RobustScaler(), Ridge(alpha=15.0)),
                               cv=4, n_jobs=-1)
    stack.fit(X_train, y_train)

    os.makedirs('models', exist_ok=True)
    joblib.dump(stack, 'models/stacking_model.pkl')
    joblib.dump(list(X_train.columns), 'models/feature_columns.pkl')
    print(f"Model saved! Features: {len(X_train.columns)}")

if __name__ == '__main__':
    save_model()
