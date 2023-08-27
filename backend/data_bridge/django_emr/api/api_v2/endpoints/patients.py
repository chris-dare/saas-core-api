from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi_pagination import paginate
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session
from sqlmodel import select

from data_bridge.core import security
from data_bridge.django_emr import crud as django_emr_crud
from data_bridge.django_emr import models as django_emr_models
from data_bridge.django_emr.api import deps as django_emr_deps
from data_bridge.middleware.pagination import JsonApiPage

router = APIRouter()


@router.get("/{mr_number}", response_model=django_emr_models.Patient)
async def get_patient_by_mr_number(
    mr_number: str,
    current_user: django_emr_models.User = Depends(
        django_emr_deps.get_current_active_user
    ),
    db: Session = Depends(django_emr_deps.get_async_db),
) -> Any:
    """
    Get a specific patient by id
    """
    patient = await django_emr_crud.patient.get_by_mr_number(db=db, mr_number=mr_number)
    if not patient:
        raise HTTPException(
            status_code=404, detail="Couldn't find a patient with this MR number"
        )
    return patient
