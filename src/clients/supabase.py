from supabase import create_client
from app.config import settings
from app.logging_config import get_logger

logger = get_logger()

supabase = create_client(settings.SUPABASE_PROJECT_URL, settings.SUPABASE_PUBLISHABLE_KEY)
logger.info("Supabase client connected to %s", settings.SUPABASE_PROJECT_URL)
