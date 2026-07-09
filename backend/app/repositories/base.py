"""Shared repository primitives."""

from __future__ import annotations

from typing import Any, Generic, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session


ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Provide basic CRUD helpers for a single ORM model."""

    model: Type[ModelType]
    id_field: str

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, **data: Any) -> ModelType:
        instance = self.model(**data)
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance

    def get_by_id(self, entity_id: str) -> Optional[ModelType]:
        identifier = getattr(self.model, self.id_field)
        statement = select(self.model).where(identifier == entity_id)
        return self.session.scalar(statement)

    def list_all(self) -> list[ModelType]:
        statement = select(self.model)
        return list(self.session.scalars(statement).all())

    def update(self, entity_id: str, **changes: Any) -> Optional[ModelType]:
        instance = self.get_by_id(entity_id)
        if instance is None:
            return None

        for field, value in changes.items():
            setattr(instance, field, value)

        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance

    def delete(self, entity_id: str) -> bool:
        instance = self.get_by_id(entity_id)
        if instance is None:
            return False

        self.session.delete(instance)
        self.session.commit()
        return True
