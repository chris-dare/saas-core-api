import datetime
import uuid as uuid_pkg
from typing import Any, Optional

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


@router.get("/", response_model=JsonApiPage[models.WalletRead])
async def read_wallets(
    db: Session = Depends(deps.get_async_db),
    offset: int = 0,
    limit: int = 100,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[OAuthScopeType.READ_CURRENT_USER],
    ),
    managing_organization_id: Optional[uuid_pkg.UUID] = None,
) -> Any:
    """
    Retrieves a list of wallets
    """
    wallets = await crud.wallet.get_multi(
        db=db,
        limit=limit,
        skip=offset,
        managing_organization_id=managing_organization_id,
        owner_id=current_user.uuid,
    )
    return paginate(wallets)


@router.get("/{wallet_id}", response_model=models.WalletRead)
async def read_wallet_by_id(
    wallet_id: str,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[OAuthScopeType.READ_USERS],
    ),
    db: Session = Depends(deps.get_async_db),
) -> Any:
    """
    Get a specific wallet by id
    """
    wallet = await crud.wallet.get(db=db, uuid=wallet_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    if not crud.wallet.is_superuser(current_user) and (
        wallet.wallet_id != current_user.id
    ):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return wallet
