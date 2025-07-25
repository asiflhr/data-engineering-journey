# 01-SQL and Databases

This directory contains foundational exercises and examples related to SQL and database management. Mastering SQL is crucial for any Data Engineer, as it's the primary language for interacting with relational databases, data warehouses, and many data processing systems. Understanding database concepts like schemas, tables, relationships, and basic administration is equally vital.

## Table of Contents

- [01-SQL and Databases](#01-sql-and-databases)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Setup](#setup)
    - [PostgreSQL with Docker Compose](#postgresql-with-docker-compose)
  - [Contents](#contents)
    - [1. Basic SQL Queries](#1-basic-sql-queries)
    - [2. Advanced SQL Concepts](#2-advanced-sql-concepts)
    - [3. Database Administration Basics](#3-database-administration-basics)
  - [How to Run Examples](#how-to-run-examples)
  - [Key Learnings](#key-learnings)

---

## Introduction

In this section, you will learn to:

- Write and execute basic to advanced SQL queries.
- Understand common SQL operations like `SELECT`, `INSERT`, `UPDATE`, `DELETE`.
- Explore joins, aggregations, window functions, and common table expressions (CTEs).
- Get hands-on experience with a relational database management system (RDBMS), specifically PostgreSQL.
- Perform basic database setup and user management.

---

## Setup

The primary database used in this section is **PostgreSQL**, deployed using **Docker Compose** for easy setup and teardown.

### PostgreSQL with Docker Compose

1.  **Prerequisites:**
    - [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running on your system.
2.  **Navigate:** Go to the `01-sql_and_databases` directory:
    ```bash
    cd data-engineering-journey/01-sql_and_databases
    ```
3.  **Docker Compose File:** You should find a `docker-compose-postgres.yml` file here (or a similarly named file). This file defines the PostgreSQL service.

    _Example `docker-compose-postgres.yml` (if you don't have one, create it):_

    ```yaml
    version: '3.8'

    services:
      postgres_db:
        image: postgres:16-alpine
        container_name: de_postgres_container
        environment:
          POSTGRES_DB: your_de_db # Replace with your desired database name
          POSTGRES_USER: your_user # Replace with your desired username
          POSTGRES_PASSWORD: your_password # Replace with a strong password
        ports:
          - '5432:5432' # Host:Container port
        volumes:
          - postgres_data:/var/lib/postgresql/data # Persistent data volume
        healthcheck:
          test: ['CMD-SHELL', 'pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB']
          interval: 5s
          timeout: 5s
          retries: 5

    volumes:
      postgres_data:
    ```

    **IMPORTANT:** Before starting the container, **replace `your_de_db`, `your_user`, and `your_password`** with your actual desired credentials. Remember these, as they will be used in subsequent sections (e.g., Python scripts connecting to the DB).

4.  **Start the PostgreSQL container:**

    ```bash
    docker compose -f docker-compose-postgres.yml up -d
    ```

    This command will:

    - Download the `postgres:16-alpine` image (if not already present).
    - Create and start a container named `de_postgres_container`.
    - Expose port `5432` on your host machine, mapping it to the container's PostgreSQL port.
    - Create a Docker volume `postgres_data` for persistent storage of your database data.

5.  **Verify the container is running:**

    ```bash
    docker ps
    ```

    You should see `de_postgres_container` listed with status `Up`.

6.  **Connect to the Database (using psql client):**
    You can connect to your running PostgreSQL instance using a SQL client like `psql` (if installed locally) or from within the Docker container:

    ```bash
    # From your host machine, using psql (requires psql client installed locally)
    psql -h localhost -p 5432 -U your_user -d your_de_db

    # Or, from within the Docker container (no local psql needed)
    docker exec -it de_postgres_container psql -U your_user -d your_de_db
    ```

    Enter your password when prompted.

7.  **Stop the PostgreSQL container (when done):**

    ```bash
    docker compose -f docker-compose-postgres.yml down
    ```

    This will stop and remove the container. The `postgres_data` volume will persist by default, so your data remains for future starts.

8.  **Remove the data volume (if you want a fresh start):**
    ```bash
    docker compose -f docker-compose-postgres.yml down -v
    ```
    **CAUTION:** This will permanently delete all data stored in the `postgres_data` volume. Only do this if you want to wipe your database clean.

---

## Contents

This directory will contain `.sql` files and potentially `.py` scripts for database interactions, organized into sub-sections.

### 1. Basic SQL Queries

(e.g., `basic_select.sql`, `insert_data.sql`, `update_delete.sql`)

- **Purpose:** Introduce fundamental SQL commands for data retrieval and manipulation.
- **Examples:**
  - `SELECT` statements with `WHERE`, `ORDER BY`, `LIMIT`.
  - `INSERT` new records.
  - `UPDATE` existing records.
  - `DELETE` records.
  - `CREATE TABLE` and `DROP TABLE`.

### 2. Advanced SQL Concepts

(e.g., `joins_aggregations.sql`, `window_functions.sql`, `ctes.sql`)

- **Purpose:** Dive into more complex SQL features essential for data analysis and transformation.
- **Examples:**
  - `INNER JOIN`, `LEFT JOIN`, `RIGHT JOIN`, `FULL OUTER JOIN`.
  - `GROUP BY` with aggregate functions (`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`).
  - Subqueries.
  - Window functions (`ROW_NUMBER()`, `RANK()`, `LAG()`, `LEAD()`, `SUM() OVER (...)`).
  - Common Table Expressions (CTEs) for better query readability and modularity.

### 3. Database Administration Basics

(e.g., `user_management.sql`, `schema_management.sql`)

- **Purpose:** Cover basic administrative tasks for managing users, roles, and schemas.
- **Examples:**
  - `CREATE USER`, `CREATE ROLE`.
  - `GRANT` and `REVOKE` permissions.
  - `CREATE SCHEMA`.

---

## How to Run Examples

1.  **Ensure PostgreSQL is running** (refer to the [Setup](#setup) section).
2.  **Connect to your database** using `psql` (via `docker exec` or local client).
3.  **Execute `.sql` files:**
    Once connected to `psql`, you can execute SQL scripts using the `\i` command:

    ```sql
    \i /path/to/your/sql_file.sql
    ```

    For example:

    ```sql
    \i /tmp/basic_select.sql
    ```

    (Note: If running from outside Docker, ensure the path is accessible to your local `psql` client. If running inside `docker exec`, you might need to copy files into the container or mount a volume.)

    Alternatively, you can copy the SQL content and paste it directly into the `psql` terminal.

---

## Key Learnings

By completing the exercises in this directory, you will gain:

- A solid understanding of relational database principles.
- Proficiency in writing efficient and complex SQL queries.
- Hands-on experience with PostgreSQL, a widely used open-source RDBMS.
- The ability to set up and manage basic database environments using Docker.
