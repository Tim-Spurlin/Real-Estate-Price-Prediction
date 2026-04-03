"""Quick model trainer: trains a Ridge baseline on Ames data and saves to models/"""
import os, sys
import numpy as np
import pandas as pd
import joblib
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import RobustScaler

FEATURE_COLS = [
    'GrLivArea','LotArea','OverallQual','OverallCond','YearBuilt','YearRemodAdd',
    'TotalBsmtSF','BsmtFinSF1','GarageArea','GarageCars','FullBath','HalfBath',
    'BedroomAbvGr','TotRmsAbvGrd','Fireplaces','YrSold','MoSold','BsmtFullBath',
    'BsmtHalfBath','ScreenPorch','PoolArea','MiscVal','LotFrontage','1stFlrSF',
    '2ndFlrSF','MasVnrArea','BsmtUnfSF','EnclosedPorch','3SsnPorch','LowQualFinSF',
    'KitchenAbvGr','GarageYrBlt','WoodDeckSF','OpenPorchSF',
    'TotalUsableAreaSF','TotalBathrooms','AgeAtSale','YearsSinceRemodel',
    'OverallPropertyScore','LivingAreaToLotRatio','BasementFinishedRatio',
    'HasPool','HasGarage','HasBasement','HasFireplace','IsNewConstruction'
]

def main():
    train = pd.read_csv('data/train.csv')
    y = np.log1p(train['SalePrice'])
    X = pd.DataFrame(0.0, index=range(len(train)), columns=FEATURE_COLS)
    
    for c in FEATURE_COLS:
        if c in train.columns:
            X[c] = pd.to_numeric(train[c], errors='coerce').fillna(0)
    
    X['TotalUsableAreaSF'] = X['GrLivArea'] + X['TotalBsmtSF']
    X['TotalBathrooms'] = X['FullBath'] + 0.5*X['HalfBath'] + X['BsmtFullBath'] + 0.5*X['BsmtHalfBath']
    X['AgeAtSale'] = X['YrSold'] - X['YearBuilt']
    X['YearsSinceRemodel'] = X['YrSold'] - X['YearRemodAdd']
    X['OverallPropertyScore'] = X['OverallQual'] * X['OverallCond']
    la = X['LotArea'].replace(0, np.nan).fillna(1)
    X['LivingAreaToLotRatio'] = X['GrLivArea'] / la
    tb = X['TotalBsmtSF'].replace(0, np.nan).fillna(1)
    X['BasementFinishedRatio'] = X['BsmtFinSF1'] / tb
    X['HasPool'] = (X['PoolArea'] > 0).astype(float)
    X['HasGarage'] = (X['GarageArea'] > 0).astype(float)
    X['HasBasement'] = (X['TotalBsmtSF'] > 0).astype(float)
    X['HasFireplace'] = (X['Fireplaces'] > 0).astype(float)
    X['IsNewConstruction'] = (X['YrSold'] == X['YearBuilt']).astype(float)
    
    model = make_pipeline(RobustScaler(), Ridge(alpha=15.0))
    model.fit(X, y)
    
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, 'models/stacking_model.pkl')
    joblib.dump(FEATURE_COLS, 'models/feature_columns.pkl')
    print(f'Model saved! R2={model.score(X,y):.4f}')

if __name__ == '__main__':
    main()
