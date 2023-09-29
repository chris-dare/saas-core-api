from fastapi import APIRouter

from .endpoints import auth

patient_portal_api_v2_router = APIRouter()
patient_portal_api_v2_router.include_router(
    auth.router, prefix="/auth", tags=["Patient Portal"]
)
