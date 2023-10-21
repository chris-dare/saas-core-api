from fastapi import APIRouter

from .endpoints import auth, users

api_v1_router = APIRouter()
api_v1_router.include_router(
    auth.router, prefix="/auth", tags=["Auth"]
)
api_v1_router.include_router(users.router, prefix="/users", tags=["users"])
