import uuid as uuid_pkg
from typing import Optional

from app import models, schemas
from app.utils import get_country_currency, quantize_monetary_number
from fastapi.encoders import jsonable_encoder
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from .crud_base import CRUDBase


class CRUDOrganization(
    CRUDBase[models.Organization, models.OrganizationCreate, models.OrganizationRead]
):
    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: models.OrganizationCreate,
        current_user: models.User,
    ) -> models.Organization:
        from app import crud

        # set the current auth user as owner if no owner is provided
        if not obj_in.owner_id:
            obj_in.owner_id = current_user.uuid

        if current_user.uuid != obj_in.owner_id:
            raise ValueError(
                "Can't create organization for another user."
                + " Invite them to create instead"
            )
        # find all organizations with existing name or owned by the obj_in.owner_id
        statement = select(models.Organization).where(
            or_(
                models.Organization.name_chars == obj_in.name_chars(),
                models.Organization.owner_id == obj_in.owner_id,
            )
        )
        results = await db.execute(statement)
        records = results.scalars().all()
        error_messages = []
        for i in records:
            if i.name == obj_in.name:
                error_messages.append("An organization with this name already exists")
            if i.owner_id == obj_in.owner_id:
                error_messages.append(
                    f"User has already created {len(records)} organizations"
                    + " (Maximum allowed is 1)"
                )
        if error_messages:
            raise ValueError(", ".join(error_messages))

        owner = (
            current_user
            if current_user.uuid == obj_in.owner_id
            else await crud.user.get_by_uuid(obj_in.owner_id)
        )
        currency = get_country_currency(country=obj_in.country)
        obj_in_data = jsonable_encoder(obj_in)
        org_db_obj = models.Organization(
            **obj_in_data,
            owner_first_name=owner.first_name,
            owner_last_name=owner.last_name,
            created_by_id=current_user.uuid,
            created_by_name=current_user.full_name,
            default_wallet_currency=currency,
            name_chars=obj_in.name_chars(),
        )
        db.add(org_db_obj)
        # Create a default healthcare policy
        policy_in = models.WalletPolicyCreate(
            name="Default",
            managing_organization_id=org_db_obj.uuid,
            contribution_type=schemas.PaymentContributionType.COINSURANCE,
            coinsurance=quantize_monetary_number(0),
            currency=org_db_obj.default_wallet_currency,
        )
        policy_obj = await crud.wallet_policy.create(
            db=db,
            obj_in=policy_in,
            is_core=True,
            managing_organization=org_db_obj,
            commit=False,
        )
        db.add(policy_obj)
        # Create org managed healthcare wallet for user
        # allow return of uncommited object so it happens all together here
        # i.e. (commit=False)
        wallet_db_obj: models.Wallet = await crud.wallet.create(
            db=db,
            owner=current_user,
            managing_organization=org_db_obj,
            balance=quantize_monetary_number("0.00"),
            obj_in=models.WalletCreate(
                currency=currency,
                owner_id=org_db_obj.owner_id,
                managing_organization_id=org_db_obj.uuid,
            ),
            commit=False,
        )
        db.add(wallet_db_obj)
        await db.commit()
        # apply the policy to the wallet
        wallet_db_obj: models.Wallet = await crud.wallet.apply_policy(
            db=db, db_obj=wallet_db_obj, policy_obj=policy_obj, commit=True
        )
        await db.refresh(org_db_obj)
        return org_db_obj

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        owner_id: Optional[uuid_pkg.UUID] = None,
    ):
        stmt = select(models.Organization)
        if owner_id:
            stmt = stmt.where(
                models.Organization.owner_id == owner_id,
            )
        stmt = stmt.offset(skip).limit(limit)
        stmt = stmt.order_by(models.Organization.name)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get(
        self,
        db: AsyncSession,
        uuid: uuid_pkg.UUID,
        owner_id: uuid_pkg.UUID = None,
    ) -> Optional[models.Organization]:
        stmt = select(self.model).where(
            self.model.uuid == uuid,
        )
        if owner_id:
            stmt = stmt.where(
                self.model.owner_id == owner_id,
            )
        obj = await db.execute(statement=stmt)
        return obj.scalar_one_or_none()

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: models.Organization,
        obj_in: models.OrganizationUpdate,
    ) -> models.Organization:
        raise NotImplementedError

    async def remove(
        self,
        db: AsyncSession,
        *,
        uuid: Optional[uuid_pkg.UUID],
        obj: models.Organization = None,
        soft_delete: bool = True,
    ) -> models.Organization:
        raise NotImplementedError


organization = CRUDOrganization(models.Organization)
