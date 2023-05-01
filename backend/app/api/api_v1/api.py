from fastapi import APIRouter

from app.api.api_v1.endpoints import login, users, utils, organizations, organization_members, events, bills, transactions, subaccounts

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
# important to list organization members before organization
# due to how the endpoints are registered by the framework
# Do not change unless you really know what you are doing
# api_router.include_router(organization_members.router, prefix="/organizations", tags=["organization_members"])
# api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(bills.router, prefix="/bills", tags=["bills"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(subaccounts.router, prefix="/subaccounts", tags=["subaccounts"])
