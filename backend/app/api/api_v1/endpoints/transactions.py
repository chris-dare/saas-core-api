from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import paginate
from sqlalchemy.orm import Session

from app import crud, models, models
from app.api import deps
from app.middleware.pagination import JsonApiPage

router = APIRouter()


@router.get("/", response_model=JsonApiPage[models.TransactionRead])
async def read_transactions(
    db: Session = Depends(deps.get_async_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieves a customer's transactions
    Returns all transactions if user is a superuser
    """
    transactions = await crud.transaction.get_multi_by_owner(
        db=db, customer_id=current_user.uuid, skip=skip, limit=limit,
    )
    return paginate(transactions)


@router.post("/", response_model=models.TransactionRead)
async def initialize_transaction(
    *,
    db: Session = Depends(deps.get_async_db),
    transaction_in: models.TransactionCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Initialize a transaction for a given customer
    """
    bill = await crud.bill.get(db=db, uuid=transaction_in.bill_id)
    transaction = await crud.transaction.create_with_owner(db=db, obj_in=transaction_in, user=current_user, bill=bill)
    return transaction


@router.put("/{transaction_id}", response_model=models.TransactionRead)
async def update_transaction(
    *,
    db: Session = Depends(deps.get_async_db),
    transaction_id: str,
    transaction_in: models.TransactionUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a transaction
    """
    transaction = await crud.transaction.get(db=db, uuid=transaction_id, customer_id=current_user.uuid)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    transaction = await crud.transaction.update(db=db, db_obj=transaction, obj_in=transaction_in)
    return transaction


@router.get("/{transaction_id}", response_model=models.TransactionRead)
async def read_transaction(
    *,
    db: Session = Depends(deps.get_async_db),
    transaction_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get transaction by ID
    """
    transaction = await crud.transaction.get(db=db, uuid=transaction_id, customer_id=current_user.uuid)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.delete("/{transaction_id}", response_model=models.TransactionRead)
async def cancel_transaction(
    *,
    db: Session = Depends(deps.get_async_db),
    transaction_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Cancels a transaction
    """
    transaction = await crud.transaction.get(db=db, uuid=transaction_id, customer_id=current_user.uuid)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if not crud.user.is_superuser(current_user) and (transaction.customer_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    transaction = await crud.transaction.remove(db=db, id=id)
    return transaction
