from fastapi import APIRouter

from .endpoints import auth, organizations, users, valuesets, wallets

api_v1_router = APIRouter()
api_v1_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_v1_router.include_router(users.router, prefix="/users", tags=["users"])
api_v1_router.include_router(valuesets.router, prefix="/valuesets", tags=["valuesets"])
api_v1_router.include_router(
    organizations.router, prefix="/organizations", tags=["Corporates"]
)
api_v1_router.include_router(wallets.router, prefix="/wallets", tags=["Wallets"])
