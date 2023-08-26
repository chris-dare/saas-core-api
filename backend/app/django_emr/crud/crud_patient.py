from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import CRUDBase
from app.django_emr.models import Patient


class CRUDPatient(CRUDBase[Patient, Patient, Patient]):
    async def get_by_mr_number(
        self, db: AsyncSession, *, mr_number: str
    ) -> Optional[Patient]:
        statement = select(Patient).where(Patient.mr_number == mr_number)
        patient = await db.execute(statement)
        return patient.scalar_one_or_none()


patient = CRUDPatient(Patient)
