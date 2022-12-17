from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import paginate
from sqlalchemy.orm import Session

from app import crud, models, models
from app.api import deps
from app.middleware.pagination import JsonApiPage

router = APIRouter()


@router.get("/{organization_id}/members", response_model=JsonApiPage[models.OrganizationMemberRead])
def read_organization_members(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    organization: models.Organization = Depends(deps.get_adminstrative_organization),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve organizations owned or managed by the session user
    Returns all organizations if user is a superuser
    """
    if crud.user.is_superuser(current_user):
        organizations = crud.organization_member.get_multi(db, skip=skip, limit=limit)
    else:
        organizations = crud.organization_member.get_multi_by_owner(
            db=db, user_id=current_user.uuid, skip=skip, limit=limit
        )
    return paginate(organizations)


@router.post("/organizations//{organization_id}/members", response_model=models.OrganizationRead)
def create_organization_member(
    *,
    db: Session = Depends(deps.get_db),
    organization_id: str,
    organization_in: models.OrganizationCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new organization.
    """
    organization = crud.organization_member.create_with_owner(db=db, obj_in=organization_in, user=current_user)
    return organization


@router.put("/organizations//{organization_id}/members/{member_id}", response_model=models.OrganizationRead)
def update_organization_member(
    *,
    db: Session = Depends(deps.get_db),
    member_id: str,
    organization_in: models.OrganizationUpdate,
    organization_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an organization.
    """
    organization = crud.organization_member.get(db=db, uuid=member_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    if not crud.user.is_superuser(current_user) and (organization.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    organization = crud.organization_member.update(db=db, db_obj=organization, obj_in=organization_in)
    return organization


@router.get("/organizations/{organization_id}/members/{member_id}", response_model=models.OrganizationRead)
def read_organization(
    *,
    db: Session = Depends(deps.get_db),
    member_id: int,
    organization_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get organization by ID.
    """
    organization = crud.organization_member.get(db=db, uuid=member_id)
    if not organization:
        raise HTTPException(status_code=404, detail="organization not found")
    if not crud.user.is_superuser(current_user) and (organization.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return organization


@router.delete("/organizations//{organization_id}/members/{member_id}", response_model=models.OrganizationRead)
def delete_organization(
    *,
    db: Session = Depends(deps.get_db),
    member_id: int,
    organization_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Suspends a user's membership from an organization
    """
    organization = crud.organization_member.get(db=db, uuid=member_id)
    if not organization:
        raise HTTPException(status_code=404, detail="organization not found")
    if not crud.user.is_superuser(current_user) and (organization.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    organization = crud.organization_member.remove(db=db, id=id)
    return organization
