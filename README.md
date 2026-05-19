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

#### Common Migration Commands:
- **Apply migrations**: `export PYTHONPATH=$PYTHONPATH:. && alembic upgrade head`
- **Create new migration**: `export PYTHONPATH=$PYTHONPATH:. && alembic revision --autogenerate -m "description"`
- **Check current version**: `export PYTHONPATH=$PYTHONPATH:. && alembic current`
- **View history**: `export PYTHONPATH=$PYTHONPATH:. && alembic history`

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
7.  **[Raw Daily Readings](docs/page-7-raw-daily-readings.md)** - Details on the raw sensor data collection.
8.  **[Experiments Model](docs/page-8-experiments.md)** - Details on the experimental configuration schema.
9.  **[Image Crops](docs/page-9-image-crops.md)** - Details on the segmented plant images used for AI.
10. **[NPK Predictions](docs/page-10-npk-predictions.md)** - Details on the numerical AI estimation outputs.
11. **[Image Crop Progress](docs/page-11-image-crop-progress.md)** - Task tracking for image processing.
12. **[Image Processing Logic](docs/page-12-image-processing-logic.md)** - Details on segmentation and greenness filtering.
13. **[Tank Configuration](docs/page-13-tank-configuration.md)** - Dynamic system settings and fertilizer profiles.
14. **[Mobile API Integration](docs/page-14-mobile-api-integration.md)** - How to connect your mobile app to the config API.
15. **[IoT Pi Integration](docs/page-15-iot-pi-integration.md)** - How to upload data from a Raspberry Pi.
16. **[Monitoring Dashboard](docs/page-16-dashboard-api.md)** - The data aggregation API for the farmer's UI.

---

## 🧪 Verification Tools

- **Verify Discovery**: `python scripts/verify-zeroconf.py`
- **Process Images**: `python scripts/image_processor.py`
- **Seed Predictions**: `python scripts/seed_predictions.py`
- **Run SQL Queries**: `./scripts/run-query.sh "SELECT * FROM users;"`
