# slate_runner
RESTful FastAPI for fixing it in post.

## Run 
```bash
# 1. Create a virtual environment
python3 -m venv .venv

# 2. Activate the venv
source .venv/bin/activate

# 43 Install dependencies
pip install -r requirements.txt

# 4. Start the app
fastapi dev src/main.py
```

## .env Example
```dotenv
# server
LOG_LEVEL=info

# auth
API_USERNAME=admin
API_TOKEN=secure_token
SECRET_KEY=secure_secret_key

# supabase 
DB_HOST=aws-0-us-east-1.pooler.supabase.com  
DB_NAME=postgres
DB_USER=postgres.project-ref
DB_PASSWORD=hash
```

## SQL Schema
`sql/001_schema.sql`

---
