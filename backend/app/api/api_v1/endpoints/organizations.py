import datetime
from typing import Any

from app import crud, models
from app.api import deps
from app.core import security
from app.core.config import OAuthScopeType
from app.middleware.pagination import JsonApiPage
from app.session import engine
from fastapi import APIRouter, Body, Depends, HTTPException, Security
from fastapi_pagination import paginate
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session
from sqlmodel import select

router = APIRouter()


@router.get("/", response_model=JsonApiPage[models.OrganizationRead])
async def read_organizations(
    db: Session = Depends(deps.get_async_db),
    offset: int = 0,
    limit: int = 100,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[OAuthScopeType.READ_CURRENT_USER],
    ),
) -> Any:
    """
    Retrieves a list of organizations owned by the user.
    In future versions, this will also include organizations the user can administrate
    """
    organizations = await crud.organization.get_multi(
        db=db, limit=limit, skip=offset, owner_id=current_user.uuid
    )
    return paginate(organizations)


@router.post("/", response_model=models.OrganizationRead)
async def create_organization(
    *,
    db: Session = Depends(deps.get_async_db),
    organization_in: models.OrganizationCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new organization.
    """
    try:
        organization = await crud.organization.create(
            db=db, obj_in=organization_in, current_user=current_user
        )
        return organization
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"{e}")


@router.put("/{id}", response_model=models.OrganizationRead)
async def update_organization(
    *,
    db: Session = Depends(deps.get_async_db),
    id: str,
    organization_in: models.OrganizationUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an organization.
    """
    organization = await crud.organization.get(
        db=db, uuid=id, owner_id=current_user.uuid
    )
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    organization = await crud.organization.update(
        db=db, db_obj=organization, obj_in=organization_in
    )
    return organization


@router.get("/{organization_id}", response_model=models.OrganizationRead)
async def read_organization_by_id(
    organization_id: str,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[OAuthScopeType.READ_CURRENT_USER],
    ),
    db: Session = Depends(deps.get_async_db),
) -> Any:
    """
    Get a specific organization by id
    """
    organization = await crud.organization.get(
        db=db, uuid=organization_id, owner_id=current_user.uuid
    )
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    # extra precaution to confirm that user is not reading an organization
    # they should not have access to
    if not crud.user.is_superuser(current_user) and (
        organization.owner_id != current_user.uuid
    ):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return organization
