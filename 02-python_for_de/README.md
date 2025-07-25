# 02-Python for Data Engineering

This directory is dedicated to honing your Python skills for Data Engineering tasks. Python is the most versatile language in the DE ecosystem, used for everything from scripting ETL jobs to building API integrations, data quality checks, and interacting with big data frameworks.

## Table of Contents

- [02-Python for Data Engineering](#02-python-for-data-engineering)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Setup](#setup)
    - [Virtual Environment](#virtual-environment)
    - [Dependencies](#dependencies)
    - [Database (PostgreSQL)](#database-postgresql)
  - [Contents](#contents)
    - [1. `file_processing_scripts/`](#1-file_processing_scripts)
    - [2. `api_ingestion/`](#2-api_ingestion)
  - [Key Learnings](#key-learnings)

---

## Introduction

In this section, you will learn to:

- Write robust Python scripts for data extraction, transformation, and loading (ETL).
- Handle various file formats (CSV, JSON, JSONL).
- Interact with REST APIs, including handling pagination and retries.
- Implement data validation and quality checks.
- Manage script configuration using `.ini` files.
- Perform incremental data processing and deduplication.
- Interact with relational databases (PostgreSQL) using Python.
- Implement logging and error handling for production-ready scripts.

---

## Setup

### Virtual Environment

It is highly recommended to use a Python virtual environment to manage dependencies for this project.

1.  **Navigate to the root of your project:**
    ```bash
    cd data-engineering-journey
    ```
2.  **Create a virtual environment (if you haven't already):**
    ```bash
    python -m venv venv
    ```
3.  **Activate the virtual environment:**
    - **On Windows:**
      ```bash
      .\venv\Scripts\activate
      ```
    - **On macOS/Linux:**
      `bash
    source venv/bin/activate
    `
      You should see `(venv)` prefixed to your terminal prompt, indicating the environment is active.

### Dependencies

All Python dependencies for this section are listed in the `requirements.txt` file in the root directory.

1.  **Install dependencies:**
    With your virtual environment activated:
    ```bash
    pip install -r requirements.txt
    ```
    This will install necessary libraries such as `pandas`, `requests`, `pendulum`, `psycopg2-binary`, `SQLAlchemy`, etc.

### Database (PostgreSQL)

Some examples in this directory (specifically within `file_processing_scripts`) require a running PostgreSQL database.

- **Ensure your PostgreSQL container is running** as set up in the `01-SQL and Databases` section.
- Verify the database name, username, and password in your `02-python_for_de/file_processing_scripts/config.ini` match your PostgreSQL setup.

---

## Contents

This directory is organized into sub-directories, each focusing on a specific aspect of Python for Data Engineering.

### 1. `file_processing_scripts/`

This sub-directory contains Python scripts for processing data from various file formats, focusing on robust ETL patterns.

- **Concepts Covered:** File I/O (CSV, JSON), incremental processing, data cleaning, transformations, aggregations, data validation, error logging (bad records), and loading data into a database.

- **Key Files:**

  - `config.ini`: Configuration file for database credentials and file paths. **(REQUIRED: Update DB credentials)**
  - `data/`: Input data files (`transactions_YYYYMMDD.csv`, `products_YYYYMMDD.csv`, `inventory_YYYYMMDD.json`). These files are often created automatically by the scripts for initial testing.
  - `last_processed_date.txt`: (Used by `process_transactions.py`) A state file to track the last successfully processed date for incremental processing.
  - `bad_records/`: Output directory for records that fail data quality checks.
  - `processed_output/`: Output directory for processed files (if any).
  - `process_transactions.py`:
    - **Purpose:** Demonstrates incremental processing of daily transaction CSVs and advanced aggregations.
    - **Scenario:** Processes new daily transaction files, validates data, aggregates sales by category and region, and outputs to a new CSV. It uses `last_processed_date.txt` to track processed files.
  - `etl_products.py`:
    - **Purpose:** Implements a full ETL pipeline, combining data from CSV and JSON sources, performing complex validations, and loading into PostgreSQL.
    - **Scenario:** Merges product details (CSV) with inventory updates (JSON), validates all fields, handles invalid records by writing them to a `bad_records` log, calculates derived metrics (`CurrentValue`), and performs an upsert (update or insert) into a PostgreSQL `products` table.

- **How to Run `file_processing_scripts`:**
  1.  **Navigate:** Change directory to `02-python_for_de/file_processing_scripts/`:
      ```bash
      cd data-engineering-journey/02-python_for_de/file_processing_scripts
      ```
  2.  **Ensure `config.ini` exists and is updated:**
      - The `etl_products.py` script will create a dummy `config.ini` if it doesn't exist.
      - **Open `config.ini` and update the `db_user`, `db_password`, and `db_name`** to match your PostgreSQL setup (from `01-sql_and_databases`).
      - **Ensure PostgreSQL is running!** (`docker compose -f ../../01-sql_and_databases/docker-compose-postgres.yml up -d`)
  3.  **Run scripts:**
      ```bash
      python process_transactions.py
      python etl_products.py
      ```
  4.  **Explore Outputs:** Check the `processed_output/` and `bad_records/` directories for generated files. Connect to your PostgreSQL DB to verify data loaded by `etl_products.py`.

### 2. `api_ingestion/`

This sub-directory focuses on interacting with REST APIs for data ingestion, emphasizing resilience and structured storage.

- **Concepts Covered:** API client design, retry logic (exponential backoff), handling API rate limits (conceptual), dynamic API calls (nested fetches), data deduplication, and saving data to daily-partitioned JSONL files.

- **Key Files:**

  - `config.ini`: Configuration file for API base URLs and output paths.
  - `processed_user_ids.txt`: A state file to track already ingested user/order IDs for deduplication.
  - `data/`: Output directory structured for partitioned data (e.g., `data/orders/YYYY/MM/DD/`).
  - `ingest_orders.py`:
    - **Purpose:** Orchestrates API calls to fetch "orders" (users) and their corresponding "items" (todos) from `jsonplaceholder.typicode.com`.
    - **Scenario:** Fetches a list of users (simulated orders), then for each user, fetches their associated todos (simulated order items). It implements robust retry logic for API calls, uses a state file for deduplication across script runs, and saves the enriched data into daily-partitioned `.jsonl` files.

- **How to Run `api_ingestion`:**
  1.  **Navigate:** Change directory to `02-python_for_de/api_ingestion/`:
      ```bash
      cd data-engineering-journey/02-python_for_de/api_ingestion
      ```
  2.  **Ensure `config.ini` exists:** The `ingest_orders.py` script will create a dummy `config.ini` if it doesn't exist. The default `base_url` for `jsonplaceholder.typicode.com` should work.
  3.  **Run script:**
      ```bash
      python ingest_orders.py
      ```
      Run it multiple times to observe the deduplication logic.
  4.  **Explore Outputs:** Check the `data/orders/` directory for the partitioned `.jsonl` files.

---

## Key Learnings

By completing the exercises in this directory, you will develop:

- Strong Python programming skills applicable to diverse data engineering tasks.
- The ability to build robust and fault-tolerant data pipelines.
- Practical experience with file processing, API interactions, and database loading.
- An understanding of incremental processing, data quality, and deduplication strategies.
- Best practices for script organization, configuration, logging, and error handling.
