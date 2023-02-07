from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import paginate
from sqlalchemy.orm import Session

from app import crud, models, models
from app.api import deps
from app.middleware.pagination import JsonApiPage

router = APIRouter()


@router.get("/", response_model=JsonApiPage[models.BillRead])
def read_bills(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieves bills created under a user's organization
    Returns all bills if user is a superuser
    """
    if crud.user.is_superuser(current_user):
        bills = crud.bill.get_multi(db, skip=skip, limit=limit)
    else:
        bills = crud.bill.get_multi_by_owner(
            db=db, user_id=current_user.uuid, skip=skip, limit=limit,
        )
    return paginate(bills)


@router.post("/", response_model=models.BillRead)
def create_bill(
    *,
    db: Session = Depends(deps.get_db),
    bill_in: models.BillCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    This endpoint creates a draft bill for a given customer which allows you to pay or send the invoice to your customers.
    """
    bill = crud.bill.create_with_owner(db=db, obj_in=bill_in, user=current_user)
    return bill


@router.put("/{bill_id}", response_model=models.BillRead)
def update_bill(
    *,
    db: Session = Depends(deps.get_db),
    bill_id: str,
    bill_in: models.BillUpdate,
    organization: models.Organization = Depends(deps.get_organization),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a bill
    """
    bill = crud.bill.get(db=db, uuid=bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    if not crud.user.is_superuser(current_user) and (bill.customer_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    bill = crud.bill.update(db=db, db_obj=bill, obj_in=bill_in)
    return bill


@router.get("/{bill_id}", response_model=models.BillRead)
def read_bill(
    *,
    db: Session = Depends(deps.get_db),
    bill_id: int,
    organization_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get bill by ID
    """
    bill = crud.bill.get(db=db, uuid=bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    if not crud.user.is_superuser(current_user) and (bill.customer_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return bill


@router.delete("/{bill_id}", response_model=models.BillRead)
def cancel_bill(
    *,
    db: Session = Depends(deps.get_db),
    bill_id: int,
    organization_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Cancels a bill
    """
    bill = crud.bill.get(db=db, uuid=bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    if not crud.user.is_superuser(current_user) and (bill.customer_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    bill = crud.bill.remove(db=db, id=id)
    return bill
