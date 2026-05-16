# PostgreSQL Database Setup: `leafcloud3`

This document details the setup and migration from SQLite to **PostgreSQL**.

## 1. What was done?
We transitioned from a file-based database (SQLite) to a more powerful relational database management system (RDBMS), PostgreSQL.

### Changes:
*   Created a new PostgreSQL database named `leafcloud3`.
*   Updated the `.env` file to use the PostgreSQL connection string.
*   Configured the SQLAlchemy engine to support the PostgreSQL driver (`psycopg2`).

---

## 2. Configuration Details

The credentials set in the `.env` file for local development:

*   **DB_USER**: `fil`
*   **DB_PASSWORD**: (none)
*   **DB_HOST**: `localhost`
*   **DB_PORT**: `5432`
*   **DB_NAME**: `leafcloud3`
*   **DATABASE_URL**: `postgresql://fil:@localhost:5432/leafcloud3`

---

## 3. How to Setup the Database

### A. Manual Creation (if needed)
If you need to recreate the database manually:
```bash
psql -U fil -d postgres -c "CREATE DATABASE leafcloud3;"
```

### B. Database Query Utility Script
We added a utility script at `scripts/run-query.sh` to easily execute SQL queries and save results to a file.

**How to use:**
```bash
./scripts/run-query.sh "SELECT * FROM users;"
```
*Results are saved to `database-query.result`.*

To append to results:
```bash
./scripts/run-query.sh --append "SELECT count(*) FROM users;"
```

### C. Database Migrations (Alembic)
Instead of automatic table creation, we now use **Alembic** for more controlled management of the database schema.

**How to run migrations:**
1.  **Check current status**:
    ```bash
    export PYTHONPATH=$PYTHONPATH:.
    ~/.env_leafcloud/bin/alembic current
    ```
2.  **Upgrade to latest version**:
    ```bash
    export PYTHONPATH=$PYTHONPATH:.
    ~/.env_leafcloud/bin/alembic upgrade head
    ```
3.  **Create new migration** (if there are changes in `models.py`):
    ```bash
    export PYTHONPATH=$PYTHONPATH:.
    ~/.env_leafcloud/bin/alembic revision --autogenerate -m "Description of changes"
    ```

### D. Automatic Admin Seeding

1.  **Start the Server**:
    ```bash
    ~/.env_leafcloud/bin/uvicorn app.main:app --reload
    ```
2.  **Check PostgreSQL Tables**:
    You can check if tables were created using `psql`:
    ```bash
    psql -U fil -d leafcloud3 -c "\dt"
    ```
3.  **Test Login**:
    When the server starts, it will still seed the default admin user in PostgreSQL. You can test the login endpoint using `curl` (see `docs/page-1-login.md`).

---

## 5. Why PostgreSQL?
*   **Concurrency**: PostgreSQL is better at handling multiple simultaneous users/requests.
*   **Data Integrity**: PostgreSQL is stricter with types and constraints.
*   **Scalability**: Easier to scale in a production environment (like Cloud SQL or AWS RDS).
