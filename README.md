# AI SDLC Backend — Car Management

A Python/PostgreSQL backend service for Car Management. Database schema is managed via [Alembic](https://alembic.sqlalchemy.org/) migrations using raw SQL (no ORM).

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Database Configuration](#database-configuration)
- [Setup](#setup)
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
└── tests/
    └── test_migrations.py               # Unit tests for migrations
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

## Setup

```bash
# 1. Clone the repository (if you haven't already)
git clone https://github.com/RavishankarDuMCA10/ai-sdlc-backend.git
cd ai-sdlc-backend

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set the database connection string
export DATABASE_URL="postgresql://myuser:mypassword@localhost:5432/ai_sdlc"
```

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
