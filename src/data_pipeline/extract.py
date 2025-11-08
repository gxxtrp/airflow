# Standard library imports
import os

# ML library imports
import pandas as pd

def extract_data(fileName: str) -> pd.DataFrame:
    # ==============================================================================
    # Define the path to the CSV file
    # =============================================================================
    data_dir = "data"
    data_path = os.path.join(data_dir, fileName)
    absolute_data_path = os.path.abspath(data_path)
    """
    Loads the user's data from `fileName`.
    """
    try:
        df = pd.read_csv(absolute_data_path)
        print("\n" + "="*50)
        print(f"Data Loaded Successfully from {fileName} Shape: {df.shape}")
        print("="*50)
        return df
    except FileNotFoundError:
        print(f"ERROR: '{fileName}' not found. Please ensure the file is correctly uploaded.")
        return pd.DataFrame() # Return empty DataFrame on failure