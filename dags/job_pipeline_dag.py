from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Any

# Adding src to sys.path if not there
import sys

sys.path.append("/opt/airflow")

from src.extract.extractor import AdzunaExtractor
from src.extract.s3_utils import S3Manager
from src.transform.transformer import JobTransformer
from src.load.loader import JobLoader

# Default arguments
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "daily_job_pipeline",
    default_args=default_args,
    description="A daily pipeline to extract, transform, and load job market data.",
    schedule=timedelta(days=1),
    catchup=False,
)


def extract_jobs_task(**kwargs):
    extractor = AdzunaExtractor()
    all_raw_results: List[Dict[str, Any]] = []

    # Track different tech roles to get a diverse dataset
    search_queries = [
        "software engineer",
        "data engineer",
        "data scientist",
        "devops",
        "internship",
    ]

    for query in search_queries:
        try:
            logging.info(f"Fetching jobs for: {query}")
            jobs = extractor.fetch_jobs(
                what=query, where="Winnipeg", results_per_page=20
            )
            all_raw_results.extend(jobs.get("results", []))
        except Exception as e:
            logging.error(f"Error fetching {query}: {e}")
            continue

    # Deduplicate results by ID
    seen_ids = set()
    unique_results = []
    for job in all_raw_results:
        if job["id"] not in seen_ids:
            unique_results.append(job)
            seen_ids.add(job["id"])

    all_jobs: Dict[str, List[Dict[str, Any]]] = {"results": unique_results}
    kwargs["ti"].xcom_push(key="raw_jobs", value=all_jobs)
    return all_jobs


def store_raw_s3_task(**kwargs):
    ti = kwargs["ti"]
    jobs = ti.xcom_pull(key="raw_jobs", task_ids="extract_jobs")
    s3 = S3Manager(bucket_name="job-market-raw", endpoint_url="http://localstack:4566")
    s3.create_bucket()
    file_name = f"raw_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    s3.upload_json(jobs, file_name)
    return file_name


def transform_jobs_task(**kwargs):
    ti = kwargs["ti"]
    jobs = ti.xcom_pull(key="raw_jobs", task_ids="extract_jobs")
    transformer = JobTransformer()
    cleaned_jobs = transformer.clean_jobs(jobs)
    ti.xcom_push(key="cleaned_jobs", value=cleaned_jobs)
    return cleaned_jobs


def load_to_db_task(**kwargs):
    ti = kwargs["ti"]
    cleaned_jobs = ti.xcom_pull(key="cleaned_jobs", task_ids="transform_jobs")
    loader = JobLoader(db_url="postgresql://airflow:airflow@postgres:5432/airflow")
    loader.load_jobs(cleaned_jobs)
    return True


def data_quality_check_task(**kwargs):
    ti = kwargs["ti"]
    cleaned_jobs = ti.xcom_pull(key="cleaned_jobs", task_ids="transform_jobs")

    if not cleaned_jobs:
        raise ValueError("Data Quality Check FAILED: No cleaned jobs found.")

    for job in cleaned_jobs:
        if not job.get("title"):
            raise ValueError(
                f"Data Quality Check FAILED: Job {job.get('job_id')} has no title."
            )

        # Check salary range if available
        avg_salary = job.get("avg_salary")
        if avg_salary is not None:
            if avg_salary < 10000 or avg_salary > 500000:
                logging.warning(
                    f"Data Quality Alert: Unusual salary for job {job.get('job_id')}: {avg_salary}"
                )

    logging.info("Data Quality Check PASSED.")
    return True


# Task Definitions
extract_task = PythonOperator(
    task_id="extract_jobs",
    python_callable=extract_jobs_task,
    dag=dag,
)

s3_task = PythonOperator(
    task_id="store_raw_s3",
    python_callable=store_raw_s3_task,
    dag=dag,
)

transform_task = PythonOperator(
    task_id="transform_jobs",
    python_callable=transform_jobs_task,
    dag=dag,
)

load_task = PythonOperator(
    task_id="load_to_db",
    python_callable=load_to_db_task,
    dag=dag,
)

quality_check_task = PythonOperator(
    task_id="data_quality_check",
    python_callable=data_quality_check_task,
    dag=dag,
)

# DAG Structure
extract_task >> [s3_task, transform_task]
transform_task >> load_task >> quality_check_task
