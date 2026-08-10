import json
from datetime import UTC, datetime
from pathlib import Path

import httpx

from app.config import settings
from app.logging_config import get_logger

logger = get_logger()

SCHEMA_PATH = Path(__file__).parent.parent / "db" / "schema.sql"
SEED_PATH = Path(__file__).parent.parent / "db" / "seed.sql"
SEED_API_KEYS_PATH = Path(__file__).parent.parent / "db" / "seed_api_keys.sql"

# Columns stored as JSON text
JSON_COLUMNS = {"metadata", "context", "payload"}

# Columns stored as INTEGER but returned as bool
BOOL_COLUMNS = {"is_admin"}


class D1Backend:
    """Cloudflare D1 executor over the REST API (SQL + params, same contract)."""

    def __init__(self, account_id: str, database_id: str, api_token: str):
        self._url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/d1/database/{database_id}/query"
        self._client = httpx.Client(
            headers={"Authorization": f"Bearer {api_token}"},
            timeout=30,
        )
        logger.info("D1 connected (database %s)", database_id)

    def _post(self, sql: str, params: list | None = None) -> list[dict]:
        payload: dict = {"sql": sql}
        if params:
            payload["params"] = params
        res = self._client.post(self._url, json=payload)
        body = res.json()
        if not body.get("success"):
            raise RuntimeError(f"D1 query failed: {body.get('errors')}")
        return body["result"]

    def rows(self, sql: str, params: list) -> list[dict]:
        result = self._post(sql, params)
        return result[0].get("results", []) if result else []

    def run(self, sql: str, params: list) -> int | None:
        result = self._post(sql, params)
        meta = result[-1].get("meta", {}) if result else {}
        return meta.get("last_row_id")

    def scalar(self, sql: str, params: list):
        rows = self.rows(sql, params)
        if not rows:
            return None
        return next(iter(rows[0].values()), None)

    def script(self, sql_text: str):
        self._post(sql_text)

    def ping(self):
        self._post("SELECT 1")

    def close(self):
        self._client.close()


class QueryResult:
    """Container for query execution results."""

    def __init__(self, data: list[dict], count: int | None = None):
        self.data = data
        self.count = count


class QueryBuilder:
    """Lightweight query builder matching Supabase PostgREST patterns."""

    def __init__(self, backend, table: str):
        self._backend = backend
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
        if self._operation == "select":
            return self._exec_select()
        elif self._operation == "insert":
            return self._exec_insert()
        elif self._operation == "update":
            return self._exec_update()
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
        """Prepare row data for storage: JSON columns and now() replacement."""
        out = {}
        for k, v in data.items():
            if k in JSON_COLUMNS and isinstance(v, (dict, list)):
                out[k] = json.dumps(v)
            elif v == "now()":
                out[k] = datetime.now(UTC).isoformat()
            elif k in BOOL_COLUMNS and isinstance(v, bool):
                out[k] = int(v)
            else:
                out[k] = v
        return out

    def _deserialise(self, row: dict) -> dict:
        """Parse JSON columns and booleans from a stored row."""
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

    def _exec_select(self) -> QueryResult:
        where, params = self._build_where()

        total = None
        if self._count:
            total = self._backend.scalar(f'SELECT COUNT(*) FROM "{self._table}"{where}', params)

        sql = f'SELECT * FROM "{self._table}"{where}'

        if self._order_clauses:
            sql += " ORDER BY " + ", ".join(self._order_clauses)
        if self._limit is not None:
            sql += f" LIMIT {self._limit}"
            if self._offset is not None:
                sql += f" OFFSET {self._offset}"

        rows = [self._deserialise(r) for r in self._backend.rows(sql, params)]
        return QueryResult(rows, count=total)

    def _exec_insert(self) -> QueryResult:
        data = self._serialise(self._insert_data)
        now = datetime.now(UTC).isoformat()
        data.setdefault("created_at", now)
        data.setdefault("updated_at", now)

        cols = list(data.keys())
        col_names = ", ".join(f'"{c}"' for c in cols)
        placeholders = ", ".join(["?"] * len(cols))
        sql = f'INSERT INTO "{self._table}" ({col_names}) VALUES ({placeholders})'
        row_id = self._backend.run(sql, list(data.values()))

        rows = self._backend.rows(f'SELECT * FROM "{self._table}" WHERE id = ?', [row_id])
        return QueryResult([self._deserialise(rows[0])] if rows else [])

    def _exec_update(self) -> QueryResult:
        data = self._serialise(self._update_data)
        data["updated_at"] = datetime.now(UTC).isoformat()

        where, where_params = self._build_where()
        set_clause = ", ".join(f'"{k}" = ?' for k in data)
        params = list(data.values()) + where_params

        self._backend.run(f'UPDATE "{self._table}" SET {set_clause}{where}', params)

        rows = [self._deserialise(r) for r in self._backend.rows(f'SELECT * FROM "{self._table}"{where}', where_params)]
        return QueryResult(rows)


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
        """Create tables if they do not exist."""
        if SCHEMA_PATH.exists():
            self._backend.script(SCHEMA_PATH.read_text())
            logger.info("database schema initialised")

    def seed(self):
        """Insert seed data if database is empty."""
        if self._backend.scalar("SELECT COUNT(*) FROM projects", []) == 0 and SEED_PATH.exists():
            self._backend.script(SEED_PATH.read_text())
            logger.info("seed data inserted")

        if SEED_API_KEYS_PATH.exists():
            self._backend.script(SEED_API_KEYS_PATH.read_text())
            logger.info("API keys seeded")

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
