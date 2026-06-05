[Prev](./page-47-model-evolution-history.md)

# 🪟 Windows & WSL PostgreSQL Setup Guide

This document is a comprehensive, step-by-step developer's guide focused specifically on setting up, migrating, and running the LeafCloud Server V2 backend on **Windows**, using **PostgreSQL** running inside the **Windows Subsystem for Linux (WSL)**.

---

## 📋 1. Prerequisites
Ensure you have the following installed on your Windows machine:
*   **Python 3.8 to 3.13** (installed on Windows)
*   **Git** (installed on Windows)
*   **WSL** (with Ubuntu/Debian installed and running)

---

## ⚙️ 2. Repository Cloning & Environment Setup

### Step A: Clone the Repository (Windows)
Open PowerShell and clone the repository:
```powershell
git clone https://github.com/ChristineToraque/leafcloud_server.git
cd leafcloud_server
```

### Step B: Create and Activate the Virtual Environment
Create your Python virtual environment. In Windows, you need to set the execution policy to allow script activation:
```powershell
python -m venv .venv
(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned) ; (& .venv\Scripts\Activate.ps1)
```

### Step C: Install Dependencies & Drivers
Install the Python packages along with `psycopg2-binary` (the PostgreSQL adapter) and machine learning modules:
```powershell
pip install -r requirements.txt alembic tensorflow opencv-python psycopg2-binary
```

> [!IMPORTANT]
> **Passlib & Bcrypt Compatibility Fix**:
> Newer versions of `bcrypt` (4.0.0+) strictly forbid passwords longer than 72 bytes. This causes an internal wrap-bug check in `passlib` to throw a crash during startup.
>
> To resolve this compatibility gap, install `bcrypt` version 3.x:
> ```powershell
> pip install "bcrypt<4.0.0"
> ```

---

## 🗄️ 3. WSL PostgreSQL Setup & Terminal Connection

To use the PostgreSQL instance running inside WSL, follow these steps:

### Step A: Start PostgreSQL service inside WSL
In your WSL terminal (or via Windows PowerShell by prefixing `wsl`):
```powershell
wsl sudo service postgresql start
```

### Step B: Connect to the PostgreSQL Terminal from Windows
You do not need to install the `psql` client on Windows. Instead, connect to the WSL database terminal directly from PowerShell:
```powershell
wsl -u postgres psql
```

### Step C: Create the Database & User
Inside the PostgreSQL terminal (`psql` shell), run the following queries to create the user and database:
```sql
-- Create user tin with password tin123
CREATE USER tin WITH PASSWORD 'tin123';

-- Create the leafcloud3 database owned by tin
CREATE DATABASE leafcloud3 OWNER tin;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE leafcloud3 TO tin;

-- Exit the psql terminal
\q
```

*Note: If you already have the `tin` user and want to update/set the password, run:*
```powershell
wsl -u postgres psql -c "ALTER USER tin WITH PASSWORD 'tin123';"
```

---

## 🔧 4. Environment Variables Configuration

Copy the template environment configuration file to create your active `.env` file:
```powershell
copy .env.example .env
```

Open the newly created `.env` file and configure the database URL to point to WSL PostgreSQL (WSL 2 automatically forwards localhost ports, so `localhost:5432` from Windows routes directly to WSL):
```env
DATABASE_URL="postgresql://tin:tin123@localhost:5432/leafcloud3"
DB_USER="tin"
DB_PASSWORD="tin123"
DB_HOST="localhost"
DB_PORT=5432
DB_NAME="leafcloud3"
```

---

## 🔄 5. Run Database Migrations (Windows PowerShell)

Run the Alembic migrations command from Windows to create all tables inside the WSL PostgreSQL database:
```powershell
$env:PYTHONPATH="."
python -m alembic upgrade head
```

You can verify the tables were created successfully by running this query from PowerShell:
```powershell
wsl -u postgres psql -d leafcloud3 -c "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"
```

---

## ⚡ 6. Start the Server

Ensure the static directory for images exists:
```powershell
mkdir images
```

Launch the FastAPI backend server:
```powershell
$env:PYTHONPATH="."
uvicorn app.main:app --reload
```

Upon startup, the server automatically:
1. Registers Zeroconf (mDNS) broadcasting on the local network.
2. Seeds the default admin account into your WSL PostgreSQL database:
   *   **Admin Email**: `admin@leafcloud.com`
   *   **Admin Password**: `admin123`

---

## 🔍 7. Troubleshooting Windows-WSL Connection Issues

*   **Error**: `fe_sendauth: no password supplied`
    *   **Fix**: PostgreSQL inside WSL requires password authentication for network loopback connections. Verify your `.env` contains `tin123` in both the `DATABASE_URL` and `DB_PASSWORD` variables, and that you ran `ALTER USER tin WITH PASSWORD 'tin123';`.
*   **Error**: `Connection timed out` or `Is the server running and accepting TCP/IP connections?`
    *   **Fix**: Verify that the PostgreSQL service is actively running inside WSL by running `wsl service postgresql status`.

---

[Prev](./page-47-model-evolution-history.md)
