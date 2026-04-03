FROM apache/airflow:2.10.0

USER root
# Install system dependencies if needed (e.g., for compiled Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow
# Ensure the user's local bin is in PATH
ENV PATH="/home/airflow/.local/bin:${PATH}"

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir "apache-airflow==2.10.0" -r requirements.txt --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.0/constraints-3.12.txt"
