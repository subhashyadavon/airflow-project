# System Architecture

![Data Pipeline 3D Architecture Visualization](docs/img/architecture_3d.png)

This document provides a technical overview of the **Airflow Job Pipeline** architecture and data flow.

## High-Level Architecture Diagram

The system follows a standard ETL/ELT pattern using a Medallion-style approach (Raw -> Cleaned).

```mermaid
graph TD
    subgraph "External Resources"
        API["Adzuna Job API"]
    end

    subgraph "Orchestration Layer (Airflow)"
        direction TB
        DAG["DAG: daily_job_pipeline"]
        
        EXT["Extract Task<br/>(AdzunaExtractor)"]
        S3S["Store Raw S3 Task<br/>(S3Manager)"]
        TRF["Transform Task<br/>(JobTransformer)"]
        LOD["Load to DB Task<br/>(JobLoader)"]
        QC["Data Quality Check"]

        EXT --> S3S
        EXT --> TRF
        TRF --> LOD
        LOD --> QC
    end

    subgraph "Storage Layer"
        direction LR
        LS["LocalStack (S3 Mock)<br/>'job-market-raw' bucket"]
        PG["PostgreSQL DB<br/>'jobs' table"]
    end

    subgraph "Visualization Layer"
        ST["Streamlit Dashboard"]
    end

    %% Data Flows
    API -- "JSON Data" --> EXT
    S3S -- "Upload Raw JSON" --> LS
    LOD -- "Insert Cleaned Data" --> PG
    PG -- "Query Insights" --> ST
    ST -- "User View" --> User((User))

    %% Styling for Readability
    classDef external fill:#FFEAEA,stroke:#C0392B,stroke-width:2px,color:#641E16;
    classDef storage fill:#EAF2FF,stroke:#2E86C1,stroke-width:2px,color:#1B4F72;
    classDef airflow fill:#E9F7EF,stroke:#27AE60,stroke-width:2px,color:#186A3B;
    classDef viz fill:#FEF9E7,stroke:#D4AC0D,stroke-width:2px,color:#7D6608;

    class API external;
    class LS,PG storage;
    class DAG,EXT,S3S,TRF,LOD,QC airflow;
    class ST viz;
```

## Component Roles

### 1. Extraction (Bronze Layer)

* **Adzuna API**: External source for job listings.
* **LocalStack (S3)**: Acts as a staging area. Storing raw JSON ensures data lineage and allows for reconciliation or logic changes without losing historical data.

### 2. Transformation (Silver Layer)

* **Airflow Orchestrator**: Managed via the `daily_job_pipeline` DAG.
* **JobTransformer**: A Python utility that handles:
  * Missing data imputation.
  * Salary normalization (Min/Max to Average).
  * Removal of duplicate records.

### 3. Loading (Gold Layer)

* **PostgreSQL**: The production-ready database where cleaned data is structured for fast querying.
* **Data Quality Check**: An automated task that validates schema integrity and critical field presence before finalizing the load.

### 4. Presentation

* **Streamlit Dashboard**: A high-performance UI that visualizes trends, salary distributions, and job availability geographically.

---

## Infrastructure

The entire stack is containerized using **Docker Compose**, including:

* **Airflow Webserver/Scheduler**
* **PostgreSQL 15**
* **LocalStack** (for S3 API simulation)
* **Streamlit** (interactive dashboard)
