import pandas as pd
import numpy as np
from geopy.distance import geodesic
from sklearn.cluster import KMeans

def generate_geo_features(df):
    """Pillar V: Geospatial Vectorization"""
    anchors = {
        "ISU": (42.0268, -93.6432),
        "MainSt": (42.0258, -93.6168),
        "HighSchool": (42.0263, -93.6172)
    }
    
    neighborhoods = df['Neighborhood'].unique() if 'Neighborhood' in df.columns else []
    
    # Deterministic pseudo-locations distributed closely around Ames for Kaggle test parity
    np.random.seed(42)
    lat_map = {n: 42.0347 + np.random.normal(0, 0.02) for n in neighborhoods}
    lon_map = {n: -93.6199 + np.random.normal(0, 0.02) for n in neighborhoods}
    
    if 'Neighborhood' in df.columns:
        df['Lat'] = df['Neighborhood'].map(lat_map)
        df['Lon'] = df['Neighborhood'].map(lon_map)
    else:
        df['Lat'] = 42.0347
        df['Lon'] = -93.6199
        
    for anchor_name, coords in anchors.items():
        df[f'Distance_to_{anchor_name}'] = df.apply(lambda row: geodesic((row['Lat'], row['Lon']), coords).miles, axis=1)
        
    # Micro-Socioeconomic clustering (KMeans)
    n_clusters = min(5, len(df))
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df['GeoCluster'] = kmeans.fit_predict(df[['Lat', 'Lon']])
    
    return df
