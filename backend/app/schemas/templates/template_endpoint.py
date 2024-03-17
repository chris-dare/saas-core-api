import datetime
from typing import Any

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


@router.get("/", response_model=JsonApiPage[models.Template])
async def read_templates(
    db: Session = Depends(deps.get_async_db),
    offset: int = 0,
    limit: int = 100,
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[OAuthScopeType.READ_CURRENT_USER],
    ),
) -> Any:
    """
    Retrieves a list of templates
    """
    templates = await crud.template.get_multi(db=db, limit=limit, skip=offset)
    return paginate(templates)


@router.get("/{template_id}", response_model=models.TemplateRead)
async def read_template_by_id(
    template_id: str,
    current_user: models.User = Security(
        deps.get_current_active_superuser,
        scopes=[OAuthScopeType.READ_USERS],
    ),
    db: Session = Depends(deps.get_async_db),
) -> Any:
    """
    Get a specific template by id
    """
    template = await crud.template.get(db=db, uuid=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    if not crud.template.is_superuser(current_user) and (
        template.template_id != current_user.id
    ):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return template
