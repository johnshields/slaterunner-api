import hashlib

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from clients.db import db

security = HTTPBearer()


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def require_token(
        credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Dependency to enforce API token authentication against DB.
    Returns a dict with authentication details.
    Raises 401 if token is invalid or missing.
    """
    hashed = hash_token(credentials.credentials)

    result = db.table("api_keys").select("*").eq("token", hashed).limit(1).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    api_key = result.data[0]

    return {
        "user_authenticated": True,
        "role": api_key["role"],
        "is_admin": api_key["is_admin"],
        "has_token": True,
        "expires_at": api_key["expires_at"],
    }


def is_authenticated(request: Request) -> dict:
    """
    Returns dict with user_authenticated flag, role, and username if token is valid.
    Lightweight check from request headers.
    """
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
        hashed = hash_token(token)

        result = db.table("api_keys").select("*").eq("token", hashed).limit(1).execute()
        if result.data:
            api_key = result.data[0]
            return {
                "user_authenticated": True,
                "username": api_key.get("description") or "service",
                "role": api_key["role"],
                "expires_at": api_key["expires_at"],
            }

    return {"user_authenticated": False}
