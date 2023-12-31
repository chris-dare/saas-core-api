import uuid as uuid_pkg
from typing import Optional

from app import models, schemas
from app.utils import quantize_monetary_number
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .crud_base import CRUDBase


class CRUDWallet(CRUDBase[models.Wallet, models.WalletCreate, models.WalletRead]):
    async def create(
        self,
        db: AsyncSession,
        *,
        owner: models.User,
        managing_organization: models.Organization,
        obj_in: models.WalletCreate,
        balance=quantize_monetary_number("0.00"),
        commit=True,
    ) -> models.Wallet:
        # check if wallet already exists with the same owner_id, currency and
        # managing_organization_id. If it does, raise an error.
        if (
            owner.uuid != obj_in.owner_id
            or managing_organization.uuid != obj_in.managing_organization_id
        ):
            raise ValueError(
                "Technical error: Owner and managing org must match."
                + " Contact developer support"
            )
        wallets = await self.get_multi(
            db,
            owner_id=owner.uuid,
            managing_organization_id=managing_organization.uuid,
            currency=obj_in.currency,
        )
        if wallets:
            raise ValueError(
                "Wallet(s) with the same owner_id, currency and"
                + " managing_organization already exists"
            )

        obj_in_data: models.WalletCreate = jsonable_encoder(obj_in)
        db_obj = models.Wallet(
            **obj_in_data,
            balance=balance,
            owner_name=owner.full_name,
            owner_mobile=owner.mobile,
            managing_organization_name=managing_organization.name,
        )
        if not commit:
            return db_obj
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        owner_id: uuid_pkg.UUID,
        managing_organization_id: uuid_pkg.UUID = None,
        currency: schemas.WalletCurrencyType = None,
        status: schemas.WalletStatusType = None,
        skip: int = 0,
        limit: int = 100,
    ):
        stmt = select(models.Wallet).where(
            models.Wallet.owner_id == owner_id,
        )
        if managing_organization_id:
            stmt = stmt.where(
                models.Wallet.managing_organization_id == managing_organization_id
            )
        if currency:
            stmt = stmt.where(models.Wallet.currency == currency)
        if status:
            stmt = stmt.where(models.Wallet.status == status)
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        wallets = result.scalars().all()
        return wallets

    async def update(
        self, db: AsyncSession, *, db_obj: models.Wallet, obj_in: models.WalletUpdate
    ) -> models.Wallet:
        raise NotImplementedError

    async def apply_policy(
        self,
        db: AsyncSession,
        *,
        db_obj: models.Wallet,
        policy_obj: models.WalletPolicy,
        commit=True,
    ) -> models.Wallet:
        if db_obj.managing_organization_id != policy_obj.managing_organization_id:
            raise ValueError(
                "Unable to attach policy. Policy is managed by a different organization"
            )
        if db_obj.currency != policy_obj.currency:
            raise ValueError("Cannot apply policy to wallet of a different currency")
        db_obj.contribution_type = policy_obj.contribution_type
        if policy_obj.contribution_type == schemas.PaymentContributionType.COINSURANCE:
            db_obj.copay_amount = None
            db_obj.coinsurance = policy_obj.coinsurance
        elif policy_obj.contribution_type == schemas.PaymentContributionType.COPAY:
            db_obj.coinsurance = None
            db_obj.copay_amount = policy_obj.copay_amount
        else:
            # if this case is true,
            # then there's a new type that hasn't been properly accounted for
            # by whoever's ammending the code
            # Raise an error so that it can be flagged by tests
            raise ValueError(
                "Technical error. Unrecognized payment contribution type."
                + " Please contact developers"
            )
        db_obj.deductible = policy_obj.deductible
        db_obj.out_of_pocket_limit = policy_obj.out_of_pocket_limit
        db_obj.policy_id = policy_obj.uuid
        db_obj.policy_name = policy_obj.name
        if not commit:
            return db_obj
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(
        self,
        db: AsyncSession,
        *,
        uuid: Optional[uuid_pkg.UUID],
        obj: models.Wallet = None,
        soft_delete: bool = True,
    ) -> models.Wallet:
        raise NotImplementedError


wallet = CRUDWallet(models.Wallet)
