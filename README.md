# slaterunner

> RESTful FastAPI for fixing it in post.

slaterunner is a production pipeline API for managing VFX/animation projects, shots, assets, tasks, versions, renders, and publishes.

## Stack

- **API** - Python 3.13, FastAPI, Pydantic
- **Database** - Cloudflare D1 (SQLite dialect, serverless)
- **Auth** - Hashed API keys stored in DB
- **Tooling** - Ruff, Black, Flake8, Pytest

## API

All routes under `/api/v1`, token-authenticated via `Authorization: Bearer <token>`.

| Resource   | Endpoint              |
|------------|-----------------------|
| Projects   | `/projects`           |
| Shots      | `/shots`              |
| Assets     | `/assets`             |
| Tasks      | `/tasks`              |
| Versions   | `/versions`           |
| Renders    | `/renders`            |
| Publishes  | `/publishes`          |
| Events     | `/events`             |

System routes (health, info) live at `/api/system`.

## Run

The backend lives in `api/`; the Vite frontend is a sibling in `app/`.

```bash
cd api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
fastapi dev src/main.py
```

## .env

```dotenv
LOG_LEVEL=info
ENVIRONMENT=development
CF_ACCOUNT_ID=<cloudflare account id>
D1_DATABASE_ID=<d1 database id>
D1_API_TOKEN=<api token with D1 edit>
API_USERNAME=admin
```

## Licence

MIT. See [LICENSE](LICENSE).
