# ML library imports
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import numpy as np

def _clean(df: pd.DataFrame) -> pd.DataFrame:
    print("\n" + "="*50)
    print("CLEANING DATA")
    print("="*50)
    
    TARGET_COL = df.columns[-1]
    SYMPTOM_COLS = df.columns[:-1].tolist()

    # Check for missing values
    missing_counts = df.isnull().sum()
    missing_data_cols = missing_counts[missing_counts > 0]
    
    if not missing_data_cols.empty:
        print(f"Found missing values in the following columns:")
        print(missing_data_cols)
        
        # Strategy: Impute missing symptom data (binary columns) with 0, 
        # and use the mode for the categorical target column.
        
        # Impute symptom columns with 0 (since a missing symptom likely means 'not present')
        print("\nImputing missing symptom data with 0...")
        df[SYMPTOM_COLS] = df[SYMPTOM_COLS].fillna(0)

        # Impute missing target type with the mode (most frequent type)
        if df[TARGET_COL].isnull().any():
            mode_type = df[TARGET_COL].mode()[0]
            print(f"Imputing missing target '{TARGET_COL}' with mode: {mode_type}...")
            df[TARGET_COL] = df[TARGET_COL].fillna(mode_type)

        # Verify cleaning
        print("\nVerification: Missing values remaining:")
        print(df.isnull().sum().sum())
    else:
        print("No missing values found. Data is clean.")

    # Ensure all symptom columns are integer (0 or 1)
    df[SYMPTOM_COLS] = df[SYMPTOM_COLS].astype(int)

    return df

def _encode(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, int]]:
    print("\n" + "="*50)
    print("ENCODING DATA")
    print("="*50)

    TARGET_COL = df.columns[-1]

    """
    Encodes the categorical target column to integers using LabelEncoder.
    Returns: DataFrame X, Encoded Series y, and the mapping dictionary.
    """
    # Separate features (X) and raw target (y_raw)
    X = df.drop(columns=[TARGET_COL])
    y_raw = df[TARGET_COL]

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y_raw)

    # Store the mapping for later interpretation (e.g., 0 -> 'ALLERGY')
    encoded_values = label_encoder.transform(label_encoder.classes_).tolist() # type: ignore
    type_mapping = dict(list(zip(label_encoder.classes_, encoded_values)))
    
    y = pd.Series(y_encoded, name='target', index=df.index) # type: ignore

    return X, y, type_mapping # type: ignore

def _split(X: pd.DataFrame, y: pd.DataFrame) -> dict[str, pd.DataFrame]:
    print("\n" + "="*50)
    print("SPLITTING DATA (Train/Test)")
    print("="*50)

    # Split the data into 80% training and 20% testing sets
    # We use stratify=y to ensure the class distribution in the splits is the same as the original data.
    # random_state is used for reproducibility.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=0.2, 
        random_state=42, 
        stratify=y # Important for imbalanced classification tasks
    )
    
    result = {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test
    }
    
    print(f"X (Features) Shape: {X.shape}, y (Target) Shape: {y.shape}")
    print("\n--- Split Shapes ---")
    print(f"X_train (Training Features) Shape: {X_train.shape}")
    print(f"X_test (Testing Features) Shape:   {X_test.shape}")
    print(f"y_train (Training Target) Shape:   {y_train.shape}")
    print(f"y_test (Testing Target) Shape:     {y_test.shape}")

    return result

def transform_data(df: pd.DataFrame) -> tuple[dict[str, pd.DataFrame], dict[str, int]]:
    cleaned = _clean(df)
    X, y, label_mapping = _encode(cleaned)
    split_df = _split(X, y)
    return split_df, label_mapping
