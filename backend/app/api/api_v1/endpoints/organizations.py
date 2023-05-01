from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import paginate
from sqlalchemy.orm import Session

from app import crud, models, models
from app.api import deps
from app.middleware.pagination import JsonApiPage

router = APIRouter()


@router.get("/", response_model=JsonApiPage[models.OrganizationRead])
async def read_organizations(
    db: Session = Depends(deps.get_async_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve organizations owned by the session user
    """
    try:
        if crud.user.is_superuser(current_user):
            organizations = await crud.organization.get_multi(db, skip=skip, limit=limit)
        else:
            organizations = await crud.organization.get_multi_by_owner(
                db=db, user_id=current_user.uuid, skip=skip, limit=limit
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
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
    organization = await crud.organization.create_with_owner(db=db, obj_in=organization_in, user=current_user)
    return organization


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
    organization = await crud.organization.get(db=db, uuid=id, owner_id=current_user.uuid)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    organization = await crud.organization.update(db=db, db_obj=organization, obj_in=organization_in)
    return organization


@router.get("/{organization_id}", response_model=models.OrganizationRead)
async def read_organization(
    *,
    db: Session = Depends(deps.get_async_db),
    organization_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get organization by public ID.
    """
    organization = await crud.organization.get(db=db, uuid=organization_id, owner_id=current_user.uuid)
    if not organization:
        raise HTTPException(status_code=404, detail="organization not found")
    if not crud.user.is_superuser(current_user) and (organization.owner_id != current_user.uuid):
        raise HTTPException(status_code=400, detail="Not enough permissions to view this organization")
    return organization

