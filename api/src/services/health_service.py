from datetime import datetime, timezone
from typing import Dict, Any, List
from clients.db import db
from app.config import settings
from app.logging_config import get_logger

logger = get_logger()


class HealthChecker:
    """Comprehensive health check system"""

    def __init__(self):
        self.checks: List[Dict[str, Any]] = []

    def add_check(self, name: str, check_func, critical: bool = True):
        self.checks.append({
            "name": name,
            "function": check_func,
            "critical": critical,
        })

    def run_checks(self) -> Dict[str, Any]:
        results = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "checks": {},
        }

        all_healthy = True

        for check in self.checks:
            try:
                check_result = check["function"]()
                results["checks"][check["name"]] = {
                    "status": "healthy",
                    "details": check_result,
                }
            except Exception as e:
                logger.error("Health check '%s' failed: %s", check["name"], e)
                results["checks"][check["name"]] = {
                    "status": "unhealthy",
                    "error": str(e),
                }

                if check["critical"]:
                    all_healthy = False

        results["status"] = "healthy" if all_healthy else "unhealthy"
        return results


def check_database() -> Dict[str, Any]:
    try:
        db.ping()
        return {"connected": True, "engine": "d1"}
    except Exception as e:
        raise Exception(f"Database check failed: {e}")


def check_disk_space() -> Dict[str, Any]:
    import shutil

    try:
        logs_path = settings.ROOT_DIR / "logs" if hasattr(settings, "ROOT_DIR") else None
        if logs_path and logs_path.exists():
            total, used, free = shutil.disk_usage(logs_path)
            free_gb = free / (1024 ** 3)
            return {
                "free_gb": round(free_gb, 2),
                "sufficient": free_gb > 1.0,
            }
        else:
            return {"status": "logs_directory_not_found"}
    except Exception as e:
        raise Exception(f"Disk space check failed: {e}")


def check_memory() -> Dict[str, Any]:
    try:
        import psutil

        memory = psutil.virtual_memory()
        return {
            "total_gb": round(memory.total / (1024 ** 3), 2),
            "available_gb": round(memory.available / (1024 ** 3), 2),
            "percent_used": memory.percent,
            "sufficient": memory.available > (1024 ** 3),
        }
    except ImportError:
        return {"status": "psutil_not_available"}
    except Exception as e:
        raise Exception(f"Memory check failed: {e}")


def check_configuration() -> Dict[str, Any]:
    try:
        config_status = {
            "database": settings.D1_DATABASE_ID,
            "environment": settings.ENVIRONMENT,
            "debug_mode": settings.DEBUG,
            "log_level": settings.LOG_LEVEL,
        }

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

health_checker.add_check("database", check_database, critical=True)
health_checker.add_check("configuration", check_configuration, critical=True)
health_checker.add_check("disk_space", check_disk_space, critical=False)
health_checker.add_check("memory", check_memory, critical=False)


def get_health_status() -> Dict[str, Any]:
    return health_checker.run_checks()
