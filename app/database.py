import psycopg2
from psycopg2.extras import RealDictCursor
from app.config import DATABASE_URL


def get_connection():
    """Create and return a new database connection."""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
