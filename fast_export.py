import pandas as pd
import json
from src.features_domain import generate_domain_features
from src.features_geo import generate_geo_features
from src.features_macro import generate_macro_features

def fast_export():
    print("Extracting subset for UI...")
    df = pd.read_csv('data/test.csv').head(100)
    
    print("Generating Phase II visual metrics...")
    df = generate_domain_features(df)
    df = generate_geo_features(df)
    df = generate_macro_features(df)
    
    try:
        sub = pd.read_csv('submission.csv')
        df = df.merge(sub, on='Id', how='left')
    except:
        df['SalePrice'] = 0
        
    df = df.fillna(0)
    data = df.to_dict(orient='records')
    
    with open('app/data.js', 'w') as f:
        f.write('const propertyData = ' + json.dumps(data) + ';')
    
    print("New intelligence dataset bound to application!")

if __name__ == '__main__':
    fast_export()
