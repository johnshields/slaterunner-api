from fastapi import APIRouter, Depends
from .pipeline.projects import router as projects
from .pipeline.assets import router as assets
from .pipeline.shots import router as shots
from .pipeline.tasks import router as tasks
from .pipeline.versions import router as versions
from .pipeline.publishes import router as publishes
from .pipeline.renders import router as renders
from .pipeline.events import router as events
from ..dependencies.auth import require_token

router = APIRouter(dependencies=[Depends(require_token)])

router.include_router(projects, tags=["projects"])
router.include_router(assets, tags=["assets"])
router.include_router(shots, tags=["shots"])
router.include_router(tasks, tags=["tasks"])
router.include_router(versions, tags=["versions"])
router.include_router(publishes, tags=["publishes"])
router.include_router(renders, tags=["renders"])
router.include_router(events, tags=["events"])
