# Development Guide

This document describes the coding guidelines, tooling, and workflow conventions for the **ai-sdlc-backend** project.

---

## Table of Contents

1. [Tech Stack](#tech-stack)
2. [Prerequisites](#prerequisites)
3. [Local Setup](#local-setup)
4. [Environment Variables](#environment-variables)
5. [Running the Application](#running-the-application)
6. [Database Design](#database-design)
7. [Database Migrations](#database-migrations)
8. [Running Tests](#running-tests)
9. [Unit Testing](#unit-testing)
10. [Code Standards](#code-standards)
11. [Migration Conventions](#migration-conventions)
12. [Testing Conventions](#testing-conventions)
13. [Git & Commit Conventions](#git--commit-conventions)
14. [Folder Structure](#folder-structure)
15. [Code Examples](#code-examples)

---

## Tech Stack

| Concern | Technology |
|---|---|
| Language | Python ≥ 3.12 |
| Database | PostgreSQL |
| DB Driver | psycopg2-binary |
| Schema migrations | Alembic |
| API protocol | REST |
| Test framework | pytest + pytest-mock |
| Package manager | [uv](https://github.com/astral-sh/uv) |

> **No ORM.** All SQL is written by hand using raw `psycopg2` cursors or Alembic's `op.execute()`. SQLAlchemy is used only as Alembic's engine layer — do not use its ORM or query-builder features in application code.

---

## Prerequisites

- Python 3.12+
- PostgreSQL 14+ running locally (or via Docker)
- `uv` package manager — install with:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Local Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd ai-sdlc-backend

# 2. Install all dependencies (including dev extras)
uv sync --extra dev

# 3. Create the local database
psql -U postgres -c "CREATE DATABASE ai_sdlc;"

# 4. Set the database connection string
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/ai_sdlc"

# 5. Apply all migrations
uv run python scripts/migrate.py
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/ai_sdlc` | PostgreSQL connection string |

The default value is used when the variable is not set. **Never hard-code credentials in source files** — always read from the environment via `app/config.py`.

---

## Running the Application

_API server setup instructions will be added when the first service layer is introduced._

---

## Database Design

The database uses **PostgreSQL** with all schema managed through Alembic migrations. There is no ORM — all table definitions live in migration files as raw DDL.

### Naming Conventions

| Object | Convention | Example |
|---|---|---|
| Tables | `snake_case`, plural | `cars`, `car_service_schedules` |
| Columns | `snake_case` | `licence_plate`, `created_at` |
| Primary key | `{table}_pkey` | `cars_pkey` |
| Foreign key | `{table}_{col}_fkey` | `car_service_schedules_car_id_fkey` |
| Unique constraint | `{table}_{col}_unique` | `cars_licence_plate_unique` |
| Check constraint | `{table}_{col}_check` | `cars_fuel_type_check` |
| Index | `idx_{table}_{col}` | `idx_cars_status` |

### Standard columns

Every table must include the following audit columns:

| Column | Type | Default | Purpose |
|---|---|---|---|
| `id` | `UUID` | `gen_random_uuid()` | Surrogate primary key |
| `created_at` | `TIMESTAMP` | `NOW()` | Record creation timestamp |
| `updated_at` | `TIMESTAMP` | `NOW()` | Last modification timestamp |

### Entity Relationship

```
cars
├── id                  UUID PK
├── licence_plate       VARCHAR(20) UNIQUE
├── make                VARCHAR(100)
├── model               VARCHAR(100)
├── year                SMALLINT
├── colour              VARCHAR(50)
├── fuel_type           VARCHAR(20)  CHECK (petrol | diesel | electric | hybrid)
├── seating_capacity    SMALLINT
├── current_location    VARCHAR(255)
├── condition_rating    SMALLINT     CHECK (1–10)
├── status              VARCHAR(30)  CHECK (available | reserved | rented | in_service | unavailable | inactive)
├── is_active           BOOLEAN      DEFAULT true
├── next_service_date   DATE
├── created_at          TIMESTAMP
└── updated_at          TIMESTAMP

car_service_schedules
├── id                       UUID PK
├── car_id                   UUID FK → cars.id  ON DELETE CASCADE
├── service_type             VARCHAR(100)
├── scheduled_date           DATE
├── estimated_downtime_hours DECIMAL(5,2)
├── service_provider         VARCHAR(255)
├── status                   VARCHAR(20)  CHECK (scheduled | in_progress | completed | cancelled)
├── notes                    TEXT
├── completed_at             TIMESTAMP
├── created_at               TIMESTAMP
└── updated_at               TIMESTAMP
```

### Indexes

| Table | Index name | Columns | Rationale |
|---|---|---|---|
| `cars` | `idx_cars_status` | `status` | Filter by availability |
| `cars` | `idx_cars_is_active` | `is_active` | Exclude soft-deleted rows |
| `cars` | `idx_cars_next_service_date` | `next_service_date` | Service due-date queries |
| `car_service_schedules` | `idx_car_service_schedules_car_id` | `car_id` | Join to parent |
| `car_service_schedules` | `idx_car_service_schedules_scheduled_date` | `scheduled_date` | Date range queries |
| `car_service_schedules` | `idx_car_service_schedules_status` | `status` | Filter by status |

---

Migrations are managed with **Alembic** and wrapped by `scripts/migrate.py`.

### Common commands

```bash
# Apply all pending migrations (upgrade to head)
uv run python scripts/migrate.py

# Upgrade to a specific revision
uv run python scripts/migrate.py --revision 0002

# Revert the most recent migration
uv run python scripts/migrate.py --downgrade -1

# Revert all migrations
uv run python scripts/migrate.py --downgrade base

# Show current revision
uv run python scripts/migrate.py --current

# Show full migration history
uv run python scripts/migrate.py --history
```

### Creating a new migration

```bash
uv run alembic revision -m "create_<table_name>_table"
```

Then rename the generated file to follow the naming convention below and fill in `upgrade()` / `downgrade()`.

---

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run a specific test file
uv run pytest tests/test_migrations.py

# Run a specific test class or function
uv run pytest tests/test_migrate_script.py::TestUpgrade::test_upgrade_head
```

All tests must pass before opening a pull request.

---

## Unit Testing

Unit tests verify individual functions and modules in isolation — no live database or network is required.

### Guiding principles

- **Isolation** — mock every external dependency (database, filesystem, environment variables). Tests must run without a running PostgreSQL instance.
- **One assertion per test** — each test method validates a single logical outcome.
- **Descriptive names** — `test_upgrade_creates_table` is better than `test_upgrade`.
- **Independence** — no test must depend on another test's side effects. `setUp`/`teardown` via `pytest` fixtures keeps state clean.
- **Full branch coverage** — exercise every `if`/`else` path and every exception path.

### Test structure

Group related tests in a `pytest` class. Each class covers one unit (a function, method, or migration):

```
tests/
├── test_migrate_script.py       # scripts/migrate.py
│   ├── class TestAlembicConfig
│   ├── class TestUpgrade
│   ├── class TestDowngrade
│   ├── class TestCurrent
│   ├── class TestHistory
│   └── class TestMain
└── test_migrations.py           # migrations/versions/*.py
    ├── class TestCarsMigration
    └── class TestCarServiceSchedulesMigration
```

### Mocking strategy

| What to mock | How |
|---|---|
| `alembic.command` calls | `unittest.mock.patch("scripts.migrate.command")` |
| `_alembic_config()` return value | `patch("scripts.migrate._alembic_config")` |
| `op.execute()` in migration files | `patch.object(mod, "op", MagicMock())` |
| `sys.argv` for CLI tests | `patch.object(sys, "argv", ["migrate.py", ...])` |

### Coverage

```bash
# Install coverage tool
uv add --dev pytest-cov

# Run tests with coverage report
uv run pytest --cov=app --cov=scripts --cov=migrations --cov-report=term-missing
```

Aim for **≥ 90 % coverage** on all application code.

---

### General

- Follow [PEP 8](https://peps.python.org/pep-0008/) for formatting and naming.
- Maximum line length: **88 characters** (compatible with `black`).
- Use **type hints** for all function signatures.
- Prefer explicit over implicit — avoid magic numbers and unexplained literals.
- Keep functions small and focused on a single responsibility.
- Do not add comments that merely restate the code; comment only non-obvious logic.

### Python

- Use `snake_case` for variables, functions, and module names.
- Use `PascalCase` for class names.
- Use `SCREAMING_SNAKE_CASE` for module-level constants.
- Prefer `f-strings` over `.format()` or `%`-formatting.
- Do not suppress exceptions silently; log or re-raise with context.
- Do not use bare `except:` — always catch specific exception types.

### Database access

- Write raw SQL using `psycopg2` cursors. Do not use SQLAlchemy ORM models or query builders in application code.
- Use **parameterised queries** at all times to prevent SQL injection:

  ```python
  # Correct
  cursor.execute("SELECT * FROM cars WHERE id = %s", (car_id,))

  # Wrong — never do this
  cursor.execute(f"SELECT * FROM cars WHERE id = '{car_id}'")
  ```

- Always close cursors and connections, preferably using context managers (`with` blocks).
- Column and table names in SQL must use `snake_case`.

### REST API

- Use standard HTTP methods: `GET` (read), `POST` (create), `PUT`/`PATCH` (update), `DELETE` (remove).
- Return appropriate HTTP status codes (`200`, `201`, `400`, `404`, `422`, `500`, etc.).
- Request and response bodies must use **JSON**.
- Resource names in URLs must be **plural nouns** in `kebab-case` (e.g., `/cars`, `/car-service-schedules`).
- Validate all input at the API boundary before passing data to lower layers.

### Configuration

- All configuration values (DB URL, secrets, feature flags) must come from environment variables via `app/config.py`.
- Do not hard-code environment-specific values anywhere else in the codebase.

---

## Migration Conventions

- **One table per migration file** — each file creates or modifies exactly one table, together with its indexes and constraints.
- File naming pattern: `{sequence}_{description}.py`
  - Sequence is a zero-padded 4-digit integer: `0001`, `0002`, …
  - Description uses `snake_case`: `0003_create_bookings_table.py`
- Every migration **must** implement both `upgrade()` and `downgrade()`.
- Use `IF NOT EXISTS` / `IF EXISTS` guards in DDL statements to make migrations idempotent.
- `down_revision` must point to the immediately preceding revision.
- Do not modify a migration that has already been applied to any shared environment — create a new migration instead.

### Migration file template

```python
"""<description>

Revision ID: <revision>
Revises: <down_revision>
Create Date: <date>
"""
from typing import Sequence, Union
from alembic import op

revision: str = "<revision>"
down_revision: Union[str, None] = "<previous>"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS <table_name> (
            id UUID NOT NULL DEFAULT gen_random_uuid(),
            ...
            CONSTRAINT <table_name>_pkey PRIMARY KEY (id)
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS <table_name>")
```

---

## Testing Conventions

- Every module and public function must have corresponding unit tests.
- Tests live under `tests/` and mirror the module they cover:
  - `scripts/migrate.py` → `tests/test_migrate_script.py`
  - `migrations/versions/0001_*.py` → `tests/test_migrations.py`
- Use `pytest` classes to group related tests (`class TestUpgrade`, `class TestDowngrade`, etc.).
- Use `unittest.mock.patch` and `pytest-mock` to isolate units from external dependencies (database, filesystem, etc.).
- Test file and class naming:
  - Files: `test_<subject>.py`
  - Classes: `Test<Subject>` or `Test<Subject><Action>`
  - Methods: `test_<scenario>`
- Each test must assert one logical outcome — avoid combining unrelated assertions in a single test.
- Do not rely on test execution order; each test must be independently runnable.
- Aim for full branch coverage of any logic you write.

---

## Git & Commit Conventions

This project follows the [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Commit message format

```
<type>(<scope>): <short description>

[optional body]

[optional footer(s)]
```

### Allowed types

| Type | When to use |
|---|---|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `test` | Adding or updating tests |
| `docs` | Documentation only changes |
| `chore` | Build process, dependency updates, tooling |
| `perf` | Performance improvements |
| `ci` | CI/CD configuration changes |

### Examples

```
feat(cars): add GET /cars endpoint with pagination
fix(migrations): correct foreign key constraint on car_service_schedules
test(migrate_script): add tests for --history flag
docs: add DEVELOPMENT.md coding guidelines
chore(deps): upgrade alembic to 1.14.0
```

### Pull request titles

Pull request titles must also follow the Conventional Commits format, as they are used to generate the changelog.

### Branching

- Branch names should be descriptive and use `kebab-case`.
- Recommended prefixes: `feat/`, `fix/`, `chore/`, `docs/`.
- Example: `feat/get-cars-endpoint`, `fix/migration-downgrade-order`

---

## Folder Structure

```
ai-sdlc-backend/
│
├── app/                            # Application source code
│   ├── __init__.py
│   ├── config.py                   # Environment-based configuration (DATABASE_URL, etc.)
│   ├── db/                         # (planned) Database connection and helpers
│   │   ├── __init__.py
│   │   └── connection.py           # psycopg2 connection factory
│   ├── repositories/               # (planned) Raw SQL data-access layer, one file per entity
│   │   ├── __init__.py
│   │   └── car_repository.py
│   ├── services/                   # (planned) Business logic, one file per domain
│   │   ├── __init__.py
│   │   └── car_service.py
│   └── routes/                     # (planned) REST route handlers, one file per resource
│       ├── __init__.py
│       └── car_routes.py
│
├── migrations/                     # Alembic migration management
│   ├── env.py                      # Alembic runtime environment (DB URL injection)
│   ├── script.py.mako              # Template for auto-generated revision files
│   └── versions/                   # One migration file per table
│       ├── 0001_create_cars_table.py
│       └── 0002_create_car_service_schedules_table.py
│
├── scripts/
│   └── migrate.py                  # CLI wrapper around Alembic commands
│
├── tests/                          # Unit tests — mirrors the source structure
│   ├── __init__.py
│   ├── test_migrate_script.py      # Tests for scripts/migrate.py
│   └── test_migrations.py          # Tests for migrations/versions/*.py
│
├── alembic.ini                     # Alembic configuration (logging, script location)
├── pyproject.toml                  # Project metadata and dependency declarations
├── requirements.txt                # Pinned dependency list
├── DEVELOPMENT.md                  # This file
└── README.md                       # Project overview
```

### Layer responsibilities

| Layer | Location | Responsibility |
|---|---|---|
| Config | `app/config.py` | Read environment variables; expose typed constants |
| DB | `app/db/connection.py` | Open/close psycopg2 connections and cursors |
| Repository | `app/repositories/` | Execute raw SQL; return plain dicts or dataclasses |
| Service | `app/services/` | Business rules; orchestrate repository calls |
| Routes | `app/routes/` | Parse HTTP requests; call services; return JSON responses |
| Migrations | `migrations/versions/` | DDL-only: create/drop tables, indexes, constraints |
| Scripts | `scripts/` | CLI utilities (migration runner, seed scripts, etc.) |
| Tests | `tests/` | Unit tests; one test file mirrors each source file |

### Rules

- Application code lives under `app/`; never import from `migrations/` or `scripts/` in application code.
- Each layer may only import from the layer directly beneath it (routes → services → repositories → db).
- `app/config.py` may be imported by any layer.
- New entities follow the same four-file pattern: migration → repository → service → routes.

---

## Code Examples

### Reading configuration

```python
# app/config.py
import os

DATABASE_URL: str = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/ai_sdlc",
)
```

### Database connection helper (planned)

```python
# app/db/connection.py
from contextlib import contextmanager
from typing import Generator

import psycopg2
import psycopg2.extras

from app.config import DATABASE_URL


@contextmanager
def get_connection() -> Generator:
    """Yield a psycopg2 connection; auto-commit and close on exit."""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@contextmanager
def get_cursor(conn) -> Generator:
    """Yield a RealDictCursor that closes automatically."""
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        yield cursor
    finally:
        cursor.close()
```

### Repository — parameterised query (planned)

```python
# app/repositories/car_repository.py
from typing import Optional
from uuid import UUID

from app.db.connection import get_connection, get_cursor


def get_car_by_id(car_id: UUID) -> Optional[dict]:
    with get_connection() as conn:
        with get_cursor(conn) as cursor:
            cursor.execute(
                "SELECT * FROM cars WHERE id = %s AND is_active = TRUE",
                (str(car_id),),
            )
            return cursor.fetchone()


def list_cars(status: Optional[str] = None) -> list[dict]:
    query = "SELECT * FROM cars WHERE is_active = TRUE"
    params: list = []

    if status:
        query += " AND status = %s"
        params.append(status)

    query += " ORDER BY created_at DESC"

    with get_connection() as conn:
        with get_cursor(conn) as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
```

### Migration — full example

```python
"""create bookings table

Revision ID: 0003
Revises: 0002
Create Date: 2026-03-15
"""
from typing import Sequence, Union
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS bookings (
            id          UUID         NOT NULL DEFAULT gen_random_uuid(),
            car_id      UUID         NOT NULL,
            customer_id UUID         NOT NULL,
            start_date  DATE         NOT NULL,
            end_date    DATE         NOT NULL,
            status      VARCHAR(20)  NOT NULL,
            created_at  TIMESTAMP    NOT NULL DEFAULT NOW(),
            updated_at  TIMESTAMP    NOT NULL DEFAULT NOW(),
            CONSTRAINT bookings_pkey PRIMARY KEY (id),
            CONSTRAINT bookings_car_id_fkey
                FOREIGN KEY (car_id) REFERENCES cars (id) ON DELETE RESTRICT,
            CONSTRAINT bookings_status_check CHECK (
                status IN ('pending', 'confirmed', 'active', 'completed', 'cancelled')
            ),
            CONSTRAINT bookings_date_order_check CHECK (end_date > start_date)
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_bookings_car_id ON bookings (car_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings (status)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS bookings")
```

### Unit test — migration (pattern)

```python
# tests/test_migrations.py
import importlib.util
import os
from unittest.mock import MagicMock, patch

_BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "migrations", "versions")


def _load_migration(filename: str):
    path = os.path.join(_BASE_DIR, filename)
    spec = importlib.util.spec_from_file_location("_migration", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestBookingsMigration:
    FILENAME = "0003_create_bookings_table.py"

    def test_revision_metadata(self):
        mod = _load_migration(self.FILENAME)
        assert mod.revision == "0003"
        assert mod.down_revision == "0002"

    def test_upgrade_creates_table(self):
        mod = _load_migration(self.FILENAME)
        mock_op = MagicMock()
        with patch.object(mod, "op", mock_op):
            mod.upgrade()
        sql = mock_op.execute.call_args_list[0].args[0].lower()
        assert "create table" in sql
        assert "bookings" in sql

    def test_downgrade_drops_table(self):
        mod = _load_migration(self.FILENAME)
        mock_op = MagicMock()
        with patch.object(mod, "op", mock_op):
            mod.downgrade()
        sql = mock_op.execute.call_args_list[0].args[0].lower()
        assert "drop table" in sql
        assert "bookings" in sql
```

### Unit test — service function (pattern)

```python
# tests/test_car_service.py
from unittest.mock import patch

from app.services.car_service import get_car


class TestGetCar:
    def test_returns_car_when_found(self):
        fake_car = {"id": "abc", "make": "Toyota", "status": "available"}
        with patch("app.services.car_service.get_car_by_id", return_value=fake_car):
            result = get_car("abc")
        assert result == fake_car

    def test_raises_not_found_when_missing(self):
        with patch("app.services.car_service.get_car_by_id", return_value=None):
            try:
                get_car("unknown-id")
                assert False, "Expected exception not raised"
            except ValueError as exc:
                assert "not found" in str(exc).lower()
```

