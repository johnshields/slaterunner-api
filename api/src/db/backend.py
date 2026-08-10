import httpx

from app.logging_config import get_logger

logger = get_logger()

CF_API_BASE = "https://api.cloudflare.com/client/v4"
REQUEST_TIMEOUT_SECONDS = 30
PING_QUERY = "SELECT 1"


class D1Backend:
    """Cloudflare D1 executor over the REST API (SQL + params, same contract)."""

    def __init__(self, account_id: str, database_id: str, api_token: str):
        self._url = f"{CF_API_BASE}/accounts/{account_id}/d1/database/{database_id}/query"
        self._client = httpx.Client(
            headers={"Authorization": f"Bearer {api_token}"},
            timeout=REQUEST_TIMEOUT_SECONDS,
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
        self._post(PING_QUERY)

    def close(self):
        self._client.close()
