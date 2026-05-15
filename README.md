# slaterunner

> RESTful FastAPI for fixing it in post.

slaterunner is a production pipeline API for managing VFX/animation projects, shots, assets, tasks, versions, renders, and publishes.

## Stack

- **API** - Python 3.13, FastAPI, Pydantic
- **Database** - Supabase (Postgres + RLS)
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

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
fastapi dev src/main.py
```

## .env

```dotenv
LOG_LEVEL=info
ENVIRONMENT=development
API_USERNAME=admin
SUPABASE_PROJECT_URL=https://xxx.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_xxx
```

## Licence

MIT
