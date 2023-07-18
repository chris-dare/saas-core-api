from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import paginate
from sqlalchemy.orm import Session

from app import crud, models, models
from app.api import deps
from app.middleware.pagination import JsonApiPage

router = APIRouter()


@router.get("/", response_model=JsonApiPage[models.BillRead])
async def read_subscriptions(
    db: Session = Depends(deps.get_async_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieves subscriptions created under a user's organization
    Returns all subscriptions if user is a superuser
    """
    subscriptions = await crud.bill.get_multi_by_owner(
        db=db, customer_id=current_user.uuid, skip=skip, limit=limit,
    )
    return paginate(subscriptions)


@router.post("/", response_model=models.BillRead)
async def create_subscription(
    *,
    db: Session = Depends(deps.get_async_db),
    subscription_in: models.BillCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    This endpoint creates a draft subscription for a given customer which allows you to pay or send the invoice to your customers.
    """
    try:
        subscription = await crud.bill.create_with_owner(db=db, obj_in=subscription_in, user=current_user)
        return subscription
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{subscription_id}", response_model=models.BillRead)
async def update_subscription(
    *,
    db: Session = Depends(deps.get_async_db),
    subscription_id: str,
    subscription_in: models.BillUpdate,
    organization: models.Organization = Depends(deps.get_organization),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a subscription
    """
    subscription = await crud.bill.get(db=db, uuid=subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    if not crud.user.is_superuser(current_user) and (bill.customer_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    subscription = await crud.bill.update(db=db, db_obj=bill, obj_in=subscription_in)
    return subscription


@router.get("/{subscription_id}", response_model=models.BillRead)
async def read_subscription(
    *,
    db: Session = Depends(deps.get_async_db),
    subscription_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get subscription by ID
    """
    subscription = await crud.bill.get(db=db, uuid=subscription_id, customer_id=current_user.uuid)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription


@router.delete("/{subscription_id}", response_model=models.BillRead)
def cancel_subscription(
    *,
    db: Session = Depends(deps.get_db),
    subscription_id: int,
    organization_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Cancels a subscription
    """
    subscription = crud.bill.get(db=db, uuid=subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    if not crud.user.is_superuser(current_user) and (bill.customer_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    subscription = crud.bill.remove(db=db, id=id)
    return subscription
