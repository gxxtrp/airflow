# 🚀 Covid Prediction - Airflow Data Pipeline

## 🎯 Project Overview
This repository contains a set of Apache Airflow DAGs (Directed Acyclic Graphs) and supporting scripts that implement the `data pipeline` for `Covid Prediction`.

### Key Features:
* **Modular ETL:** The pipeline is broken into `extract.py`, `transform.py`, and `load.py` for clarity and maintainability.
* **Dockerized Environment:** The entire Airflow environment is set up using `docker-compose.yaml` for consistency across development and deployment.
* **Data Source:** Processes data from the included `data/raw_data.csv`.

## 🛠️ Technology Stack
* **Orchestration:** Apache Airflow [3.1.2]
* **Language:** Python [3.13]
* **Containerization:** Docker & Docker Compose
* **Database:** PostgreSQL
* **Dependencies:** Managed via `requirements.txt`

## ⚙️ Setup and Installation

### Prerequisites
* [Docker](https://www.docker.com/get-started)
* [Docker Compose](https://docs.docker.com/compose/install/)

### 1. Project Initialization
The Airflow setup requires a single initialization command to create necessary volumes and set up the environment.

### START AIRFLOW
```bash
# From the project root directory
# INIT AIRFLOW
docker compose up airflow-init
# START AIRFLOW
docker compose up -d
```
### AIRFLOW WEB UI
* [AIRFLOW WEB UI](http://localhost:8080)
* **Username:** `airflow`
* **Password:** `airflow`

### START PYTHON
```bash
# RUN From the project root directory "airflow/"
pip install -e .
python ./src/main.py
```
