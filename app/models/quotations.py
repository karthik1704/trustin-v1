from decimal import Decimal
from sqlalchemy import (
    Column,
    Integer,
    Nullable,
    String,
    ForeignKey,
    Boolean,
    Table,
    func,
    UUID,
    Date,
    DateTime,
    Text,
)
from typing import Any, List, Optional
from datetime import date, datetime

# from sqlalchemy.orm import relationship
from sqlalchemy.orm import mapped_column, Mapped, relationship, joinedload, Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models import Base
from app.models.customers import Customer
from app.models.samples import TestingParameter


class Quotation(Base):
    __tablename__ = "quotations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quatation_code: Mapped[str] = mapped_column(String, nullable=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey(Customer.id))



    @classmethod
    async def get_all(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions).order_by(desc(cls.id))
        _result = await database_session.execute(_stmt)
        return _result.scalars().all()

    @classmethod
    async def get_one(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars().first()


    def update_quatation(self, updated_data):
        for field, value in updated_data.items():
            setattr(self, field, value)


class QuotationTestParameter(Base):
    __tablename__ = "quotation_test_parameters"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    quotation_id :Mapped[int] = mapped_column(Integer, ForeignKey(Quotation.id, ondelete="CASCADE"), )
    test_parameter_id: Mapped[int] = mapped_column(Integer, ForeignKey(TestingParameter.id))
    amount:Mapped[Decimal] 
 

    
    @classmethod
    async def get_all(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions).order_by(desc(cls.id))
        _result = await database_session.execute(_stmt)
        return _result.scalars().all()

    @classmethod
    async def get_one(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars().first()


    def update_quatation(self, updated_data):
        for field, value in updated_data.items():
            setattr(self, field, value)

