
from fastapi import APIRouter, Query

import api.controllers.pipeline.publish_controller as controller
import schemas.pipeline.publish as schemas_publish
from schemas.pagination import PaginatedResponse
from schemas.response import ApiResponse

router = APIRouter()


@router.get("/publishes", response_model=PaginatedResponse[schemas_publish.PublishOut])
def get_publishes(
        uid: str | None = None,
        project_uid: str | None = None,
        version_uid: str | None = None,
        type: str | None = None,
        representation: str | None = None,
        path: str | None = None,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
        include_deleted: bool = Query(False, description="Include soft-deleted records"),
):
    """List or search Publishes with optional filters (excludes soft-deleted by default)."""
    return controller.list_publishes(uid, project_uid, version_uid, type, representation, path, limit, offset, include_deleted)


@router.post("/publishes", response_model=ApiResponse[schemas_publish.PublishOut], status_code=201)
def post_publish(data: schemas_publish.PublishCreate):
    """Create a new Publish."""
    return controller.create_publish(data)


@router.patch("/publishes/{uid}", response_model=ApiResponse[schemas_publish.PublishOut])
def patch_publish(uid: str, data: schemas_publish.PublishUpdate):
    """Update a Publish by UID."""
    return controller.update_publish(uid, data)


@router.delete("/publishes/{uid}")
def delete_publish(uid: str):
    """Delete a Publish by UID."""
    return controller.delete_publish(uid)
