# Standard library imports
import os
import json

# ML library imports
import pandas as pd

def load_data(dfs_dict: tuple[dict[str, pd.DataFrame], dict[str, int]], path: str) -> None:
    # ==============================================================================
    # Define the path to the CSV file
    # =============================================================================
    
    print(f"--- Saving {len(dfs_dict)} files to: {path} ---")
    # 1. Ensure the directory exists
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as e:
        print(f"Error creating directory {path}: {e}")
        return
    
    # 2. Iterate and save each DataFrame/Series
    for key, df in dfs_dict[0].items():
        # Create the filename using the dictionary key
        file_name = f"{key}.csv"
        file_path = os.path.join(path, file_name)
        
        # Save the DataFrame or Series to CSV (excluding the index)
        if isinstance(df, pd.Series):
            df = df.to_frame()
            
        df.to_csv(file_path, index=False)
        print(f"  > Saved {len(df)} rows to {file_path} (Key: {key})")
        
    mapping_path = os.path.join(path, "label_mapping.json")
    with open(mapping_path, 'w') as f:
        json.dump(dfs_dict[1], f, indent=4)
        
    print("--- Save complete. ---")