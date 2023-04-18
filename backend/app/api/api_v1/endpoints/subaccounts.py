from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import paginate
from sqlalchemy.orm import Session

from app import crud, models, models, utils
from app.api import deps
from app.middleware.pagination import JsonApiPage

router = APIRouter()


@router.get("/resolve", response_model=JsonApiPage[models.ResolvedBankAccount])
def resolve_account_number(
    account_number: str,
    bank_code: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Resolves the account details of a given account number and bank code
    Raises:
        ValueError: If the account number and bank code combination is invalid
    """
    resolved_bank_account = utils.bank.resolve_account_number(account_number=account_number, bank_code=bank_code)
    return resolved_bank_account


@router.get("/banks", response_model=JsonApiPage[models.PaystackBank])
def get_banks(
    bank_code: str,
    country: str,
    items_per_page: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List:
    """Gets a list of banks and their bank codes
    """
    return utils.bank.get_bank_list(country=country, items_per_page=100)

@router.get("", response_model=JsonApiPage[models.EventRead])
def read_subaccounts(
    organization_id: str,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    organization: models.Organization = Depends(deps.get_organization),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieves subaccounts created under a user's organization
    Returns all subaccounts if user is a superuser
    """
    if crud.user.is_superuser(current_user):
        subaccounts = crud.subaccount.get_multi(db, skip=skip, limit=limit)
    else:
        subaccounts = crud.subaccount.get_multi_by_owner(
            db=db, user_id=current_user.uuid, skip=skip, limit=limit,
            organization_id=organization.uuid,
        )
    return paginate(subaccounts)


@router.post("", response_model=models.EventRead)
def create_subaccount(
    *,
    organization_id: str,
    db: Session = Depends(deps.get_db),
    subaccount_in: models.EventCreate,
    organization: models.Organization = Depends(deps.get_organization),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new subaccount.
    """
    subaccount = crud.subaccount.create_with_owner(db=db, obj_in=subaccount_in, user=current_user, organization=organization)
    return subaccount


@router.put("/{subaccount_id}", response_model=models.EventRead)
def update_subaccount(
    *,
    db: Session = Depends(deps.get_db),
    subaccount_id: str,
    subaccount_in: models.EventUpdate,
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
    subaccount = crud.subaccount.update(db=db, db_obj=subaccount, obj_in=subaccount_in)
    return subaccount


@router.get("/{subaccount_id}", response_model=models.EventRead)
def read_subaccount(
    *,
    db: Session = Depends(deps.get_db),
    subaccount_id: int,
    organization_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get organization by ID.
    """
    subaccount = crud.subaccount.get(db=db, uuid=subaccount_id)
    if not subaccount:
        raise HTTPException(status_code=404, detail="Event not found")
    if not crud.user.is_superuser(current_user) and (subaccount.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return subaccount


@router.delete("/{subaccount_id}", response_model=models.EventRead)
def delete_subaccount(
    *,
    db: Session = Depends(deps.get_db),
    subaccount_id: int,
    organization_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Removes a subaccount from the commercial space
    """
    subaccount = crud.subaccount.get(db=db, uuid=subaccount_id)
    if not subaccount:
        raise HTTPException(status_code=404, detail="Event not found")
    if not crud.user.is_superuser(current_user) and (subaccount.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    subaccount = crud.subaccount.remove(db=db, id=id)
    return subaccount
