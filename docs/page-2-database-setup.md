# PostgreSQL Database Setup: `leafcloud3`

Kini nga dokumento nag-detalye sa pag-setup ug migration gikan sa SQLite ngadto sa **PostgreSQL**.

## 1. Unsa ang gibuhat?
Nag-transition kita gikan sa file-based database (SQLite) ngadto sa usa ka mas powerful nga relational database management system (RDBMS) nga mao ang PostgreSQL.

### Mga kausaban:
*   Nag-create og bag-ong database sa PostgreSQL nga ginganlan og `leafcloud3`.
*   Gi-update ang `.env` file aron gamiton ang PostgreSQL connection string.
*   Gi-configure ang SQLAlchemy engine aron mo-support sa PostgreSQL driver (`psycopg2`).

---

## 2. Configuration Details

Ang mga credentials nga gi-set sa `.env` para sa local development:

*   **DB_USER**: `fil`
*   **DB_PASSWORD**: (none)
*   **DB_HOST**: `localhost`
*   **DB_PORT**: `5432`
*   **DB_NAME**: `leafcloud3`
*   **DATABASE_URL**: `postgresql://fil:@localhost:5432/leafcloud3`

---

## 3. Giunsa pag-setup ang Database?

### A. Manual Creation (kung wala pa)
Kung kinahanglan nimo i-recreate ang database manually:
```bash
psql -U fil -d postgres -c "CREATE DATABASE leafcloud3;"
```

### B. Automatic Table Creation
Inig start sa FastAPI server, ang SQLAlchemy automatic nga mo-create sa mga tables (sama sa `users` table) kung wala pa kini sa `leafcloud3` database. Kini tungod sa kini nga code sa `app/main.py`:
```python
models.Base.metadata.create_all(bind=engine)
```

---

## 4. Unsaon Pag-verify?

1.  **Start the Server**:
    ```bash
    ~/.env_leafcloud/bin/uvicorn app.main:app --reload
    ```
2.  **Check PostgreSQL Tables**:
    Mahimo nimo i-check kung na-create ba ang tables gamit ang `psql`:
    ```bash
    psql -U fil -d leafcloud3 -c "\dt"
    ```
3.  **Test Login**:
    Inig start sa server, i-seed gihapon niini ang default admin user sa PostgreSQL. Mahimo nimo i-test ang login endpoint gamit ang `curl` (tan-awa ang `docs/page-1-login.md`).

---

## 5. Nganong PostgreSQL?
*   **Concurrency**: Mas maayo ang PostgreSQL sa pag-handle og daghang simultaneous users/requests.
*   **Data Integrity**: Mas stricto ang PostgreSQL sa types ug constraints.
*   **Scalability**: Mas sayon i-scale sa production environment (sama sa Cloud SQL o AWS RDS).
