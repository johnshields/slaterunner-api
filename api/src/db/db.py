from pathlib import Path

from app.config import settings
from app.logging_config import get_logger

from .backend import D1Backend
from .query import QueryBuilder

logger = get_logger()

SCHEMA_DIR = Path(__file__).parent / "schemas"
SEED_PATH = SCHEMA_DIR / "099_seed.sql"

SEED_CHECK_TABLE = "projects"


class Database:
    """Cloudflare D1 database client for slaterunner."""

    def __init__(self):
        self._backend = None

    def connect(self):
        if not settings.d1_enabled:
            raise RuntimeError(
                "D1 credentials missing — set CF_ACCOUNT_ID, D1_DATABASE_ID and D1_API_TOKEN"
            )
        self._backend = D1Backend(settings.CF_ACCOUNT_ID, settings.D1_DATABASE_ID, settings.D1_API_TOKEN)

    def init_schema(self):
        """Create tables if they do not exist, running each schema file in numeric order."""
        schema_files = sorted(
            (f for f in SCHEMA_DIR.rglob("*.sql") if f != SEED_PATH),
            key=lambda f: f.name,
        )
        for schema_file in schema_files:
            self._backend.script(schema_file.read_text())
        if schema_files:
            logger.info("database schema initialised")

    def seed(self):
        """Insert seed data if database is empty."""
        if self._backend.scalar(f"SELECT COUNT(*) FROM {SEED_CHECK_TABLE}", []) == 0 and SEED_PATH.exists():
            self._backend.script(SEED_PATH.read_text())
            logger.info("seed data inserted")

    def table(self, name: str) -> QueryBuilder:
        if not self._backend:
            raise RuntimeError("Database not connected — call db.connect() first")
        return QueryBuilder(self._backend, name)

    def ping(self):
        """Health check."""
        self._backend.ping()

    def close(self):
        if self._backend:
            self._backend.close()
            self._backend = None


db = Database()
