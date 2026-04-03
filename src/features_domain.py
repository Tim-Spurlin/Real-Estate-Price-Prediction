import pandas as pd
import numpy as np

def generate_domain_features(df):
    """Pillar I: Intrinsic Domain Engineering"""
    # Cumulative Space
    if 'GrLivArea' in df.columns and 'TotalBsmtSF' in df.columns:
        df['TotalUsableAreaSF'] = df['GrLivArea'] + df['TotalBsmtSF']
        
    outdoor_cols = ['WoodDeckSF', 'OpenPorchSF', 'EnclosedPorch', '3SsnPorch', 'ScreenPorch']
    df['TotalOutdoorAreaSF'] = df[[c for c in outdoor_cols if c in df.columns]].sum(axis=1)
    
    # Utility
    if all(c in df.columns for c in ['FullBath', 'HalfBath', 'BsmtFullBath', 'BsmtHalfBath']):
        df['TotalBathrooms'] = df['FullBath'] + (0.5 * df['HalfBath']) + df['BsmtFullBath'] + (0.5 * df['BsmtHalfBath'])
        
    # Temporal Adjustments
    if 'YrSold' in df.columns and 'YearBuilt' in df.columns:
        df['AgeAtSale'] = pd.to_numeric(df['YrSold'], errors='coerce') - pd.to_numeric(df['YearBuilt'], errors='coerce')
    if 'YrSold' in df.columns and 'YearRemodAdd' in df.columns:
        df['YearsSinceRemodel'] = pd.to_numeric(df['YrSold'], errors='coerce') - pd.to_numeric(df['YearRemodAdd'], errors='coerce')
        
    # Quality indices
    if 'OverallQual' in df.columns and 'OverallCond' in df.columns:
        df['OverallPropertyScore'] = df['OverallQual'] * df['OverallCond']
        
    # Proportional Ratios
    if 'GrLivArea' in df.columns and 'LotArea' in df.columns:
        df['LivingAreaToLotRatio'] = df['GrLivArea'] / df['LotArea'].replace(0, np.nan)
    if 'BsmtFinSF1' in df.columns and 'TotalBsmtSF' in df.columns:
        df['BasementFinishedRatio'] = df['BsmtFinSF1'] / df['TotalBsmtSF'].replace(0, np.nan)
    
    # Boolean Flags  
    df['HasPool'] = (df.get('PoolArea', 0) > 0).astype(int)
    df['HasGarage'] = (df.get('GarageArea', 0) > 0).astype(int)
    df['HasBasement'] = (df.get('TotalBsmtSF', 0) > 0).astype(int)
    df['HasFireplace'] = (df.get('Fireplaces', 0) > 0).astype(int)
    if 'YrSold' in df.columns and 'YearBuilt' in df.columns:
        df['IsNewConstruction'] = (pd.to_numeric(df['YrSold'], errors='coerce') == pd.to_numeric(df['YearBuilt'], errors='coerce')).astype(int)
        
    return df
