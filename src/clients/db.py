import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from app.config import settings
from app.logging_config import get_logger

logger = get_logger()

SCHEMA_PATH = Path(__file__).parent.parent / "db" / "schema.sql"
SEED_PATH = Path(__file__).parent.parent / "db" / "seed.sql"
SEED_API_KEYS_PATH = Path(__file__).parent.parent / "db" / "seed_api_keys.sql"

# Columns stored as JSON text in SQLite
JSON_COLUMNS = {"metadata", "context", "payload"}

# Columns stored as INTEGER but returned as bool
BOOL_COLUMNS = {"is_admin"}


class QueryResult:
    """Mimics Supabase execute() result."""

    def __init__(self, data: list[dict], count: int | None = None):
        self.data = data
        self.count = count


class QueryBuilder:
    """Lightweight SQLite query builder matching Supabase PostgREST patterns."""

    def __init__(self, conn: sqlite3.Connection, table: str):
        self._conn = conn
        self._table = table
        self._operation = None
        self._filters: list[tuple[str, list]] = []
        self._order_clauses: list[str] = []
        self._limit: int | None = None
        self._offset: int | None = None
        self._count = False
        self._insert_data: dict | None = None
        self._update_data: dict | None = None

    # Operations

    def select(self, columns: str = "*", *, count: str | None = None) -> "QueryBuilder":
        self._operation = "select"
        if count == "exact":
            self._count = True
        return self

    def insert(self, data: dict) -> "QueryBuilder":
        self._operation = "insert"
        self._insert_data = dict(data)
        return self

    def update(self, data: dict) -> "QueryBuilder":
        self._operation = "update"
        self._update_data = dict(data)
        return self

    # Filters

    def eq(self, column: str, value) -> "QueryBuilder":
        self._filters.append((f'"{column}" = ?', [value]))
        return self

    def is_(self, column: str, value: str) -> "QueryBuilder":
        if value == "null":
            self._filters.append((f'"{column}" IS NULL', []))
        else:
            self._filters.append((f'"{column}" IS NOT NULL', []))
        return self

    def ilike(self, column: str, pattern: str) -> "QueryBuilder":
        self._filters.append((f'"{column}" LIKE ? COLLATE NOCASE', [pattern]))
        return self

    def gte(self, column: str, value) -> "QueryBuilder":
        self._filters.append((f'"{column}" >= ?', [value]))
        return self

    def lte(self, column: str, value) -> "QueryBuilder":
        self._filters.append((f'"{column}" <= ?', [value]))
        return self

    # Modifiers

    def order(self, column: str, *, desc: bool = False) -> "QueryBuilder":
        direction = "DESC" if desc else "ASC"
        self._order_clauses.append(f'"{column}" {direction}')
        return self

    def limit(self, n: int) -> "QueryBuilder":
        self._limit = n
        return self

    def range(self, start: int, end: int) -> "QueryBuilder":
        self._offset = start
        self._limit = end - start + 1
        return self

    # Execution

    def execute(self) -> QueryResult:
        cursor = self._conn.cursor()

        if self._operation == "select":
            return self._exec_select(cursor)
        elif self._operation == "insert":
            return self._exec_insert(cursor)
        elif self._operation == "update":
            return self._exec_update(cursor)
        else:
            raise ValueError("No operation specified on query builder")

    # Internal

    def _build_where(self) -> tuple[str, list]:
        if not self._filters:
            return "", []
        clauses, params = [], []
        for clause, p in self._filters:
            clauses.append(clause)
            params.extend(p)
        return " WHERE " + " AND ".join(clauses), params

    def _serialise(self, data: dict) -> dict:
        """Prepare row data for SQLite: JSON columns and now() replacement."""
        out = {}
        for k, v in data.items():
            if k in JSON_COLUMNS and isinstance(v, (dict, list)):
                out[k] = json.dumps(v)
            elif v == "now()":
                out[k] = datetime.now(timezone.utc).isoformat()
            elif k in BOOL_COLUMNS and isinstance(v, bool):
                out[k] = int(v)
            else:
                out[k] = v
        return out

    def _deserialise(self, row: dict) -> dict:
        """Parse JSON columns and booleans from SQLite row."""
        for col in JSON_COLUMNS:
            if col in row and isinstance(row[col], str):
                try:
                    row[col] = json.loads(row[col])
                except (json.JSONDecodeError, TypeError):
                    pass
        for col in BOOL_COLUMNS:
            if col in row and isinstance(row[col], int):
                row[col] = bool(row[col])
        return row

    def _row_from_cursor(self, cursor) -> dict | None:
        if not cursor.description:
            return None
        columns = [desc[0] for desc in cursor.description]
        raw = cursor.fetchone()
        if raw is None:
            return None
        return self._deserialise(dict(zip(columns, raw)))

    def _rows_from_cursor(self, cursor) -> list[dict]:
        if not cursor.description:
            return []
        columns = [desc[0] for desc in cursor.description]
        return [self._deserialise(dict(zip(columns, r))) for r in cursor.fetchall()]

    def _exec_select(self, cursor) -> QueryResult:
        where, params = self._build_where()

        total = None
        if self._count:
            cursor.execute(f'SELECT COUNT(*) FROM "{self._table}"{where}', params)
            total = cursor.fetchone()[0]

        sql = f'SELECT * FROM "{self._table}"{where}'

        if self._order_clauses:
            sql += " ORDER BY " + ", ".join(self._order_clauses)
        if self._limit is not None:
            sql += f" LIMIT {self._limit}"
            if self._offset:
                sql += f" OFFSET {self._offset}"

        cursor.execute(sql, params)
        return QueryResult(self._rows_from_cursor(cursor), count=total)

    def _exec_insert(self, cursor) -> QueryResult:
        data = self._serialise(self._insert_data)
        now = datetime.now(timezone.utc).isoformat()
        data.setdefault("created_at", now)
        data.setdefault("updated_at", now)

        cols = list(data.keys())
        sql = (
            f'INSERT INTO "{self._table}" ({", ".join(f"{c}" for c in cols)}) '
            f'VALUES ({", ".join(["?"] * len(cols))})'
        )
        cursor.execute(sql, list(data.values()))
        self._conn.commit()

        row_id = cursor.lastrowid
        cursor.execute(f'SELECT * FROM "{self._table}" WHERE id = ?', [row_id])
        row = self._row_from_cursor(cursor)
        return QueryResult([row] if row else [])

    def _exec_update(self, cursor) -> QueryResult:
        data = self._serialise(self._update_data)
        data["updated_at"] = datetime.now(timezone.utc).isoformat()

        where, where_params = self._build_where()
        set_clause = ", ".join(f'"{k}" = ?' for k in data.keys())
        params = list(data.values()) + where_params

        cursor.execute(f'UPDATE "{self._table}" SET {set_clause}{where}', params)
        self._conn.commit()

        cursor.execute(f'SELECT * FROM "{self._table}"{where}', where_params)
        return QueryResult(self._rows_from_cursor(cursor))


class Database:
    """SQLite database client for slaterunner."""

    def __init__(self):
        self._conn: sqlite3.Connection | None = None

    def connect(self, db_path: str | None = None):
        path = db_path or settings.DATABASE_PATH
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        logger.info("SQLite connected to %s", path)

    def init_schema(self):
        """Create tables if they do not exist."""
        if SCHEMA_PATH.exists():
            self._conn.executescript(SCHEMA_PATH.read_text())
            self._conn.commit()
            logger.info("database schema initialised")

    def seed(self):
        """Insert seed data if database is empty."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM projects")
        if cursor.fetchone()[0] == 0 and SEED_PATH.exists():
            self._conn.executescript(SEED_PATH.read_text())
            self._conn.commit()
            logger.info("seed data inserted")

        if SEED_API_KEYS_PATH.exists():
            self._conn.executescript(SEED_API_KEYS_PATH.read_text())
            self._conn.commit()
            logger.info("API keys seeded")

    def table(self, name: str) -> QueryBuilder:
        if not self._conn:
            raise RuntimeError("Database not connected — call db.connect() first")
        return QueryBuilder(self._conn, name)

    def ping(self):
        """Health check."""
        self._conn.execute("SELECT 1")

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None


db = Database()
