from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
    DateTime,
    Date,
    func,
    UUID,
    Enum,
)
from typing import Any, Literal, Optional
import datetime

# from sqlalchemy.orm import relationship
from sqlalchemy.orm import mapped_column, Mapped, relationship, joinedload, Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models import Base, Branch, TRF, Customer, TestingParameter, TestType
from pydantic import BaseModel, ConfigDict, ValidationError
from enum import Enum as PyEnum
from .users import Department, User

class ReceivedCondition(PyEnum):
    DAMAGED = 'DAMAGED'
    GOOD = 'GOOD'
class FrontDeskStatus(PyEnum):
    NOT_REGISTRATION = 'NOT_REGISTRATION'
    REGISTRATION = 'REGISTRATION'

class ParcelType(PyEnum):
    SAMPLE = 'SAMPLE'
    Material = 'Material'




class FrontDesk(Base):
    __tablename__ = "frontdesks"
    
    type_annotation_map = {
        PyEnum: Enum(PyEnum, native_enum=False),
    }

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey(Customer.id), nullable=False)
    courier_name: Mapped[str]
    date_of_received: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    parcel_received: Mapped[ParcelType] = mapped_column(Enum(ParcelType))
    received_condition: Mapped[ReceivedCondition] = mapped_column(Enum(ReceivedCondition))
    temperature: Mapped[str]
    deparment_id: Mapped[int] = mapped_column(ForeignKey(Department.id))
    status: Mapped[FrontDeskStatus] = mapped_column(Enum(FrontDeskStatus))

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
    created_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    updated_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    customer: Mapped["Customer"] = relationship(back_populates="front_desks", uselist=False,  lazy="selectin")
    department: Mapped["Department"] = relationship(back_populates="front_desks",   lazy="selectin")

    @classmethod
    async def get_all(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions).order_by(desc(cls.created_at))
        _result = await database_session.execute(_stmt)
        return _result.scalars()

    @classmethod
    async def get_one(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars().first()

    @classmethod
    async def create_front_desk(cls, db: AsyncSession, desk):
        db.add(desk)

    def update_front_desk(self, updated_data):
        for field, value in updated_data.items():
            setattr(self, field, value)
