# File Processing Scripts

This directory contains Python scripts demonstrating various techniques for extracting, transforming, and loading (ETL) data from local files. Examples here focus on handling different file formats, performing data quality checks, implementing incremental processing, and loading data into a database.

## Table of Contents

- [File Processing Scripts](#file-processing-scripts)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Scripts Overview](#scripts-overview)
  - [Setup and Running](#setup-and-running)
    - [Prerequisites](#prerequisites)
    - [Configuration](#configuration)
    - [Input Data](#input-data)
    - [Running the ETL Script](#running-the-etl-script)
  - [Output](#output)

## Introduction

Working with files is a fundamental part of data engineering. These scripts illustrate how to build robust pipelines for common file-based data sources, including:

- Reading data from CSV and JSON (JSON Lines) files.
- Performing data validation and type conversions.
- Handling and logging "bad records" that fail quality checks.
- Aggregating data.
- Implementing incremental processing (processing only new data).
- Loading processed data into a PostgreSQL database using SQLAlchemy.

## Scripts Overview

- `process_transactions.py`:
  - **Purpose**: Demonstrates incremental processing of daily CSV transaction files and aggregates sales data.
  - **Concepts**: Incremental processing, file discovery, basic aggregation, state management (`last_processed_date.txt`).
- `etl_products.py`:
  - **Purpose**: Implements a full ETL pipeline for product and inventory data from CSV and JSON, merging them, performing rigorous data quality checks, and loading into PostgreSQL.
  - **Concepts**: Multi-source data ingestion, complex transformations, comprehensive data validation, "bad records" logging, database upserts (insert or update), configuration management (`config.ini`).

## Setup and Running

### Prerequisites

1.  **Activated Python Virtual Environment**: Ensure you are in your project's root directory (`data-engineering-journey/`) and your `venv` is activated.
2.  **Installed Dependencies**: All packages listed in your root `requirements.txt` (especially `pandas`, `requests`, `pendulum`, `psycopg2-binary`, `SQLAlchemy`) should be installed.
    ```bash
    # From project root: data-engineering-journey/
    pip install -r requirements.txt
    ```
3.  **Running PostgreSQL Database**: The `etl_products.py` script requires a running PostgreSQL instance. Refer to [`01-sql_and_databases/README.md`](../../01-sql_and_databases/README.md) for instructions on how to set it up using Docker.

### Configuration

This directory uses a `config.ini` file for configurable parameters like database credentials and file paths.

1.  **Create `config.ini`**:
    Create a file named `config.ini` directly within the `02-python_for_de/file_processing_scripts/` directory:

    ```ini
    [database]
    db_host = localhost
    db_port = 5432
    db_name = your_de_db
    db_user = your_user
    db_password = your_password

    [paths]
    data_input_dir = data
    processed_output_dir = processed_output
    bad_records_dir = bad_records
    ```

    **IMPORTANT**: Update `db_name`, `db_user`, and `db_password` to match your PostgreSQL setup. The provided `etl_products.py` will try to create a dummy `config.ini` if it doesn't exist, but you still need to fill in the correct DB credentials.

### Input Data

The scripts expect input data files in the `data/` sub-directory.

1.  **Create `data/` directory**:
    ```bash
    mkdir -p data
    ```
2.  **Generate Dummy Input Files**:
    The Python scripts (`process_transactions.py`, `etl_products.py`) include logic to create dummy input CSV/JSON files if they don't exist. This is helpful for initial testing.
    - For `process_transactions.py`: `transactions_YYYYMMDD.csv`
    - For `etl_products.py`: `products_YYYYMMDD.csv`, `inventory_YYYYMMDD.json`
      (Where `YYYYMMDD` is the current date).

### Running the ETL Script

1.  **Navigate to the directory**:
    ```bash
    cd data-engineering-journey/02-python_for_de/file_processing_scripts
    ```
2.  **Run `process_transactions.py`**:

    ```bash
    python process_transactions.py
    ```

    This script will process new transaction files and output aggregated sales data to `processed_output/`. It will also create/update `last_processed_date.txt`.

3.  **Run `etl_products.py`**:
    **Ensure your PostgreSQL database is running and accessible before running this!**
    ```bash
    python etl_products.py
    ```
    This script will:
    - Read product CSV and inventory JSON.
    - Perform validations.
    - Load valid records into the `products` table in your PostgreSQL database.
    - Write any invalid records to `bad_records/bad_records_YYYYMMDD.jsonl`.

## Output

- `process_transactions.py`: Generates `daily_aggregated_sales_YYYYMMDD.csv` in the `processed_output/` directory and updates `last_processed_date.txt`.
- `etl_products.py`: Loads data directly into your PostgreSQL database. Any records failing validation are written to `bad_records/bad_records_YYYYMMDD.jsonl`.
