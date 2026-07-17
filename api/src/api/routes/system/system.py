from fastapi import APIRouter, Request, Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.controllers.system.system_controller import status_payload, db_conn
from api.dependencies.auth import require_token
from services.health_service import get_health_status

router = APIRouter(tags=["system"])
bearer = HTTPBearer(auto_error=False)


@router.get("", summary="API status / load balancer check")
def api_root(request: Request):
    """Endpoint for LBs / uptime checks."""
    return status_payload(request.app)


@router.get("/authz", summary="Auth status")
def authz(auth=Depends(require_token)):
    """Check whether the caller is authenticated + role info."""
    return auth


@router.get("/healthz", summary="Liveness")
def healthz(credentials: HTTPAuthorizationCredentials = Security(bearer)):
    """
    Health endpoint.
    - If caller is authenticated -> return full health status
    - If caller is not authenticated -> return minimal liveness
    """
    if not credentials:
        return {"ok": True}

    try:
        auth = require_token(credentials=credentials)
        if auth.get("user_authenticated"):
            return get_health_status()
    except HTTPException:
        return {"ok": True}

    return {"ok": True}


@router.get("/readyz", summary="Readiness", dependencies=[Depends(require_token)])
def readyz():
    """Check DB readiness (only authenticated users)."""
    return db_conn()
