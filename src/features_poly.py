import pandas as pd
from sklearn.preprocessing import PolynomialFeatures

def generate_poly_features(df):
    """Pillar III: Advanced Polynomial Interaction Expansion"""
    numeric_df = df.select_dtypes(include=['float64', 'int64']).drop(columns=['Id', 'SalePrice'], errors='ignore')
    if numeric_df.empty: return df
    
    # Top 15 correlated/highest variance parameters to prevent memory collapse
    vars_std = numeric_df.std().sort_values(ascending=False).head(15).index
    poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
    
    poly_feats = poly.fit_transform(numeric_df[vars_std].fillna(0))
    poly_cols = poly.get_feature_names_out(vars_std)
    
    # Remove special characters from columns to prevent XGBoost JSON errors
    poly_cols = [str(c).replace(' ', '_').replace('^', '_pow_') for c in poly_cols]
    
    poly_df = pd.DataFrame(poly_feats, columns=poly_cols, index=df.index)
    
    # Reduce memory before merge
    poly_df = poly_df.astype('float32')
    return pd.concat([df, poly_df.drop(columns=vars_std, errors='ignore')], axis=1)
