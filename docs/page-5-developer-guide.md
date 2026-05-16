# Developer Guide: LeafCloud Server V2 Architecture

Welcome to the LeafCloud Server V2 codebase. This project has been structured following **SOLID principles** and **FastAPI best practices** to ensure scalability and maintainability.

## 1. Project Structure Overview

The application logic resides in the `app/` directory, organized by layer:

- **`app/core/`**: The "brain" of the application.
  - `config.py`: Environment variable management using `pydantic-settings`.
  - `database.py`: SQLAlchemy engine, session management, and `get_db` dependency.
  - `security.py`: JWT operations and password hashing logic.
- **`app/models/`**: Database definitions.
  - Each file represents a table or a group of related tables (e.g., `user.py`).
- **`app/schemas/`**: Data Transfer Objects (DTOs).
  - Pydantic models for request validation and response serialization.
- **`app/api/v1/`**: Routing layer.
  - `api.py`: The main router that aggregates all endpoints.
  - `endpoints/`: Individual route handlers (controllers), grouped by functionality (e.g., `auth.py`).
- **`app/services/`**: Business logic and external integrations.
  - Use this for complex logic that doesn't belong in a route handler (e.g., `discovery.py` for Zeroconf).
- **`app/main.py`**: Entry point. Handles app initialization, lifespan events, and global router inclusion.

---

## 2. Common Workflows

### How to add a new Feature (e.g., "Devices")

1.  **Define the Model**: Create `app/models/device.py` and add it to `app/models/__init__.py`.
2.  **Create Migrations**:
    ```bash
    export PYTHONPATH=$PYTHONPATH:.
    alembic revision --autogenerate -m "Add device table"
    alembic upgrade head
    ```
3.  **Define Schemas**: Create `app/schemas/device.py` for input/output validation.
4.  **Create Endpoints**: Create `app/api/v1/endpoints/devices.py`.
5.  **Register Router**: Import and include the new router in `app/api/v1/api.py`.

---

## 3. Best Practices & SOLID Principles

-   **Single Responsibility (SRP)**: Keep your route handlers thin. Move complex logic to `app/services/`.
-   **Dependency Inversion**: Use FastAPI's `Depends()` for database sessions or security checks.
-   **Configuration**: Never hardcode values. Add them to `app/core/config.py` and use the `settings` object.
-   **Type Safety**: Always use Python type hints and Pydantic schemas for API inputs and outputs.

---

## 4. Development Tools

-   **Run Server**: `uvicorn app.main:app --reload`
-   **Verify Zeroconf**: `python scripts/verify-zeroconf.py`
-   **Database Queries**: `./scripts/run-query.sh "SELECT * FROM users;"`
-   **Migrations**: Use `alembic` for all schema changes.

## 5. Environment Setup
Always copy `.env.example` to `.env` and configure your local settings before starting development.
