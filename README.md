# LeafCloud Server V2

LeafCloud Server V2 is a robust, scalable backend built with **FastAPI**, **PostgreSQL**, and **SQLAlchemy**. It features a secure JWT-based authentication system and automated network discovery using **Zeroconf (mDNS)**.

The project is architected following **SOLID principles** and modular layered patterns to ensure high maintainability and developer productivity.

## 🚀 Key Features

- **Modular Architecture**: Layered separation of concerns (Core, API, Models, Schemas, Services).
- **Secure Authentication**: JWT-based auth with Bcrypt password hashing.
- **Service Discovery**: Automatic mDNS broadcasting for easy local network discovery.
- **Database Migrations**: Systematic schema management using Alembic.
- **Environment Management**: Type-safe configuration via `pydantic-settings`.

---

## 🛠 Quick Start

### 1. Prerequisites
- Python 3.8+
- PostgreSQL
- A virtual environment (recommended)

### 2. Installation
```bash
git clone <repository-url>
cd mimeng_leafcloud_server_v2
pip install -r requirements.txt
```

### 3. Environment Setup
Copy the template and fill in your local database credentials:
```bash
cp .env.example .env
```

### 4. Database Migration
Update your PostgreSQL database to the latest schema:
```bash
export PYTHONPATH=$PYTHONPATH:.
alembic upgrade head
```

### 5. Start the Server
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000` and the interactive docs at `http://localhost:8000/docs`.

---

## 📖 Documentation Index

For detailed guides, please refer to our documentation pages:

1.  **[Authentication System](docs/page-1-login.md)** - Details on JWT and Login logic.
2.  **[Database Setup](docs/page-2-database-setup.md)** - Guide on PostgreSQL configuration.
3.  **[Migrations (Alembic)](docs/page-3-migrations-alembic.md)** - How to manage schema changes.
4.  **[Network Discovery](docs/page-4-zeroconf-discovery.md)** - Details on Zeroconf/mDNS implementation.
5.  **[Developer Guide](docs/page-5-developer-guide.md)** - **Start here** for architecture and contribution workflows.
6.  **[Daily Readings Model](docs/page-6-daily-readings.md)** - Details on the sensor data schema.

---

## 🧪 Verification Tools

- **Verify Discovery**: `python scripts/verify-zeroconf.py`
- **Run SQL Queries**: `./scripts/run-query.sh "SELECT * FROM users;"`
