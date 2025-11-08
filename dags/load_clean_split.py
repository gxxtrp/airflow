from __future__ import annotations
import pickle

import pendulum

# Airflow Imports
from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator # type: ignore
from airflow.operators.python import PythonOperator # type: ignore
from airflow.models.taskinstance import TaskInstance

# Standard Python Imports
import os
import logging
import pandas as pd

# --- IMPORT LOCAL MODULES ---
from src.data_pipeline.extract import extract_data as extract_data_module
from src.data_pipeline.transform import transform_data as transform_data_module
from src.data_pipeline.load import load_data as load_data_module

logging.basicConfig(level=logging.INFO)

# --- 1. CONFIGURATION (Constants for paths and XCom keys) ---
DATA_FILE_NAME = 'raw_data.csv' # File name passed to extract
XCOM_KEY_PATH = 'data_file_path' # Unique XCom key for the file location
TEMP_DIR = '/tmp/airflow_data' # Shared temp location on the worker file system
FINAL_PROCESSED_PATH = os.path.join("data", "processed")

# --- 2. EXTRACT WRAPPER (Handles path setup and XCom push) ---
def airflow_extract_data(ti: TaskInstance | None = None):
    """
    Airflow wrapper: Handles paths, calls core extraction logic, and pushes 
    the temporary file path to XCom instead of the entire DataFrame.
    """
    # 1. Setup paths
    os.makedirs(TEMP_DIR, exist_ok=True)
    temp_file_path = os.path.join(TEMP_DIR, 'raw_data.pkl')
    
    # The module function expects the file name or path.
    # We'll use the core function from the user's files and hardcode the path logic here
    df = extract_data_module(DATA_FILE_NAME)

    # 2. Robust XCom Handling: Save the DataFrame to a temporary file
    if df.empty:
        raise ValueError("Extraction returned an empty DataFrame. Terminating.")
        
    df.to_pickle(temp_file_path)
    
    # 3. Push the file path to XCom
    ti.xcom_push(key=XCOM_KEY_PATH, value=temp_file_path) # type: ignore
    logging.info(f"Pushed raw data path to XCom: {temp_file_path}")
    logging.info(f"--- Extract Task completed (Data stored externally) ---")


# --- 3. TRANSFORM WRAPPER (Handles XCom pull/push of file paths) ---
def airflow_transform_data(ti: TaskInstance):
    """
    Airflow wrapper: Pulls raw data path, loads data, calls core transform logic, 
    and saves the transformed data path back to XCom.
    """
    # 1. Pull data path from XCom
    raw_data_path = ti.xcom_pull(task_ids='extract_task', key=XCOM_KEY_PATH)
    if not raw_data_path or not os.path.exists(raw_data_path):
        raise FileNotFoundError("Raw data file not found. Extraction failed.")
    
    # 2. Load data from disk
    df = pd.read_pickle(raw_data_path)
    logging.info(f"Loaded DataFrame from disk for transformation. Shape: {df.shape}")

    # 3. CALL CORE LOGIC (returns the tuple: (split_dfs, label_mapping))
    transformed_data = transform_data_module(df)
    
    # 4. Robust XCom Handling: Save result externally
    transformed_data_path = os.path.join(TEMP_DIR, 'transformed_data_set.pkl')
    with open(transformed_data_path, 'wb') as file:
        pickle.dump(transformed_data, file)
    
    # 5. Push the file path to XCom
    ti.xcom_push(key=XCOM_KEY_PATH, value=transformed_data_path)
    logging.info(f"Pushed transformed data path to XCom: {transformed_data_path}")
    logging.info(f"--- Transform Task completed (Data stored externally) ---")


# --- 4. LOAD WRAPPER (Handles XCom pull and calls core load logic) ---
def airflow_load_data(ti: TaskInstance):
    """
    Airflow wrapper: Pulls transformed data path, loads data, and calls core load logic.
    """
    # 1. Pull data path from XCom
    transformed_data_path = ti.xcom_pull(task_ids='transform_task', key=XCOM_KEY_PATH)
    if not transformed_data_path or not os.path.exists(transformed_data_path):
        raise FileNotFoundError("Transformed data file not found. Transformation failed.")
        
    # 2. Load the transformed data (which is a tuple: (split_dfs, label_mapping))
    transformed_data_path = os.path.join(TEMP_DIR, 'transformed_data_set.pkl')
    with open(transformed_data_path, 'rb') as file:
        loaded_data = pickle.load(file)
    
    # 3. CALL CORE LOGIC (The core load function handles saving the data permanently)
    # The load function expects the data tuple and the final path
    load_data_module(loaded_data, os.path.abspath(FINAL_PROCESSED_PATH)) # type: ignore
    logging.info(f"--- Load Task completed (Saved to {FINAL_PROCESSED_PATH}) ---")


# --- 5. AIRFLOW DAG DEFINITION ---

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['admin@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': pendulum.duration(minutes=5),
}

with DAG(
    dag_id='project-load_clean_split',
    default_args=default_args,
    description='load data, clean, encode, and split into train/test sets',
    schedule="0 9 * * *",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,
    tags=['project', 'etl'],
) as dag:
    
    # Task 1: Setup
    setup_task = BashOperator(
        task_id='setup_environment',
        bash_command=f'echo "Starting robust ETL pipeline"; mkdir -p {TEMP_DIR}',
    )

    # Task 2: Extract (Pushes file path)
    extract_task = PythonOperator(
        task_id='extract_task',
        python_callable=airflow_extract_data,
    )

    # Task 3: Transform (Pulls path, pushes new path)
    transform_task = PythonOperator(
        task_id='transform_task',
        python_callable=airflow_transform_data,
    )

    # Task 4: Load (Pulls path, writes to permanent storage)
    load_task = PythonOperator(
        task_id='load_task',
        python_callable=airflow_load_data,
    )

    # Task 5: Cleanup (Removes temporary files)
    cleanup_task = BashOperator(
        task_id='cleanup_temp_data',
        bash_command=f'echo "Cleaning up temp directory..."; rm -rf {TEMP_DIR}',
        trigger_rule='all_done', # Runs even if tasks fail, to ensure clean up
    )

    # 6. Define Dependencies
    setup_task >> extract_task >> transform_task >> load_task >> cleanup_task # type: ignore