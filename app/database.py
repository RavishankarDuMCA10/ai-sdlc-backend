from contextlib import contextmanager
from typing import Generator

import psycopg2
import psycopg2.extras

from app.config import DATABASE_URL


def get_connection() -> psycopg2.extensions.connection:
    """Create and return a new PostgreSQL database connection."""
    conn = psycopg2.connect(DATABASE_URL)
    psycopg2.extras.register_uuid(conn)
    return conn


@contextmanager
def get_db() -> Generator[psycopg2.extensions.cursor, None, None]:
    """Context manager that yields a database cursor and handles commit/rollback."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
