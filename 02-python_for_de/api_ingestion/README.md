# API Ingestion Scripts

This directory contains Python scripts for ingesting data from external APIs. The examples here demonstrate advanced API interaction patterns, including handling pagination, implementing retry mechanisms, orchestrating multiple API calls, and saving data in a structured, partitioned manner suitable for data lakes.

## Table of Contents

- [API Ingestion Scripts](#api-ingestion-scripts)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Scripts Overview](#scripts-overview)
  - [Setup and Running](#setup-and-running)
    - [Prerequisites](#prerequisites)
    - [Configuration](#configuration)
    - [Running the Ingestion Script](#running-the-ingestion-script)
  - [Output](#output)

## Introduction

API ingestion is a common task in data engineering, but it comes with its own set of challenges: rate limits, pagination, inconsistent data, and network failures. These scripts provide solutions for:

- Making robust API requests with retry logic.
- Handling "paginated" data (even when simulated for demonstration).
- Fetching related data across multiple API endpoints (orchestration).
- Implementing basic data deduplication using state files.
- Storing ingested data in a well-organized, partitioned file structure.

## Scripts Overview

- `ingest_orders.py`:
  - **Purpose**: Simulates fetching "orders" (users) and their "items" (todos) from `jsonplaceholder.typicode.com`, enriching the data, applying deduplication, and saving to daily-partitioned JSON Lines files.
  - **Concepts**: API client class, retry decorator, API orchestration (nested calls), simulated pagination, state management for deduplication (`processed_user_ids.txt`), structured data lake partitioning (`data/orders/YYYY/MM/DD/`).

## Setup and Running

### Prerequisites

1.  **Activated Python Virtual Environment**: Ensure you are in your project's root directory (`data-engineering-journey/`) and your `venv` is activated.
2.  **Installed Dependencies**: All packages listed in your root `requirements.txt` (especially `requests`, `pendulum`) should be installed.
    ```bash
    # From project root: data-engineering-journey/
    pip install -r requirements.txt
    ```
3.  **Internet Connectivity**: The script will make live API calls to `jsonplaceholder.typicode.com`.

### Configuration

This directory uses a `config.ini` file to define the API base URL and file paths.

1.  **Create `config.ini`**:
    Create a file named `config.ini` directly within the `02-python_for_de/api_ingestion/` directory:

    ```ini
    [api]
    base_url = [https://jsonplaceholder.typicode.com](https://jsonplaceholder.typicode.com)

    [paths]
    output_data_dir = data
    processed_ids_file = processed_user_ids.txt
    ```

    The script will create a dummy `config.ini` if it doesn't exist.

### Running the Ingestion Script

1.  **Navigate to the directory**:
    ```bash
    cd data-engineering-journey/02-python_for_de/api_ingestion
    ```
2.  **Run `ingest_orders.py`**:
    ```bash
    python ingest_orders.py
    ```
    This script will:
    - Fetch users (simulated orders) and their todos (simulated order items).
    - Enrich the user data with their todos.
    - Skip users whose IDs are already recorded in `processed_user_ids.txt`.
    - Save the enriched data into `data/orders/YYYY/MM/DD/orders_YYYYMMDD_HHMMSS.jsonl` files.
    - Update `processed_user_ids.txt` with newly processed IDs.
    - Try running the script multiple times to observe the deduplication logic in action.

## Output

- `ingest_orders.py`: Generates enriched JSON Lines files in a partitioned directory structure like `data/orders/YYYY/MM/DD/`. It also manages the `processed_user_ids.txt` file for state tracking.
