# slate_runner
RESTful FastAPI for fixing it in post.

## Run 
```bash
# create a virtual environment
python3 -m venv .venv

# activate the venv
source .venv/bin/activate

# install dependencies
pip install -r requirements.txt

# start the app
fastapi dev src/main.py
```

## .env Example
```dotenv
# server
LOG_LEVEL=info

# auth
API_USERNAME=admin
ADMIN_API_TOKEN=secure_token

# supabase 
SUPABASE_PROJECT_URL=https://slaterunner.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_xxx
```

## SQL Schemas
`src/db/schemas/`

---
