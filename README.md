# Airflow Job Pipeline Project

![Project Dashboard](airflow-project.png)

This project implements a complete ETL (Extract, Transform, Load) pipeline for processing job market data using Apache Airflow. The pipeline extracts job listings from the Adzuna API, transforms and cleans the data, and loads it into a PostgreSQL database.

## Features

- **ETL Pipeline**: Automates the extraction, transformation, and loading of job data.
- **S3 Integration**: Raw job data is stored in an S3 bucket (simulated using LocalStack).
- **Data Quality Checks**: Ensures data integrity before loading into the database.
- **Streamlit Dashboard**: Visualizes job market trends and insights.

## Prerequisites

- Docker and Docker Compose
- Python 3.8+

## Setup

1.  **Clone the repository** (if not already done).

2.  **Create a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

## Running the Project

1.  **Start all services** using Docker Compose:
    ```bash
    docker-compose up -d
    ```

2.  **Initialize Airflow** (first time only):
    ```bash
    docker-compose exec airflow-webserver airflow db init
    ```

3.  **Initialize Application Database Schema** (first time only):
    ```bash
    docker-compose exec -T postgres psql -U airflow -d airflow < src/load/schema.sql
    ```

4.  **Create an admin user** (first time only):
    ```bash
    docker-compose exec airflow-webserver airflow users create \
        --username admin \
        --password admin \
        --firstname Subhash \
        --lastname Yadav \
        --role Admin \
        --email [EMAIL_ADDRESS]
    ```

4.  **Unpause the DAG** in the Airflow UI:
    - Open [http://localhost:8080](http://localhost:8080) in your browser.
    - Log in with username `admin` and password `admin`.
    - Find the `daily_job_pipeline` DAG and toggle it to **Unpaused**.
    - Click the **Trigger DAG** button (play icon) to start the pipeline.

## Accessing the Dashboard

- Open [http://localhost:8501](http://localhost:8501) to view the job market dashboard.

## Project Structure

```
airflow-project/
├── dags/                  # Airflow DAG definitions
├── src/                   # Source code
│   ├── extract/           # Data extraction logic
│   ├── transform/         # Data transformation logic
│   └── load/              # Data loading logic
├── dashboard/             # Streamlit dashboard code
├── docker-compose.yml     # Docker services configuration
├── Dockerfile             # Docker image definition
└── requirements.txt       # Python dependencies
```

## Environment Variables

Ensure the following environment variables are set in your `.env` file (or passed to Docker Compose):

- `ADZUNA_APP_ID`: Your Adzuna API application ID.
- `ADZUNA_APP_KEY`: Your Adzuna API application key.
- `DB_URL`: Database connection string (default: `postgresql://airflow:airflow@postgres:5432/airflow`).
- `AWS_ACCESS_KEY_ID`: AWS credentials for S3 (default: `test`).
- `AWS_SECRET_ACCESS_KEY`: AWS credentials for S3 (default: `test`).
- `AWS_DEFAULT_REGION`: AWS region (default: `us-east-1`).
