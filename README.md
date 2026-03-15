# AI SDLC Backend — Car Management

A Python/PostgreSQL backend service for Car Management. Database schema is managed via [Alembic](https://alembic.sqlalchemy.org/) migrations using raw SQL (no ORM).

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Database Configuration](#database-configuration)
- [Modifying the Database Connection](#modifying-the-database-connection)
- [Starting the Application](#starting-the-application)
- [Running Migrations](#running-migrations)
- [Rolling Back Migrations](#rolling-back-migrations)
- [Running Tests](#running-tests)
- [Database Schema](#database-schema)

---

## Prerequisites

| Tool | Minimum Version |
|------|----------------|
| Python | 3.9+ |
| PostgreSQL | 13+ |
| pip | 23+ |

---

## Project Structure

```
ai-sdlc-backend/
├── alembic.ini                          # Alembic configuration
├── requirements.txt                     # Python dependencies
├── app/
│   ├── __init__.py
│   └── config.py                        # Reads DATABASE_URL from environment
├── migrations/
│   ├── env.py                           # Alembic runtime environment
│   ├── script.py.mako                   # Migration file template
│   └── versions/
│       ├── 0001_create_cars_table.py
│       └── 0002_create_car_service_schedules_table.py
├── scripts/
│   └── migrate.py                       # Python CLI to trigger migrations
└── tests/
    ├── test_migrations.py               # Unit tests for migration SQL
    └── test_migrate_script.py           # Unit tests for migrate.py CLI
```

---

## Database Configuration

The application reads the database connection string from the `DATABASE_URL` environment variable.

**Format:**
```
postgresql://<user>:<password>@<host>:<port>/<database>
```

**Default (used when `DATABASE_URL` is not set):**
```
postgresql://postgres:postgres@localhost:5432/ai_sdlc
```

### Option 1 — Export the environment variable

```bash
export DATABASE_URL="postgresql://myuser:mypassword@localhost:5432/ai_sdlc"
```

### Option 2 — Use a `.env` file

Create a `.env` file in the project root (it is already in `.gitignore`):

```dotenv
DATABASE_URL=postgresql://myuser:mypassword@localhost:5432/ai_sdlc
```

Then source it before running any commands:

```bash
source .env   # or: set -a && source .env && set +a
```

### Creating the PostgreSQL database

```sql
-- Connect to PostgreSQL as a superuser, then run:
CREATE DATABASE ai_sdlc;
CREATE USER myuser WITH PASSWORD 'mypassword';
GRANT ALL PRIVILEGES ON DATABASE ai_sdlc TO myuser;
```

Or with `createdb`:

```bash
createdb -U postgres ai_sdlc
```

---

## Modifying the Database Connection

The database connection is configured in **`app/config.py`**:

```python
import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/ai_sdlc",
)
```

The connection string has the following components:

```
postgresql://<username>:<password>@<host>:<port>/<database>
```

| Component | Default value | Description |
|-----------|--------------|-------------|
| `username` | `postgres` | PostgreSQL user |
| `password` | `postgres` | Password for the user |
| `host` | `localhost` | Database server hostname or IP |
| `port` | `5432` | PostgreSQL port |
| `database` | `ai_sdlc` | Target database name |

### Option A — Change via environment variable (recommended)

Set `DATABASE_URL` before running any command. This overrides the default in `app/config.py` without modifying any source file:

```bash
export DATABASE_URL="postgresql://myuser:mysecretpassword@db.example.com:5432/mydb"
```

To make it permanent for your shell session, add the line to `~/.bashrc` or `~/.zshrc`.

### Option B — Use a `.env` file

Create `.env` in the project root (already listed in `.gitignore`):

```dotenv
DATABASE_URL=postgresql://myuser:mysecretpassword@db.example.com:5432/mydb
```

Load it before running migrations:

```bash
source .env            # Linux / macOS
# or
set -a && source .env && set +a
```

### Option C — Edit the default in `app/config.py`

If you want to hard-code a different default (useful for local dev only — never commit credentials), edit the fallback value in `app/config.py`:

```python
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://myuser:mysecretpassword@localhost:5432/mydb",  # ← change here
)
```

> **Security note:** Options A and B are preferred. Never commit passwords or credentials to source control.

---

## Starting the Application

> **Note:** This project currently consists of the database layer only (schema migrations). There is no HTTP server to start. The steps below get the database ready so the application can be developed on top of it.

Follow these steps in order to get the application running from scratch:

**Step 1 — Clone the repository**

```bash
git clone https://github.com/RavishankarDuMCA10/ai-sdlc-backend.git
cd ai-sdlc-backend
```

**Step 2 — Create and activate a virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

**Step 3 — Install dependencies**

```bash
pip install -r requirements.txt
```

**Step 4 — Configure the database connection**

Set the `DATABASE_URL` environment variable to point to your PostgreSQL instance (see [Modifying the Database Connection](#modifying-the-database-connection) for all options):

```bash
export DATABASE_URL="postgresql://myuser:mypassword@localhost:5432/ai_sdlc"
```

**Step 5 — Create the PostgreSQL database** (first time only)

```bash
createdb -U postgres ai_sdlc
# or via psql:
# CREATE DATABASE ai_sdlc;
```

**Step 6 — Apply all database migrations**

```bash
python scripts/migrate.py
```

`scripts/migrate.py` is the Python entry point for managing the database schema. It wraps Alembic so you do not need the `alembic` CLI on your PATH. After this command succeeds, the `cars` and `car_service_schedules` tables will exist in your database and the application is ready for further development.

**Additional `scripts/migrate.py` commands:**

| Command | Description |
|---------|-------------|
| `python scripts/migrate.py` | Apply all pending migrations (upgrade to `head`) |
| `python scripts/migrate.py --revision 0001` | Apply migrations up to a specific revision |
| `python scripts/migrate.py --downgrade -1` | Revert the most recent migration |
| `python scripts/migrate.py --downgrade base` | Revert all migrations (drops all tables) |
| `python scripts/migrate.py --current` | Show the current migration revision |
| `python scripts/migrate.py --history` | Show the full migration history |

---

## Running Migrations

Apply all pending migrations to bring the database schema up to the latest version:

```bash
alembic upgrade head
```

Apply migrations up to a specific revision:

```bash
alembic upgrade 0001   # apply only the cars table migration
alembic upgrade 0002   # apply up to car_service_schedules table
```

Check the current migration state:

```bash
alembic current
```

View the full migration history:

```bash
alembic history --verbose
```

---

## Rolling Back Migrations

Roll back the most recent migration:

```bash
alembic downgrade -1
```

Roll back to a specific revision:

```bash
alembic downgrade 0001   # revert car_service_schedules, keep cars
```

Roll back all migrations (empty database):

```bash
alembic downgrade base
```

---

## Running Tests

Unit tests validate the SQL emitted by each migration without requiring a live database.

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run only migration tests
pytest tests/test_migrations.py -v
```

---

## Database Schema

### `cars`

Stores the master record for each rental vehicle.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK, NOT NULL | Unique identifier |
| `licence_plate` | VARCHAR(20) | NOT NULL, UNIQUE | Vehicle licence plate |
| `make` | VARCHAR(100) | NOT NULL | Manufacturer |
| `model` | VARCHAR(100) | NOT NULL | Model name |
| `year` | SMALLINT | NOT NULL | Year of manufacture |
| `colour` | VARCHAR(50) | NOT NULL | Exterior colour |
| `fuel_type` | VARCHAR(20) | NOT NULL | `petrol` \| `diesel` \| `electric` \| `hybrid` |
| `seating_capacity` | SMALLINT | NOT NULL | Number of seats |
| `current_location` | VARCHAR(255) | NOT NULL | Location or depot reference |
| `condition_rating` | SMALLINT | NOT NULL | Score 1 (poor) – 10 (excellent) |
| `status` | VARCHAR(30) | NOT NULL | `available` \| `reserved` \| `rented` \| `in_service` \| `unavailable` \| `inactive` |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | In active rental pool |
| `next_service_date` | DATE | | Next scheduled service date |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record creation timestamp (UTC) |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp (UTC) |

**Indexes:** `idx_cars_status`, `idx_cars_is_active`, `idx_cars_next_service_date`

---

### `car_service_schedules`

Stores planned and historical service/maintenance entries per vehicle.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK, NOT NULL | Unique identifier |
| `car_id` | UUID | FK → `cars.id`, NOT NULL | Associated vehicle |
| `service_type` | VARCHAR(100) | NOT NULL | Type of service |
| `scheduled_date` | DATE | NOT NULL | Planned service date |
| `estimated_downtime_hours` | DECIMAL(5,2) | | Estimated hours unavailable |
| `service_provider` | VARCHAR(255) | | Name of workshop/provider |
| `status` | VARCHAR(20) | NOT NULL | `scheduled` \| `in_progress` \| `completed` \| `cancelled` |
| `notes` | TEXT | | Additional notes |
| `completed_at` | TIMESTAMP | | When service was marked complete |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record creation timestamp (UTC) |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp (UTC) |

**Indexes:** `idx_car_service_schedules_car_id`, `idx_car_service_schedules_scheduled_date`, `idx_car_service_schedules_status`

**Foreign key:** `car_id` → `cars(id)` with `ON DELETE CASCADE`
