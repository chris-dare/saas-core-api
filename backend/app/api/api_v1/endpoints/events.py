from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import paginate
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models
from app.api import deps
from app.middleware.pagination import JsonApiPage

router = APIRouter()


@router.get("/", response_model=JsonApiPage[models.EventRead])
async def read_events(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    skip: int = 0,
    limit: int = 100,
    organization_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieves coures created under a user's organization
    Returns all events if user is a superuser
    """
    if crud.user.is_superuser(current_user):
        events = await crud.event.get_multi(db, skip=skip, limit=limit)
    else:
        events = await crud.event.get_multi_by_owner(
            db=db, user_id=current_user.uuid, skip=skip, limit=limit,
            organization_id=organization_id,
        )
    return paginate(events)


@router.post("/", response_model=models.EventRead)
async def create_event(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    event_in: models.EventCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new event.
    """
    event = await crud.event.create_with_owner(db=db, obj_in=event_in, user=current_user)
    return event


@router.put("/{event_id}", response_model=models.EventRead)
async def update_event(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    event_id: str,
    event_in: models.EventUpdate,
    organization: models.Organization = Depends(deps.get_organization),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a event.
    """
    event = await crud.event.get(db=db, uuid=event_id, user_id=current_user.uuid, organization_id=organization.uuid)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if not crud.user.is_superuser(current_user) and (event.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    event = await crud.event.update(db=db, db_obj=event, obj_in=event_in)
    return event


@router.get("/{event_id}", response_model=models.EventRead)
async def read_event(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    event_id: int,
    organization_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get event by ID.
    """
    event = await crud.event.get(db=db, uuid=event_id, user_id=current_user.uuid, organization_id=organization_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if not crud.user.is_superuser(current_user) and (event.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return event


@router.delete("/{event_id}", response_model=models.EventRead)
async def delete_event(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    event_id: int,
    organization_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Removes an event from the commercial space (soft delete)
    """
    event = await crud.event.get(db=db, uuid=event_id, user_id=current_user.uuid, organization_id=organization_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if not crud.user.is_superuser(current_user) and (event.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    event = await crud.event.remove(db=db, obj=event)
    return event
