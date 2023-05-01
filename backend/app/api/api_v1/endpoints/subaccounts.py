from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import paginate
from sqlalchemy.orm import Session

from app import crud, models, models, utils
from app.api import deps
from app.middleware.pagination import JsonApiPage

router = APIRouter()


@router.get("/resolve", response_model=models.ResolvedBankAccount)
async def resolve_account_number(
    account_number: str,
    bank_code: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Retrieves the account details of a given account number and bank code
    Raises:
        HTTPException: If the account number and bank code combination are invalid
    """
    try:
        resolved_bank_account = await utils.bank.resolve_account_number(account_number=account_number, bank_code=bank_code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return resolved_bank_account


@router.get("/banks", response_model=JsonApiPage[models.PaystackBank])
async def get_banks(
    country: str,
    bank_code: Optional[str] = None,
    items_per_page: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List:
    """Gets a list of banks and their bank codes
    """
    banks = await utils.bank.get_bank_list(country=country, items_per_page=items_per_page)
    # go through the list of banks and filter by bank code if provided
    if bank_code:
        for bank in banks:
            if bank.code == bank_code:
                return [bank]
        raise HTTPException(status_code=404, detail="Bank code not found")
    return paginate(banks)

@router.get("", response_model=JsonApiPage[models.SubAccountRead])
async def read_subaccounts(
    db: Session = Depends(deps.get_async_db),
    skip: int = 0,
    limit: int = 100,
    organization: models.Organization = Depends(deps.get_organization),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieves subaccounts created under a user's organization
    """
    if organization.owner_id != current_user.uuid:
        raise HTTPException(status_code=403, detail="Not enough permissions. "
                                                    "You must be the owner of this organization to perform this action")
    subaccounts = await crud.subaccount.get_multi_by_owner(
        db=db, user_id=current_user.uuid, skip=skip, limit=limit,
        organization_id=organization.uuid,
    )
    return paginate(subaccounts)


@router.post("", response_model=models.SubAccountRead)
async def create_subaccount(
    *,
    db: Session = Depends(deps.get_async_db),
    subaccount_in: models.SubAccountCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new subaccount.
    """
    subaccount = await crud.subaccount.create_with_owner(db=db, obj_in=subaccount_in, user=current_user)
    return subaccount


@router.put("/{subaccount_id}", response_model=models.SubAccountUpdate)
async def update_subaccount(
    *,
    db: Session = Depends(deps.get_async_db),
    subaccount_id: str,
    subaccount_in: models.SubAccountUpdate,
    organization: models.Organization = Depends(deps.get_organization),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a subaccount.
    """
    subaccount = crud.subaccount.get(db=db, uuid=subaccount_id)
    if not subaccount:
        raise HTTPException(status_code=404, detail="Event not found")
    if not crud.user.is_superuser(current_user) and (subaccount.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    subaccount = await crud.subaccount.update(db=db, db_obj=subaccount, obj_in=subaccount_in)
    return subaccount


@router.get("/{subaccount_id}", response_model=models.SubAccountRead)
async def read_subaccount(
    *,
    db: Session = Depends(deps.get_db),
    subaccount_id: str,
    organization_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get organization by ID.
    """
    subaccount = await crud.subaccount.get(db=db, uuid=subaccount_id)
    if not subaccount or subaccount.owner_id != current_user.uuid:
        raise HTTPException(status_code=404, detail="Subaccount not found")
    return subaccount


@router.delete("/{subaccount_id}", response_model=models.SubAccountRead)
def delete_subaccount(
    *,
    db: Session = Depends(deps.get_db),
    subaccount_id: str,
    organization_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Removes a subaccount from the commercial space
    """
    raise NotImplementedError("This endpoint is not yet implemented")
    subaccount = crud.subaccount.get(db=db, uuid=subaccount_id)
    if not subaccount:
        raise HTTPException(status_code=404, detail="Event not found")
    if not crud.user.is_superuser(current_user) and (subaccount.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    subaccount = crud.subaccount.remove(db=db, id=id)
    return subaccount
