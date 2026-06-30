import uvicorn
from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        reload=True,
        log_level=settings.LOG_LEVEL.lower(),
        app_dir="src",
    )
