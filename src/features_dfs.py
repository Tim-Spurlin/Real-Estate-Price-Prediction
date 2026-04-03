import featuretools as ft
import pandas as pd

def generate_dfs_features(df):
    """Pillar II: Automated Deep Feature Synthesis"""
    df_dfs = df.copy()
    if 'Id' not in df_dfs.columns:
        df_dfs['Id'] = range(len(df_dfs))
        
    es = ft.EntitySet(id="AmesHousing")
    
    # Only include stable column types to prevent DFS failure
    valid_cols = []
    for c in df_dfs.columns:
        if df_dfs[c].dtype == 'object' or pd.api.types.is_numeric_dtype(df_dfs[c]):
            valid_cols.append(c)
            
    df_dfs = df_dfs[valid_cols].fillna("Unknown")
    es = es.add_dataframe(dataframe_name="houses", dataframe=df_dfs, index="Id")
    
    # Specific categorical tables
    cats = ['Neighborhood', 'MSZoning', 'HouseStyle', 'BldgType']
    for cat in cats:
        if cat in df_dfs.columns:
            es = es.normalize_dataframe(base_dataframe_name="houses", new_dataframe_name=cat, index=cat)
            
    agg_primitives = ["mean", "max", "min", "std", "skew", "count"]
    trans_primitives = ["percentile"]
    
    # Running DFS with max_depth=1 to conserve extreme memory limits locally
    feature_matrix, _ = ft.dfs(entityset=es, target_dataframe_name="houses",
                               agg_primitives=agg_primitives,
                               trans_primitives=trans_primitives,
                               max_depth=1, features_only=False,
                               verbose=False)
                               
    feature_matrix['Id'] = feature_matrix.index
    return feature_matrix.reset_index(drop=True)
