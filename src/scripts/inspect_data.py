# import local modules
from data_pipeline import extract

def inspect_data(file_name: str) -> None:
    # ==============================================================================
    # 1. LOAD DATA
    # ==============================================================================
    # file_name = input("Enter dataset_folder/dataset_file_name (e.g., 'dataset_1/data.csv'): ")
    df = extract.extract_data(file_name)

    # ==============================================================================
    # 2. DATA INVESTIGATION (EDA)
    # ==============================================================================
    print("\n" + "="*50)
    print("2. DATA INVESTIGATION: INITIAL CHECKS")
    print("="*50)

    TARGET_COL = df.columns[int(input(f"Enter the index of the target column (0 to {len(df.columns)-1}): "))]
    SYMPTOM_COLS = df.columns[:-1].tolist()

    # 2.1 Display initial rows
    print("\n--- 2.1 Head of the DataFrame (First 5 Rows) ---")
    print(df.head())

    # 2.2 Concise summary
    print("\n--- 2.2 DataFrame Information (Dtypes & Non-Null Counts) ---")
    df.info()

    # 2.3 Missing Values
    print("\n--- 2.3 Missing Values Check ---")
    missing_values = df.isnull().sum()
    print(missing_values[missing_values > 0].sort_values(ascending=False))

    # 2.4 Target Variable Counts
    print(f"\n--- 2.4 Target Variable '{TARGET_COL}' Value Counts ---")
    target_counts = df[TARGET_COL].value_counts()
    print(target_counts)
    
if __name__ == "__main__":
    # Example usage
    inspect_data("dataset_2/DiseaseAndSymptoms.csv")
