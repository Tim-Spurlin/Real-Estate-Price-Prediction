import pandas as pd
import datetime

def generate_macro_features(df):
    """Pillar IV: Extrinsic Macroeconomic Time-Series Integration"""
    if 'YrSold' not in df.columns or 'MoSold' not in df.columns:
        return df

    start = datetime.datetime(2005, 1, 1)
    end = datetime.datetime(2011, 1, 1)
    try:
        # Load FRED Indicators
        macro = web.DataReader(['MORTGAGE30US', 'AMES119URN', 'IAUR'], 'fred', start, end)
        
        # Resample to strict monthly frequency and forward-fill to prevent lookahead bias
        macro_monthly = macro.resample('ME').ffill().reset_index()
        macro_monthly['YrSold'] = macro_monthly['DATE'].dt.year
        macro_monthly['MoSold'] = macro_monthly['DATE'].dt.month
        
        df_merged = pd.merge(df, macro_monthly.drop(columns=['DATE']), on=['YrSold', 'MoSold'], how='left')
        return df_merged
    except Exception as e:
        print(f"Warning: FRED Macro integration bypassed due to API error: {e}")
        return df
