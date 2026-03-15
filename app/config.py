import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL: str = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/ai_sdlc",
)
