from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import paginate
from sqlalchemy.orm import Session

from app import crud, models
from app.api import deps
from app.middleware.pagination import JsonApiPage

router = APIRouter()


@router.get("/", response_model=JsonApiPage[models.EventRead])
def read_events(
    *,
    db: Session = Depends(deps.get_db),
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
        events = crud.event.get_multi(db, skip=skip, limit=limit)
    else:
        events = crud.event.get_multi_by_owner(
            db=db, user_id=current_user.uuid, skip=skip, limit=limit,
            organization_id=organization_id,
        )
    return paginate(events)


@router.post("/", response_model=models.EventRead)
def create_event(
    *,
    db: Session = Depends(deps.get_db),
    event_in: models.EventCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new event.
    """
    organization = deps.get_organization(organization_id=event_in.organization_id, db=db)
    event = crud.event.create_with_owner(db=db, obj_in=event_in, user=current_user, organization=organization)
    return event


@router.put("/{event_id}", response_model=models.EventRead)
def update_event(
    *,
    db: Session = Depends(deps.get_db),
    event_id: str,
    event_in: models.EventUpdate,
    organization: models.Organization = Depends(deps.get_organization),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a event.
    """
    event = crud.event.get(db=db, uuid=event_id, user_id=current_user.uuid, organization_id=organization.uuid)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if not crud.user.is_superuser(current_user) and (event.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    event = crud.event.update(db=db, db_obj=event, obj_in=event_in)
    return event


@router.get("/{event_id}", response_model=models.EventRead)
def read_event(
    *,
    db: Session = Depends(deps.get_db),
    event_id: int,
    organization_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get event by ID.
    """
    event = crud.event.get(db=db, uuid=event_id, user_id=current_user.uuid, organization_id=organization_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if not crud.user.is_superuser(current_user) and (event.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return event


@router.delete("/{event_id}", response_model=models.EventRead)
def delete_event(
    *,
    db: Session = Depends(deps.get_db),
    event_id: int,
    organization_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Removes an event from the commercial space (soft delete)
    """
    event = crud.event.get(db=db, uuid=event_id, user_id=current_user.uuid, organization_id=organization_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if not crud.user.is_superuser(current_user) and (event.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    event = crud.event.remove(db=db, id=id)
    return event
