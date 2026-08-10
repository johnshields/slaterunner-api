# slaterunner

> RESTful FastAPI for fixing it in post.

slaterunner is a production pipeline API for managing VFX/animation projects, shots, assets, tasks, versions, renders, and publishes, all backed by a serverless Cloudflare D1 database and secured with hashed API keys.

## API

- **/projects**: top-level container for a VFX/animation production. Every shot, asset, task, version, render, and publish is scoped to a project.
- **/shots**: shot-level entries within a project, the unit most tasks and renders are tracked against.
- **/assets**: reusable production assets (models, rigs, textures) tied to a project.
- **/tasks**: work items assigned against shots or assets.
- **/versions**: version history recorded per task.
- **/renders**: render output tracked per version.
- **/publishes**: approved, published deliverables.
- **/events**: activity log across the pipeline.

All routes live under `/api/v1`, token-authenticated via `Authorization: Bearer <token>`. System routes (health, info) live at `/api/system`.

## Database

Cloudflare D1 accessed over its REST API, no ORM:

- `D1Backend` posts raw SQL + params to the D1 query endpoint and returns the parsed result rows
- `QueryBuilder` layers a lightweight, chainable filter/select/insert/update API on top, matching Supabase's PostgREST style
- JSON columns (`metadata`, `context`, `payload`) are serialised to text on write, parsed back on read; `is_admin` round-trips as a bool over D1's INTEGER storage
- Schema is applied from `db/schema.sql` on startup; `db/seed.sql` and `db/seed_api_keys.sql` seed an empty database

## Auth

- API tokens are SHA-256 hashed and matched against the `api_keys` table, never stored or compared in plaintext
- `require_token` enforces a valid `Bearer` token per request, raising 401 on a miss
- Each key carries a `role`, an `is_admin` flag, and an `expires_at`, returned alongside the auth result for downstream checks

## Running the Project

### Stack

- Python 3.13, FastAPI, Pydantic
- Cloudflare D1 (SQLite dialect, serverless)
- Hashed API keys stored in DB
- Ruff, Black, Flake8, Pytest

### 1. Set up the environment

The backend lives in `api/`; the Vite frontend is a sibling in `app/`.

```bash
cd api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure `.env`

```dotenv
LOG_LEVEL=info
ENVIRONMENT=development
CF_ACCOUNT_ID=<cloudflare account id>
D1_DATABASE_ID=<d1 database id>
D1_API_TOKEN=<api token with D1 edit>
API_USERNAME=admin
```

### 3. Start the API

```bash
fastapi dev src/main.py
```

## Licence

[MIT](LICENSE)
