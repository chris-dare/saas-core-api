import datetime
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(
        self, db: Session, id: Optional[Any] = None, uuid: Optional[Any] = None
    ) -> Optional[ModelType]:
        if id:
            return db.query(self.model).filter(self.model.id == id).first()
        elif uuid:
            return db.query(self.model).filter(self.model.uuid == uuid).first()
        else:
            raise ValueError("QueryError. No id or uuid for object search provided!")

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, uuid: Optional[Any], obj: ModelType = None, soft_delete: bool = True) -> ModelType:
        if not obj:
            # confirm that we're deleting the right type of object for this manager class
            statement = select(
                self.model
            ).where(
                self.model.uuid == uuid,
            )
            obj = await db.execute(statement=statement)
        elif not isinstance(obj, self.model):
            raise ValueError("Technical error: Invalid object provided for deletion!")
        if soft_delete:
            obj.is_deleted = True
            obj.deleted_at = datetime.datetime.now()
            db.add(obj)
        else:
            db.delete(obj)
        await db.commit()
        return obj
