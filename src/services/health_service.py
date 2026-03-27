from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy import text
from db.db import engine
from app.config import settings
from app.logging_config import get_logger

logger = get_logger()


class HealthChecker:
    """Comprehensive health check system"""

    def __init__(self):
        self.checks: List[Dict[str, Any]] = []

    def add_check(self, name: str, check_func, critical: bool = True):
        """Add a health check function"""
        self.checks.append({
            "name": name,
            "function": check_func,
            "critical": critical
        })

    def run_checks(self) -> Dict[str, Any]:
        """Run all health checks and return status"""
        results = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "checks": {}
        }

        all_healthy = True

        for check in self.checks:
            try:
                check_result = check["function"]()
                results["checks"][check["name"]] = {
                    "status": "healthy",
                    "details": check_result
                }
            except Exception as e:
                logger.error("Health check '%s' failed: %s", check["name"], e)
                results["checks"][check["name"]] = {
                    "status": "unhealthy",
                    "error": str(e)
                }

                if check["critical"]:
                    all_healthy = False

        results["status"] = "healthy" if all_healthy else "unhealthy"
        return results


def check_database() -> Dict[str, Any]:
    """Check database connectivity and basic operations"""
    try:
        with engine.connect() as conn:
            # Test basic connectivity
            result = conn.execute(text("SELECT 1")).scalar()

            # Test database version
            version_result = conn.execute(text("SELECT version()")).scalar()

            # Test table existence
            tables_result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)).scalar()

            return {
                "connected": True,
                "version": version_result.split()[0] if version_result else "unknown",
                "tables_count": tables_result
            }
    except Exception as e:
        raise Exception(f"Database check failed: {e}")


def check_disk_space() -> Dict[str, Any]:
    """Check available disk space"""
    import shutil

    try:
        # Check space in logs directory
        logs_path = settings.ROOT_DIR / "logs" if hasattr(settings, 'ROOT_DIR') else None
        if logs_path and logs_path.exists():
            total, used, free = shutil.disk_usage(logs_path)
            free_gb = free / (1024 ** 3)

            return {
                "free_gb": round(free_gb, 2),
                "sufficient": free_gb > 1.0  # At least 1GB free
            }
        else:
            return {"status": "logs_directory_not_found"}
    except Exception as e:
        raise Exception(f"Disk space check failed: {e}")


def check_memory() -> Dict[str, Any]:
    """Check memory usage"""
    try:
        import psutil

        memory = psutil.virtual_memory()
        return {
            "total_gb": round(memory.total / (1024 ** 3), 2),
            "available_gb": round(memory.available / (1024 ** 3), 2),
            "percent_used": memory.percent,
            "sufficient": memory.available > (1024 ** 3)  # At least 1GB available
        }
    except ImportError:
        return {"status": "psutil_not_available"}
    except Exception as e:
        raise Exception(f"Memory check failed: {e}")


def check_configuration() -> Dict[str, Any]:
    """Check configuration validity"""
    try:
        config_status = {
            "database_configured": bool(
                settings.DB_HOST and
                settings.DB_NAME and
                settings.DB_USER and
                settings.DB_PASSWORD
            ),
            "environment": settings.ENVIRONMENT,
            "debug_mode": settings.DEBUG,
            "log_level": settings.LOG_LEVEL
        }

        # Check for production security issues
        if settings.is_production():
            if settings.SECRET_KEY == "your-secret-key-change-in-production":
                config_status["security_warning"] = "Default secret key in production"
            if settings.CORS_ORIGINS == ["*"]:
                config_status["security_warning"] = "CORS allows all origins in production"

        return config_status
    except Exception as e:
        raise Exception(f"Configuration check failed: {e}")


# Create global health checker instance
health_checker = HealthChecker()

# Add default checks
health_checker.add_check("database", check_database, critical=True)
health_checker.add_check("configuration", check_configuration, critical=True)
health_checker.add_check("disk_space", check_disk_space, critical=False)
health_checker.add_check("memory", check_memory, critical=False)


def get_health_status() -> Dict[str, Any]:
    """Get comprehensive health status"""
    return health_checker.run_checks()
