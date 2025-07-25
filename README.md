# My Data Engineering Learning Journey

This repository contains all my practice projects and code as I follow the comprehensive [Data Engineering Roadmap By Data With Baraa](https://www.notion.so/Data-Engineering-Roadmap-By-Data-With-Baraa-239080cfd3d4800e83d0c94ba5880247). This journey covers fundamental concepts and practical applications across various data engineering domains, designed to build a solid foundation in the field.

## Project Overview

This repository serves as a practical portfolio showcasing hands-on experience in:

- **Database Management:** Designing, interacting with, and querying relational databases.
- **Python for Data Engineering:** Developing robust scripts for data extraction, transformation, and loading (ETL).
- **Containerization:** Utilizing Docker for consistent development and deployment environments.
- **Workflow Orchestration:** Building and managing data pipelines with Apache Airflow.
- **Big Data Processing:** Leveraging Apache Spark for scalable data transformations.
- **Data Quality & Observability:** Implementing data validation, error handling, and logging for reliable pipelines.

## Setup Instructions

To get this repository up and running on your local machine, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/asif8/data-engineering-journey.git](https://github.com/asif8/data-engineering-journey.git) # Replace with your actual repo URL if different
    cd data-engineering-journey
    ```
2.  **Create and activate a Python virtual environment:**
    It's highly recommended to use a virtual environment to manage project dependencies isolation.
    ```bash
    python3 -m venv venv
    # On Linux/macOS:
    source venv/bin/activate
    # On Windows:
    .\venv\Scripts\activate
    ```
3.  **Install the required dependencies:**
    All necessary Python packages are listed in `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```
4.  **Database Setup (for relevant modules):**
    Some projects, particularly within `01-sql_and_databases` and `02-python_for_de`, require a PostgreSQL database. You can set this up using Docker Compose provided in the repository.
    - Navigate to the `01-sql_and_databases` directory:
      ```bash
      cd 01-sql_and_databases
      ```
    - Start the PostgreSQL container:
      ```bash
      docker compose -f docker-compose-postgres.yml up -d
      ```
    - **Crucially:** Ensure you create the database and user as specified in the respective `config.ini` files (e.g., `your_de_db`, `your_user`, `your_password`). You can connect to the running PostgreSQL instance (e.g., using `psql` or `pgAdmin`) to do this. For testing, you might use default `postgres` for user/password if suitable.
    - When done, you can stop the container: `docker compose -f docker-compose-postgres.yml down`
    - Return to the root directory: `cd ..`

## Folder Structure

This repository is organized by technology or core data engineering concept, allowing for focused learning and easy navigation:

- `01-sql_and_databases`:
  - Contains SQL scripts for database schema creation, data manipulation, and complex queries.
  - Includes `docker-compose-postgres.yml` for setting up a local PostgreSQL instance for practice.
  - Examples cover topics like DDL, DML, joins, window functions, and database design principles.
- `02-python_for_de`:
  - Dedicated to Python scripts demonstrating common data engineering tasks.
  - **`file_processing_scripts/`**: Examples for handling various file formats (CSV, JSON, JSONL), including:
    - Data cleaning and transformation.
    - Incremental data processing and state management.
    - Advanced aggregation and data quality checks.
    - Robust error handling with bad records logging.
    - Full ETL pipelines integrated with external configurations and database loading (e.g., PostgreSQL).
  - **`api_ingestion/`**: Scripts for interacting with RESTful APIs, featuring:
    - API pagination and dynamic nested API calls.
    - Robust error recovery with retry mechanisms (e.g., exponential backoff).
    - Data deduplication strategies.
    - Saving ingested data in structured, partitioned formats (e.g., daily JSONL files for data lakes).
  - **`config.ini` files**: Used to manage configurable parameters (database credentials, file paths, API URLs), promoting reusability and maintainability.
- `03-containerization_docker`:
  - Examples of Dockerfiles for packaging applications and their dependencies.
  - Demonstrations of `docker-compose` for orchestrating multi-service applications (e.g., a database and an application).
  - Focus on creating reproducible and isolated development environments.
- `04-workflow_orchestration_airflow`:
  - Contains Apache Airflow Directed Acyclic Graphs (DAGs).
  - Illustrates how to schedule, monitor, and manage data pipelines programmatically.
  - Examples might include task dependencies, data sensors, and different operator types.
- `05-data-processing-spark`:
  - Focuses on using Apache Spark (PySpark) for big data processing.
  - Examples will cover:
    - Reading and writing large datasets (e.g., Parquet, Delta Lake).
    - Data transformations (ETL) at scale.
    - Spark SQL queries and DataFrame operations.
    - Performance considerations for distributed computing.
  - **(Future Content: Potential for integrating Spark with Docker/Airflow for end-to-end big data pipelines).**

## How to Run Examples

Each major directory (`01-sql_and_databases`, `02-python_for_de`, etc.) will typically contain its own `README.md` or detailed comments within the scripts explaining how to run the specific examples within that module.

**General Steps:**

1.  Navigate to the relevant directory (e.g., `cd 02-python_for_de/file_processing_scripts`).
2.  Ensure any required `config.ini` files are properly configured with your local settings.
3.  Execute the Python script (e.g., `python etl_products.py`).
4.  Observe output in the console, generated files, or check your database.

---

**Contributions & Feedback:**

This repository is a personal learning journey. However, feedback, suggestions, or constructive criticism are always welcome! Feel free to open an issue or pull request.

**Connect with me:**

- [LinkedIn](https://www.linkedin.com/in/asiflhr)
- [Personal Website/Blog](https://asiflhr.vercel.app)

---
