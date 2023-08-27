from fastapi import APIRouter

from .endpoints import auth, patients

django_emr_api_v2_router = APIRouter()
django_emr_api_v2_router.include_router(
    patients.router, prefix="/patients", tags=["Django EMR"]
)
django_emr_api_v2_router.include_router(
    auth.router, prefix="/auth", tags=["Django EMR"]
)
