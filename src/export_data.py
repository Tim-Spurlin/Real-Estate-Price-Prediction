import pandas as pd
import json
import os

def export_to_json():
    print("Loading data...")
    test_df = pd.read_csv("data/test.csv")
    sub_df = pd.read_csv("submission.csv")
    
    # Merge on ID
    merged = pd.merge(test_df, sub_df, on="Id")
    
    # Select important features for UI display
    # Keep it lightweight, top 50 properties
    export_df = merged.head(100).copy()
    
    # Fill NAs for UI representation
    export_df = export_df.fillna("N/A")
    
    records = export_df.to_dict(orient="records")
    
    output_dir = "app"
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "data.json")
    
    with open(out_path, "w") as f:
        json.dump(records, f, indent=2)
        
    print(f"Successfully exported {len(records)} properties to {out_path}")

if __name__ == "__main__":
    export_to_json()
